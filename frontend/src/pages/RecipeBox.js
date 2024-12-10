import React, { useState, useEffect } from 'react';

function RecipeBox({ user }) {
  const [recipes, setRecipes] = useState([]);
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  const API_BASE_URL = 'https://recipe-extractor-backend.onrender.com';

  // Fetch recipes when the component mounts and the user is logged in
  useEffect(() => {
    if (user) {
      fetch(`${API_BASE_URL}/api/users/${user.id}/saved-recipes`)
        .then((response) => response.json())
        .then((data) => {
          // Sort recipes alphabetically by name
          const sortedRecipes = data.sort((a, b) =>
            a.recipe_name.localeCompare(b.recipe_name)
          );
          setRecipes(sortedRecipes);
        })
        .catch((error) => console.error('Error fetching recipes:', error));
    }
  }, [user]);

  const handleDelete = (recipeId) => {
    const API_BASE_URL = 'https://recipe-extractor-backend.onrender.com';
  
    fetch(`${API_BASE_URL}/api/users/${user.id}/saved-recipes/${recipeId}`, {
      method: 'DELETE',
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          alert(`Failed to delete recipe: ${data.error}`);
        } else {
          setRecipes((prevRecipes) =>
            prevRecipes.filter((recipe) => recipe.id !== recipeId)
          );
          alert('Recipe deleted successfully!');
        }
      })
      .catch((err) => {
        console.error('Error deleting recipe:', err);
        alert('Failed to delete recipe. Please try again.');
      });
  };
  

  // Handle opening the modal
  const handleOpenModal = (recipe) => {
    setSelectedRecipe(recipe);
    setModalOpen(true);
  };

  // Handle closing the modal
  const handleCloseModal = () => {
    setSelectedRecipe(null);
    setModalOpen(false);
  };

  if (!user) {
    return (
      <div className="recipe-box">
        <h1>Your Recipe Box</h1>
        <p>You will need to log in to access your box</p>
      </div>
    );
  }

  return (
    <div className="recipe-box">
      <h1>Your Recipe Box</h1>
      {recipes.length === 0 ? (
        <p>No recipes found.</p>
      ) : (
        <div className="recipe-list">
          {recipes.map((recipe) => (
            <div key={recipe.id} className="recipe-card">
              <span onClick={() => handleOpenModal(recipe)}>{recipe.recipe_name}</span>
              <button onClick={() => handleDelete(recipe.id)} className="delete-button">
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
      {/* Modal for displaying full recipe */}
      {modalOpen && selectedRecipe && (
        <div className="modal">
          <div className="modal-content">
            <span className="close" onClick={handleCloseModal}>
              &times;
            </span>
            <h2>{selectedRecipe.recipe_name}</h2>
            <h3>Ingredients</h3>
            <ul>
              {selectedRecipe.recipe_data.ingredients.map((ingredient, index) => (
                <li key={index}>{ingredient}</li>
              ))}
            </ul>
            <h3>Instructions</h3>
            <ol>
              {selectedRecipe.recipe_data.instructions.map((instruction, index) => (
                <li key={index}>{instruction}</li>
              ))}
            </ol>
          </div>
        </div>
      )}
    </div>
  );
}

export default RecipeBox;
