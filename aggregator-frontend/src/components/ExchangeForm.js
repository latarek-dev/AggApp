import { useState } from "react";

const ExchangeForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    token_from: "ETH",
    token_to: "USDT",
    amount: ""
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      ...formData,
      amount: parseFloat(formData.amount)
    });
  };

  return (
    <div className="exchange-form-wrapper">
      <form onSubmit={handleSubmit}>
        <label>Token do wymiany:</label>
        <select name="token_from" value={formData.token_from} onChange={handleChange}>
          <option value="ETH">ETH</option>
          <option value="USDT">USDT</option>
          <option value="USDC">USDC</option>
          <option value="DAI">DAI</option>
          <option value="WBTC">WBTC</option>
        </select>

        <label>Token docelowy:</label>
        <select name="token_to" value={formData.token_to} onChange={handleChange}>
          <option value="ETH">ETH</option>
          <option value="USDT">USDT</option>
          <option value="USDC">USDC</option>
          <option value="DAI">DAI</option>
          <option value="WBTC">WBTC</option>
        </select>

        <label>Ilość:</label>
        <input
          type="number"
          name="amount"
          value={formData.amount}
          onChange={handleChange}
          step="any"
        />

        <button type="submit">Wymień</button>
      </form>
    </div>
  );
};

export default ExchangeForm;
