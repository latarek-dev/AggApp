import PercentageChange from "./PercentageChange";
import { FaExchangeAlt, FaInfoCircle } from "react-icons/fa";

const ResultItem = ({ option, tokenFrom, tokenTo, index, isSelected, onSelect }) => {
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
          
          {/* Token Pair and Exchange */}
          <div className="flex-1">
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

        {/* Center - Amounts */}
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

        {/* Right Side - Output and Actions */}
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

      {/* Additional Info Row */}
      <div className="px-3 pb-3">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <span>Slippage:</span>
              <span className="text-white">{(option.slippage * 100).toFixed(3)}%</span>
            </div>
            <div className="flex items-center space-x-1">
              <span>Liquidity:</span>
              <span className="text-white">{formatLiquidity(option.liquidity)}</span>
            </div>
            <div className="flex items-center space-x-1">
              <span>Gas:</span>
              <span className="text-white">${option.gas_cost?.toFixed(4) || '0.0000'}</span>
            </div>
          </div>
          
          <PercentageChange value={option.percentage_change} />
        </div>
      </div>
    </div>
  );
};

export default ResultItem;