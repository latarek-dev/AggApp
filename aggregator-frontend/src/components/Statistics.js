import React from "react";
import { FaChartBar, FaExchangeAlt, FaClock, FaUsers, FaCoins } from "react-icons/fa";

const Statistics = () => {
  return (
    <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 backdrop-blur-xl border border-gray-700/50 rounded-lg shadow-lg p-8">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <FaChartBar size={24} className="text-white" />
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">Statystyki Aplikacji</h2>
        <p className="text-gray-400">Wkrótce dostępne szczegółowe statystyki użytkowania</p>
      </div>

      {/* Placeholder Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Total Exchanges */}
        <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700/50">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg flex items-center justify-center">
              <FaExchangeAlt size={16} className="text-white" />
            </div>
            <div>
              <h3 className="text-white font-semibold">Wymiany</h3>
              <p className="text-gray-400 text-sm">Łącznie wykonane</p>
            </div>
          </div>
          <div className="text-2xl font-bold text-white mb-1">-</div>
          <div className="text-xs text-gray-500">Wkrótce</div>
        </div>

        {/* Average Response Time */}
        <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700/50">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-lg flex items-center justify-center">
              <FaClock size={16} className="text-white" />
            </div>
            <div>
              <h3 className="text-white font-semibold">Czas odpowiedzi</h3>
              <p className="text-gray-400 text-sm">Średni czas</p>
            </div>
          </div>
          <div className="text-2xl font-bold text-white mb-1">~2s</div>
          <div className="text-xs text-gray-500">Aktualny</div>
        </div>

        {/* Active Users */}
        <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700/50">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg flex items-center justify-center">
              <FaUsers size={16} className="text-white" />
            </div>
            <div>
              <h3 className="text-white font-semibold">Użytkownicy</h3>
              <p className="text-gray-400 text-sm">Aktywni dzisiaj</p>
            </div>
          </div>
          <div className="text-2xl font-bold text-white mb-1">-</div>
          <div className="text-xs text-gray-500">Wkrótce</div>
        </div>

        {/* Supported Tokens */}
        <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700/50">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-10 h-10 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-lg flex items-center justify-center">
              <FaCoins size={16} className="text-white" />
            </div>
            <div>
              <h3 className="text-white font-semibold">Tokeny</h3>
              <p className="text-gray-400 text-sm">Obsługiwane</p>
            </div>
          </div>
          <div className="text-2xl font-bold text-white mb-1">5+</div>
          <div className="text-xs text-gray-500">ETH, USDT, USDC, DAI, WBTC</div>
        </div>

        {/* DEX Count */}
        <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700/50">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
              <FaExchangeAlt size={16} className="text-white" />
            </div>
            <div>
              <h3 className="text-white font-semibold">DEX-y</h3>
              <p className="text-gray-400 text-sm">Zintegrowane</p>
            </div>
          </div>
          <div className="text-2xl font-bold text-white mb-1">3</div>
          <div className="text-xs text-gray-500">Uniswap, SushiSwap, Camelot</div>
        </div>

        {/* Success Rate */}
        <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700/50">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-green-600 rounded-lg flex items-center justify-center">
              <FaChartBar size={16} className="text-white" />
            </div>
            <div>
              <h3 className="text-white font-semibold">Sukces</h3>
              <p className="text-gray-400 text-sm">Wskaźnik powodzenia</p>
            </div>
          </div>
          <div className="text-2xl font-bold text-white mb-1">-</div>
          <div className="text-xs text-gray-500">Wkrótce</div>
        </div>
      </div>

      {/* Coming Soon Message */}
      <div className="mt-8 text-center">
        <div className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-lg p-6">
          <h3 className="text-white font-semibold mb-2">Wkrótce dostępne</h3>
          <p className="text-gray-400 text-sm">
            Szczegółowe statystyki użytkowania, wykresy wydajności, analiza trendów i wiele więcej!
          </p>
        </div>
      </div>
    </div>
  );
};

export default Statistics;
