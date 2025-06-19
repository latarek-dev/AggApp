import { useState } from "react";
import Select from "react-select";
import { FaEthereum, FaBitcoin, FaDollarSign, FaCoins, FaRegMoneyBillAlt } from "react-icons/fa";

// Custom styles for react-select
const customStyles = {
  control: (styles) => ({
    ...styles,
    borderColor: "#d1d5db", // Custom border color
    boxShadow: "none",
    "&:hover": {
      borderColor: "#3b82f6", // Custom hover border color
    },
  }),
  singleValue: (styles) => ({
    ...styles,
    color: "#333", // Text color inside the select dropdown
    display: "flex",
    alignItems: "center", // Ensure text aligns well with icons
    paddingLeft: "35px", // Adjust this value to add space between the icon and text
  }),
  option: (styles) => ({
    ...styles,
    color: "#333", // Text color inside the options
    display: "flex",
    alignItems: "center", // Align icons and text horizontally in options
    paddingLeft: "35px", // Space between icon and text
  }),
  menu: (styles) => ({
    ...styles,
    zIndex: 999,  // Make sure the dropdown appears above other elements
  })
};

const ExchangeForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    token_from: "ETH",   // Default token to exchange
    token_to: "USDT",    // Default token to receive
    amount: "",          // Amount to exchange
  });

  // Handle select change
  const handleSelectChange = (selectedOption, actionMeta) => {
    setFormData((prevData) => ({
      ...prevData,
      [actionMeta.name]: selectedOption.value,  // Update the selected token by name
    }));
  };

  // Handle input change for amount
  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      amount: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      ...formData,
      amount: parseFloat(formData.amount),
    });
  };

  const tokenOptions = [
    {
      value: "ETH",
      label: (
        <>
          <FaEthereum size={18} className="absolute left-2" /> {/* Positioning the icon on the left */}
          ETH
        </>
      ),
    },
    {
      value: "USDT",
      label: (
        <>
          <FaDollarSign size={18} className="absolute left-2" />
          USDT
        </>
      ),
    },
    {
      value: "USDC",
      label: (
        <>
          <FaRegMoneyBillAlt size={18} className="absolute left-2" />
          USDC
        </>
      ),
    },
    {
      value: "DAI",
      label: (
        <>
          <FaCoins size={18} className="absolute left-2" />
          DAI
        </>
      ),
    },
    {
      value: "WBTC",
      label: (
        <>
          <FaBitcoin size={18} className="absolute left-2" />
          WBTC
        </>
      ),
    },
  ];

  return (
    <div className="bg-white shadow-lg rounded-xl p-8 max-w-md mx-auto">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Token From */}
        <div>
          <label className="text-lg font-medium text-gray-800">Token do wymiany:</label>
          <Select
            name="token_from"
            value={tokenOptions.find((option) => option.value === formData.token_from)} // Set the selected token based on the state
            onChange={handleSelectChange} // Use handleSelectChange for updating state
            options={tokenOptions}
            styles={customStyles}
            // No need to add getOptionLabel here anymore since icon is added directly in label
          />
        </div>

        {/* Token To */}
        <div>
          <label className="text-lg font-medium text-gray-800">Token docelowy:</label>
          <Select
            name="token_to"
            value={tokenOptions.find((option) => option.value === formData.token_to)} // Set the selected token based on the state
            onChange={handleSelectChange} // Use handleSelectChange for updating state
            options={tokenOptions}
            styles={customStyles}
          />
        </div>

        {/* Amount */}
        <div>
          <label className="text-lg font-medium text-gray-800">Ilość:</label>
          <input
            type="number"
            name="amount"
            value={formData.amount}
            onChange={handleInputChange} // Update amount state
            step="any"
            className="w-full p-4 bg-transparent border-2 border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-300 ease-in-out transform hover:scale-105"
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className="w-full py-4 bg-blue-600 text-white text-lg font-semibold rounded-lg shadow-lg hover:bg-blue-700 transition-all duration-300 ease-in-out transform hover:scale-105"
        >
          Wymień
        </button>
      </form>
    </div>
  );
};

export default ExchangeForm;
