import { useState } from "react";
import Select from "react-select";
import { FaEthereum, FaBitcoin, FaDollarSign, FaRegMoneyBillAlt, FaExchangeAlt, FaWallet } from "react-icons/fa";
import { BiTransfer } from "react-icons/bi";
import { useTokenBalance } from "../hooks/useTokenBalance";
import { useAccount } from "wagmi";

const customStyles = {
  control: (styles, { isFocused }) => ({
    ...styles,
    backgroundColor: '#1f2937',
    border: '2px solid',
    borderColor: isFocused ? '#3b82f6' : '#374151',
    borderRadius: '10px',
    boxShadow: isFocused ? '0 0 0 3px rgba(59, 130, 246, 0.1)' : 'none',
    padding: '4px 10px',
    minHeight: '42px',
    transition: 'all 0.3s ease',
    '&:hover': {
      borderColor: '#60a5fa',
      transform: 'translateY(-1px)',
      boxShadow: '0 6px 16px rgba(0, 0, 0, 0.2)',
    },
  }),
  singleValue: (styles) => ({
    ...styles,
    color: '#f9fafb',
    fontSize: '13px',
    fontWeight: '600',
    display: 'flex',
    alignItems: 'center',
  }),
  option: (styles, { isFocused, isSelected }) => ({
    ...styles,
    backgroundColor: isSelected ? '#3b82f6' : isFocused ? '#374151' : '#1f2937',
    color: isSelected ? '#ffffff' : '#f9fafb',
    padding: '10px 14px',
    cursor: 'pointer',
    fontSize: '13px',
    fontWeight: '500',
    display: 'flex',
    alignItems: 'center',
    transition: 'all 0.2s ease',
    '&:hover': {
      backgroundColor: isSelected ? '#3b82f6' : '#4b5563',
    },
  }),
  menu: (styles) => ({
    ...styles,
    backgroundColor: '#1f2937',
    border: '1px solid #374151',
    borderRadius: '10px',
    boxShadow: '0 16px 32px rgba(0, 0, 0, 0.5)',
    zIndex: 999,
    marginTop: '4px',
  }),
  input: (styles) => ({
    ...styles,
    color: '#f9fafb',
  }),
  placeholder: (styles) => ({
    ...styles,
    color: '#9ca3af',
  }),
};

const ExchangeForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    token_from: "ETH",
    token_to: "USDT",
    amount: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const { isConnected } = useAccount();
  
  const { balance: balanceFrom, formatted: formattedFrom, fullAmount: fullAmountFrom, isLoading: isLoadingBalance } = useTokenBalance(formData.token_from);

  const handleSelectChange = (selectedOption, actionMeta) => {
    setFormData((prevData) => ({
      ...prevData,
      [actionMeta.name]: selectedOption.value,
    }));
  };

  const handleInputChange = (e) => {
    const value = e.target.value;
    if (/^\d*\.?\d*$/.test(value) || value === '') {
      setFormData({
        ...formData,
        amount: value,
      });
    }
  };

  const handleMaxClick = () => {
    if (fullAmountFrom && parseFloat(fullAmountFrom) > 0) {
      setFormData({
        ...formData,
        amount: fullAmountFrom,
      });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.amount || parseFloat(formData.amount) <= 0) return;
    
    setIsLoading(true);
    try {
      await onSubmit({
        ...formData,
        amount: parseFloat(formData.amount),
      });
    } finally {
      setIsLoading(false);
    }
  };

  const tokenOptions = [
    {
      value: "ETH",
      label: (
        <div className="flex items-center space-x-2">
          <div className="w-5 h-5 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <FaEthereum size={14} className="text-white" />
          </div>
          <div>
            <div className="font-semibold text-white text-sm">ETH</div>
            <div className="text-xs text-gray-400">Ethereum</div>
          </div>
        </div>
      ),
    },
    {
      value: "USDT",
      label: (
        <div className="flex items-center space-x-2">
          <div className="w-5 h-5 bg-gradient-to-br from-green-500 to-teal-600 rounded-full flex items-center justify-center">
            <FaDollarSign size={14} className="text-white" />
          </div>
          <div>
            <div className="font-semibold text-white text-sm">USDT</div>
            <div className="text-xs text-gray-400">Tether USD</div>
          </div>
        </div>
      ),
    },
    {
      value: "USDC",
      label: (
        <div className="flex items-center space-x-2">
          <div className="w-5 h-5 bg-gradient-to-br from-blue-400 to-cyan-600 rounded-full flex items-center justify-center">
            <FaRegMoneyBillAlt size={14} className="text-white" />
          </div>
          <div>
            <div className="font-semibold text-white text-sm">USDC</div>
            <div className="text-xs text-gray-400">USD Coin</div>
          </div>
        </div>
      ),
    },
    {
      value: "DAI",
      label: (
        <div className="flex items-center space-x-2">
          <div className="w-5 h-5 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-full flex items-center justify-center">
            <FaRegMoneyBillAlt size={14} className="text-white" />
          </div>
          <div>
            <div className="font-semibold text-white text-sm">DAI</div>
            <div className="text-xs text-gray-400">Dai Stablecoin</div>
          </div>
        </div>
      ),
    },
    {
      value: "WBTC",
      label: (
        <div className="flex items-center space-x-2">
          <div className="w-5 h-5 bg-gradient-to-br from-orange-500 to-red-600 rounded-full flex items-center justify-center">
            <FaBitcoin size={14} className="text-white" />
          </div>
          <div>
            <div className="font-semibold text-white text-sm">WBTC</div>
            <div className="text-xs text-gray-400">Wrapped Bitcoin</div>
          </div>
        </div>
      ),
    },
  ];

  return (
    <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 backdrop-blur-xl border border-gray-700/50 shadow-2xl rounded-2xl p-5 w-full mx-auto ml-0 lg:ml-8">
      <div className="text-center mb-4">
        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-2">
          <FaExchangeAlt size={18} className="text-white" />
        </div>
        <h2 className="text-lg font-bold text-white mb-1">Wymiana Tokenów</h2>
        <p className="text-xs text-gray-400">Znajdź najlepsze kursy wymiany</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-3">
        {/* Token From */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-gray-300 uppercase tracking-wide">
            Token do wymiany
          </label>
          <Select
            name="token_from"
            value={tokenOptions.find((option) => option.value === formData.token_from)}
            onChange={handleSelectChange}
            options={tokenOptions}
            styles={customStyles}
            placeholder="Wybierz token..."
            isSearchable={true}
          />
        </div>

        {/* Swap Direction Button */}
        <div className="flex justify-center">
          <button
            type="button"
            className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white shadow-lg hover:shadow-xl transform hover:scale-110 transition-all duration-300"
            onClick={() => {
              setFormData(prev => ({
                ...prev,
                token_from: prev.token_to,
                token_to: prev.token_from
              }));
            }}
          >
            <BiTransfer size={14} />
          </button>
        </div>

        {/* Token To */}
        <div className="space-y-1.5">
          <label className="text-xs font-semibold text-gray-300 uppercase tracking-wide">
            Token docelowy
          </label>
          <Select
            name="token_to"
            value={tokenOptions.find((option) => option.value === formData.token_to)}
            onChange={handleSelectChange}
            options={tokenOptions}
            styles={customStyles}
            placeholder="Wybierz token..."
            isSearchable={true}
          />
        </div>

        {/* Amount */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-gray-300 uppercase tracking-wide">
              Ilość
            </label>
            {isConnected && (
              <div className="flex items-center space-x-2">
                <div className="flex items-center space-x-1 text-xs text-gray-400">
                  <FaWallet size={10} />
                  <span>
                    {isLoadingBalance ? (
                      <span className="animate-pulse">...</span>
                    ) : (
                      <span className="font-mono">{formattedFrom}</span>
                    )}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={handleMaxClick}
                  disabled={isLoadingBalance || !formattedFrom}
                  className="px-2 py-0.5 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white text-xs font-bold rounded transition-colors"
                >
                  MAX
                </button>
              </div>
            )}
          </div>
          <div className="relative">
            <input
              type="text"
              inputMode="decimal"
              name="amount"
              value={formData.amount}
              onChange={handleInputChange}
              placeholder="0.0"
              autoComplete="off"
              className="w-full p-2.5 bg-gray-800/50 border-2 border-gray-600 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300 text-sm font-medium"
            />
            <div className="absolute right-2.5 top-1/2 transform -translate-y-1/2 text-gray-400 text-xs font-medium">
              {formData.token_from}
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading || !formData.amount || parseFloat(formData.amount) <= 0}
          className={`w-full py-2.5 rounded-lg text-sm font-bold transition-all duration-300 transform ${
            isLoading || !formData.amount || parseFloat(formData.amount) <= 0
              ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
              : 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg hover:shadow-xl hover:scale-105'
          }`}
        >
          {isLoading ? (
            <div className="flex items-center justify-center space-x-2">
              <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Wyszukiwanie...</span>
            </div>
          ) : (
            'Znajdź najlepszy kurs'
          )}
        </button>
      </form>
    </div>
  );
};

export default ExchangeForm;