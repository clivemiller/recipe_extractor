import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import json
import re
import logging

# Configure logging once at the module level
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

def extract_recipe(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    print(f"DEBUG: Fetching URL: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.RequestException as e:
        print(f"DEBUG: Request failed: {e}")
        return None

    if response.status_code != 200:
        print(f"DEBUG: Failed to fetch URL. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # 1. Check if Smitten Kitchen
    if "smittenkitchen.com" in url:
        print("DEBUG: URL is from Smitten Kitchen.")
        smitten_recipe = extract_smittenkitchen_recipe(soup)
        if smitten_recipe:
            print("DEBUG: Successfully extracted Smitten Kitchen recipe.")
            return smitten_recipe
        else:
            print("DEBUG: Failed to extract Smitten Kitchen recipe.")

    # 2. Check if Half Baked Harvest
    elif ("halfbakedharvest.com" in url or
      "minimalistbaker.com" in url or
      "davidlebovitz.com" in url or
      "damndelicious.net" in url or
      "loveandlemons.com" in url or
      "feelgoodfoodie.net" in url or
      "servingdumplings.com" in url or
      "budgetbytes.com" in url):
        print("DEBUG: URL is from a supported site (e.g., Half Baked Harvest, Minimalist Baker, David Lebovitz, Damn Delicious, Love and Lemons, Budget Bytes).")
        wprm_recipe = extract_wprm_recipe(soup)
        if wprm_recipe:
            print("DEBUG: Successfully extracted recipe.")
            return wprm_recipe
        else:
            print("DEBUG: Failed to extract recipe.")

    # 3. Structured data (JSON-LD)
    structured_recipe = extract_recipe_from_jsonld(soup)
    if structured_recipe:
        print("DEBUG: Found structured data.")
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

    print("DEBUG: No structured data found.")
    return None
