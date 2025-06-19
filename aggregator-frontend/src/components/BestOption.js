import React from "react";
import PercentageChange from "./PercentageChange";

const BestOption = ({ option, tokenFrom, tokenTo }) => {

  return (
    <div className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300">
      <strong className="text-xl font-semibold text-gray-800">{option.pair} ({option.dex})</strong>
      <div className="text-lg font-medium text-green-600 mt-2">Najlepsza opcja</div>
      <div className="mt-4 text-sm text-gray-700">
        {option.amount_from.toFixed(6)} {tokenFrom} (${option.value_from_usd.toFixed(2)}) →
        {option.amount_to.toFixed(6)} {tokenTo} (${option.value_to_usd.toFixed(2)})
      </div>
      <div className="mt-4">
        <PercentageChange fromUsd={option.value_from_usd} toUsd={option.value_to_usd} />
      </div>
    </div>
  );
};

export default BestOption;
