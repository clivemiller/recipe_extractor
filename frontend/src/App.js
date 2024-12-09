import React, { useState } from 'react';
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

  const handleFetchRecipe = async (e, navigate) => {
    e.preventDefault();
    setRecipe(null);
    setError('');

    try {
      const response = await fetch(
        // `https://recipe-extractor-backend.onrender.com/extract-recipe?url=${encodeURIComponent(url)}`
        // for local testing
        `http://127.0.0.1:5000/extract-recipe?url=${encodeURIComponent(url)}`
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
              <RecipeResult recipe={recipe} onReset={handleReset} />
            ) : (
              <div>Please fetch a recipe first!</div>
            )
          }
        />
        <Route path="/recipe-box" element={<RecipeBox />} />
        <Route path="/account" element={<Account />} />
      </Routes>
    );
  };

  return (
    <Router>
      <div className="app">
        <Navbar />
        <AppRoutes />
      </div>
    </Router>
  );
}

export default App;
