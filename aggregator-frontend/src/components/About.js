import React from "react";
import { FaInfoCircle, FaExchangeAlt, FaChartLine, FaShieldAlt, FaRocket } from "react-icons/fa";

const About = () => {
  return (
    <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 backdrop-blur-xl border border-gray-700/50 rounded-lg shadow-lg p-8">
      <div className="text-center mb-8">
        <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <FaInfoCircle size={24} className="text-white" />
        </div>
        <h2 className="text-2xl font-bold text-white mb-2">O Aplikacji</h2>
        <p className="text-gray-400">AggApp - Najlepsze kursy wymiany w jednym miejscu</p>
      </div>

      {/* Main Description */}
      <div className="max-w-4xl mx-auto">
        <div className="bg-gray-800/50 rounded-lg p-6 mb-8 border border-gray-700/50">
          <p className="text-gray-300 text-lg leading-relaxed text-center">
            AggApp to zaawansowany agregator kursów wymiany kryptowalut, który porównuje oferty 
            z różnych zdecentralizowanych giełd (DEX) w czasie rzeczywistym, pomagając użytkownikom 
            znaleźć najlepsze kursy wymiany dla swoich transakcji.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* Real-time Comparison */}
          <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700/50">
            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg flex items-center justify-center mb-4">
              <FaExchangeAlt size={20} className="text-white" />
            </div>
            <h3 className="text-white font-semibold text-lg mb-2">Porównanie w czasie rzeczywistym</h3>
            <p className="text-gray-400 text-sm">
              Porównuje kursy z Uniswap, SushiSwap i Camelot w czasie rzeczywistym
            </p>
          </div>

          {/* Best Rates */}
          <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700/50">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-lg flex items-center justify-center mb-4">
              <FaChartLine size={20} className="text-white" />
            </div>
            <h3 className="text-white font-semibold text-lg mb-2">Najlepsze kursy</h3>
            <p className="text-gray-400 text-sm">
              Automatycznie znajduje najlepsze oferty wymiany dla Twoich tokenów
            </p>
          </div>

          {/* Security */}
          <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700/50">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-lg flex items-center justify-center mb-4">
              <FaShieldAlt size={20} className="text-white" />
            </div>
            <h3 className="text-white font-semibold text-lg mb-2">Bezpieczeństwo</h3>
            <p className="text-gray-400 text-sm">
              Bezpieczne połączenie z DEX-ami bez przechowywania kluczy prywatnych
            </p>
          </div>

          {/* Performance */}
          <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700/50">
            <div className="w-12 h-12 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-lg flex items-center justify-center mb-4">
              <FaRocket size={20} className="text-white" />
            </div>
            <h3 className="text-white font-semibold text-lg mb-2">Wydajność</h3>
            <p className="text-gray-400 text-sm">
              Szybkie wyszukiwanie i odświeżanie kursów w tle
            </p>
          </div>

          {/* Supported Tokens */}
          <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700/50">
            <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center mb-4">
              <FaExchangeAlt size={20} className="text-white" />
            </div>
            <h3 className="text-white font-semibold text-lg mb-2">Obsługiwane tokeny</h3>
            <p className="text-gray-400 text-sm">
              ETH, USDT, USDC, DAI, WBTC i wiele innych popularnych tokenów
            </p>
          </div>

          {/* Auto-refresh */}
          <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700/50">
            <div className="w-12 h-12 bg-gradient-to-br from-teal-500 to-green-600 rounded-lg flex items-center justify-center mb-4">
              <FaChartLine size={20} className="text-white" />
            </div>
            <h3 className="text-white font-semibold text-lg mb-2">Auto-odświeżanie</h3>
            <p className="text-gray-400 text-sm">
              Automatyczne odświeżanie kursów co 10-60 sekund
            </p>
          </div>
        </div>

        {/* Technical Details */}
        <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700/50">
          <h3 className="text-white font-semibold text-lg mb-4">Szczegóły techniczne</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-400">Zintegrowane DEX-y:</span>
              <span className="text-white ml-2">Uniswap V3, SushiSwap V3, Camelot</span>
            </div>
            <div>
              <span className="text-gray-400">Sieć:</span>
              <span className="text-white ml-2">Arbitrum</span>
            </div>
            <div>
              <span className="text-gray-400">Czas odpowiedzi:</span>
              <span className="text-white ml-2">~2 sekundy</span>
            </div>
            <div>
              <span className="text-gray-400">Wersja:</span>
              <span className="text-white ml-2">1.0.0</span>
            </div>
          </div>
        </div>

        {/* Contact/Support */}
        <div className="mt-8 text-center">
          <div className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 rounded-lg p-6">
            <h3 className="text-white font-semibold mb-2">Potrzebujesz pomocy?</h3>
            <p className="text-gray-400 text-sm">
              Wkrótce dostępny system wsparcia i dokumentacja użytkownika
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default About;
