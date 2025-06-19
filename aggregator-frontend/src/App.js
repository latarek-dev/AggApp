import { useState } from "react";
import Header from "./components/Header";
import ExchangeForm from "./components/ExchangeForm";
import Results from "./components/Results";

function App() {
  const [results, setResults] = useState([]);
  const [tokens, setTokens] = useState({ tokenFrom: "", tokenTo: "" });

  const handleExchange = (data) => {
    setTokens({ tokenFrom: data.token_from, tokenTo: data.token_to });

    fetch("/exchange", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
      .then((res) => res.json())
      .then((data) => setResults(data.options || []))
      .catch((err) => {
        console.error("Błąd API", err);
        setResults([]);
      });
  };

 return (
    <div className="bg-gray-100 min-h-screen flex flex-col items-center">
      <Header />
      <div className="flex flex-col lg:flex-row gap-6 mt-4 px-4 md:px-8 w-full max-w-6xl">
        {/* Left Section: Exchange Form */}
        <div className="flex-1 max-w-lg mt-16">
          <ExchangeForm onSubmit={handleExchange} />
        </div>

        {/* Right Section: Results */}
        <div className="flex-1 max-w-lg ml-12">
          <Results options={results} tokenFrom={tokens.tokenFrom} tokenTo={tokens.tokenTo} />
        </div>
      </div>
    </div>
  );
}

export default App;
