import { useAccount, useBalance, useReadContract } from 'wagmi';
import { useState, useEffect } from 'react';
import { formatUnits } from 'viem';
import { ERC20_ABI, getContractsConfig } from '../config/contracts';

export const useTokenBalance = (tokenSymbol) => {
  const { address, isConnected } = useAccount();
  const [contractsConfig, setContractsConfig] = useState(null);
  const [tokenAddress, setTokenAddress] = useState(null);
  const [decimals, setDecimals] = useState(18);

  useEffect(() => {
    getContractsConfig().then(config => {
      setContractsConfig(config);
      if (tokenSymbol && config) {
        setTokenAddress(config.tokens[tokenSymbol]);
        setDecimals(config.decimals[tokenSymbol] || 18);
      }
    });
  }, [tokenSymbol]);

  const { data: ethBalance } = useBalance({
    address: address,
    query: {
      enabled: isConnected && tokenSymbol === 'ETH'
    }
  });

  const { data: erc20Balance } = useReadContract({
    address: tokenAddress,
    abi: ERC20_ABI,
    functionName: 'balanceOf',
    args: [address],
    query: {
      enabled: isConnected && tokenSymbol !== 'ETH' && !!tokenAddress
    }
  });

  if (!isConnected || !tokenSymbol) {
    return { balance: '0', formatted: '0.00', isLoading: false };
  }

  if (tokenSymbol === 'ETH') {
    if (!ethBalance) {
      return { balance: '0', formatted: '0.00', fullAmount: '0', isLoading: true };
    }
    const fullAmount = formatUnits(ethBalance.value, 18);
    return {
      balance: ethBalance.value.toString(),
      formatted: parseFloat(fullAmount).toFixed(6),
      fullAmount: fullAmount,
      isLoading: false
    };
  }

  if (!erc20Balance) {
    return { balance: '0', formatted: '0.00', fullAmount: '0', isLoading: true };
  }

  const fullAmount = formatUnits(erc20Balance, decimals);
  return {
    balance: erc20Balance.toString(),
    formatted: parseFloat(fullAmount).toFixed(6),
    fullAmount: fullAmount,
    isLoading: false
  };
};

