// frontend/src/App.jsx
import { useState, useEffect } from 'react';
import axios from 'axios';
import 'react-pdf/dist/Page/AnnotationLayer.css';
import 'react-pdf/dist/Page/TextLayer.css';
import DocumentList from './components/DocumentList';
import DocumentViewer from './components/DocumentViewer';
import QA_Panel from './components/QA_Panel';
import { ToastContainer } from 'react-toastify';
import './index.css';
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Main App Component
function App() {
  const [documents, setDocuments] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [pageToView, setPageToView] = useState(1);

  // Citation click handler
  const onCitationClick = (docName, pageNumber) => {
    const docToSelect = documents.find(doc => doc.name === docName);
    if (docToSelect) {
      setSelectedDoc(docToSelect);
      setPageToView(pageNumber);
    }
  };
  useEffect(() => {
        const fetchDocuments = async () => {
            try {
                const response = await axios.get(`${API_URL}/api/documents`);
                const fetchedDocuments = response.data.documents;
                setDocuments(fetchedDocuments);
            } catch (error) {
                console.error("Failed to fetch documents:", error);
            }
        };

        fetchDocuments();
    }, []);


  // Polling for document status
  useEffect(() => {
    const intervals = {};

    documents.forEach(doc => {
      if (doc.status !== 'Indexed' && doc.status !== 'Failed') {
        const pollStatus = setInterval(async () => {
          try {
            const response = await axios.get(`${API_URL}/api/status/${doc.id}`);
            const newStatus = response.data.status;
            setDocuments(prevDocs =>
              prevDocs.map(d => (d.id === doc.id ? { ...d, status: newStatus } : d))
            );
            if (newStatus === 'Indexed' || newStatus === 'Failed') {
              clearInterval(intervals[doc.id]);
              delete intervals[doc.id];
            }
          } catch (error) {
            console.error(`Polling failed for ${doc.id}:`, error);
            clearInterval(intervals[doc.id]);
            delete intervals[doc.id];
          }
        }, 2000);
        intervals[doc.id] = pollStatus;
      }
    });

    return () => {
      for (const id in intervals) {
        clearInterval(intervals[id]);
      }
    };
  }, [documents]);

  // Document upload handler
  const handleDocumentUpload = (newDoc) => {
    setDocuments(prevDocs => [...prevDocs, newDoc]);
  };

  return (
    <div className="flex flex-col min-h-screen  font-sans">
      <ToastContainer />
      <header className="bg-red-900 text-white p-4 shadow-md">
        <h1 className="text-2xl font-bold text-center">askDOCS</h1>
      </header>
      <div className="flex flex-1 bg-red-100 overflow-hidden">
        <div className="w-1/4 overflow-y-auto p-4  border-r border-gray-300">
          <DocumentList
            documents={documents}
            onSelectDoc={setSelectedDoc}
            onUpload={handleDocumentUpload}
          />
        </div>
        <div className="flex-1 overflow-y-auto p-4 flex justify-center  bg-white">
          {selectedDoc ? (
            <DocumentViewer doc={selectedDoc} pageToView={pageToView} />
          ) : (
            <div className="text-center text-gray-500 mt-20">Select a document to view.</div>
          )}
        </div>
        <div className="w-1/4 overflow-y-auto p-4 bg-red-100 border-l border-gray-300">
          <QA_Panel
            selectedDocId={selectedDoc ? selectedDoc.id : null}
            onCitationClick={onCitationClick}
          />
        </div>
      </div>
    </div>
  );
}

export default App;