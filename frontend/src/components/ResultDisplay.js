import React from 'react';

const ResultDisplay = ({ result, loading, error }) => {
  if (loading) {
    return (
      <div className="result">
        <p className="loader-text">🔄 Predicting acceptance...</p>
        <div className="loader"></div>
      </div>
    );
  }
  

  if (error) return <p style={{ color: 'red' }}>❌ {error}</p>;

  return (
    result && (
      <div className="result">
        <h3>Prediction Result</h3>
        <p>This paper is likely to be: {result.verdict === 'ACCEPTED' ? '✅ Accepted' : '❌ Rejected'}</p>
    
        {result.feedback && (
          <>
            <h4>Why?</h4>
            <ul>
              {result.feedback.map((point, index) => (
                <li key={index}>{point}</li>
              ))}
            </ul>
          </>
        )}
      </div>
    )
  );
};

export default ResultDisplay;
