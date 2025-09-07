import React from "react";
import { FaHistory, FaExchangeAlt, FaClock, FaCheckCircle } from "react-icons/fa";

const History = () => {
  return (
    <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 backdrop-blur-xl border border-gray-700/50 rounded-lg shadow-lg p-8">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <FaHistory size={24} className="text-white" />
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">Historia Wymian</h2>
        <p className="text-gray-400">Wkrótce dostępna historia Twoich transakcji</p>
      </div>

      {/* Placeholder Content */}
      <div className="space-y-6">
        {/* Empty State */}
        <div className="text-center py-12">
          <div className="w-20 h-20 bg-gray-800/50 rounded-full flex items-center justify-center mx-auto mb-4">
            <FaExchangeAlt size={32} className="text-gray-500" />
          </div>
          <h3 className="text-white text-lg font-semibold mb-2">Brak historii</h3>
          <p className="text-gray-400 text-sm mb-6">
            Po wykonaniu pierwszej wymiany, historia pojawi się tutaj
          </p>
        </div>

        {/* Sample History Items (Placeholder) */}
        <div className="space-y-4 opacity-50">
          <div className="bg-gray-800/30 rounded-lg p-4 border border-gray-700/30">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-green-500/20 rounded-full flex items-center justify-center">
                  <FaCheckCircle size={14} className="text-green-400" />
                </div>
                <div>
                  <div className="text-white font-medium">1.0 ETH → 4,275.67 USDT</div>
                  <div className="text-gray-400 text-sm">Uniswap V3 · 0.05%</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-gray-400 text-sm">Dzisiaj, 14:32</div>
                <div className="text-green-400 text-sm font-medium">+0.07%</div>
              </div>
            </div>
          </div>

          <div className="bg-gray-800/30 rounded-lg p-4 border border-gray-700/30">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-green-500/20 rounded-full flex items-center justify-center">
                  <FaCheckCircle size={14} className="text-green-400" />
                </div>
                <div>
                  <div className="text-white font-medium">0.5 ETH → 2,137.83 USDT</div>
                  <div className="text-gray-400 text-sm">Camelot V3 · 0.01%</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-gray-400 text-sm">Wczoraj, 09:15</div>
                <div className="text-red-400 text-sm font-medium">-0.91%</div>
              </div>
            </div>
          </div>
        </div>

        {/* Coming Soon Message */}
        <div className="mt-8 text-center">
          <div className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-lg p-6">
            <h3 className="text-white font-semibold mb-2">Wkrótce dostępne</h3>
            <p className="text-gray-400 text-sm mb-4">
              Pełna historia transakcji, eksport danych, filtry czasowe i szczegółowe statystyki
            </p>
            <div className="flex items-center justify-center space-x-4 text-xs text-gray-500">
              <div className="flex items-center space-x-1">
                <FaClock size={12} />
                <span>Filtry czasowe</span>
              </div>
              <div className="flex items-center space-x-1">
                <FaExchangeAlt size={12} />
                <span>Szczegóły transakcji</span>
              </div>
              <div className="flex items-center space-x-1">
                <FaCheckCircle size={12} />
                <span>Status wykonania</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default History;
