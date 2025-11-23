import { useState, useEffect } from 'react';
import { useAccount, useWriteContract, useWaitForTransactionReceipt, useSwitchChain } from 'wagmi';
import { parseUnits, encodeFunctionData } from 'viem';
import { arbitrum } from 'wagmi/chains';
import { ERC20_ABI, getRouterABI, getContractsConfig } from '../config/contracts';
import { saveSwapToHistory } from '../utils/historyStorage';

export const useSwap = () => {
  const { address, isConnected, chain } = useAccount();
  const { writeContract, data: hash, isPending: isWritePending, error: writeError } = useWriteContract();
  const { isLoading: isConfirming, isSuccess: isConfirmed } = useWaitForTransactionReceipt({ hash });
  const { switchChain } = useSwitchChain();
  
  const [contractsConfig, setContractsConfig] = useState(null);
  const [currentSwapData, setCurrentSwapData] = useState(null);
  const [swapState, setSwapState] = useState({
    status: 'idle',
    txHash: null,
    error: null,
    step: null
  });

  useEffect(() => {
    getContractsConfig().then(setContractsConfig);
  }, []);

  useEffect(() => {
    if (hash && isConfirming) {
      setSwapState(prev => ({ 
        ...prev, 
        status: 'confirming', 
        step: 'Oczekiwanie na potwierdzenie...', 
        txHash: hash 
      }));
    }
    
    if (hash && isConfirmed && currentSwapData) {
      // Transakcja potwierdzona - zapisz do historii
      saveSwapToHistory({
        txHash: hash,
        tokenFrom: currentSwapData.tokenFrom,
        tokenTo: currentSwapData.tokenTo,
        amountFrom: currentSwapData.amount,
        amountTo: currentSwapData.option.amount_to,
        valueUSD: currentSwapData.option.value_from_usd,
        dex: currentSwapData.option.dex,
        fee: currentSwapData.option.dex_fee,
        gasUsed: currentSwapData.option.gas_cost,
        percentageChange: currentSwapData.option.percentage_change
      });
      
      setSwapState(prev => ({ 
        ...prev, 
        status: 'success', 
        step: 'Transakcja potwierdzona!', 
        txHash: hash 
      }));
      
      setCurrentSwapData(null);
    }

    if (writeError) {
      setSwapState(prev => ({ 
        ...prev, 
        status: 'error', 
        error: writeError.message || 'Błąd transakcji' 
      }));
      setCurrentSwapData(null);
    }
  }, [hash, isConfirming, isConfirmed, writeError, currentSwapData]);

  const checkAllowance = async (tokenAddress, routerAddress, amountNeeded) => {
    try {
      return false;
    } catch (error) {
      console.error('Błąd sprawdzania allowance:', error);
      return false;
    }
  };

  const approveToken = async (tokenSymbol, dexName, amount, decimals) => {
    try {
      setSwapState({ status: 'approving', step: 'Zatwierdzanie tokena...', error: null, txHash: null });
      
      if (!contractsConfig) {
        throw new Error('Konfiguracja kontraktów nie załadowana');
      }
      
      const tokenAddress = contractsConfig.tokens[tokenSymbol];
      const routerAddress = contractsConfig.routers[dexName];
      const amountInWei = parseUnits(amount.toString(), decimals);

      await writeContract({
        address: tokenAddress,
        abi: ERC20_ABI,
        functionName: 'approve',
        args: [routerAddress, amountInWei]
      });

      setSwapState({ status: 'approved', step: 'Token zatwierdzony', error: null, txHash: hash });
      return true;
    } catch (error) {
      console.error('Błąd approval:', error);
      setSwapState({ status: 'error', step: null, error: error.message, txHash: null });
      return false;
    }
  };

  const executeSwap = async (option, tokenFrom, tokenTo, amount) => {
    if (!isConnected) {
      setSwapState({ status: 'error', error: 'Portfel nie połączony', step: null, txHash: null });
      return;
    }

    if (chain?.id !== arbitrum.id) {
      try {
        setSwapState({ status: 'approving', step: 'Przełączanie na Arbitrum...', error: null, txHash: null });
        await switchChain({ chainId: arbitrum.id });

        await new Promise(resolve => setTimeout(resolve, 1000));
      } catch (error) {
        setSwapState({ status: 'error', error: 'Musisz być na sieci Arbitrum', step: null, txHash: null });
        return;
      }
    }

    if (!contractsConfig) {
      setSwapState({ status: 'error', error: 'Konfiguracja nie załadowana', step: null, txHash: null });
      return;
    }

    setCurrentSwapData({ option, tokenFrom, tokenTo, amount });

    try {
      const dexName = option.dex;
      const routerAddress = contractsConfig.routers[dexName];
      const routerABI = getRouterABI(dexName);
      
      const wethAddress = contractsConfig.tokens['WETH'] || contractsConfig.tokens['ETH'];
      
      const tokenInAddress = tokenFrom === 'ETH' ? wethAddress : contractsConfig.tokens[tokenFrom];
      const tokenOutAddress = tokenTo === 'ETH' ? wethAddress : contractsConfig.tokens[tokenTo];
      
      const decimalsIn = contractsConfig.decimals[tokenFrom] || 18;
      const decimalsOut = contractsConfig.decimals[tokenTo] || 18;
      
      const amountInWei = parseUnits(amount.toString(), decimalsIn);
      
      const amountOutMinimum = parseUnits((option.amount_to * 0.995).toFixed(decimalsOut), decimalsOut);
      
      const deadline = Math.floor(Date.now() / 1000) + 1200;

      if (tokenFrom !== 'ETH') {
        setSwapState({ status: 'approving', step: 'Sprawdzam allowance...', error: null, txHash: null });
        
        const hasAllowance = await checkAllowance(tokenInAddress, routerAddress, amountInWei);
        
        if (!hasAllowance) {
          const approved = await approveToken(tokenFrom, dexName, amount, decimalsIn);
          if (!approved) return;
          
          await new Promise(resolve => setTimeout(resolve, 2000));
        }
      }

      setSwapState({ status: 'swapping', step: 'Wykonywanie wymiany...', error: null, txHash: null });

      const feeMap = {
        0.0001: 100,
        0.0005: 500,
        0.003: 3000,
        0.01: 10000
      };
      const feeTier = feeMap[option.dex_fee] || 500;

      if (dexName === 'Camelot') {
        await writeContract({
          address: routerAddress,
          abi: routerABI,
          functionName: 'exactInputSingle',
          args: [{
            tokenIn: tokenInAddress,
            tokenOut: tokenOutAddress,
            recipient: address,
            deadline: deadline,
            amountIn: amountInWei,
            amountOutMinimum: amountOutMinimum,
            limitSqrtPrice: 0n
          }],
          value: tokenFrom === 'ETH' ? amountInWei : 0n
        });
      } else if (tokenTo === 'ETH') {
        // Uniswap/SushiSwap z ETH output → multicall (swap + unwrap)

        const swapCall = encodeFunctionData({
          abi: routerABI,
          functionName: 'exactInputSingle',
          args: [{
            tokenIn: tokenInAddress,
            tokenOut: tokenOutAddress,
            fee: feeTier,
            recipient: routerAddress,
            deadline: deadline,
            amountIn: amountInWei,
            amountOutMinimum: amountOutMinimum,
            sqrtPriceLimitX96: 0n
          }]
        });
        
        const unwrapCall = encodeFunctionData({
          abi: routerABI,
          functionName: 'unwrapWETH9',
          args: [amountOutMinimum, address]
        });
        
        await writeContract({
          address: routerAddress,
          abi: routerABI,
          functionName: 'multicall',
          args: [[swapCall, unwrapCall]],
          value: tokenFrom === 'ETH' ? amountInWei : 0n
        });
      } else {
        // Uniswap/SushiSwap - standardowy swap
        await writeContract({
          address: routerAddress,
          abi: routerABI,
          functionName: 'exactInputSingle',
          args: [{
            tokenIn: tokenInAddress,
            tokenOut: tokenOutAddress,
            fee: feeTier,
            recipient: address,
            deadline: deadline,
            amountIn: amountInWei,
            amountOutMinimum: amountOutMinimum,
            sqrtPriceLimitX96: 0n
          }],
          value: tokenFrom === 'ETH' ? amountInWei : 0n
        });
      }
      
    } catch (error) {
      console.error('Błąd swap:', error);
      setSwapState({ 
        status: 'error', 
        step: null, 
        error: error.message || 'Nieznany błąd', 
        txHash: null 
      });
    }
  };

  const resetSwap = () => {
    setSwapState({
      status: 'idle',
      txHash: null,
      error: null,
      step: null
    });
  };

  return {
    executeSwap,
    resetSwap,
    swapState,
    isConnected,
    isPending: isWritePending || isConfirming,
    isSuccess: isConfirmed,
    txHash: hash
  };
};

