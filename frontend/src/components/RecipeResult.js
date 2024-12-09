import React, { useRef, useCallback, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useLocation, useNavigate } from 'react-router-dom';

function RecipeResult({ recipe, onReset }) {
  const location = useLocation();
  const navigate = useNavigate();
  const resultRef = useRef(null);

  const { url } = location.state || {}; // Retrieve URL from state

  // Utility to get the base website name
  const getBaseWebsiteName = (url) => {
    try {
      const hostname = new URL(url).hostname;
      // Remove 'www.' if present
      return hostname.startsWith('www.') ? hostname.slice(4) : hostname;
    } catch (error) {
      console.error('Invalid URL:', url);
      return url; // Fallback to the original URL if parsing fails
    }
  };

  const decodeHTML = (html) => {
    const txt = document.createElement('textarea');
    txt.innerHTML = html;
    return txt.value;
  };

  const formatInstructions = (instructions) => {
    if (instructions.length === 1) {
      const singleInstruction = instructions[0];
      const stepRegex = /\d+\.\s+/g;
      if (stepRegex.test(singleInstruction)) {
        const steps = singleInstruction.split(stepRegex).filter(Boolean);
        return steps;
      }
    }
    return instructions;
  };

  const decodedRecipe = {
    ...recipe,
    name: recipe.name ? decodeHTML(recipe.name) : 'Untitled Recipe',
    ingredients: recipe.ingredients
      ? recipe.ingredients.map((ing) => decodeHTML(ing))
      : [],
    instructions: recipe.instructions
      ? formatInstructions(recipe.instructions.map((inst) => decodeHTML(inst)))
      : [],
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

  // Redirect to homepage if no recipe is available
  useEffect(() => {
    if (!recipe) {
      navigate('/recipe_extractor'); // Navigate to the homepage
    }
  }, [recipe, navigate]);

  if (!recipe) {
    return null; // Render nothing while redirecting
  }

  return (
    <div className="recipe-result" ref={resultRef}>
      <header className="result-header">
        <h4 className="recipe-result-link">
          <a href={url} target="_blank" rel="noopener noreferrer">
            Recipe from: {getBaseWebsiteName(url)}
          </a>
          <button onClick={onReset} className="start-over" aria-label="Start Over">
            <p>Start Over</p>
          </button>
        </h4>
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
        <button onClick={handleCopy}>Save to Recipe Box -coming soon</button>
      </div>
    </div>
  );
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
  }),
  onReset: PropTypes.func.isRequired,
};

export default RecipeResult;
