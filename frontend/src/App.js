import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import Hero from './components/Hero';
import RecipeResult from './components/RecipeResult';
import Navbar from './components/Navbar';
import RecipeBox from './pages/RecipeBox';
import Account from './pages/Account';

function App() {
  const [url, setUrl] = useState('');
  const [recipe, setRecipe] = useState(null);
  const [error, setError] = useState('');
  const [user, setUser] = useState(null);

  // Restore user from localStorage on app load
  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

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
        navigate('/results', { state: { url } });
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
        {/* Main Recipe Extractor */}
        <Route
          path="/"
          element={
            <Hero
              url={url}
              setUrl={setUrl}
              handleFetchRecipe={(e) => handleFetchRecipe(e, navigate)}
              error={error}
            />
          }
        />

        {/* Results Page */}
        <Route
          path="/results"
          element={
            recipe ? (
              <RecipeResult recipe={recipe} user={user} onReset={handleReset} />
            ) : (
              <Navigate to="/" replace /> /* Redirect if no recipe */
            )
          }
        />

        {/* Recipe Box */}
        <Route
          path="/recipe-box"
          element={<RecipeBox user={user} />}
        />

        {/* Account Page */}
        <Route
          path="/account"
          element={<Account user={user} setUser={setUser} />}
        />

        {/* Redirect for unknown paths */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    );
  };

  return (
    <Router>
      <div className="app">
        <Navbar user={user} onLogout={() => setUser(null)} />
        <AppRoutes />
      </div>
    </Router>
  );
}

export default App;
