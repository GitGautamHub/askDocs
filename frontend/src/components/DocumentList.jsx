// frontend/src/components/DocumentList.jsx
import axios from 'axios';
import { toast } from 'react-toastify';
import FileUploader from './FileUploader';


// Document List Component
const DocumentList = ({ documents, onSelectDoc, onUpload }) => {
    const getProgress = (status) => {
        switch (status) {
            case 'Uploading...':
                return 20;
            case 'Extracting':
                return 40;
            case 'Chunking/Embedding':
                return 80;
            case 'Indexed':
                return 100;
            default:
                return 0;
        }
    };

    // Delete document handler
    const handleDelete = async (file_id, file_name) => {
        try {
            await axios.delete(`http://127.0.0.1:8000/api/documents/${file_id}`);
            toast.success(`Document '${file_name}' deleted.`);
            window.location.reload();
        } catch (error) {
            console.error("Failed to delete document:", error);
            toast.error(`Failed to delete document '${file_name}'.`);
        }
    };

    return (
        <div className="p-4 bg-gray-100 h-full border-r border-gray-300">
            <FileUploader onUploadSuccess={onUpload} />
            <div className="mt-6">
                <h4 className="text-lg font-semibold mb-3 text-red-800">Uploaded Documents</h4>
                {documents.length > 0 ? (
                    <ul className="space-y-2">
                        {documents.map((doc) => (
                            <li
                                key={doc.id}
                                className="p-3 bg-white rounded-lg shadow-sm cursor-pointer hover:bg-gray-50 transition-colors"
                            >
                                <div className="flex justify-between items-center" onClick={() => onSelectDoc(doc)}>
                                    <span className="flex-grow text-sm font-medium text-gray-700 truncate">
                                        {doc.name}
                                    </span>
                                    {doc.status.toLowerCase() !== 'indexed' && doc.status.toLowerCase() !== 'failed' ? (
                                        <div className="flex flex-col items-end space-y-1 w-1/3">
                                            <span className="text-xs text-gray-500">{doc.status}</span>
                                            <div className="flex-grow bg-gray-200 rounded-full h-2.5 w-full">
                                                <div
                                                    className="bg-blue-600 h-2.5 rounded-full transition-all duration-500 ease-in-out"
                                                    style={{ width: `${getProgress(doc.status)}%` }}
                                                ></div>
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="flex items-center space-x-2">
                                            <span
                                                className={`text-xs font-semibold px-2 py-1 rounded-full
                                                    ${doc.status.toLowerCase() === 'indexed' ? 'bg-green-500 text-white' : ''}
                                                    ${doc.status.toLowerCase() === 'failed' ? 'bg-red-500 text-white' : ''}
                                                `}
                                            >
                                                {doc.status}
                                            </span>
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation(); 
                                                    handleDelete(doc.id, doc.name);
                                                }}
                                                className="text-red-500 hover:text-red-700 transition-colors"
                                                title="Delete document"
                                            >
                                                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                                    <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                                                </svg>
                                            </button>
                                        </div>
                                    )}
                                </div>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p className="text-sm text-gray-500 text-center mt-8">No documents uploaded yet.</p>
                )}
            </div>
        </div>
    );
};

export default DocumentList;