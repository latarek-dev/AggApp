import React from "react";
import { FaSync, FaCog, FaClock, FaInfoCircle } from "react-icons/fa";

const SettingsPanel = ({ 
  autoRefresh, 
  setAutoRefresh, 
  refreshInterval, 
  setRefreshInterval, 
  isRefreshing, 
  onRefresh 
}) => {
  return (
    <div className="w-full lg:w-1/5 lg:flex-shrink-0">
      <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 backdrop-blur-xl border border-gray-700/50 rounded-lg shadow-lg p-6">
        {/* Header */}
        <div className="flex items-center space-x-2 mb-6">
          <FaCog className="text-purple-500" size={20} />
          <h3 className="text-white text-lg font-semibold">Ustawienia</h3>
        </div>

        {/* Auto-refresh Section */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <label className="flex items-center space-x-2 text-sm text-gray-300">
              <FaClock className="text-gray-400" size={14} />
              <span>Auto-odświeżanie</span>
            </label>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="w-4 h-4 text-purple-600 bg-gray-700 border-gray-600 rounded focus:ring-purple-500 focus:ring-2"
            />
          </div>

          {/* Refresh Interval */}
          {autoRefresh && (
            <div className="space-y-2">
              <label className="text-xs text-gray-400">Interwał odświeżania</label>
              <select
                value={refreshInterval}
                onChange={(e) => setRefreshInterval(Number(e.target.value))}
                className="w-full bg-gray-700 border border-gray-600 text-white text-sm rounded-lg px-3 py-2 focus:ring-purple-500 focus:border-purple-500"
              >
                <option value={10}>10 sekund</option>
                <option value={30}>30 sekund</option>
                <option value={60}>60 sekund</option>
              </select>
            </div>
          )}

          {/* Manual Refresh Button */}
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="w-full flex items-center justify-center space-x-2 px-4 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white text-sm font-medium rounded-lg transition-colors duration-200"
          >
            <FaSync className={isRefreshing ? "animate-spin" : ""} size={16} />
            <span>{isRefreshing ? "Odświeżanie..." : "Odśwież teraz"}</span>
          </button>

          {/* Refresh Status */}
          {isRefreshing && (
            <div className="flex items-center space-x-2 text-green-400 text-xs">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span>Odświeżanie w tle...</span>
            </div>
          )}
        </div>

        {/* Divider */}
        <div className="border-t border-gray-700 my-6"></div>

        {/* Info Section */}
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <FaInfoCircle className="text-gray-400" size={14} />
            <span className="text-gray-400 text-xs font-medium">O aplikacji</span>
          </div>
          
          <div className="text-xs text-gray-500 leading-relaxed">
            AggApp porównuje kursy wymiany z różnych DEX-ów w czasie rzeczywistym, 
            pomagając znaleźć najlepsze oferty dla Twoich transakcji.
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPanel;