import React from "react";
import { getDifferencePercent } from "../getDifferencePercent";

const PercentageChange = ({ fromUsd, toUsd }) => {
  const percentDiff = getDifferencePercent(fromUsd, toUsd);
  const isPositive = parseFloat(percentDiff) >= 0;

  return (
    <div
      style={{
        color: isPositive ? "#27ae60" : "#c0392b",
        fontWeight: "bold",
        fontSize: "0.95rem",
      }}
    >
      {isPositive ? "+" : ""}
      {percentDiff}%
    </div>
  );
};

export default PercentageChange;
