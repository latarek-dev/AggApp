import { useState } from "react";
import Header from "./components/Header";
import ExchangeForm from "./components/ExchangeForm";
import Results from "./components/Results";
import SettingsPanel from "./components/SettingsPanel";

function App() {
  const [results, setResults] = useState([]);
  const [tokens, setTokens] = useState({ tokenFrom: "", tokenTo: "", amount: 1 });
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedOfferIndex, setSelectedOfferIndex] = useState(0);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(30);

  const handleExchange = async (data) => {
    setIsLoading(true);
    setTokens({ tokenFrom: data.token_from, tokenTo: data.token_to, amount: data.amount });
    setSelectedOfferIndex(0);

    try {
      const response = await fetch("/exchange", {
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
      const response = await fetch("/exchange", {
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

  return (
    <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 min-h-screen">
      <Header />
      
      <main className="container mx-auto px-4 py-6 max-w-7xl">
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
      </main>
    </div>
  );
}

export default App;