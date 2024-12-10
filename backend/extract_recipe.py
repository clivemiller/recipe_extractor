import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import json
import re
import logging
import random

# Configure logging once at the module level
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Example USER_AGENTS and PROXIES lists
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    # Add more user agents as needed
]

# PROXIES = [
#     "http://proxy1.example.com:8080",
#     "http://proxy2.example.com:8080",
#     # Add more proxies as needed
# ]

def extract_recipe(url):
    session = requests.Session()
    
    # Define fallback headers
    fallback_headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    # Update session headers with fallback headers
    session.headers.update(fallback_headers)
    
    # Primary headers for the initial request
    primary_headers = {
        "User-Agent": "Mozilla/5.0"
    }
    
    # # Optionally, set a proxy
    # proxy = random.choice(PROXIES)
    # session.proxies.update({
    #     "http": proxy,
    #     "https": proxy
    # })
    
    logger.debug(f"Fetching URL: {url}")
    
    # Define a helper function to make requests
    def make_request(headers):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
            return response
        except requests.RequestException as e:
            logger.error(f"Request with headers {headers} failed: {e}")
            return None
    
    # First attempt with primary headers
    response = make_request(primary_headers)
    
    # If the first attempt fails, retry with fallback headers
    if response is None:
        logger.info("Retrying with fallback headers...")
        response = make_request(session.headers)
    
    # If both attempts fail, return None
    if response is None:
        logger.error("Both attempts to fetch the URL failed.")
        return None
    
    # Proceed with processing the successful response
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check for WPRM (WP Recipe Maker) structured data
    isWPRM = soup.select_one('.wprm-recipe-ingredients-container')
    
    # 1. Check if Smitten Kitchen
    if "smittenkitchen.com" in url:
        logger.debug("URL is from Smitten Kitchen.")
        smitten_recipe = extract_smittenkitchen_recipe(soup)
        if smitten_recipe:
            logger.debug("Successfully extracted Smitten Kitchen recipe.")
            return smitten_recipe
        else:
            logger.debug("Failed to extract Smitten Kitchen recipe.")
    
    # 2. Check if WPRM
    elif isWPRM:
        logger.debug("URL is from a WPRM site.")
        wprm_recipe = extract_wprm_recipe(soup)
        if wprm_recipe:
            logger.debug("Successfully extracted WPRM recipe.")
            return wprm_recipe
        else:
            logger.debug("Failed to extract WPRM recipe.")
    
    # 3. Check if Tasty Recipes
    elif soup.select_one('.tasty-recipes-entry-content'):
        logger.debug("URL is from a Tasty Recipes site.")
        tasty_recipe = extract_tasty_recipes(soup)
        if tasty_recipe:
            logger.debug("Successfully extracted Tasty Recipes recipe.")
            return tasty_recipe
        else:
            logger.debug("Failed to extract Tasty Recipes recipe.")
    
    # 4. Check if Food Network
    elif soup.select_one('section.o-AssetTitle'):
        logger.debug("URL is from a Food Network site.")
        foodnetwork_recipe = extract_foodnetwork_recipe(soup)
        if foodnetwork_recipe:
            logger.debug("Successfully extracted Food Network recipe.")
            return foodnetwork_recipe
        else:
            logger.debug("Failed to extract Food Network recipe.")
    
    # 5. Structured data (JSON-LD)
    else:
        structured_recipe = extract_recipe_from_jsonld(soup)
        if structured_recipe:
            logger.debug("Found structured data.")
            name = structured_recipe.get('name', '')
            ingredients = structured_recipe.get('recipeIngredient', [])
            instructions_data = structured_recipe.get('recipeInstructions', [])
            instructions = []
            if isinstance(instructions_data, list):
                for step in instructions_data:
                    if isinstance(step, str):
                        instructions.append(step)
                    elif isinstance(step, dict) and 'text' in step:
                        instructions.append(step['text'])
            else:
                if isinstance(instructions_data, str):
                    instructions = [instructions_data]
    
            return {
                "name": name,
                "ingredients": ingredients,
                "instructions": instructions
            }
    
        logger.debug("No structured data found.")
    
    logger.warning("No suitable recipe format found on the page.")
    return None

def extract_smittenkitchen_recipe(soup):
    def is_within_ad_div(tag):
        """Check if a tag is within an advertisement div."""
        return any(
            parent.name == 'div' and any(cls.startswith('code-block') for cls in parent.get('class', []))
            for parent in tag.parents
        )

    try:
        logger.debug("Starting Smitten Kitchen recipe extraction.")

        # Extract Recipe Name
        name_tag = soup.select_one('h1.entry-title')
        recipe_name = name_tag.get_text(" ", strip=True) if name_tag else "Untitled Recipe"
        if name_tag:
            logger.debug(f"Extracted recipe name: {recipe_name}")
        else:
            logger.debug("Recipe name not found. Using default title.")

        # Extract Ingredients
        ingredients = []
        ingredients_container = soup.select_one('.jetpack-recipe-ingredients')
        if ingredients_container:
            logger.debug("Found ingredients container.")
            for li in ingredients_container.find_all('li', class_='jetpack-recipe-ingredient'):
                if not is_within_ad_div(li):
                    text = li.get_text(" ", strip=True)
                    if text:
                        ingredients.append(text)
                        logger.debug(f"Extracted ingredient: {text}")
        else:
            logger.warning("Ingredients container not found.")

        # Extract Instructions
        instructions = []
        instructions_container = soup.select_one('.jetpack-recipe-directions.e-instructions')
        if instructions_container:
            logger.debug("Found instructions container.")

            # Navigate to the parent <p> tag
            parent_p = instructions_container.find_parent('p')
            if parent_p:
                logger.debug("Located parent <p> of instructions container.")

                # Initialize a list to collect all relevant <p> tags (including parent_p)
                relevant_ps = [parent_p]

                # Collect all subsequent sibling <p> tags that contain instruction steps
                for sibling in parent_p.find_next_siblings('p'):
                    # Stop if we reach a <p> that signifies the end of instructions (e.g., another section)
                    # Adjust this condition based on the actual HTML structure
                    if sibling.find(['h2', 'h3', 'h4']):
                        logger.debug("Encountered a new section. Stopping instruction extraction.")
                        break

                    relevant_ps.append(sibling)

                logger.debug(f"Number of <p> tags to process for instructions: {len(relevant_ps)}")

                # Iterate through each relevant <p> tag to extract instruction steps
                for p in relevant_ps:
                    # Since there are no ads within <p> tags, we don't need to skip any
                    # Find the <b> tag which denotes the step title
                    b_tag = p.find('b')
                    if b_tag:
                        step_title = b_tag.get_text(strip=True).rstrip(':')
                        logger.debug(f"Extracted step title: {step_title}")

                        # Extract the step description by getting all content after the <b> tag
                        step_description_elements = b_tag.next_siblings
                        step_description = []
                        for elem in step_description_elements:
                            if isinstance(elem, Tag):
                                text = elem.get_text(" ", strip=True)
                                if text:
                                    step_description.append(text)
                            elif isinstance(elem, NavigableString):
                                text = elem.strip()
                                if text:
                                    step_description.append(text)
                        step_description_text = ' '.join(step_description)
                        instructions.append(f"{step_title}: {step_description_text}")
                        logger.debug(f"Added instruction step: {step_title}: {step_description_text}")
                    else:
                        # If no <b> tag, treat the entire <p> text as a single instruction step without a title
                        step_text = p.get_text(" ", strip=True)
                        if step_text:
                            instructions.append(step_text)
                            logger.debug(f"Added instruction step without title: {step_text}")
            else:
                logger.warning("Parent <p> of instructions container not found.")
        else:
            logger.warning("Instructions container not found.")

        # Return the extracted recipe
        if ingredients or instructions:
            return {
                "name": recipe_name,
                "ingredients": ingredients,
                "instructions": instructions
            }
        else:
            logger.warning("No ingredients or instructions extracted.")
            return None

    except Exception as e:
        logger.error(f"Error extracting recipe: {e}")
        return None
    
def extract_wprm_recipe(soup):
    print("DEBUG: Starting WPRM recipe extraction.")

    name_tag = soup.select_one('.wprm-recipe-name')
    recipe_name = name_tag.get_text(" ", strip=True) if name_tag else "Untitled Recipe"

    print(f"DEBUG: Name Container: {name_tag}")
    print(f"DEBUG: Name Container: {recipe_name}")
    
    # Extract ingredients
    ingredients = []
    ingredients_container = soup.select_one('.wprm-recipe-ingredient-group')
    if not ingredients_container:
        print("DEBUG: Ingredients container not found.")
    else:
        print("DEBUG: Found ingredients container.")
        li_tags = ingredients_container.find_all('li', class_='wprm-recipe-ingredient')
        for li in li_tags:
            # Extract amount
            amount = li.find('span', class_='wprm-recipe-ingredient-amount')
            amount_text = amount.get_text(" ", strip=True) if amount else ""
            
            # Extract unit
            unit = li.find('span', class_='wprm-recipe-ingredient-unit')
            unit_text = unit.get_text(" ", strip=True) if unit else ""
            
            # Extract ingredient name
            name = li.find('span', class_='wprm-recipe-ingredient-name')
            if name:
                # Some ingredients have links, some don't
                ingredient_text = name.get_text(" ", strip=True)
            else:
                ingredient_text = ""
            
            # Combine amount, unit, and name
            if amount_text and unit_text:
                full_ingredient = f"{amount_text} {unit_text} {ingredient_text}"
            elif amount_text:
                full_ingredient = f"{amount_text} {ingredient_text}"
            else:
                full_ingredient = ingredient_text
            
            # Extract notes if any
            notes = li.find('span', class_='wprm-recipe-ingredient-notes')
            if notes:
                notes_text = notes.get_text(" ", strip=True)
                full_ingredient += f" {notes_text}"
            
            print(f"DEBUG: Extracted ingredient: {full_ingredient}")
            if full_ingredient:
                ingredients.append(full_ingredient)

    # Extract instructions
    instructions = []
    instructions_container = soup.select_one('.wprm-recipe-instructions')
    if not instructions_container:
        print("DEBUG: Instructions container not found.")
    else:
        print("DEBUG: Found instructions container.")

        # Remove ads, scripts, and irrelevant elements
        for ad in instructions_container.select('.wprm-recipe-instruction-image, iframe, script, .ad-container'):
            print(f"DEBUG: Removing ad or irrelevant element: {ad}")
            ad.decompose()

        # Attempt to find individual instruction steps
        instruction_steps = instructions_container.find_all('div', class_='wprm-recipe-instruction-text')
        if instruction_steps:
            print("DEBUG: Found separate instruction steps.")
            for step in instruction_steps:
                step_text = step.get_text(" ", strip=True)
                if step_text:
                    instructions.append(step_text)
                    print(f"DEBUG: Extracted instruction step: {step_text}")
        else:
            # If instructions are in a single paragraph with numbering
            print("DEBUG: No separate instruction steps found. Checking for single paragraph with numbering.")
            paragraphs = instructions_container.find_all(['p', 'div'])
            for p in paragraphs:
                text = p.get_text(" ", strip=True)
                if not text:
                    continue

                # Use regex to split instructions based on numbering (e.g., "1. ", "2. ", etc.)
                # This regex looks for numbers followed by a dot and a space or similar pattern
                split_steps = re.split(r'\b\d+\.\s+', text)
                # The first split item might be empty if the text starts with a number
                if split_steps and split_steps[0].strip() == '':
                    split_steps = split_steps[1:]
                
                # Find all step numbers to reconstruct step numbering
                step_numbers = re.findall(r'\b\d+\.\s+', text)
                for i, step in enumerate(split_steps):
                    if i < len(step_numbers):
                        step_number = step_numbers[i].strip()
                        step_text = f"{step_number} {step.strip()}"
                    else:
                        step_text = step.strip()
                    if step_text:
                        instructions.append(step_text)
                        print(f"DEBUG: Extracted instruction step: {step_text}")

    print("DEBUG: Final extracted ingredients:", ingredients)
    print("DEBUG: Final extracted instructions:", instructions)

    return {
        "name": recipe_name,
        "ingredients": ingredients,
        "instructions": instructions
    } if ingredients or instructions else None

def extract_tasty_recipes(soup):
    """
    Extract recipe data from pages using the Tasty Recipes format, including handling grouped ingredients.
    
    :param soup: BeautifulSoup object of the page HTML
    :return: Dictionary containing recipe name, ingredients, and instructions
    """
    logger.debug("Starting Tasty Recipes extraction.")
    
    # Extract Recipe Name
    name_tag = soup.select_one('.tasty-recipes-title')
    recipe_name = name_tag.get_text(strip=True) if name_tag else "Untitled Recipe"
    logger.debug(f"Extracted recipe name: {recipe_name}")
    
    # Extract Ingredients (handling grouped sections)
    ingredients = []
    ingredients_container = soup.select_one('.tasty-recipes-ingredients-body')
    logger.debug(f"Initail container: {ingredients_container}")
    if ingredients_container == None:
        ingredients_container_container = soup.select_one('.tasty-recipes-ingredients')
        logger.debug(f"Fallback container container: {ingredients_container_container}")
        if ingredients_container_container: 
            logger.debug("Found fallback container.")
            ingredients_container = ingredients_container_container.select_one('[data-tasty-recipes-customization="body-color.color"]')
            logger.debug(f"fallback container: {ingredients_container}")
        
            # Step 1: Remove all advertisement and irrelevant elements within the ingredients container
            ad_selectors = ['div[id^="AdThrive"]', 'iframe', 'script', '.ad-container']
            for ad in ingredients_container.select(', '.join(ad_selectors)):
                ad.decompose()
                logger.debug("Removed an advertisement or irrelevant element from ingredients.")
            
            # Step 2: Iterate over each ingredient group
            for group in ingredients_container.find_all(['p', 'ul']):
                if group.name == 'p':
                    # Start a new ingredient group
                    current_group = group.get_text(strip=True)
                    ingredients.append(f"{current_group}:")
                    logger.debug(f"Started new ingredient group: {current_group}")
                elif group.name == 'ul':
                    # Process all <li> elements within the current <ul>
                    li_elements = group.find_all('li')
                    logger.debug(f"Found ingredient group list: {li_elements}")
                    for li in li_elements:
                        ingredient_text = li.get_text(" ", strip=True)
                        if ingredient_text:
                            # Append the ingredient with indentation for clarity
                            ingredients.append(f"  - {ingredient_text}")
                            logger.debug(f"Extracted ingredient: {ingredient_text}")
    elif ingredients_container:
        logger.debug("Found ingredients container.")
        
        # Step 1: Remove all advertisement and irrelevant elements within the ingredients container
        ad_selectors = ['div[id^="AdThrive"]', 'iframe', 'script', '.ad-container']
        for ad in ingredients_container.select(', '.join(ad_selectors)):
            ad.decompose()
            logger.debug("Removed an advertisement or irrelevant element from ingredients.")
        
        # Step 2: Iterate over each ingredient group
        for group in ingredients_container.find_all(['h4', 'ul']):
            if group.name == 'h4':
                # Start a new ingredient group
                current_group = group.get_text(strip=True)
                ingredients.append(f"{current_group}:")
                logger.debug(f"Started new ingredient group: {current_group}")
            elif group.name == 'ul':
                # Process all <li> elements within the current <ul>
                li_elements = group.find_all('li')
                logger.debug(f"Found ingredient group list: {li_elements}")
                for li in li_elements:
                    ingredient_text = li.get_text(" ", strip=True)
                    if ingredient_text:
                        # Append the ingredient with indentation for clarity
                        ingredients.append(f"  - {ingredient_text}")
                        logger.debug(f"Extracted ingredient: {ingredient_text}")
    else:
        logger.warning("Ingredients container not found.")
    
    # Extract Instructions
    instructions = []
    instructions_container = soup.select_one('.tasty-recipes-instructions-body')

    if instructions_container == None:
        instructions_container_container = soup.select_one('.tasty-recipes-instructions')
        if instructions_container_container:
            instructions_container = instructions_container_container.select_one('[data-tasty-recipes-customization="body-color.color"]')
            logger.debug("Found fallback instructions container.")
            
            # Iterate over each instruction step
            for _ in instructions_container.find_all('ol'):
                for li in instructions_container.find_all('li'):
                    instruction_text = li.get_text(" ", strip=True)
                    if instruction_text:
                        instructions.append(instruction_text)
                        logger.debug(f"Extracted instruction step: {instruction_text}")
    elif instructions_container:
        logger.debug("Found instructions container.")
        
        # Remove all advertisement and irrelevant elements within the instructions container
        ad_selectors = ['div[id^="AdThrive"]', 'iframe', 'script', '.ad-container']
        for ad in instructions_container.select(', '.join(ad_selectors)):
            ad.decompose()
            logger.debug("Removed an advertisement or irrelevant element from instructions.")
        
        # Iterate over each instruction step
        for li in instructions_container.find_all('li'):
            instruction_text = li.get_text(" ", strip=True)
            if instruction_text:
                instructions.append(instruction_text)
                logger.debug(f"Extracted instruction step: {instruction_text}")
    else:
        logger.warning("Instructions container not found.")
    
    # Combine and return the result
    recipe_data = {
        "name": recipe_name,
        "ingredients": ingredients,
        "instructions": instructions
    }
    
    # Only return the recipe if there is meaningful content
    if ingredients or instructions:
        logger.debug("Successfully extracted Tasty Recipes recipe.")
        return recipe_data
    else:
        logger.warning("No ingredients or instructions found.")
        return None

def extract_recipe_from_jsonld(soup):
    jsonld_tags = soup.find_all('script', type='application/ld+json')
    for tag in jsonld_tags:
        if not tag.string:
            continue
        try:
            data = json.loads(tag.string.strip())
            candidates = data if isinstance(data, list) else [data]
            for item in candidates:
                if item.get('@type', '') == 'Recipe' or 'recipeInstructions' in item:
                    return item
        except (ValueError, TypeError) as e:
            print(f"DEBUG: JSON-LD parsing error: {e}")
            continue
    return None

def extract_foodnetwork_recipe(soup):
    """
    Extract recipe data from Food Network pages with a specific HTML structure.
    
    :param soup: BeautifulSoup object of the page HTML
    :return: Dictionary containing recipe name, ingredients, and instructions
    """
    logger.debug("Starting Food Network recipe extraction.")
    
    try:
        # Extract Recipe Name
        name_section = soup.select_one('section.o-AssetTitle')
        if not name_section:
            logger.warning("Recipe title section not found.")
            recipe_name = "Untitled Recipe"
        else:
            name_tag = name_section.select_one('h1.o-AssetTitle__a-Headline > span.o-AssetTitle__a-HeadlineText')
            recipe_name = name_tag.get_text(strip=True) if name_tag else "Untitled Recipe"
            if name_tag:
                logger.debug(f"Extracted recipe name: {recipe_name}")
            else:
                logger.debug("Recipe name not found. Using default title.")
        
        # Extract Ingredients
        ingredients = []
        ingredients_section = soup.select_one('section.o-Ingredients[data-module="recipe-ingredients"]')
        if not ingredients_section:
            logger.warning("Ingredients section not found.")
        else:
            logger.debug("Found ingredients section.")
            ingredient_elements = ingredients_section.select('p.o-Ingredients__a-Ingredient')
            logger.debug(f"Found {len(ingredient_elements)} ingredient elements.")
            
            for idx, ingredient_p in enumerate(ingredient_elements):
                # Skip the first ingredient if it's "Deselect All"
                if idx == 0:
                    label = ingredient_p.find('span', class_='o-Ingredients__a-Ingredient--CheckboxLabel')
                    if label and "Deselect All" in label.get_text():
                        logger.debug("Skipping 'Deselect All' ingredient.")
                        continue
                
                label = ingredient_p.find('span', class_='o-Ingredients__a-Ingredient--CheckboxLabel')
                ingredient_text = label.get_text(" ", strip=True) if label else ""
                if ingredient_text:
                    ingredients.append(ingredient_text)
                    logger.debug(f"Extracted ingredient: {ingredient_text}")
        
        # Extract Instructions
        instructions = []
        instructions_section = soup.select_one('section.o-Method[data-module="recipe-method"]')
        if not instructions_section:
            logger.warning("Instructions section not found.")
        else:
            logger.debug("Found instructions section.")
            instruction_steps = instructions_section.select('ol > li.o-Method__m-Step')
            logger.debug(f"Found {len(instruction_steps)} instruction steps.")
            
            for idx, step_li in enumerate(instruction_steps, start=1):
                step_text = step_li.get_text(" ", strip=True)
                if step_text:
                    instructions.append(step_text)
                    logger.debug(f"Extracted instruction step {idx}: {step_text}")
        
        # Return the extracted recipe
        if ingredients or instructions:
            logger.debug("Successfully extracted Food Network recipe.")
            return {
                "name": recipe_name,
                "ingredients": ingredients,
                "instructions": instructions
            }
        else:
            logger.warning("No ingredients or instructions extracted from Food Network recipe.")
            return None
    
    except Exception as e:
        logger.error(f"Error extracting Food Network recipe: {e}")
        return None
