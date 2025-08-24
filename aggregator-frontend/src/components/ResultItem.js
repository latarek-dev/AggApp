import PercentageChange from "./PercentageChange";
import { FaExchangeAlt } from "react-icons/fa";

const ResultItem = ({ option, tokenFrom, tokenTo, index, isSelected, onSelect }) => {
  return (
    <div className={`bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 backdrop-blur-xl border rounded-lg shadow-md hover:shadow-lg transition-all duration-300 transform hover:scale-[1.002] ${
      isSelected 
        ? 'border-2 border-gradient-to-r from-blue-500 to-purple-600' 
        : 'border border-gray-700/50 hover:border-gray-600'
    }`}>
      {/* Main Content - Horizontal Layout */}
      <div className="flex items-center justify-between p-3">
        {/* Left Side - Token Info and Ranking */}
        <div className="flex items-center space-x-3 flex-1">
          <div className="w-7 h-7 bg-gradient-to-br from-gray-600 to-gray-700 rounded-full flex items-center justify-center text-white text-xs font-bold">
            {index + 2}
          </div>
          <div className="w-7 h-7 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <FaExchangeAlt size={11} className="text-white" />
          </div>
          <div>
            <div className="text-sm font-semibold text-white">{option.pair}</div>
            <div className="text-xs text-gray-400">{option.dex}</div>
          </div>
        </div>

        {/* Center - Exchange Rate */}
        <div className="flex items-center space-x-2 flex-1 justify-center">
          <div className="text-center">
            <div className="text-sm font-medium text-white">
              {option.amount_from.toFixed(6)} {tokenFrom}
            </div>
            <div className="text-xs text-gray-400">${option.value_from_usd.toFixed(2)}</div>
          </div>
          
          <div className="w-3 h-3 bg-gradient-to-r from-gray-600 to-gray-700 rounded-full flex items-center justify-center">
            <div className="w-0.5 h-0.5 bg-gray-400 rounded-full"></div>
          </div>
          
          <div className="text-center">
            <div className="text-sm font-medium text-white">
              {option.amount_to.toFixed(6)} {tokenTo}
            </div>
            <div className="text-xs text-gray-400">${option.value_to_usd.toFixed(2)}</div>
          </div>
        </div>

        {/* Right Side - Actions */}
        <div className="flex items-center space-x-2 flex-shrink-0">
          <PercentageChange fromUsd={option.value_from_usd} toUsd={option.value_to_usd} />
          {isSelected ? (
            <button className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-2.5 py-1.5 rounded-lg font-medium hover:shadow-lg transform hover:scale-105 transition-all duration-300 text-xs">
              Wymień
            </button>
          ) : (
            <button 
              onClick={onSelect}
              className="bg-gradient-to-r from-gray-600 to-gray-700 text-white px-2.5 py-1.5 rounded-lg font-medium hover:from-gray-500 hover:to-gray-600 transform hover:scale-105 transition-all duration-300 text-xs"
            >
              Wybierz
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResultItem;
