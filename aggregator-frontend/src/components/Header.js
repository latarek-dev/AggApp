import React from 'react';
import { FaExchangeAlt, FaChartBar, FaInfoCircle, FaHistory, FaWallet, FaSignOutAlt } from 'react-icons/fa';
import { useAccount, useConnect, useDisconnect } from 'wagmi'

const Header = ({ activeTab, setActiveTab }) => {
  const { address, isConnected, chain } = useAccount()
  const { connect, connectors, isPending } = useConnect()
  const { disconnect } = useDisconnect()
  
  const navItems = [
    { id: 'swap', label: 'Wymiana', icon: FaExchangeAlt },
    { id: 'stats', label: 'Statystyki', icon: FaChartBar },
    { id: 'history', label: 'Historia', icon: FaHistory },
    { id: 'about', label: 'O aplikacji', icon: FaInfoCircle },
  ];

  return (
    <header className="w-full bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 border-b border-gray-700/50 backdrop-blur-xl relative z-[1000]">
      <div className="max-w-6xl mx-auto px-4 py-3">
        <div className="flex items-center">
          {/* Logo */}
          <div className="w-full lg:w-2/5 lg:flex-shrink-0 lg:mr-20 flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center flex-shrink-0">
              <FaExchangeAlt size={20} className="text-white" />
            </div>
            <div className="flex-1">
              <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                AggApp
              </h1>
              <p className="text-xs text-gray-400">Najlepsze kursy wymiany</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="hidden lg:flex lg:w-2/5 lg:flex-shrink-0 lg:mr-8 items-center justify-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-300 ${
                    activeTab === item.id
                      ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                      : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
                  }`}
                >
                  <Icon size={14} />
                  <span className="text-sm font-medium">{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Connect Wallet Button */}
          <div className="lg:w-1/5 lg:flex-shrink-0 flex items-center justify-end">
            {isConnected ? (
              <div className="flex items-center space-x-2 bg-green-900/20 border border-green-500/30 rounded-lg px-3 py-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <div className="flex flex-col">
                  <span className="text-green-400 text-xs font-mono">
                    {address.slice(0, 6)}...{address.slice(-4)}
                  </span>
                  <span className="text-green-300/70 text-[10px]">
                    {chain?.name || 'Arbitrum'}
                  </span>
                </div>
                <button
                  onClick={() => disconnect()}
                  className="p-1.5 text-green-400 hover:text-red-400 hover:bg-red-900/20 rounded transition-colors"
                  title="Rozłącz"
                >
                  <FaSignOutAlt size={12} />
                </button>
              </div>
            ) : (
              <div className="relative group">
                <button className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-lg font-semibold hover:shadow-lg transform hover:scale-105 transition-all duration-300 text-sm flex items-center space-x-2">
                  <FaWallet size={14} />
                  <span>Połącz Portfel</span>
                </button>
                
                <div className="absolute right-0 mt-2 w-56 bg-gray-800 border border-gray-700 rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-[9999]">
                  <div className="p-2 space-y-1">
                    {connectors.map((connector) => (
                      <button
                        key={connector.id}
                        onClick={() => connect({ connector })}
                        disabled={isPending}
                        className="w-full p-2 text-left text-white hover:bg-gray-700 rounded-lg transition-colors text-sm flex items-center space-x-2 disabled:opacity-50"
                      >
                        <FaWallet size={12} />
                        <span>{connector.name}</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;