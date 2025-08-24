import React from "react";
import { getDifferencePercent } from "../getDifferencePercent";
import { FaArrowUp, FaArrowDown } from "react-icons/fa";

const PercentageChange = ({ fromUsd, toUsd }) => {
  const percentDiff = getDifferencePercent(fromUsd, toUsd);
  const isPositive = parseFloat(percentDiff) >= 0;

  return (
    <div className={`flex items-center space-x-1.5 px-2 py-1.5 rounded-lg font-semibold text-xs ${
      isPositive 
        ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
        : 'bg-red-500/20 text-red-400 border border-red-500/30'
    }`}>
      {isPositive ? (
        <FaArrowUp size={12} className="text-green-400" />
      ) : (
        <FaArrowDown size={12} className="text-red-400" />
      )}
      <span>
        {isPositive ? "+" : ""}
        {percentDiff}%
      </span>
    </div>
  );
};

export default PercentageChange;
