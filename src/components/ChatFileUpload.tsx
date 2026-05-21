/**
 * File upload component for mentor chat
 */
import React, { useRef, useState } from 'react';

interface ChatFileUploadProps {
  sessionId: number;
  token: string;
  onFileUploaded: (fileData: any) => void;
  onError?: (error: string) => void;
}

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

const ALLOWED_FILES = [
  '.jpg', '.jpeg', '.png', '.gif', '.webp',
  '.pdf', '.doc', '.docx', '.txt', '.md',
  '.zip', '.rar',
  '.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css', '.json'
];

export default function ChatFileUpload({ 
  sessionId, 
  token, 
  onFileUploaded,
  onError 
}: ChatFileUploadProps) {
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
      onError?.('File too large. Maximum size is 10MB');
      return;
    }

    // Validate file type
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!ALLOWED_FILES.includes(ext)) {
      onError?.(`File type ${ext} not allowed`);
      return;
    }

    // Upload file
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('session_id', sessionId.toString());

      const response = await fetch('http://localhost:8001/api/v1x/chat/files/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Upload failed');
      }

      const fileData = await response.json();
      onFileUploaded(fileData);

      // Reset input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error: any) {
      console.error('Upload error:', error);
      onError?.(error.message || 'Failed to upload file');
    } finally {
      setUploading(false);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="relative">
      <input
        ref={fileInputRef}
        type="file"
        onChange={handleFileSelect}
        accept={ALLOWED_FILES.join(',')}
        className="hidden"
        disabled={uploading}
      />
      <button
        onClick={handleClick}
        disabled={uploading}
        className={`p-2 rounded-lg transition-colors ${
          uploading
            ? 'bg-gray-200 cursor-not-allowed'
            : 'hover:bg-gray-100 active:bg-gray-200'
        }`}
        title="Upload file"
      >
        {uploading ? (
          <svg
            className="animate-spin h-5 w-5 text-blue-600"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        ) : (
          <svg
            className="h-5 w-5 text-gray-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"
            />
          </svg>
        )}
      </button>
    </div>
  );
}

interface FileMessageProps {
  file: {
    id: number;
    original_filename: string;
    file_size: number;
    mime_type: string;
    category: string;
    download_url: string;
    sender_id: number;
  };
  isOwn: boolean;
  token: string;
}

export function FileMessage({ file, isOwn, token }: FileMessageProps) {
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const getFileIcon = (category: string) => {
    switch (category) {
      case 'image':
        return '🖼️';
      case 'document':
        return '📄';
      case 'archive':
        return '📦';
      case 'code':
        return '💻';
      default:
        return '📎';
    }
  };

  const handleDownload = async () => {
    try {
      const response = await fetch(`http://localhost:8001${file.download_url}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Download failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = file.original_filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Download error:', error);
      alert('Failed to download file');
    }
  };

  // Show image preview for image files
  const isImage = file.category === 'image';
  const imageUrl = isImage ? `http://localhost:8001${file.download_url}` : null;

  return (
    <div
      className={`max-w-xs rounded-lg p-3 ${
        isOwn ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-900'
      }`}
    >
      {isImage && imageUrl ? (
        <div className="mb-2">
          <img
            src={imageUrl}
            alt={file.original_filename}
            className="rounded max-w-full h-auto cursor-pointer"
            onClick={handleDownload}
            style={{ maxHeight: '200px' }}
          />
        </div>
      ) : null}
      <div className="flex items-center space-x-2">
        <span className="text-2xl">{getFileIcon(file.category)}</span>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium truncate">
            {file.original_filename}
          </p>
          <p className={`text-xs ${isOwn ? 'text-blue-100' : 'text-gray-500'}`}>
            {formatFileSize(file.file_size)}
          </p>
        </div>
      </div>
      <button
        onClick={handleDownload}
        className={`mt-2 w-full text-sm py-1 px-2 rounded transition-colors ${
          isOwn
            ? 'bg-blue-700 hover:bg-blue-800 text-white'
            : 'bg-gray-300 hover:bg-gray-400 text-gray-900'
        }`}
      >
        Download
      </button>
    </div>
  );
}
