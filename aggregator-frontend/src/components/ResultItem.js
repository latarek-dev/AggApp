import React from "react";
import ExchangeOption from "./ExchangeOption";

const ResultItem = ({ option, tokenFrom, tokenTo, amount, index, isSelected, onSelect }) => {
  return (
    <ExchangeOption
      option={option}
      tokenFrom={tokenFrom}
      tokenTo={tokenTo}
      amount={amount}
      index={index}
      isSelected={isSelected}
      onSelect={onSelect}
      isBest={false}
      showTooltips={false}
    />
  );
};

export default ResultItem;