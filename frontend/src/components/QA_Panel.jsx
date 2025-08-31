import { useState } from 'react';


const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const QA_Panel = ({ selectedDocId, onCitationClick }) => {
  const [query, setQuery] = useState('');
  const [scope, setScope] = useState('this_document');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const handleQuery = async () => {
      if (!query) return;

      setLoading(true);
      setAnswer('');

      const requestBody = {
          query: query,
          scope: scope,
      };

      if (scope === 'this_document' && selectedDocId) {
          requestBody.doc_id = selectedDocId;
      }

      try {
          const response = await fetch(`${API_URL}/api/qa`, {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
              },
              body: JSON.stringify(requestBody),
          });

          if (!response.body) {
              setAnswer('Sorry, no response body received.');
              setLoading(false);
              return;
          }

          const reader = response.body.getReader();
          const decoder = new TextDecoder();
          let result = '';

          while (true) {
              const { done, value } = await reader.read();
              if (done) break;
              result += decoder.decode(value, { stream: true });
              setAnswer(result);
          }
      } catch (err) {
          setAnswer('Sorry, I could not find an answer to that question.');
          console.error('QA API failed:', err);
      } finally {
          setLoading(false);
      }
  };

  const renderAnswerWithCitations = (text) => {
    if (!text) return null;
    
    const citationRegex = /\[Source: (.+?), Page: (\d+)\]/g;
    const parts = [];
    let lastIndex = 0;
    let match;

    while ((match = citationRegex.exec(text)) !== null) {
      const plainText = text.substring(lastIndex, match.index);
      const fullCitation = match[0];
      const docName = match[1];
      const pageNumber = parseInt(match[2], 10);

      if (plainText) {
        parts.push(plainText);
      }

      parts.push(
        <button
          key={`citation-${lastIndex}`}
          className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full hover:bg-blue-200 transition-colors cursor-pointer inline-flex items-center space-x-1 mx-1"
          onClick={() => onCitationClick(docName, pageNumber)}
        >
          <span>{fullCitation}</span>
        </button>
      );
      lastIndex = citationRegex.lastIndex;
    }

    parts.push(text.substring(lastIndex));

    return <div>{parts}</div>;
  };

  return (
    <div className="flex flex-col h-full bg-white p-6 shadow-md rounded-lg">
      <h3 className="text-xl font-bold mb-4 text-gray-800">Document Q&A</h3>
      
      <div className="flex space-x-4 mb-4">
        <label className="flex items-center space-x-1 text-sm text-gray-700">
          <input
            type="radio"
            value="this_document"
            checked={scope === 'this_document'}
            onChange={() => setScope('this_document')}
            disabled={!selectedDocId}
            className="form-radio text-blue-600"
          />
          <span>This document</span>
        </label>
        <label className="flex items-center space-x-1 text-sm text-gray-700">
          <input
            type="radio"
            value="all_documents"
            checked={scope === 'all_documents'}
            onChange={() => setScope('all_documents')}
            className="form-radio text-blue-600"
          />
          <span>All documents</span>
        </label>
      </div>
      
      <textarea
        rows="4"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask a question..."
        className="w-full p-3 border border-gray-300 rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4 text-sm"
      />
      
      <button
        onClick={handleQuery}
        disabled={loading || !query.trim()}
        className="w-full px-4 py-2 bg-blue-600 text-white rounded-md font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? 'Thinking...' : 'Get Answer'}
      </button>

      <div className="mt-6 flex-grow overflow-y-auto border-t border-gray-200 pt-4">
        <h4 className="text-lg font-semibold mb-2 text-gray-800">Answer:</h4>
        <div className="prose max-w-none text-gray-800">
          {loading ? (
            <p className="text-sm italic text-gray-500">...thinking...</p>
          ) : (
            renderAnswerWithCitations(answer)
          )}
        </div>
      </div>
    </div>
  );
};

export default QA_Panel;