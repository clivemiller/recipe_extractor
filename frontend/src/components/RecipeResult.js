import React, { useRef, useCallback, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useLocation, useNavigate } from 'react-router-dom';

function RecipeResult({ recipe, onReset, user }) {
  const location = useLocation();
  const navigate = useNavigate();
  const resultRef = useRef(null);

  const { url } = location.state || {}; // Retrieve URL from state

  const getBaseWebsiteName = (url) => {
    try {
      const hostname = new URL(url).hostname;
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

  const handleSave = useCallback(() => {
    if (!user) {
      alert('You must be logged in to save recipes.');
      navigate('/account');
      return;
    }
  
    const API_BASE_URL = 'https://recipe-extractor-backend.onrender.com';
  
    fetch(`${API_BASE_URL}/api/users/${user.id}/saved-recipes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        recipe_name: decodedRecipe.name,
        recipe_data: {
          ingredients: decodedRecipe.ingredients,
          instructions: decodedRecipe.instructions,
        },
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          if (data.error.includes('already exists')) {
            alert('This recipe already exists in your Recipe Box.');
          } else {
            alert(`Failed to save recipe: ${data.error}`);
          }
        } else {
          alert('Recipe saved successfully!');
        }
      })
      .catch((err) => {
        console.error('Error saving recipe:', err);
        alert('Failed to save recipe. Please try again.');
      });
  }, [decodedRecipe, navigate, user]);
  

  const handlePrint = useCallback(() => {
    window.print();
  }, []);

  useEffect(() => {
    if (!recipe) {
      navigate('/home'); // Redirect if no recipe
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
        <button onClick={handleSave}>Save to Recipe Box</button>
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
  user: PropTypes.object, // Add user as a prop
};

export default RecipeResult;
