import React from "react";
import { FaArrowUp, FaArrowDown } from "react-icons/fa";

const PercentageChange = ({ value }) => {
  if (value === null || value === undefined || isNaN(value)) {
    return (
      <div className="flex items-center space-x-1 text-gray-400">
        <span className="text-sm">-</span>
      </div>
    );
  }

  const isPositive = value > 0;
  const isNegative = value < 0;
  const absValue = Math.abs(value);

  return (
    <div className={`flex items-center space-x-1 ${
      isPositive 
        ? 'text-green-400' 
        : isNegative 
        ? 'text-red-400' 
        : 'text-gray-400'
    }`}>
      {isPositive && <FaArrowUp className="text-sm" />}
      {isNegative && <FaArrowDown className="text-sm" />}
      <span className="text-sm font-bold">
        {isPositive ? '+' : ''}{value.toFixed(2)}%
      </span>
    </div>
  );
};

export default PercentageChange;