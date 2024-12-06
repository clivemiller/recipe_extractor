import requests
from bs4 import BeautifulSoup
import json
import re

def is_recipe_like(ingredients, instructions):
    if not ingredients or not instructions:
        return False

    cooking_verbs = ['bake', 'boil', 'simmer', 'stir', 'mix', 'cook', 'grill', 'saute', 'whisk', 'marinate', 'roast']
    instruction_score = sum(any(verb in step.lower() for verb in cooking_verbs) for step in instructions)
    if instruction_score < len(instructions) * 0.3:
        return False

    measurement_words = ['cup', 'cups', 'tbsp', 'tablespoon', 'tsp', 'teaspoon', 'oz', 'ounce', 
                         'pound', 'lb', 'lbs', 'grams', 'g', 'kg', 'ml', 'l', 'pinch', 'clove', 'bunch', 'slice', 'slices']
    ingredient_score = sum(any(mw in ing.lower() for mw in measurement_words) for ing in ingredients)
    if ingredient_score < len(ingredients) * 0.3:
        return False

    return True

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
        except (ValueError, TypeError):
            continue
    return None

def heuristic_search_for_ingredients(soup):
    measurement_words = ['cup', 'cups', 'tbsp', 'tablespoon', 'tsp', 'teaspoon', 'oz', 'ounce', 
                          'pound', 'lb', 'lbs', 'grams', 'g', 'kg', 'ml', 'l', 'pinch', 'clove', 'bunch']
    candidate_ul_lists = []
    for ul in soup.find_all('ul'):
        text_list = [li.get_text(strip=True) for li in ul.find_all('li')]
        if text_list:
            score = sum(any(mw in li.lower() for mw in measurement_words) for li in text_list)
            if score > len(text_list) / 2:
                candidate_ul_lists.append(text_list)
    return candidate_ul_lists

def heuristic_search_for_instructions(soup):
    instruction_candidates = []

    # First try <ol> lists
    for ol in soup.find_all('ol'):
        steps = [li.get_text(strip=True) for li in ol.find_all('li')]
        if len(steps) > 2:
            instruction_candidates.append(steps)

    # Try known selectors
    if not instruction_candidates:
        instruction_containers = soup.select('div.instructions, div.directions')
        for container in instruction_containers:
            text = container.get_text('\n', strip=True)
            steps = [line.strip() for line in text.split('\n') if line.strip()]
            if len(steps) > 2:
                instruction_candidates.append(steps)

    # Try fallback with headings
    if not instruction_candidates:
        for header_text in ['instructions', 'directions', 'method']:
            header = soup.find(lambda tag: tag.name in ['h2','h3','strong','span','b'] and header_text in tag.get_text('', True).lower())
            if header:
                candidate_elements = header.find_all_next(['p','li'], limit=50)
                steps = [el.get_text(strip=True) for el in candidate_elements if el.get_text(strip=True)]
                if len(steps) >= 2:
                    instruction_candidates.append(steps)

    return instruction_candidates

def extract_recipe_heuristically(soup):
    ingredient_candidates = heuristic_search_for_ingredients(soup)
    instruction_candidates = heuristic_search_for_instructions(soup)

    for ingredients in ingredient_candidates:
        for instructions in instruction_candidates:
            if is_recipe_like(ingredients, instructions):
                return {
                    'ingredients': ingredients,
                    'instructions': instructions
                }

    return None

def final_fallback_search(soup):
    keywords = ['recipe', 'ingredients', 'instructions', 'directions', 'cooking']
    candidate_tags = soup.find_all(['div', 'section', 'article', 'span'], 
                                   attrs={'class': True}) + soup.find_all(['div', 'section', 'article', 'span'], 
                                                                           attrs={'id': True})
    filtered_candidates = []
    for tag in candidate_tags:
        attrs_to_check = []
        if tag.get('class'):
            attrs_to_check.extend(tag.get('class'))
        if tag.get('id'):
            attrs_to_check.append(tag.get('id'))

        attr_str = ' '.join(attrs_to_check).lower()
        if any(k in attr_str for k in keywords):
            filtered_candidates.append(tag)

    for container in filtered_candidates:
        container_soup = BeautifulSoup(str(container), 'html.parser')
        result = extract_recipe_heuristically(container_soup)
        if result and is_recipe_like(result['ingredients'], result['instructions']):
            return result

    return None

def extract_wprm_recipe(soup):
    ingredients_container = soup.select_one('.wprm-recipe-ingredients-container')
    instructions_container = soup.select_one('.wprm-recipe-instructions-container')

    ingredients = []
    instructions = []

    if ingredients_container:
        ingredient_items = ingredients_container.select('.wprm-recipe-ingredients li.wprm-recipe-ingredient')
        if not ingredient_items:
            ingredient_items = ingredients_container.find_all('li')
        for item in ingredient_items:
            text = item.get_text(" ", strip=True)
            if text:
                ingredients.append(text)

    if instructions_container:
        instruction_items = instructions_container.select('.wprm-recipe-instructions li.wprm-recipe-instruction')
        if not instruction_items:
            instruction_items = instructions_container.find_all('li')
        for step in instruction_items:
            text = step.get_text(" ", strip=True)
            if text:
                instructions.append(text)

    if ingredients and instructions and is_recipe_like(ingredients, instructions):
        return {
            'ingredients': ingredients,
            'instructions': instructions
        }
    return None

def extract_from_entry_content(soup):
    entry_content = soup.select_one('.entry-content')
    if not entry_content:
        return None

    paragraphs = entry_content.find_all(['p'])
    lines = [p.get_text(" ", strip=True) for p in paragraphs if p.get_text(strip=True)]

    ingredients = []
    instructions = []
    found_ingredients_section = False
    found_instructions_section = False

    ingredients_heading_keywords = ['ingredients']
    instructions_heading_keywords = ['instructions', 'method', 'directions']

    for line in lines:
        lower_line = line.lower()
        if any(kw in lower_line for kw in ingredients_heading_keywords):
            found_ingredients_section = True
            found_instructions_section = False
            continue
        if any(kw in lower_line for kw in instructions_heading_keywords):
            found_instructions_section = True
            found_ingredients_section = False
            continue

        if found_ingredients_section:
            if re.search(r'\d', line) or any(m in lower_line for m in ['cup', 'tablespoon', 'teaspoon', 'tbsp', 'tsp', 'oz', 'ounce', 'pound']):
                ingredients.append(line)
        elif found_instructions_section:
            instructions.append(line)

    if not ingredients and not instructions:
        possible_ingredients = [l for l in lines if re.search(r'\d', l.lower()) and any(m in l.lower() for m in ['cup','tbsp','tablespoon','tsp','teaspoon','oz','pound','grams','ml'])]
        possible_instructions = [l for l in lines if any(verb in l.lower() for verb in ['preheat','bake','boil','mix','stir','cook'])]

        if possible_ingredients and possible_instructions:
            ingredients = possible_ingredients
            instructions = possible_instructions

    if ingredients and instructions and is_recipe_like(ingredients, instructions):
        return {
            'ingredients': ingredients,
            'instructions': instructions
        }

    return None

def extract_recipe(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # 1. Structured data
    structured_recipe = extract_recipe_from_jsonld(soup)
    name = ''
    ingredients = []
    instructions = []
    if structured_recipe:
        ingredients = structured_recipe.get('recipeIngredient', [])
        instructions_data = structured_recipe.get('recipeInstructions', [])
        if isinstance(instructions_data, list):
            for step in instructions_data:
                if isinstance(step, str):
                    instructions.append(step)
                elif isinstance(step, dict) and 'text' in step:
                    instructions.append(step['text'])
        else:
            if isinstance(instructions_data, str):
                instructions = [instructions_data]

        name = structured_recipe.get('name', '')

        if is_recipe_like(ingredients, instructions):
            return {
                "name": name,
                "ingredients": ingredients,
                "instructions": instructions
            }

    # 2. Heuristic extraction
    heuristic_recipe = extract_recipe_heuristically(soup)
    if heuristic_recipe and is_recipe_like(heuristic_recipe['ingredients'], heuristic_recipe['instructions']):
        return {
            "name": name or "Unknown Recipe",
            "ingredients": heuristic_recipe['ingredients'],
            "instructions": heuristic_recipe['instructions']
        }

    # 3. Final fallback: general container search
    fallback_recipe = final_fallback_search(soup)
    if fallback_recipe and is_recipe_like(fallback_recipe['ingredients'], fallback_recipe['instructions']):
        return {
            "name": name or "Unknown Recipe",
            "ingredients": fallback_recipe['ingredients'],
            "instructions": fallback_recipe['instructions']
        }

    # 4. WPRM fallback
    wprm_recipe = extract_wprm_recipe(soup)
    if wprm_recipe and is_recipe_like(wprm_recipe['ingredients'], wprm_recipe['instructions']):
        return {
            "name": name or "Unknown Recipe",
            "ingredients": wprm_recipe['ingredients'],
            "instructions": wprm_recipe['instructions']
        }

    # 5. New fallback: Extract from entry-content by scanning for keywords
    entry_content_recipe = extract_from_entry_content(soup)
    if entry_content_recipe and is_recipe_like(entry_content_recipe['ingredients'], entry_content_recipe['instructions']):
        return {
            "name": name or "Unknown Recipe",
            "ingredients": entry_content_recipe['ingredients'],
            "instructions": entry_content_recipe['instructions']
        }

    # If all fail
    return None
