export const getDifferencePercent = (fromUsd, toUsd) => {
    const diff = toUsd - fromUsd;
    const percent = (diff / fromUsd) * 100;
    return percent.toFixed(2);
  };
  