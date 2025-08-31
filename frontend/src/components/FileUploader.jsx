// frontend/src/components/FileUploader.jsx
import { useState } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// File Upload Component
const FileUploader = ({ onUploadSuccess }) => {
    const [file, setFile] = useState(null);
    const [status, setStatus] = useState('');
    const [error, setError] = useState('');

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        setStatus(e.target.files[0] ? 'Ready to upload' : ''); // Update status here
        setError('');
    };

    const handleUpload = async () => {
        if (!file) {
            setError('Please select a file first.');
            return;
        }

        const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50 MB
        if (file.size > MAX_FILE_SIZE) {
            setError('File size exceeds the 50 MB limit.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        setStatus('Uploading...');
        setError('');

        try {
            const response = await axios.post(`${API_URL}/api/upload`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            onUploadSuccess({
                id: response.data.file_id,
                name: file.name,
                status: response.data.status,
            });
            
            // Set the status to 'Upload successful' and show a toast
            setStatus('Upload successful');
            toast.success(`File '${file.name}' uploaded successfully!`);
            
            // Reset the file input field after successful upload
            setFile(null);
            document.querySelector('input[type="file"]').value = null;

        } catch (err) {
            console.error('Upload failed:', err);
            setStatus('Failed');
            setError('Upload failed. Please try again.');
        }
    };

    return (
        <div className="flex flex-col space-y-4">
            <h3 className="text-lg font-semibold text-gray-800">Upload Documents</h3>
            <p className="text-sm text-gray-500">
                Supported files: PDF, DOCX, TXT, JPG, PNG, JPEG (Max size: 50 MB)
            </p>
            <div className="flex items-center space-x-2">
                <label className="flex-grow">
                    <input
                        type="file"
                        onChange={handleFileChange}
                        className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer"
                    />
                </label>
                <button
                    onClick={handleUpload}
                    disabled={status === 'Uploading...' || !file}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                    {status === 'Uploading...' ? 'Uploading...' : 'Upload'}
                </button>
            </div>
            {status && <p className="text-sm font-medium mt-2 text-gray-600">Status: <span className="font-bold">{status}</span></p>}
            {error && <p className="text-sm text-red-500 mt-2">{error}</p>}
        </div>
    );
};

export default FileUploader;