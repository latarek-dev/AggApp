import React, { useState } from "react";
import PercentageChange from "./PercentageChange";
import TransactionModal from "./TransactionModal";
import { FaExchangeAlt, FaInfoCircle, FaSpinner, FaCheckCircle } from "react-icons/fa";
import { useSwap } from "../hooks/useSwap";

const ExchangeOption = ({ 
  option, 
  tokenFrom, 
  tokenTo,
  amount,
  index, 
  isSelected, 
  onSelect, 
  isBest = false,
  showTooltips = false 
}) => {
  const { executeSwap, swapState, isConnected, isPending, isSuccess, txHash, resetSwap } = useSwap();
  const [showModal, setShowModal] = useState(false);
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

  const getBorderClasses = () => {
    if (isBest) {
      return isSelected 
        ? 'border-2 border-gradient-to-r from-green-400 to-emerald-800' 
        : 'border-2 border-gray-700/50 hover:border-gray-600';
    } else {
      return isSelected 
        ? 'border-2 border-gradient-to-r from-blue-500 to-purple-600' 
        : 'border border-gray-700/50 hover:border-gray-600';
    }
  };

  const getRankingCircle = () => {
    if (isBest) {
      return (
        <div className="w-7 h-7 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center text-white text-xs font-bold">
          1
        </div>
      );
    } else {
      return (
        <div className="w-7 h-7 bg-gradient-to-br from-gray-600 to-gray-700 rounded-full flex items-center justify-center text-white text-xs font-bold">
          {index + 2}
        </div>
      );
    }
  };

  const handleSwapClick = async () => {
    if (!isSelected) {
      onSelect();
      return;
    }
    
    if (!isConnected) {
      alert('Połącz portfel aby wykonać wymianę');
      return;
    }

    setShowModal(true);
    await executeSwap(option, tokenFrom, tokenTo, amount);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    resetSwap();
  };

  const getActionButton = () => {
    const baseClasses = "px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 flex items-center space-x-2";
    
    if (isPending || swapState.status === 'approving' || swapState.status === 'swapping' || swapState.status === 'confirming') {
      return (
        <button disabled className={`${baseClasses} bg-gray-600 text-gray-300 cursor-not-allowed`}>
          <FaSpinner className="animate-spin" size={12} />
          <span>{swapState.step || 'Przetwarzanie...'}</span>
        </button>
      );
    }

    if (isSuccess || swapState.status === 'success') {
      return (
        <button disabled className={`${baseClasses} bg-green-600 text-white cursor-not-allowed`}>
          <FaCheckCircle size={12} />
          <span>Wykonano!</span>
        </button>
      );
    }

    const selectedClasses = isBest
      ? "bg-gradient-to-r from-green-500 to-emerald-600 text-white hover:shadow-lg"
      : "bg-gradient-to-r from-purple-500 to-blue-600 text-white hover:shadow-lg";
    const unselectedClasses = "bg-gray-700 text-gray-300 hover:bg-gray-600";

    return (
      <button
        onClick={handleSwapClick}
        disabled={!isConnected && isSelected}
        className={`${baseClasses} ${
          isSelected ? selectedClasses : unselectedClasses
        } ${!isConnected && isSelected ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        {isSelected ? (
          <>
            <FaExchangeAlt size={12} />
            <span>Wymień</span>
          </>
        ) : (
          <span>Wybierz</span>
        )}
      </button>
    );
  };

  const getAdditionalInfo = () => {
    const infoItems = [
      { label: "Liquidity:", value: formatLiquidity(option.liquidity) },
      { label: "Gas:", value: `$${option.gas_cost?.toFixed(4) || '0.0000'}` }
    ];

    if (showTooltips) {
      return (
        <div className="flex items-center space-x-4">
          {infoItems.map((item, idx) => (
            <div key={idx} className="flex items-center space-x-1 group relative">
              <span className="text-gray-400">{item.label}</span>
              <span className="text-white">{item.value}</span>
              <FaInfoCircle className="text-gray-400 group-hover:text-white transition-colors cursor-help" size={12} />
              
              {/* Tooltip */}
              <div className="absolute bottom-full left-0 mb-2 w-48 bg-gray-900 border border-gray-700 rounded-lg p-2 shadow-xl opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-10">
                <div className="text-xs text-gray-300">
                  <div className="font-semibold text-white mb-1">{item.label.replace(':', '')}</div>
                  <div>
                    {item.label === "Płynność:" && "Całkowita wartość tokenów w puli (wyższa = lepsza)"}
                    {item.label === "Gaz:" && "Szacowany koszt transakcji na blockchain"}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      );
    } else {
      return (
        <div className="flex items-center space-x-4">
          {infoItems.map((item, idx) => (
            <div key={idx} className="flex items-center space-x-1">
              <span className="text-gray-400">{item.label}</span>
              <span className="text-white">{item.value}</span>
            </div>
          ))}
        </div>
      );
    }
  };

  return (
    <>
      <TransactionModal 
        swapState={swapState}
        txHash={txHash}
        onClose={handleCloseModal}
      />
      
      <div className={`bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 backdrop-blur-xl rounded-lg shadow-lg relative transition-all duration-300 ${
        isBest ? 'shadow-lg' : 'shadow-md hover:shadow-lg transform hover:scale-[1.002]'
      } ${getBorderClasses()}`}>
      
      {/* Main Content - Horizontal Layout */}
      <div className="flex items-center justify-between p-3">
        {/* Left Side - Token Info and Ranking */}
        <div className="flex items-center space-x-3 flex-1">
          {getRankingCircle()}
          
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
          {getActionButton()}
        </div>
      </div>

      {/* Additional Info Row */}
      <div className="px-3 pb-3">
        <div className="flex items-center justify-between text-xs text-gray-400">
          {getAdditionalInfo()}
          <PercentageChange value={option.percentage_change} />
        </div>
      </div>
    </div>
    </>
  );
};

export default ExchangeOption;
