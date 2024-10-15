import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [documentsCount, setDocumentsCount] = useState(0);
  const [documents, setDocuments] = useState([]); 
  const [uploadSuccess, setUploadSuccess] = useState(''); // State to hold the success message

  useEffect(() => {
    getDocuments(); // Fetch initial document count on component mount
    getDocumentsCount();
  }, []);

  const uploadFile = async () => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://127.0.0.1:5000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      if (response.status === 200) {
        setUploadSuccess('Document uploaded successfully!'); // Set success message
        getDocuments(); // Refresh the document count
        setTimeout(() => {
          setUploadSuccess(''); // Clear success message after 3 seconds
        }, 3000);
      } else {
        setUploadSuccess('Failed to upload document.'); // Set error message if status is not 200
      }
    } catch (error) {
      setUploadSuccess('An error occurred during upload.'); // Set error message on exception
    }
  };

  const searchDocuments = async () => {
    const response = await axios.post('http://127.0.0.1:5000/search', { query });
    setResults(response.data);
  };

  const getDocumentsCount = async () => {
    const response = await axios.get('http://127.0.0.1:5000/documentsCount');
    setDocumentsCount(response.data.total_documents);
  };

  const getDocuments = async () => {
    const response = await axios.get('http://127.0.0.1:5000/documents');
    setDocuments(response.data.documents);
  };

  const deleteDocument = async (id) => {
    try {
      const response = await axios.delete('http://127.0.0.1:5000/document', {
        data: { id },
      });

      if (response.status === 200) {
        setUploadSuccess('Document deleted successfully!');
        getDocuments(); // Refresh the list of documents after deletion
        setTimeout(() => {
          setUploadSuccess('');
        }, 3000);
      } else {
        setUploadSuccess('Failed to delete document.');
      }
    } catch (error) {
      setUploadSuccess('An error occurred during deletion.');
    }
  };

  return (
    <div className="App">
      <h1 className="app-title">Semantic Search Application</h1>

      {uploadSuccess && <div className="upload-success">{uploadSuccess}</div>} {/* Display the success message */}

      <div className="upload-section">
        <h2>Upload Document</h2>
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        <button className="upload-button" onClick={uploadFile}>Upload</button>
      </div>

      <div className="documents-section">
        <h2>Documents</h2>
        <table>
          <thead>
            <tr>
              <th>Filename</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc, index) => (
              <tr key={index}>
                <td>{doc.filename}</td>
                <td>
                  <button className="delete-button" onClick={() => deleteDocument(doc.id)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="search-section">
        <h2>Search</h2>
        <input
          className="search-input"
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button className="search-button" onClick={searchDocuments}>Search</button>
      </div>

      <div className="results-section">
        <h2>Search Results</h2>
        <table>
          <thead>
            <tr>
              <th>Filename</th>
              <th>Similarity</th>
              <th>Matching Sentence</th>
            </tr>
          </thead>
          <tbody>
            {results.map((result, index) => (
              <tr key={index}>
                <td>{result.filename}</td>
                <td>{result.similarity.toFixed(3)}</td>
                <td>{result.sentence}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default App;
