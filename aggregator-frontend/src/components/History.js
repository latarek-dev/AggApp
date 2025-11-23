import React, { useState, useEffect } from "react";
import { FaHistory, FaExchangeAlt, FaTrash, FaExternalLinkAlt, FaCheckCircle } from "react-icons/fa";
import { getSwapHistory, clearSwapHistory } from '../utils/historyStorage';

const History = () => {
  const [history, setHistory] = useState([]);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = () => {
    const data = getSwapHistory();
    setHistory(data);
  };

  const handleClearHistory = () => {
    if (window.confirm('Czy na pewno chcesz wyczyścić całą historię?')) {
      clearSwapHistory();
      setHistory([]);
    }
  };

  const filteredHistory = filter === 'all' 
    ? history 
    : history.filter(item => item.dex === filter);

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleString('pl-PL', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatAmount = (amount) => {
    return parseFloat(amount).toFixed(6);
  };

  const getDexColor = (dex) => {
    const colors = {
      'Uniswap': 'bg-pink-500/20 text-pink-400 border-pink-500/30',
      'SushiSwap': 'bg-blue-500/20 text-blue-400 border-blue-500/30',
      'Camelot': 'bg-purple-500/20 text-purple-400 border-purple-500/30'
    };
    return colors[dex] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  };

  return (
    <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 backdrop-blur-xl border border-gray-700/50 rounded-lg shadow-lg p-8">
      <div className="flex justify-between items-center mb-8">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <FaHistory size={20} className="text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">Historia Wymian</h2>
            <p className="text-gray-400 text-sm">
              {history.length > 0 ? `${history.length} transakcji` : 'Brak transakcji'}
            </p>
          </div>
        </div>
        {history.length > 0 && (
          <button
            onClick={handleClearHistory}
            className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors flex items-center gap-2 border border-red-500/30"
          >
            <FaTrash size={14} />
            Wyczyść
          </button>
        )}
      </div>

      {/* Filtry */}
      {history.length > 0 && (
        <div className="flex gap-2 mb-6 flex-wrap">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg transition-colors border ${
              filter === 'all' 
                ? 'bg-purple-500 text-white border-purple-600' 
                : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700/50 border-gray-700'
            }`}
          >
            Wszystkie ({history.length})
          </button>
          {['Uniswap', 'SushiSwap', 'Camelot'].map(dex => {
            const count = history.filter(item => item.dex === dex).length;
            if (count === 0) return null;
            return (
              <button
                key={dex}
                onClick={() => setFilter(dex)}
                className={`px-4 py-2 rounded-lg transition-colors border ${
                  filter === dex 
                    ? 'bg-purple-500 text-white border-purple-600' 
                    : 'bg-gray-800/50 text-gray-400 hover:bg-gray-700/50 border-gray-700'
                }`}
              >
                {dex} ({count})
              </button>
            );
          })}
        </div>
      )}

      {/* Lista transakcji */}
      {filteredHistory.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-20 h-20 bg-gray-800/50 rounded-full flex items-center justify-center mx-auto mb-4">
            <FaExchangeAlt size={32} className="text-gray-500" />
          </div>
          <h3 className="text-white text-lg font-semibold mb-2">
            {filter === 'all' 
              ? 'Brak historii' 
              : `Brak transakcji na ${filter}`}
          </h3>
          <p className="text-gray-400 text-sm">
            {filter === 'all'
              ? 'Po wykonaniu pierwszej wymiany, historia pojawi się tutaj'
              : 'Spróbuj wybrać inny filtr lub wykonaj wymianę'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredHistory.map((item) => (
            <div
              key={item.id}
              className="bg-gray-800/30 hover:bg-gray-800/50 rounded-lg p-4 border border-gray-700/50 transition-all"
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                {/* Lewa strona - tokeny */}
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-8 h-8 bg-green-500/20 rounded-full flex items-center justify-center">
                      <FaCheckCircle size={14} className="text-green-400" />
                    </div>
                    <div>
                      <div className="text-white font-semibold text-lg">
                        {formatAmount(item.amountFrom)} {item.tokenFrom} → {formatAmount(item.amountTo)} {item.tokenTo}
                      </div>
                      <div className="flex items-center gap-2 flex-wrap mt-1">
                        <span className={`px-2 py-1 rounded text-xs font-medium border ${getDexColor(item.dex)}`}>
                          {item.dex}
                        </span>
                        <span className="text-gray-400 text-xs">
                          {formatDate(item.timestamp)}
                        </span>
                        {item.percentageChange && item.percentageChange !== 0 && (
                          <span className="text-green-400 text-xs font-medium">
                            +{item.percentageChange.toFixed(2)}%
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Prawa strona - szczegóły */}
                <div className="flex flex-col items-end gap-1">
                  <div className="text-white font-medium">
                    ${item.valueUSD?.toFixed(2) || '0.00'}
                  </div>
                  <div className="text-gray-400 text-xs">
                    Fee: {(item.fee * 100).toFixed(2)}% · Gas: ${item.gasUsed?.toFixed(4) || '0'}
                  </div>
                  <a
                    href={`https://arbiscan.io/tx/${item.txHash}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-purple-400 hover:text-purple-300 text-xs flex items-center gap-1 mt-1"
                  >
                    Zobacz na Arbiscan <FaExternalLinkAlt size={10} />
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default History;
