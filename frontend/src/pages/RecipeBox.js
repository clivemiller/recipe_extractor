import React, { useState, useEffect } from 'react';

function RecipeBox({ user }) {
  const [recipes, setRecipes] = useState([]);
  const [tabs, setTabs] = useState([]);
  const [selectedTab, setSelectedTab] = useState('All');
  const [newTabName, setNewTabName] = useState('');
  const API_BASE_URL = 'https://recipe-extractor-backend.onrender.com';

  // Fetch recipes and tabs when the component mounts
  useEffect(() => {
    if (user) {
      fetch(`${API_BASE_URL}/api/users/${user.id}/saved-recipes`)
        .then((response) => response.json())
        .then(setRecipes)
        .catch((error) => console.error('Error fetching recipes:', error));

      fetch(`${API_BASE_URL}/api/users/${user.id}/tabs`)
        .then((response) => response.json())
        .then(setTabs)
        .catch((error) => console.error('Error fetching tabs:', error));
    }
  }, [user]);

  const handleAddTab = () => {
    if (!newTabName.trim()) {
      alert('Tab name cannot be empty.');
      return;
    }

    fetch(`${API_BASE_URL}/api/users/${user.id}/tabs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tab_name: newTabName }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          alert(data.error);
        } else {
          setTabs((prevTabs) => [...prevTabs, newTabName]);
          setNewTabName('');
        }
      })
      .catch((err) => {
        console.error('Error adding tab:', err);
        alert('Failed to add tab. Please try again.');
      });
  };

  const handleDeleteTab = (tabName) => {
    fetch(`${API_BASE_URL}/api/users/${user.id}/tabs/${tabName}`, {
      method: 'DELETE',
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.error) {
          alert(data.error);
        } else {
          setTabs((prevTabs) => prevTabs.filter((tab) => tab !== tabName));
          if (selectedTab === tabName) setSelectedTab('All');
        }
      })
      .catch((err) => {
        console.error('Error deleting tab:', err);
        alert('Failed to delete tab. Please try again.');
      });
  };

  const filteredRecipes = selectedTab === 'All'
    ? recipes
    : recipes.filter((recipe) => recipe.tab_name === selectedTab);

  return (
    <div className="recipe-box">
      <h1>Your Recipe Box</h1>
      <div className="tabs">
        <button onClick={() => setSelectedTab('All')}>All</button>
        {tabs.map((tab) => (
          <div key={tab}>
            <button onClick={() => setSelectedTab(tab)}>{tab}</button>
            <button onClick={() => handleDeleteTab(tab)}>X</button>
          </div>
        ))}
        <div>
          <input
            value={newTabName}
            onChange={(e) => setNewTabName(e.target.value)}
            placeholder="New Tab"
          />
          <button onClick={handleAddTab}>Add Tab</button>
        </div>
      </div>
      {filteredRecipes.length === 0 ? (
        <p>No recipes found in this tab.</p>
      ) : (
        <div className="recipe-list">
          {filteredRecipes.map((recipe) => (
            <div key={recipe.id} className="recipe-card">
              <span>{recipe.recipe_name}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default RecipeBox;
