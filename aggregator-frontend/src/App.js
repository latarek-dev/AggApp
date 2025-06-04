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
    <div>
      <Header />
      <div className="container">
        <ExchangeForm onSubmit={handleExchange} />
        <Results options={results} tokenFrom={tokens.tokenFrom} tokenTo={tokens.tokenTo} />
      </div>
    </div>
  );
}

export default App;
