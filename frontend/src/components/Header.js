import React from 'react';
import './Header.css';

const Header = () => {
  return (
    <header className="header">
      <img src="/Logo FInal.png" alt="ReadReview Logo" className="logo" />
      <h1 className="title">ReadReview</h1>
      <p className="subtitle">Predict your research paper's acceptance with AI</p>
    </header>
  );
};

export default Header;
