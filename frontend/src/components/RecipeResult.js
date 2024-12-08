import React, { useRef, useCallback } from 'react';
import PropTypes from 'prop-types';

function RecipeResult({ recipe, onReset }) {
  const resultRef = useRef(null);

  // Utility function to decode HTML entities
  const decodeHTML = (html) => {
    const txt = document.createElement('textarea');
    txt.innerHTML = html;
    return txt.value;
  };

  // Utility function to format instructions
  const formatInstructions = (instructions) => {
    if (instructions.length === 1) {
      const singleInstruction = instructions[0];
      // Regular expression to match numbered steps (e.g., "1. Step one.")
      const stepRegex = /\d+\.\s+/g;
      if (stepRegex.test(singleInstruction)) {
        // Split the string at each numbered step
        const steps = singleInstruction.split(stepRegex).filter(Boolean);
        return steps;
      }
    }
    return instructions;
  };

  // Decode necessary recipe fields
  const decodedRecipe = {
    ...recipe,
    name: recipe.name ? decodeHTML(recipe.name) : 'Untitled Recipe',
    ingredients: recipe.ingredients
      ? recipe.ingredients.map((ing) => decodeHTML(ing))
      : [],
    instructions: recipe.instructions
      ? formatInstructions(recipe.instructions.map((inst) => decodeHTML(inst)))
      : [],
    // If other fields might contain HTML entities, decode them similarly
  };

  const handleCopy = useCallback(() => {
    const text = resultRef.current.innerText;
    navigator.clipboard
      .writeText(text)
      .then(() => {
        alert('Recipe copied to clipboard!');
      })
      .catch((err) => {
        console.error('Failed to copy: ', err);
        alert('Failed to copy recipe. Please try again.');
      });
  }, [resultRef]);

  const handlePrint = useCallback(() => {
    window.print();
  }, []);

  return (
    <div className="recipe-result" ref={resultRef}>
      <header className="result-header">
        <button onClick={onReset} className="start-over" aria-label="Start Over">
          Start Over
        </button>
      </header>
      {decodedRecipe.image && (
        <img
          src={decodedRecipe.image}
          alt={decodedRecipe.name || 'Recipe Image'}
          className="recipe-image"
          onError={(e) => {
            if (!e.target.dataset.fallback) {
              e.target.src = '/sample-image.jpg';
              e.target.dataset.fallback = true;
            }
          }}
        />
      )}
      <h2 className="recipe-title">{decodedRecipe.name}</h2>
      <div className="recipe-meta">
        {decodedRecipe.recipeYield && (
          <span>
            <strong>Servings:</strong> {decodedRecipe.recipeYield}
          </span>
        )}
        {decodedRecipe.prepTime && (
          <span>
            <strong>Prep Time:</strong> {parseTime(decodedRecipe.prepTime)}
          </span>
        )}
        {decodedRecipe.cookTime && (
          <span>
            <strong>Cook Time:</strong> {parseTime(decodedRecipe.cookTime)}
          </span>
        )}
        {decodedRecipe.nutrition && decodedRecipe.nutrition.calories && (
          <span>
            <strong>Calories:</strong> {decodedRecipe.nutrition.calories}
          </span>
        )}
      </div>
      {decodedRecipe.ingredients && decodedRecipe.ingredients.length > 0 ? (
        <div className="ingredients-section">
          <h3>Ingredients</h3>
          <ul>
            {decodedRecipe.ingredients.map((ing, i) => (
              <li key={i}>
                <label>
                  <input type="checkbox" /> <span>{ing}</span>
                </label>
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <p>No ingredients provided.</p>
      )}
      {decodedRecipe.instructions && decodedRecipe.instructions.length > 0 ? (
        <div className="instructions-section">
          <h3>Instructions</h3>
          <ol>
            {decodedRecipe.instructions.map((step, i) => (
              <li key={i}>{step}</li>
            ))}
          </ol>
        </div>
      ) : (
        <p>No instructions provided.</p>
      )}
      <div className="actions">
        <button onClick={handlePrint}>Print</button>
        <button onClick={handleCopy}>Save to Recipe Book -coming soon</button>
      </div>
    </div>
  );
}

function parseTime(isoTime) {
  // A simple parser for ISO time durations like PT15M, PT1H, etc.
  // Example: PT15M -> 15 minutes, PT1H -> 1 hour, PT1H30M -> 1 hour 30 minutes
  const regex = /PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/;
  const match = isoTime.match(regex);
  if (!match) return isoTime;

  const hours = match[1] ? `${match[1]} hour${match[1] !== '1' ? 's' : ''}` : '';
  const minutes = match[2] ? `${match[2]} minute${match[2] !== '1' ? 's' : ''}` : '';
  const seconds = match[3] ? `${match[3]} second${match[3] !== '1' ? 's' : ''}` : '';

  return [hours, minutes, seconds].filter(Boolean).join(' ');
}

RecipeResult.propTypes = {
  recipe: PropTypes.shape({
    image: PropTypes.string,
    name: PropTypes.string,
    recipeYield: PropTypes.string,
    prepTime: PropTypes.string,
    cookTime: PropTypes.string,
    nutrition: PropTypes.shape({
      calories: PropTypes.string,
    }),
    ingredients: PropTypes.arrayOf(PropTypes.string),
    instructions: PropTypes.arrayOf(PropTypes.string),
  }).isRequired,
  onReset: PropTypes.func.isRequired,
};

export default RecipeResult;
