from bs4 import BeautifulSoup, NavigableString

# HTML content
html_content = """
<div class="jetpack-recipe-directions e-instructions">
    <b>Heat oven:</b> To 375°F (190°C).
    <p></p>
    <div class="code-block code-block-5" style="margin: 8px 0; clear: both;">
        <div class="htlad-medrec" data-ad-processed="" id="medrec" data-google-query-id="CLCXvO7slooDFWDEwgQd75kqXQ">
            <div id="google_ads_iframe_/145131060/medrec_0__container__" style="border: 0pt none; margin: auto; text-align: center;">
                <iframe id="google_ads_iframe_/145131060/medrec_0" name="google_ads_iframe_/145131060/medrec_0" title="3rd party ad content" width="300" height="250" scrolling="no" marginwidth="0" marginheight="0" frameborder="0" aria-label="Advertisement" tabindex="0" allow="private-state-token-redemption;attribution-reporting" style="border: 0px; vertical-align: bottom;" data-google-container-id="1" data-load-complete="true"></iframe>
            </div>
        </div>
    </div>
    <p><b>Toast the crumbs:</b> In a 10-inch ovenproof skillet (I’m using <a href="https://amzn.to/3CybLK0">this one</a>), melt 2 tablespoons of the butter over medium heat and add the breadcrumbs. Toast the crumbs in the butter, stirring, until they’re a light golden brown. Season with a pinch of salt and scrape crumbs into a dish to set aside. Swipe out the pan to clean it, if you wish. Nobody will notice if a crumb ends up in the sauce, however.</p>
    <p><b>Soak your pasta:</b> Place uncooked pasta in a large bowl and cover with hot tap water. Soak for 10 minutes then drain it, shaking the pasta out. (I find it traps a lot of water.)</p>
    <p><b>Make the sauce and assemble:</b> Combine the three cheeses right on the paper or board you’ve grated them onto.</p>
    <p>Return your ovenproof skillet to the stove over medium-high heat and melt the remaining 3 tablespoons of butter in it. Add the flour, whisking to combine. Add milk, 1/2 cup at a time, whisking to combine each addition with the butter-flour mixture until smooth. When all milk is added, season with 1 1/2 teaspoons kosher salt (Diamond brand; use half of any other brand), many grinds of black pepper, cayenne, and nutmeg, and cook, stirring, until mixture comes to a simmer and begins to thicken. Once simmering, cook for 2-3 minutes, stirring. Turn the burner off.</p>
    <p>Setting aside 2/3 cup of the cheese mixture, add the rest of the cheeses to the sauce, stirring just until it has melted. Taste the sauce (carefully!) here and adjust seasonings if needed to taste. Stir in drained pasta until evenly coated. Sprinkle the surface with reserved cheese, followed by the toasted breadcrumbs.</p>
    <p><b>Bake:</b> Transfer the skillet to the oven and bake, uncovered, for 30 minutes. You can fish out a piece of macaroni just to confirm it’s cooked through, but I’ve never found this to be an issue. Add another 5 minutes in the oven, if needed for it to soften. If you want it a little more browned on top, run the pan briefly under your broiler for a minute.</p>
    <p><b>Serve:</b> Let rest for 2 to 3 minutes, then serve right away.</p>
    <p><b>Do ahead:</b> Given the choice between reheating cooked macaroni and cheese and baking it fresh, and given that it can take almost the same amount of oven time to bake it as to warm it through, I always choose baking the mac and cheese right before serving it. You can assemble it earlier, however, and bake before you’re ready to eat. Reheat leftovers in the original pan or an ovenproof dish at 350°F for 20 to 30 minutes.</p>
    <p></p>
</div>
"""

# Parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Select the container
instructions_container = soup.select_one('.jetpack-recipe-directions.e-instructions')

# Extract clean text
instructions = []
for element in instructions_container.children:
    if isinstance(element, NavigableString):
        # Add text nodes directly
        text = element.strip()
        if text:
            instructions.append(text)
    elif element.name == 'p':
        # Extract text from <p> tags
        text = element.get_text(strip=True)
        if text:
            instructions.append(text)

# Output the cleaned instructions
for i, step in enumerate(instructions, start=1):
    print(f"Step {i}: {step}")