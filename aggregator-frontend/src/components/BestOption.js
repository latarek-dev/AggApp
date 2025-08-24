import React from "react";
import PercentageChange from "./PercentageChange";
import { FaCrown, FaExchangeAlt } from "react-icons/fa";

const BestOption = ({ option, tokenFrom, tokenTo, isSelected, onSelect }) => {
  return (
    <div className={`bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 backdrop-blur-xl border-2 rounded-lg shadow-lg relative transition-all duration-300 ${
      isSelected 
        ? 'border-gradient-to-r from-yellow-400 to-orange-500' 
        : 'border-gray-700/50 hover:border-gray-600'
    }`}>
      {/* Best Option Badge */}
      <div className="absolute -top-1 -left-1 bg-gradient-to-r from-yellow-400 to-orange-500 text-gray-900 px-1.5 py-0.5 rounded-full text-xs font-bold flex items-center space-x-1">
        <FaCrown size={8} />
        <span className="text-xs">NAJLEPSZA</span>
      </div>

      {/* Main Content - Horizontal Layout */}
      <div className="flex items-center justify-between p-4">
        {/* Left Side - Token Info */}
        <div className="flex items-center space-x-4 flex-1">
          <div className="w-9 h-9 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <FaExchangeAlt size={15} className="text-white" />
          </div>
          <div>
            <div className="text-sm font-bold text-white">{option.pair}</div>
            <div className="text-xs text-gray-400">{option.dex}</div>
          </div>
        </div>

        {/* Center - Exchange Rate */}
        <div className="flex items-center space-x-3 flex-1 justify-center">
          <div className="text-center">
            <div className="text-sm font-semibold text-white">
              {option.amount_from.toFixed(6)} {tokenFrom}
            </div>
            <div className="text-xs text-gray-400">${option.value_from_usd.toFixed(2)}</div>
          </div>
          
          <div className="w-4 h-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <div className="w-1 h-1 bg-white rounded-full"></div>
          </div>
          
          <div className="text-center">
            <div className="text-sm font-semibold text-white">
              {option.amount_to.toFixed(6)} {tokenTo}
            </div>
            <div className="text-xs text-gray-400">${option.value_to_usd.toFixed(2)}</div>
          </div>
        </div>

        {/* Right Side - Actions */}
        <div className="flex items-center space-x-3 flex-shrink-0">
          <PercentageChange fromUsd={option.value_from_usd} toUsd={option.value_to_usd} />
          {isSelected ? (
            <button className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-3 py-2 rounded-lg font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-300 text-xs">
              Wymień
            </button>
          ) : (
            <button 
              onClick={onSelect}
              className="bg-gradient-to-r from-gray-600 to-gray-700 text-white px-3 py-2 rounded-lg font-semibold hover:from-gray-500 hover:to-gray-600 transform hover:scale-105 transition-all duration-300 text-xs"
            >
              Wybierz
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default BestOption;
