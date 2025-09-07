import React from "react";
import ExchangeOption from "./ExchangeOption";
import { FaCrown } from "react-icons/fa";

const BestOption = ({ option, tokenFrom, tokenTo, isSelected, onSelect }) => {
  return (
    <div className="relative">
      {/* Best Option Badge */}
      <div className="absolute -top-3 -left-3 bg-gradient-to-r from-green-400 to-emerald-500 text-gray-900 px-2 py-1 rounded-lg text-xs font-bold flex items-center space-x-1 z-10">
        <FaCrown size={8} />
        <span className="text-xs">NAJLEPSZA</span>
      </div>

      <ExchangeOption
        option={option}
        tokenFrom={tokenFrom}
        tokenTo={tokenTo}
        isSelected={isSelected}
        onSelect={onSelect}
        isBest={true}
        showTooltips={true}
      />
    </div>
  );
};

export default BestOption;