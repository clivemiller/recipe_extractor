import React, { useState } from 'react';
import Collapsible from './Collapsible';

function Hero({ url, setUrl, handleFetchRecipe, error }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="hero">
      <div className="hero-content">
        <img src="/logo.png" alt="Logo" className="hero-logo"/>
        <h1>Extract Recipes Instantly</h1>
        <p>Paste a recipe URL, and we'll extract all the details for you.</p>
        <form onSubmit={handleFetchRecipe} className="hero-form">
          <input 
            type="text" 
            value={url} 
            onChange={e => setUrl(e.target.value)} 
            placeholder="Enter recipe URL..."
          />
          <button type="submit">Extract Recipe</button>
        </form>
        {error && <div className="error-msg">{error}</div>}
        <div className="supported-sites">
          <button onClick={() => setIsOpen(!isOpen)} className="toggle-supported">
            Tested Websites that return best results {`(Tested sites)`}
          </button>
          <Collapsible isOpen={isOpen}>
            <ul>
              <li>https://www.inspiredtaste.net</li>
              <li>https://www.epicurious.com</li>
              <li>https://www.seriouseats.com</li>
              <li>https://www.allrecipes.com</li>
              <li>https://www.halfbakedharvest.com</li>
            </ul>
          </Collapsible>
          <button onClick={() => setIsOpen(!isOpen)} className="toggle-supported">
            Sites with known issues
          </button>
          <Collapsible isOpen={isOpen}>
            <ul>
              <li>https://smittenkitchen.com</li>
            </ul>
          </Collapsible>
        </div>
      </div>
    </div>
  );
}

export default Hero;
