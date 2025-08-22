import React, { useState } from 'react';

const AQIPrediction: React.FC = () => {
  const [inputData, setInputData] = useState({
    station_id: '',
    pm25: '',
    pm10: '',
    no2: '',
    so2: '',
    co: '',
    o3: '',
    temperature: '',
    humidity: ''
  });
  const [prediction, setPrediction] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputData({ ...inputData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setPrediction(null);
    try {
      const response = await fetch('/api/aqi/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(inputData)
      });
      if (!response.ok) throw new Error('Prediction failed');
      const result = await response.json();
      setPrediction(result.predicted_aqi);
    } catch (err) {
      setError('Prediction failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mt-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">AQI Prediction (AI)</h3>
      <form className="grid grid-cols-1 md:grid-cols-2 gap-4" onSubmit={handleSubmit}>
        {Object.keys(inputData).map((key) => (
          <div key={key}>
            <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor={key}>{key.replace('_', ' ').toUpperCase()}</label>
            <input
              type="text"
              name={key}
              id={key}
              value={inputData[key]}
              onChange={handleChange}
              className="border border-gray-300 rounded px-3 py-2 w-full"
            />
          </div>
        ))}
        <button
          type="submit"
          className="col-span-1 md:col-span-2 bg-green-600 text-white rounded px-4 py-2 mt-2 hover:bg-green-700"
          disabled={loading}
        >
          {loading ? 'Predicting...' : 'Predict AQI'}
        </button>
      </form>
      {prediction !== null && (
        <div className="mt-4 text-blue-700 font-bold">
          Predicted AQI: {Math.round(prediction)}
        </div>
      )}
      {error && (
        <div className="mt-4 text-red-600 font-bold">{error}</div>
      )}
    </div>
  );
};

export default AQIPrediction;
