import React, { useState, useEffect } from 'react';

function RecipeBox({ user }) {
  const [recipes, setRecipes] = useState([]);
  const [tabs, setTabs] = useState([]);
  const [selectedTab, setSelectedTab] = useState('General');
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [addToTabModalOpen, setAddToTabModalOpen] = useState(false);
  const [tabSettings, setTabSettings] = useState(null);
  const [newTabName, setNewTabName] = useState('');

  // Adjust API_BASE_URL based on environment
  const API_BASE_URL = 'https://recipe-extractor-backend.onrender.com/api';

  // Fetch recipes and tabs when the component mounts and the user is logged in
  useEffect(() => {
    if (user) {
      fetchRecipes();
      fetchTabs();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  // Fetch all saved recipes
  const fetchRecipes = () => {
    fetch(`${API_BASE_URL}/users/${user.id}/saved-recipes`)
      .then((response) => response.json())
      .then((data) => {
        // Sort recipes alphabetically by name
        const sortedRecipes = data.sort((a, b) =>
          a.recipe_name.localeCompare(b.recipe_name)
        );
        setRecipes(sortedRecipes);
      })
      .catch((error) => console.error('Error fetching recipes:', error));
  };

  // Fetch all tabs
  const fetchTabs = () => {
    fetch(`${API_BASE_URL}/users/${user.id}/tabs`)
      .then((response) => response.json())
      .then((data) => {
        setTabs(data);
      })
      .catch((error) => console.error('Error fetching tabs:', error));
  };

  // Handle selecting a tab
  const handleTabSelect = (tab) => {
    setSelectedTab(tab);
  };

  // Handle deleting a recipe
  const handleDeleteRecipe = (recipeId) => {
    fetch(`${API_BASE_URL}/users/${user.id}/saved-recipes/${recipeId}`, {
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

  // Handle opening the recipe modal
  const handleOpenModal = (recipe) => {
    setSelectedRecipe(recipe);
    setModalOpen(true);
  };

  // Handle closing the recipe modal
  const handleCloseModal = () => {
    setSelectedRecipe(null);
    setModalOpen(false);
  };

  // Handle opening the Add to Tab modal
  const handleOpenAddToTabModal = (recipe) => {
    setSelectedRecipe(recipe);
    setAddToTabModalOpen(true);
  };

  // Handle closing the Add to Tab modal
  const handleCloseAddToTabModal = () => {
    setSelectedRecipe(null);
    setAddToTabModalOpen(false);
    setNewTabName('');
  };

  // Handle assigning a recipe to a new tab
  const handleAssignToTab = (recipeId, newTab) => {
    fetch(`${API_BASE_URL}/users/${user.id}/saved-recipes/${recipeId}/tab`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ tab_name: newTab }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          alert(`Failed to assign to tab: ${data.error}`);
        } else {
          setRecipes((prevRecipes) =>
            prevRecipes.map((recipe) =>
              recipe.id === recipeId ? { ...recipe, tab_name: newTab } : recipe
            )
          );
          alert('Recipe assigned to tab successfully!');
          handleCloseAddToTabModal();
        }
      })
      .catch((err) => {
        console.error('Error assigning to tab:', err);
        alert('Failed to assign to tab. Please try again.');
      });
  };

  // Helper function to update multiple recipes' tab_name to 'General'
  const updateRecipesToGeneral = async (recipesToUpdate) => {
    const updatePromises = recipesToUpdate.map((recipe) =>
      fetch(`${API_BASE_URL}/users/${user.id}/saved-recipes/${recipe.id}/tab`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ tab_name: 'General' }),
      }).then((response) => response.json())
    );

    try {
      const results = await Promise.all(updatePromises);
      const failedUpdates = results.filter((result) => result.error);
      if (failedUpdates.length > 0) {
        console.error('Some recipes failed to update:', failedUpdates);
        alert('Some recipes could not be moved to "General". Please check the console for details.');
      } else {
        // Update local state to reflect the changes
        setRecipes((prevRecipes) =>
          prevRecipes.map((recipe) =>
            recipesToUpdate.find((r) => r.id === recipe.id)
              ? { ...recipe, tab_name: 'General' }
              : recipe
          )
        );
        alert('All recipes moved to "General" successfully!');
      }
    } catch (error) {
      console.error('Error updating recipes:', error);
      alert('Failed to update some recipes. Please try again.');
    }
  };
  // Updated handleDeleteTab using bulk update
  const handleDeleteTab = async (tab) => {
    if (tab === 'General') {
      alert('Cannot delete the default "General".');
      return;
    }

    const confirmDelete = window.confirm(
      `Are you sure you want to delete the tab "${tab}"? All recipes in this tab will be moved to "General".`
    );

    if (!confirmDelete) return;

    try {
      // Move recipes to 'General' using the bulk update endpoint
      const moveResponse = await fetch(
        `${API_BASE_URL}/users/${user.id}/saved-recipes/move-to-tab`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ source_tab: tab, target_tab: 'General' }),
        }
      );

      const moveData = await moveResponse.json();

      if (moveResponse.ok) {
        // Update local state
        setRecipes((prevRecipes) =>
          prevRecipes.map((recipe) =>
            recipe.tab_name === tab ? { ...recipe, tab_name: 'General' } : recipe
          )
        );

        // Now delete the tab
        const deleteResponse = await fetch(
          `${API_BASE_URL}/users/${user.id}/tabs/${encodeURIComponent(tab)}`,
          {
            method: 'DELETE',
          }
        );

        const deleteData = await deleteResponse.json();

        if (deleteResponse.ok) {
          // Remove the deleted tab from the tabs state
          setTabs((prevTabs) => prevTabs.filter((t) => t !== tab));

          // Update selected tab if it was deleted
          if (selectedTab === tab) {
            setSelectedTab('General');
          }

          alert('Tab deleted and recipes moved to "General" successfully!');
        } else {
          alert(`Failed to delete tab: ${deleteData.error}`);
        }
      } else {
        alert(`Failed to move recipes: ${moveData.error}`);
      }
    } catch (err) {
      console.error('Error deleting tab:', err);
      alert('Failed to delete tab. Please try again.');
    }
  };


  // Filter recipes based on selected tab
  const filteredRecipes = recipes.filter((recipe) =>
    recipe.tab_name === selectedTab
  );

  // Handle adding a new tab
  const handleAddNewTab = () => {
    const tabName = prompt('Enter new tab name:');
    if (tabName && tabName.trim() !== '') {                  
      // Check if the tab already exists
      if (tabs.includes(tabName.trim())) {
        alert('Tab with this name already exists.');
        return;
      }

      fetch(`${API_BASE_URL}/users/${user.id}/tabs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ tab_name: tabName.trim() }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.error) {
            alert(`Failed to add tab: ${data.error}`);
          } else {
            setTabs((prevTabs) => [...prevTabs, tabName.trim()]);
            alert('Tab added successfully!');
          }
        })
        .catch((err) => {
          console.error('Error adding tab:', err);
          alert('Failed to add tab. Please try again.');
        });
    } else {
      alert('Tab name cannot be empty.');
    }
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
      <div className="recipe-box-container">
        {/* First Third: Tabs Section */}
        <div className="tabs-section">
          <div className="tabs-header">
            <h2>Tabs</h2>
            <button onClick={handleAddNewTab} className="add-tab-button">
              + Add Tab
            </button>
          </div>
          <ul className="tabs-list">
            <li
              className={`tab-item ${selectedTab === 'General' ? 'active' : ''}`}
              onClick={() => handleTabSelect('General')}
            >
              General
            </li>
            {tabs.map((tab, index) => (
              <li
                key={index}
                className={`tab-item ${selectedTab === tab ? 'active' : ''}`}
                onClick={() => handleTabSelect(tab)}
              >
                {tab}
              </li>
            ))}
          </ul>
        </div>

        {/* Middle Third: Recipes Section */}
        <div className="recipes-section">
          <h2>{selectedTab} Recipes</h2>
          {filteredRecipes.length === 0 ? (
            <p>No recipes found in this tab.</p>
          ) : (
            <div className="recipe-list">
              {filteredRecipes.map((recipe) => (
                <div key={recipe.id} className="recipe-card">
                  <span onClick={() => handleOpenModal(recipe)} className="recipe-name">
                    {recipe.recipe_name}
                  </span>
                  <div className="recipe-actions">
                    <button
                      onClick={() => handleDeleteRecipe(recipe.id)}
                      className="delete-button"
                    >
                      Delete
                    </button>
                    <button
                      onClick={() => handleOpenAddToTabModal(recipe)}
                      className="add-to-tab-button"
                    >
                      Add to Tab
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Third Third: Tab Settings Section */}
        <div className="tab-settings-section">
          <h2>Tab Settings</h2>
          {selectedTab === 'General' ? (
            <p>No settings available for "General".</p>
          ) : (
            <div className="tab-settings">
              <p>
                <strong>Tab Name:</strong> {selectedTab}
              </p>
              <button
                onClick={() => handleDeleteTab(selectedTab)}
                className="delete-tab-button"
              >
                Delete Tab
              </button>
            </div>
          )}
        </div>
      </div>

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

      {/* Modal for adding recipe to a new tab */}
      {addToTabModalOpen && selectedRecipe && (
        <div className="modal">
          <div className="modal-content">
            <span className="close" onClick={handleCloseAddToTabModal}>
              &times;
            </span>
            <h2>Add "{selectedRecipe.recipe_name}" to a Tab</h2>
            <select
              onChange={(e) => setNewTabName(e.target.value)}
              value={newTabName}
              className="tab-select"
            >
              <option value="" disabled>
                Select a tab
              </option>
              {tabs.map((tab, index) => (
                <option key={index} value={tab}>
                  {tab}
                </option>
              ))}
              <option value="General">General</option>
            </select>
            <button
              onClick={() => {
                if (newTabName) {
                  handleAssignToTab(selectedRecipe.id, newTabName);
                } else {
                  alert('Please select a tab.');
                }
              }}
              className="assign-tab-button"
            >
              Assign to Tab
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default RecipeBox;
