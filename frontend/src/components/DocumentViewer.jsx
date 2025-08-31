// frontend/src/components/DocumentViewer.jsx

import React, { useState, useEffect } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';

// Set the worker source to the locally hosted file.
pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.mjs';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
// Document Viewer Component
const DocumentViewer = ({ doc, pageToView }) => {
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);

  function onDocumentLoadSuccess({ numPages }) {
    setNumPages(numPages);
  }
  useEffect(() => {
    if (pageToView) {
      setPageNumber(pageToView);
    }
  }, [pageToView]);

  return (
    <div className="flex flex-col h-full bg-white p-6 shadow-md rounded-lg w-full">
      <h3 className="text-xl font-bold mb-4 text-gray-800">Viewing: {doc.name}</h3>
      <div className="relative flex-grow overflow-hidden border border-gray-300 rounded-lg">
        <div className="absolute inset-0 overflow-y-auto">
          <Document
            file={`${API_URL}/api/download/${doc.id}`}
            onLoadSuccess={onDocumentLoadSuccess}
            className="flex justify-center"
          >
            <Page pageNumber={pageNumber} />
          </Document>
        </div>
      </div>
      <div className="flex justify-center items-center mt-4 space-x-4">
        <button
          disabled={pageNumber <= 1}
          onClick={() => setPageNumber(prevPageNumber => prevPageNumber - 1)}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md font-semibold hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Previous
        </button>
        <span className="text-md text-gray-600">
          Page {pageNumber} of {numPages}
        </span>
        <button
          disabled={pageNumber >= numPages}
          onClick={() => setPageNumber(prevPageNumber => prevPageNumber + 1)}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md font-semibold hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default DocumentViewer;