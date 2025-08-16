// import React, { useState } from 'react';

// const PaperForm = ({ onSubmit }) => {
//   const [file, setFile] = useState(null);

//   const handleSubmit = (e) => {
//     e.preventDefault();

//     if (!file) return alert("Please upload a PDF.");

//     const formData = new FormData();
//     formData.append('pdf', file);

//     onSubmit(formData); // Send to App.js
//   };

//   return (
//     <div className="form-container">
//       <h2>Research Paper Acceptance Predictor</h2>
//       <form onSubmit={handleSubmit}>
//         <input
//           type="file"
//           accept="application/pdf"
//           onChange={(e) => setFile(e.target.files[0])}
//         />
//         <button type="submit">Predict Acceptance</button>
//       </form>
//     </div>
//   );
// };

// export default PaperForm;
import React, { useState } from 'react';
import './PaperForm.css';

const PaperForm = ({ onSubmit }) => {
  const [file, setFile] = useState(null);
  const [highlight, setHighlight] = useState(false);

  const handleFileChange = (e) => {
    const uploadedFile = e.target.files[0];
    if (uploadedFile && uploadedFile.type === 'application/pdf') {
      setFile(uploadedFile);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setHighlight(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type === 'application/pdf') {
      setFile(droppedFile);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!file) return alert('Please upload a PDF file');

    const formData = new FormData();
    formData.append('pdf', file);
    onSubmit(formData);
  };

  return (
    <div className="form-container">
      <h2 className="title">SUBMIT. ANALYZE. IMPROVE.</h2>
      <p className="subtitle">
        Simply upload your document, and our AI will predict its acceptance likelihood based on key conference criteria.
      </p>

      <form onSubmit={handleSubmit}>
        <div
          className={`drop-area ${highlight ? 'highlight' : ''}`}
          onDragOver={(e) => {
            e.preventDefault();
            setHighlight(true);
          }}
          onDragLeave={() => setHighlight(false)}
          onDrop={handleDrop}
        >
          <label htmlFor="file-upload" className="upload-label">
            ⬆️ <span>Click to upload</span> or drag and drop
          </label>
          <input
            id="file-upload"
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
            hidden
          />
        </div>

        {file && <p className="file-name">📄 {file.name}</p>}

        <button type="submit" className="submit-button">Predict Acceptance</button>
      </form>
    </div>
  );
};

export default PaperForm;
