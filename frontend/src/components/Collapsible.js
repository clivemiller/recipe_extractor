import React from 'react';

function Collapsible({ isOpen, children }) {
  return (
    <div className="collapsible" style={{ maxHeight: isOpen ? '200px' : '0px', overflow: 'hidden', transition: 'max-height 0.3s ease' }}>
      {children}
    </div>
  );
}

export default Collapsible;
