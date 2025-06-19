import React from 'react';

const Header = () => {
  return (
    <header className="w-full bg-gradient-to-r from-blue-600 to-blue-400 py-3 px-6">
      <div className="max-w-6xl mx-auto"> {/* Center the content horizontally */}
        <h1 className="text-xl font-semibold text-white pl-36"> {/* Added padding-left */}
          Agregator Wymiany Tokenów
        </h1>
      </div>
    </header>
  );
};

export default Header;
