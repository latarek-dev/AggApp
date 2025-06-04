import ResultItem from "./ResultItem";
import BestOption from "./BestOption";

const Results = ({ options, tokenFrom, tokenTo }) => {
  if (!options || options.length === 0) {
    return <div className="error">Brak dostępnych opcji wymiany.</div>;
  }

  const [bestOption, ...otherOptions] = options;

  return (
    <div id="results">
      <h2>Dostępne opcje wymiany:</h2>
      <BestOption option={bestOption} tokenFrom={tokenFrom} tokenTo={tokenTo} />
      {otherOptions.map((opt, i) => (
        <ResultItem key={i} option={opt} tokenFrom={tokenFrom} tokenTo={tokenTo} />
      ))}
    </div>
  );
};

export default Results;
