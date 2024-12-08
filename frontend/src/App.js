import React, { useState } from 'react';
import Hero from './components/Hero';
import RecipeResult from './components/RecipeResult';

function App() {
  const [url, setUrl] = useState('');
  const [recipe, setRecipe] = useState(null);
  const [error, setError] = useState('');

  const handleFetchRecipe = async (e) => {
    e.preventDefault();
    setRecipe(null);
    setError('');

    try {
      const response = await fetch(`https://recipe-extractor-backend.onrender.com/extract-recipe?url=${encodeURIComponent(url)}`);
      const data = await response.json();

      if (response.ok) {
        setRecipe(data);
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

  return (
    <div className="app">
      {!recipe && (
        <Hero
          url={url}
          setUrl={setUrl}
          handleFetchRecipe={handleFetchRecipe}
          error={error}
        />
      )}
      {recipe && (
        <RecipeResult recipe={recipe} onReset={handleReset} />
      )}
    </div>
  );
}

export default App;
