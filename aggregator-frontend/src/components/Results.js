import ResultItem from "./ResultItem";
import BestOption from "./BestOption";
import { FaSearch, FaSpinner, FaSync } from "react-icons/fa";

const Results = ({ options, tokenFrom, tokenTo, isLoading, isRefreshing, selectedOfferIndex, onSelectOffer }) => {
  if (isLoading) {
    return (
      <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 backdrop-blur-xl border border-gray-700/50 rounded-lg shadow-lg p-8">
        <div className="flex flex-col items-center justify-center space-y-4">
          <FaSpinner className="animate-spin text-purple-500" size={32} />
          <h3 className="text-white text-lg font-semibold">Wyszukiwanie najlepszych kursów...</h3>
          <p className="text-gray-400 text-sm">Sprawdzam dostępne opcje wymiany</p>
        </div>
      </div>
    );
  }

  if (!options || options.length === 0) {
    return (
      <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 backdrop-blur-xl border border-gray-700/50 rounded-lg shadow-lg p-8">
        <div className="flex flex-col items-center justify-center space-y-4">
          <FaSearch className="text-gray-500" size={32} />
          <h3 className="text-white text-lg font-semibold">Brak wyników</h3>
          <p className="text-gray-400 text-sm">Spróbuj wyszukać inną parę tokenów</p>
        </div>
      </div>
    );
  }

  const bestOption = options[0];
  const otherOptions = options.slice(1);

  return (
    <div className="space-y-6">
      {/* Header - Wyśrodkowany tytuł */}
      <div className="text-center">
        <h2 className="text-white text-xl font-bold flex items-center justify-center space-x-2">
          <FaSearch className="text-purple-500" />
          <span>Wyniki wyszukiwania</span>
          {/* Background Refresh Indicator */}
          {isRefreshing && (
            <div className="flex items-center space-x-2 ml-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-xs text-green-400">Odświeżanie...</span>
            </div>
          )}
        </h2>
        <p className="text-gray-400 text-sm mt-1">
          Znalezione opcje wymiany {tokenFrom} → {tokenTo}
        </p>
      </div>

      {/* Best Option with subtle refresh indicator */}
      <div className="relative">
        {isRefreshing && (
          <div className="absolute -top-2 -right-2 z-10">
            <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
              <FaSync className="animate-spin text-white" size={10} />
            </div>
          </div>
        )}
        <BestOption
          option={bestOption}
          tokenFrom={tokenFrom}
          tokenTo={tokenTo}
          isSelected={selectedOfferIndex === 0}
          onSelect={() => onSelectOffer(0)}
        />
      </div>

      {/* Other Options */}
      {otherOptions.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-gray-300 text-sm font-medium text-center">
            Inne dostępne opcje ({otherOptions.length})
          </h3>
          <div className="space-y-3">
            {otherOptions.map((option, index) => (
              <div key={`${option.dex}-${option.pair}`} className="relative">
                {isRefreshing && (
                  <div className="absolute -top-1 -right-1 z-10">
                    <div className="w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
                      <FaSync className="animate-spin text-white" size={8} />
                    </div>
                  </div>
                )}
                <ResultItem
                  option={option}
                  tokenFrom={tokenFrom}
                  tokenTo={tokenTo}
                  index={index}
                  isSelected={selectedOfferIndex === index + 1}
                  onSelect={() => onSelectOffer(index + 1)}
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Results;