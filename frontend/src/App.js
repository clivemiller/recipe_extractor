import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import Hero from './components/Hero';
import RecipeResult from './components/RecipeResult';
import Navbar from './components/Navbar';
import RecipeBox from './pages/RecipeBox';
import Account from './pages/Account';

function App() {
  const [url, setUrl] = useState('');
  const [recipe, setRecipe] = useState(null);
  const [error, setError] = useState('');
  const [user, setUser] = useState(null); // State for logged-in user

  // Restore user from localStorage when the app loads
  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  // Handle recipe fetching
  const handleFetchRecipe = async (e, navigate) => {
    e.preventDefault();
    setRecipe(null);
    setError('');

    try {
      const response = await fetch(
        `https://recipe-extractor-backend.onrender.com/extract-recipe?url=${encodeURIComponent(url)}`
      );
      const data = await response.json();

      if (response.ok) {
        setRecipe(data);
        navigate('/results', { state: { url } }); // Pass URL in state
      } else {
        setError(data.error || 'Failed to fetch recipe');
      }
    } catch (err) {
      console.error(err);
      setError('An error occurred while fetching the recipe.');
    }
  };

  const handleReset = () => {
    setUrl('');
    setRecipe(null);
    setError('');
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    setUser(null);
  };

  const AppRoutes = () => {
    const navigate = useNavigate();

    return (
      <Routes>
        <Route
          path="/recipe_extractor"
          element={
            <Hero
              url={url}
              setUrl={setUrl}
              handleFetchRecipe={(e) => handleFetchRecipe(e, navigate)}
              error={error}
            />
          }
        />
        <Route
          path="/results"
          element={
            recipe ? (
              <RecipeResult recipe={recipe} user={user} onReset={handleReset} />
            ) : (
              <div>Please fetch a recipe first!</div>
            )
          }
        />
        <Route
          path="/recipe-box"
          element={<RecipeBox user={user} />} // Pass user to RecipeBox
        />
        <Route
          path="/account"
          element={<Account user={user} setUser={setUser} />} // Pass user and setUser to Account
        />
      </Routes>
    );
  };

  return (
    <Router>
      <div className="app">
        <Navbar user={user} onLogout={handleLogout} /> {/* Pass user and logout handler to Navbar */}
        <AppRoutes />
      </div>
    </Router>
  );
}

export default App;
