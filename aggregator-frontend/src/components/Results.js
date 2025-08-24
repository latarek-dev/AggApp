import ResultItem from "./ResultItem";
import BestOption from "./BestOption";
import { FaSearch, FaSpinner } from "react-icons/fa";

const Results = ({ options, tokenFrom, tokenTo, isLoading, selectedOfferIndex, onSelectOffer }) => {
  if (isLoading) {
    return (
      <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 backdrop-blur-xl border border-gray-700/50 shadow-2xl rounded-2xl p-5 max-w-2xl">
        <div className="text-center">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-3">
            <FaSpinner size={18} className="text-white animate-spin" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">Wyszukiwanie...</h3>
          <p className="text-sm text-gray-400">Analizuję dostępne opcje wymiany</p>
        </div>
      </div>
    );
  }

  if (!options || options.length === 0) {
    return (
      <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 backdrop-blur-xl border border-gray-700/50 shadow-2xl rounded-2xl p-5 max-w-2xl">
        <div className="text-center">
          <div className="w-10 h-10 bg-gradient-to-br from-gray-600 to-gray-700 rounded-full flex items-center justify-center mx-auto mb-3">
            <FaSearch size={18} className="text-gray-400" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">Brak wyników</h3>
          <p className="text-sm text-gray-400">Spróbuj zmienić parametry wyszukiwania</p>
        </div>
      </div>
    );
  }

  const [bestOption, ...otherOptions] = options;

  return (
    <div className="space-y-3">
      <div className="text-center mb-4">
        <h2 className="text-lg font-bold text-white mb-1">Wyniki wyszukiwania</h2>
        <p className="text-sm text-gray-400">Znalezione opcje wymiany {tokenFrom} → {tokenTo}</p>
      </div>

      {/* Best Option */}
      <BestOption 
        option={bestOption} 
        tokenFrom={tokenFrom} 
        tokenTo={tokenTo}
        isSelected={selectedOfferIndex === 0}
        onSelect={() => onSelectOffer(0)}
      />

      {/* Other Options */}
      {otherOptions.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-gray-300 text-center">
            Inne dostępne opcje ({otherOptions.length})
          </h3>
          <div className="max-h-[500px] overflow-y-auto space-y-2 pr-2">
            {otherOptions.map((opt, i) => (
              <ResultItem 
                key={i} 
                option={opt} 
                tokenFrom={tokenFrom} 
                tokenTo={tokenTo} 
                index={i}
                isSelected={selectedOfferIndex === i + 1}
                onSelect={() => onSelectOffer(i + 1)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Results;
