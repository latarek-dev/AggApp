// LocalStorage manager dla historii transakcji

const HISTORY_KEY = 'aggapp_swap_history';
const MAX_HISTORY_ITEMS = 100;

export const saveSwapToHistory = (swapData) => {
  try {
    const history = getSwapHistory();
    
    const newItem = {
      id: `${swapData.txHash}_${Date.now()}`,
      timestamp: Date.now(),
      txHash: swapData.txHash,
      tokenFrom: swapData.tokenFrom,
      tokenTo: swapData.tokenTo,
      amountFrom: swapData.amountFrom,
      amountTo: swapData.amountTo,
      valueUSD: swapData.valueUSD,
      dex: swapData.dex,
      fee: swapData.fee,
      gasUsed: swapData.gasUsed,
      percentageChange: swapData.percentageChange,
      status: 'success'
    };
    
    history.unshift(newItem);
    
    const trimmedHistory = history.slice(0, MAX_HISTORY_ITEMS);
    
    localStorage.setItem(HISTORY_KEY, JSON.stringify(trimmedHistory));
    
    return true;
  } catch (error) {
    console.error('Błąd zapisywania historii:', error);
    return false;
  }
};

export const getSwapHistory = () => {
  try {
    const stored = localStorage.getItem(HISTORY_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch (error) {
    console.error('Błąd odczytu historii:', error);
    return [];
  }
};

export const clearSwapHistory = () => {
  try {
    localStorage.removeItem(HISTORY_KEY);
    return true;
  } catch (error) {
    console.error('Błąd czyszczenia historii:', error);
    return false;
  }
};

export const getFilteredHistory = (filters = {}) => {
  const history = getSwapHistory();
  
  let filtered = history;
  
  if (filters.tokenFrom) {
    filtered = filtered.filter(item => item.tokenFrom === filters.tokenFrom);
  }
  
  if (filters.tokenTo) {
    filtered = filtered.filter(item => item.tokenTo === filters.tokenTo);
  }
  
  if (filters.dex) {
    filtered = filtered.filter(item => item.dex === filters.dex);
  }
  
  return filtered;
};

