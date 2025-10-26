import { useAccount, useConnect, useDisconnect } from 'wagmi'
import { FaWallet, FaSignOutAlt, FaCheck } from 'react-icons/fa'

const WalletConnect = () => {
  const { address, isConnected, chain } = useAccount()
  const { connect, connectors, isPending } = useConnect()
  const { disconnect } = useDisconnect()

  if (isConnected) {
    return (
      <div className="bg-green-900/20 border border-green-500/30 rounded-xl p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
              <FaWallet className="text-white" size={18} />
            </div>
            <div className="flex flex-col">
              <span className="text-green-400 text-sm font-semibold">
                Połączony
              </span>
              <span className="text-green-300 text-xs font-mono">
                {address.slice(0, 6)}...{address.slice(-4)}
              </span>
              <span className="text-green-400/70 text-xs">
                {chain?.name || 'Unknown network'}
              </span>
            </div>
          </div>
          
          <button
            onClick={() => disconnect()}
            className="p-2 text-green-400 hover:text-red-400 hover:bg-red-900/20 rounded-lg transition-all duration-200"
            title="Rozłącz portfel"
          >
            <FaSignOutAlt size={16} />
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-gray-800/50 border border-gray-700/50 rounded-xl p-4">
      <div className="text-center mb-4">
        <FaWallet className="text-gray-400 mx-auto mb-2" size={28} />
        <h3 className="text-white text-sm font-semibold mb-1">
          Połącz portfel
        </h3>
        <p className="text-gray-400 text-xs">
          Aby wykonywać transakcje
        </p>
      </div>
      
      <div className="space-y-2">
        {connectors.map((connector) => (
          <button
            key={connector.id}
            onClick={() => connect({ connector })}
            disabled={isPending}
            className="w-full p-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:shadow-lg transition-all duration-300 flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isPending ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span className="text-sm font-medium">Łączenie...</span>
              </>
            ) : (
              <>
                <FaWallet size={14} />
                <span className="text-sm font-medium">
                  {connector.name}
                </span>
              </>
            )}
          </button>
        ))}
      </div>
      
      <p className="text-gray-500 text-xs text-center mt-3">
        Obsługujemy MetaMask, Rabby i inne portfele
      </p>
    </div>
  )
}

export default WalletConnect