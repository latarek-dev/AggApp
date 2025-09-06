import React from "react";
import PercentageChange from "./PercentageChange";
import { FaCrown, FaExchangeAlt, FaInfoCircle } from "react-icons/fa";

const BestOption = ({ option, tokenFrom, tokenTo, isSelected, onSelect }) => {
  const formatRoute = (option) => {
    if (!option || !option.dex_fee) return "Unknown · 0%";
    const feePercent = (option.dex_fee * 100).toFixed(2);
    return `${option.dex} V3 · ${feePercent}%`;
  };

  const getRouteIcon = (dex) => {
    const icons = {
      'Uniswap': '🦄',
      'SushiSwap': '🍣', 
      'Camelot': '🏰'
    };
    return icons[dex] || '🔄';
  };

  const formatLiquidity = (liquidity) => {
    if (!liquidity || liquidity === 0) return '0';
    if (liquidity >= 1000000) {
      return `$${(liquidity / 1000000).toFixed(1)}M`;
    } else {
      return `$${(liquidity / 1000).toFixed(0)}k`;
    }
  };

  return (
    <div className={`bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 backdrop-blur-xl border-2 rounded-lg shadow-lg relative transition-all duration-300 ${
      isSelected 
        ? 'border-gradient-to-r from-green-400 to-emerald-800' 
        : 'border-gray-700/50 hover:border-gray-600'
    }`}>
      {/* Best Option Badge */}
      <div className="absolute -top-1 -left-1 bg-gradient-to-r from-green-400 to-emerald-500 text-gray-900 px-1.5 py-0.5 rounded-full text-xs font-bold flex items-center space-x-1">
        <FaCrown size={8} />
        <span className="text-xs">NAJLEPSZA</span>
      </div>

      {/* Main Content - Horizontal Layout */}
      <div className="flex items-center justify-between p-3">
        {/* Left Side - Token Info */}
        <div className="flex items-center space-x-3 flex-1">
          <div className="w-7 h-7 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center text-white text-xs font-bold">
            1
          </div>
          
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-white font-semibold text-sm">{option.pair}</span>
              <span className="text-gray-400 text-xs">•</span>
              <span className="text-gray-300 text-xs">{option.dex}</span>
            </div>
            
            {/* Route Info */}
            <div className="flex items-center space-x-1 mt-1">
              <span className="text-xs text-gray-400">{getRouteIcon(option.dex)}</span>
              <span className="text-xs text-gray-500">{formatRoute(option)}</span>
            </div>
          </div>
        </div>

        {/* Center - Input Amount */}
        <div className="flex-1 text-center">
          <div className="text-white font-semibold text-sm">
            {option.amount_from} {tokenFrom}
          </div>
          <div className="text-gray-400 text-xs">
            ${option.value_from_usd?.toFixed(2) || '0.00'}
          </div>
        </div>

        {/* Arrow */}
        <div className="flex items-center justify-center">
          <FaExchangeAlt className="text-gray-400" size={16} />
        </div>

        {/* Right Side - Output Amount */}
        <div className="flex-1 text-right">
          <div className="text-white font-semibold text-sm">
            {option.amount_to?.toFixed(6) || '0.000000'} {tokenTo}
          </div>
          <div className="text-gray-400 text-xs">
            ${option.value_to_usd?.toFixed(2) || '0.00'}
          </div>
        </div>

        {/* Action Button */}
        <div className="ml-4">
          <button
            onClick={onSelect}
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 ${
              isSelected
                ? 'bg-gradient-to-r from-purple-500 to-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {isSelected ? 'Wymień' : 'Wybierz'}
          </button>
        </div>
      </div>

      {/* Additional Info Row with Tooltips */}
      <div className="px-3 pb-3">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <div className="flex items-center space-x-4">
            {/* Slippage with Tooltip */}
            <div className="flex items-center space-x-1 group relative">
              <span className="text-gray-400">Slippage:</span>
              <span className="text-white">{(option.slippage * 100).toFixed(3)}%</span>
              <FaInfoCircle className="text-gray-400 group-hover:text-white transition-colors cursor-help" size={12} />
              
              {/* Tooltip */}
              <div className="absolute bottom-full left-0 mb-2 w-48 bg-gray-900 border border-gray-700 rounded-lg p-2 shadow-xl opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
                <div className="text-xs text-gray-300">
                  <div className="font-semibold text-white mb-1">Slippage</div>
                  <div>Maksymalny akceptowalny poślizg ceny podczas wymiany</div>
                </div>
              </div>
            </div>

            {/* Liquidity with Tooltip */}
            <div className="flex items-center space-x-1 group relative">
              <span className="text-gray-400">Liquidity:</span>
              <span className="text-white">{formatLiquidity(option.liquidity)}</span>
              <FaInfoCircle className="text-gray-400 group-hover:text-white transition-colors cursor-help" size={12} />
              
              {/* Tooltip */}
              <div className="absolute bottom-full left-0 mb-2 w-48 bg-gray-900 border border-gray-700 rounded-lg p-2 shadow-xl opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
                <div className="text-xs text-gray-300">
                  <div className="font-semibold text-white mb-1">Liquidity</div>
                  <div>Całkowita wartość tokenów w puli (wyższa = lepsza)</div>
                </div>
              </div>
            </div>

            {/* Gas Cost with Tooltip */}
            <div className="flex items-center space-x-1 group relative">
              <span className="text-gray-400">Gas:</span>
              <span className="text-white">${option.gas_cost?.toFixed(4) || '0.0000'}</span>
              <FaInfoCircle className="text-gray-400 group-hover:text-white transition-colors cursor-help" size={12} />
              
              {/* Tooltip */}
              <div className="absolute bottom-full left-0 mb-2 w-48 bg-gray-900 border border-gray-700 rounded-lg p-2 shadow-xl opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
                <div className="text-xs text-gray-300">
                  <div className="font-semibold text-white mb-1">Gas Cost</div>
                  <div>Szacowany koszt transakcji na blockchain</div>
                </div>
              </div>
            </div>
          </div>
          
          <PercentageChange value={option.percentage_change} />
        </div>
      </div>
    </div>
  );
};

export default BestOption;