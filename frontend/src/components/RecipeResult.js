import React, { useRef } from 'react';

function RecipeResult({ recipe, onReset }) {
  const resultRef = useRef(null);

  const handleCopy = () => {
    const text = resultRef.current.innerText;
    navigator.clipboard.writeText(text);
    alert('Recipe copied to clipboard!');
  };

  const Print = () => {
    window.print();
  };

  return (
    <div className="recipe-result" ref={resultRef}>
      <div className="result-header">
        <button onClick={onReset} className="start-over">Start Over</button>
      </div>
      {recipe.image && <img src={recipe.image} alt={recipe.name} className="recipe-image" onError={(e) => e.target.src='/sample-image.jpg'} />}
      <h2 className="recipe-title">{recipe.name || 'Untitled Recipe'}</h2>
      <div className="recipe-meta">
        {recipe.recipeYield && <span><strong>Servings:</strong> {recipe.recipeYield}</span>}
        {recipe.prepTime && <span><strong>Prep Time:</strong> {parseTime(recipe.prepTime)}</span>}
        {recipe.cookTime && <span><strong>Cook Time:</strong> {parseTime(recipe.cookTime)}</span>}
        {recipe.nutrition && recipe.nutrition.calories && <span><strong>Calories:</strong> {recipe.nutrition.calories}</span>}
      </div>
      {recipe.ingredients && recipe.ingredients.length > 0 && (
        <div className="ingredients-section">
          <h3>Ingredients</h3>
          <ul>
            {recipe.ingredients.map((ing, i) => (
              <li key={i}>
                <input type="checkbox" /> <span>{ing}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
      {recipe.instructions && recipe.instructions.length > 0 && (
        <div className="instructions-section">
          <h3>Instructions</h3>
          <ol>
            {recipe.instructions.map((step, i) => <li key={i}>{step}</li>)}
          </ol>
        </div>
      )}
      <div className="actions">
        <button onClick={Print}>Print</button>
        <button onClick={handleCopy}>Copy to Clipboard</button>
      </div>
    </div>
  );
}

function parseTime(isoTime) {
  // A simple parser for ISO time durations like PT15M, PT1H, etc.
  // Example: PT15M -> 15 minutes, PT1H -> 1 hour, PT1H30M -> 1 hour 30 minutes
  const match = isoTime.match(/PT(?:(\d+)H)?(?:(\d+)M)?/);
  if (!match) return isoTime;
  const hours = match[1] ? `${match[1]} hour${match[1] === '1' ? '' : 's'}` : '';
  const mins = match[2] ? `${match[2]} minute${match[2] === '1' ? '' : 's'}` : '';
  return [hours, mins].filter(Boolean).join(' ');
}

export default RecipeResult;
