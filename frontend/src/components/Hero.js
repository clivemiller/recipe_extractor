import React, { useState } from 'react';
import Collapsible from './Collapsible';
import logo from '../../src/logo.png';

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
        <img src={logo} alt="Logo" className="hero-logo" />
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
          <div className="toggle-supported">
            <p>We support a ton of sites, but start here if you don't know where to look!</p>
            <li><a href="https://www.inspiredtaste.net" target="_blank" rel="noopener noreferrer">https://www.inspiredtaste.net</a></li>
          </div>
          <button onClick={() => setIsOpen(!isOpen)} className="toggle-supported">
            Sites that have known issues - will be supported soon!
          </button>
          <Collapsible isOpen={isOpen}>
            <ul>
              <li>https://pinchofyum.com</li>
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

