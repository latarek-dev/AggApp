import ResultItem from "./ResultItem";
import BestOption from "./BestOption";

const Results = ({ options, tokenFrom, tokenTo }) => {
  if (!options || options.length === 0) {
    return (
      <div className="text-center text-xl text-red-600 mt-6">
        Brak dostępnych opcji wymiany.
      </div>
    );
  }

  const [bestOption, ...otherOptions] = options;

  return (
    <div id="results" className="space-y-4 mt-2 flex flex-col ml-12">
      <h2 className="text-2xl font-semibold text-gray-800 mb-2">
        Dostępne opcje wymiany:
      </h2>
      <BestOption option={bestOption} tokenFrom={tokenFrom} tokenTo={tokenTo} />

      {/* Kontener wyników z przewijaniem */}
      <div className="flex-1 overflow-y-auto max-h-[400px] space-y-4">
        {otherOptions.map((opt, i) => (
          <ResultItem key={i} option={opt} tokenFrom={tokenFrom} tokenTo={tokenTo} />
        ))}
      </div>
    </div>
  );
};

export default Results;
