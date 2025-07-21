import React, { useState } from 'react';
import './App.css';
import Header from './components/Header';
import PaperForm from './components/PaperForm';
import ResultDisplay from './components/ResultDisplay';

function App() {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handlePrediction = async (formData) => {
  setLoading(true);
  setError('');
  setPrediction(null);

  try {
    const response = await fetch('http://localhost:8000/predict', {
      method: 'POST',
      body: formData
    });
    

    if (!response.ok) {
      throw new Error('Server error while predicting.');
    }

    const data = await response.json();
    setPrediction(data);
  } catch (err) {
    setError(err.message || 'Something went wrong.');
  } finally {
    setLoading(false);
  }
};

  
  return (
    <div className="App">
      <Header />
      <PaperForm onSubmit={handlePrediction} />
      <ResultDisplay result={prediction} loading={loading} error={error} />
    </div>
  );
}

export default App;
