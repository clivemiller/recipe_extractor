import React from 'react';
import { NavLink } from 'react-router-dom';

function Navbar() {
  return (
    <nav className="navbar">
      <ul>
        <li>
          <NavLink to="/recipe_extractor" className="nav-link">
            Home
          </NavLink>
        </li>
        <li>
          <NavLink to="/recipe-box" className="nav-link">
            Recipe Box
          </NavLink>
        </li>
        <li>
          <NavLink to="/account" className="nav-link">
            Account
          </NavLink>
        </li>
      </ul>
    </nav>
  );
}

export default Navbar;
