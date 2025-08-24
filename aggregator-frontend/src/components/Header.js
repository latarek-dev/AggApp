import React, { useState } from 'react';
import { FaExchangeAlt, FaChartLine, FaWallet, FaCog } from 'react-icons/fa';

const Header = () => {
  const [activeTab, setActiveTab] = useState('swap');

  const navItems = [
    { id: 'swap', label: 'Wymiana', icon: FaExchangeAlt },
    { id: 'portfolio', label: 'Portfolio', icon: FaChartLine },
    { id: 'wallet', label: 'Portfel', icon: FaWallet },
    { id: 'settings', label: 'Ustawienia', icon: FaCog },
  ];

  return (
    <header className="w-full bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 border-b border-gray-700/50 backdrop-blur-xl">
      <div className="max-w-6xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
              <FaExchangeAlt size={20} className="text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                AggApp
              </h1>
              <p className="text-xs text-gray-400">Najlepsze kursy wymiany</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-300 ${
                    activeTab === item.id
                      ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                      : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
                  }`}
                >
                  <Icon size={14} />
                  <span className="text-sm font-medium">{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Connect Wallet Button */}
          <button className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-lg font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-300 text-sm">
            Połącz Portfel
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
