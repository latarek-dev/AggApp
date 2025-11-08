import React from 'react';
import { FaSpinner, FaCheckCircle, FaTimesCircle, FaExternalLinkAlt } from 'react-icons/fa';

const TransactionModal = ({ swapState, txHash, onClose }) => {
  if (swapState.status === 'idle') return null;

  const getStatusIcon = () => {
    switch (swapState.status) {
      case 'approving':
      case 'swapping':
        return <FaSpinner className="animate-spin text-blue-500" size={48} />;
      case 'success':
        return <FaCheckCircle className="text-green-500" size={48} />;
      case 'error':
        return <FaTimesCircle className="text-red-500" size={48} />;
      default:
        return null;
    }
  };

  const getStatusText = () => {
    switch (swapState.status) {
      case 'approving':
        return 'Zatwierdzanie tokena...';
      case 'approved':
        return 'Token zatwierdzony';
      case 'swapping':
        return 'Wysyłanie transakcji...';
      case 'confirming':
        return 'Oczekiwanie na potwierdzenie...';
      case 'success':
        return 'Wymiana zakończona!';
      case 'error':
        return 'Błąd transakcji';
      default:
        return '';
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-[10000]">
      <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 border border-gray-700 rounded-xl shadow-2xl p-8 max-w-md w-full mx-4">

        <div className="flex justify-center mb-6">
          {getStatusIcon()}
        </div>

        <h3 className="text-white text-xl font-bold text-center mb-2">
          {getStatusText()}
        </h3>

        {swapState.step && (
          <p className="text-gray-400 text-sm text-center mb-4">
            {swapState.step}
          </p>
        )}

        {swapState.error && (
          <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-3 mb-4">
            <p className="text-red-400 text-sm">{swapState.error}</p>
          </div>
        )}

        {/* Transaction Hash */}
        {txHash && (
          <a
            href={`https://arbiscan.io/tx/${txHash}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center space-x-2 text-blue-400 hover:text-blue-300 text-sm mb-4"
          >
            <span>Zobacz na Arbiscan</span>
            <FaExternalLinkAlt size={12} />
          </a>
        )}

        {/* Close Button */}
        {(swapState.status === 'success' || swapState.status === 'error') && (
          <button
            onClick={onClose}
            className="w-full bg-gradient-to-r from-purple-500 to-blue-600 text-white py-3 rounded-lg font-semibold hover:shadow-lg transition-all duration-200"
          >
            Zamknij
          </button>
        )}

        {/* Processing indicator */}
        {(swapState.status === 'approving' || swapState.status === 'swapping') && (
          <div className="flex items-center justify-center space-x-2 text-gray-400 text-sm">
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
            <span>Potwierdź w portfelu...</span>
          </div>
        )}
        
        {swapState.status === 'confirming' && (
          <div className="flex items-center justify-center space-x-2 text-blue-400 text-sm">
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
            <span>Transakcja w toku na blockchainie...</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default TransactionModal;

