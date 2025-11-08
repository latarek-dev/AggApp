import { useState, useEffect } from "react";
import { WagmiProvider } from 'wagmi'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { config } from './config/wagmi'
import Header from "./components/Header";
import ExchangeForm from "./components/ExchangeForm";
import Results from "./components/Results";
import SettingsPanel from "./components/SettingsPanel";
import Statistics from "./components/Statistics";
import History from "./components/History";
import About from "./components/About";

function App() {
  const API_BASE =
  (typeof window !== "undefined" && window.__ENV__ && window.__ENV__.API_BASE) ||
  process.env.REACT_APP_API_BASE ||
  "/api";

  const [results, setResults] = useState([]);
  const [tokens, setTokens] = useState({ tokenFrom: "", tokenTo: "", amount: 1 });
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedOfferIndex, setSelectedOfferIndex] = useState(0);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(60);
  const [activeTab, setActiveTab] = useState('swap');
  const queryClient = new QueryClient()

  const handleExchange = async (data) => {
    setIsLoading(true);
    setTokens({ tokenFrom: data.token_from, tokenTo: data.token_to, amount: data.amount });
    setSelectedOfferIndex(0);

    try {
      const response = await fetch(`${API_BASE}/exchange`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      
      const result = await response.json();
      setResults(result.options || []);
    } catch (err) {
      console.error("Błąd API", err);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    if (!tokens.tokenFrom || !tokens.tokenTo) return;
    
    setIsRefreshing(true);
    
    try {
      const response = await fetch(`${API_BASE}/exchange`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          token_from: tokens.tokenFrom,
          token_to: tokens.tokenTo,
          amount: tokens.amount
        }),
      });
      
      const result = await response.json();
      setResults(result.options || []);
    } catch (err) {
      console.error("Błąd odświeżania", err);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleSelectOffer = (index) => {
    setSelectedOfferIndex(index);
  };

  useEffect(() => {
    let intervalId;
    
    if (autoRefresh && tokens.tokenFrom && tokens.tokenTo) {
      intervalId = setInterval(() => {
        handleRefresh();
      }, refreshInterval * 1000);
    }
    
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [autoRefresh, refreshInterval, tokens.tokenFrom, tokens.tokenTo]);

  const renderContent = () => {
    switch (activeTab) {
      case 'swap':
        return (
          <div className="flex flex-col lg:flex-row items-start justify-start">
            {/* Left Section: Exchange Form */}
            <div className="w-full lg:w-2/5 lg:flex-shrink-0 lg:mr-20">
              <ExchangeForm onSubmit={handleExchange} />
            </div>

            {/* Center Section: Results */}
            <div className="w-full lg:w-2/5 lg:flex-shrink-0 lg:mr-8">
              <Results 
                options={results} 
                tokenFrom={tokens.tokenFrom} 
                tokenTo={tokens.tokenTo}
                amount={tokens.amount}
                isLoading={isLoading}
                isRefreshing={isRefreshing}
                selectedOfferIndex={selectedOfferIndex}
                onSelectOffer={handleSelectOffer}
              />
            </div>

            {/* Right Section: Settings Panel */}
            <SettingsPanel
              autoRefresh={autoRefresh}
              setAutoRefresh={setAutoRefresh}
              refreshInterval={refreshInterval}
              setRefreshInterval={setRefreshInterval}
              isRefreshing={isRefreshing}
              onRefresh={handleRefresh}
            />
          </div>
        );
      case 'stats':
        return <Statistics />;
      case 'history':
        return <History />;
      case 'about':
        return <About />;
      default:
        return <div>Nieznana zakładka</div>;
    }
  };

  return (
    <WagmiProvider config={config}>
      <QueryClientProvider client={queryClient}>
        <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 min-h-screen">
          <Header activeTab={activeTab} setActiveTab={setActiveTab} />
          
          <main className="container mx-auto px-4 py-6 max-w-7xl">
            {renderContent()}
          </main>
        </div>
      </QueryClientProvider>
    </WagmiProvider>
  );
}

export default App;