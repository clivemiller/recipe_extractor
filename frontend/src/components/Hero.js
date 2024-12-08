import React, { useState } from 'react';
import Collapsible from './Collapsible';

function Hero({ url, setUrl, handleFetchRecipe, error }) {
  const [isOpen, setIsOpen] = useState(false);

  const sendEmail = () => {
    const recipient = "the.recipe.fox@gmail.com";
    const subject = encodeURIComponent("Sad Problem Found!!!");
    const body = encodeURIComponent(
      "Hello Mr. Dev,\n\n I have a issue to report: "
    );

    // Construct the mailto link
    const mailtoLink = `mailto:${recipient}?subject=${subject}&body=${body}`;

    // Open the mailto link
    window.location.href = mailtoLink;
  };

  return (
    <div className="hero">
      <div className="hero-content">
        <img src="/logo.png" alt="Logo" className="hero-logo" />
        <h1>The Recipe Fox</h1>
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
        <button onClick={sendEmail}>
          Send Feedback or Query
        </button>
        <div className="supported-sites">
          <button onClick={() => setIsOpen(!isOpen)} className="toggle-supported">
            Websites that return best results {`(Tested sites)`}
          </button>
          <Collapsible isOpen={isOpen}>
            <ul>
              <li><a href="https://www.inspiredtaste.net" target="_blank" rel="noopener noreferrer">https://www.inspiredtaste.net</a></li>
              <li><a href="https://www.epicurious.com" target="_blank" rel="noopener noreferrer">https://www.epicurious.com</a></li>
              <li><a href="https://www.seriouseats.com" target="_blank" rel="noopener noreferrer">https://www.seriouseats.com</a></li>
              <li><a href="https://www.allrecipes.com" target="_blank" rel="noopener noreferrer">https://www.allrecipes.com</a></li>
              <li><a href="https://www.halfbakedharvest.com" target="_blank" rel="noopener noreferrer">https://www.halfbakedharvest.com</a></li>
              <li><a href="https://smittenkitchen.com" target="_blank" rel="noopener noreferrer">https://smittenkitchen.com</a></li>
              <li><a href="https://www.simplyrecipes.com" target="_blank" rel="noopener noreferrer">https://www.simplyrecipes.com</a></li>
              <li><a href="https://www.thepioneerwoman.com" target="_blank" rel="noopener noreferrer">https://www.thepioneerwoman.com</a></li>
              <li><a href="https://www.marthastewart.com" target="_blank" rel="noopener noreferrer">https://www.marthastewart.com</a></li>
              <li><a href="https://www.jamieoliver.com" target="_blank" rel="noopener noreferrer">https://www.jamieoliver.com</a></li>
              <li><a href="https://minimalistbaker.com" target="_blank" rel="noopener noreferrer">https://minimalistbaker.com</a></li>
              <li><a href="https://www.davidlebovitz.com" target="_blank" rel="noopener noreferrer">https://www.davidlebovitz.com</a></li>
              <li><a href="https://www.budgetbytes.com" target="_blank" rel="noopener noreferrer">https://www.budgetbytes.com</a></li>
              <li><a href="https://feelgoodfoodie.net" target="_blank" rel="noopener noreferrer">https://feelgoodfoodie.net</a></li>
              <li><a href="https://www.servingdumplings.com" target="_blank" rel="noopener noreferrer">https://www.servingdumplings.com</a></li>
            </ul>
          </Collapsible>
          <button onClick={() => setIsOpen(!isOpen)} className="toggle-supported">
            Sites that have known issues - will be supported soon!
          </button>
          <Collapsible isOpen={isOpen}>
            <ul>
              <li>https://www.onceuponachef.com</li>
              <li>https://pinchofyum.com</li>
              <li>https://damndelicious.net</li>
              <li>https://joythebaker.com</li>
              <li>https://www.loveandlemons.com</li>
              <li>https://food52.com</li>
              <li>https://cookieandkate.com</li>
              <li>https://barefootcontessa.com</li>
            </ul>
          </Collapsible>
        </div>
      </div>
    </div>
  );
}

export default Hero;

