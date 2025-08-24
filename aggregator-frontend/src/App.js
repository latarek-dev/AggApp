import { useState } from "react";
import Header from "./components/Header";
import ExchangeForm from "./components/ExchangeForm";
import Results from "./components/Results";

function App() {
  const [results, setResults] = useState([]);
  const [tokens, setTokens] = useState({ tokenFrom: "", tokenTo: "" });
  const [isLoading, setIsLoading] = useState(false);

  const handleExchange = async (data) => {
    setIsLoading(true);
    setTokens({ tokenFrom: data.token_from, tokenTo: data.token_to });

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

  return (
    <div className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 min-h-screen">
      <Header />
      
      <main className="container mx-auto px-4 py-6 max-w-7xl">
        <div className="flex flex-col lg:flex-row gap-8 items-start justify-start">
          {/* Left Section: Exchange Form */}
          <div className="w-full lg:w-2/5 lg:flex-shrink-0">
            <ExchangeForm onSubmit={handleExchange} />
          </div>

          {/* Right Section: Results */}
          <div className="w-full lg:w-2/5 lg:flex-shrink-0 lg:ml-12">
            <Results 
              options={results} 
              tokenFrom={tokens.tokenFrom} 
              tokenTo={tokens.tokenTo}
              isLoading={isLoading}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
