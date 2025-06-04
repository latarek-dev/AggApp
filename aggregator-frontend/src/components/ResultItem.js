import PercentageChange from "./PercentageChange";

const ResultItem = ({ option, tokenFrom, tokenTo }) => {
  
    return (
      <div className="result-item">
        <strong>{option.pair} ({option.dex})</strong>
        <div className="option-details">
          {option.amount_from.toFixed(6)} {tokenFrom} (${option.value_from_usd.toFixed(2)}) →
          {option.amount_to.toFixed(6)} {tokenTo} (${option.value_to_usd.toFixed(2)})
        </div>
        <PercentageChange fromUsd={option.value_from_usd} toUsd={option.value_to_usd} />
      </div>
    );
  };
  
  export default ResultItem;
  