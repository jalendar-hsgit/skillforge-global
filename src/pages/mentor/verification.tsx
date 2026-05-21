'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useProtectedPage } from '@/lib/useProtectedPage';
import { useToast } from '@/components/Toast';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import Layout from '@/components/Layout';
import {
  uploadMentorDocument,
  getMentorDocuments,
  deleteMentorDocument,
  DOCUMENT_TYPES,
  ALLOWED_FILE_EXTENSIONS,
  MentorDocument,
  MentorDocumentListResponse,
} from '@/lib/api/mentorVerificationApi';
import Button from '@/components/Button';
import Input from '@/components/Input';
import Card from '@/components/Card';

export default function MentorVerificationPage() {
  const router = useRouter();
  const { user, loading: authLoading, isAuthorized } = useProtectedPage('mentor');
  const { addToast } = useToast();

  const [documentType, setDocumentType] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [isDragActive, setIsDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [documents, setDocuments] = useState<MentorDocument[]>([]);
  const [stats, setStats] = useState({ total: 0, pending: 0, approved: 0, rejected: 0 });
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [docToDelete, setDocToDelete] = useState<MentorDocument | null>(null);

  // Redirect if not authenticated or not a mentor
  useEffect(() => {
    if (authLoading) return; // Wait for auth to load
    
    if (!isAuthorized) {
      return; // useProtectedPage already handles redirect
    }

    // Once auth is confirmed, load data
    loadDocuments();
  }, [isAuthorized, authLoading]);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      if (!token) throw new Error('No auth token');
      const response = await getMentorDocuments(token);
      setDocuments(response.documents);
      setStats({
        total: response.total,
        pending: response.pending_count,
        approved: response.approved_count,
        rejected: response.rejected_count,
      });
    } catch (error: any) {
      addToast({
        type: 'error',
        message: 'Failed to load documents: ' + (error.message || 'Unknown error'),
      });
    } finally {
      setLoading(false);
    }
  };

  const validateFile = (file: File): boolean => {
    // Check file size (10MB max)
    if (file.size > 10 * 1024 * 1024) {
      addToast({
        type: 'error',
        message: 'File size must be less than 10MB',
      });
      return false;
    }

    // Check file type
    const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!ALLOWED_FILE_EXTENSIONS.includes(fileExt)) {
      addToast({
        type: 'error',
        message: `Invalid file type. Allowed: ${ALLOWED_FILE_EXTENSIONS.join(', ')}`,
      });
      return false;
    }

    return true;
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true);
    } else if (e.type === 'dragleave') {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (validateFile(droppedFile)) {
        setFile(droppedFile);
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (validateFile(selectedFile)) {
        setFile(selectedFile);
      }
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!documentType) {
      addToast({
        type: 'error',
        message: 'Please select a document type',
      });
      return;
    }

    if (!file) {
      addToast({
        type: 'error',
        message: 'Please select a file',
      });
      return;
    }

    try {
      setUploading(true);
      const token = localStorage.getItem('token');
      if (!token) throw new Error('No auth token');
      const response = await uploadMentorDocument(file, documentType, token);
      addToast({
        type: 'success',
        message: 'Document uploaded successfully!',
      });

      // Reset form
      setDocumentType('');
      setFile(null);

      // Reload documents
      await loadDocuments();
    } catch (error: any) {
      addToast({
        type: 'error',
        message: 'Upload failed: ' + (error.message || 'Unknown error'),
      });
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async () => {
    if (!docToDelete) return;

    try {
      setDeletingId(docToDelete.id);
      const token = localStorage.getItem('token');
      if (!token) throw new Error('No auth token');
      await deleteMentorDocument(docToDelete.id, token);
      addToast({
        type: 'success',
        message: 'Document deleted successfully',
      });
      setShowDeleteModal(false);
      await loadDocuments();
    } catch (error: any) {
      addToast({
        type: 'error',
        message: 'Delete failed: ' + (error.message || 'Unknown error'),
      });
    } finally {
      setDeletingId(null);
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, string> = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      expired: 'bg-red-100 text-red-800',
    };
    return (
      <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${variants[status] || 'bg-gray-100 text-gray-800'}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const getDocumentTypeLabel = (value: string) => {
    return DOCUMENT_TYPES.find((dt) => dt.value === value)?.label || value;
  };

  if (authLoading) {
    return <LoadingSpinner message="Loading your documents..." />;
  }

  // Don't render if not authorized (useProtectedPage handles redirect)
  if (!isAuthorized) {
    return null;
  }

  if (loading) {
    return <LoadingSpinner message="Loading your documents..." />;
  }

  return (
    <Layout maxWidth="2xl">
      <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Mentor Verification</h1>
        <p className="text-gray-600">Upload documents to verify your mentor credentials and get approved to mentor students.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-8">
        {/* Stats Cards */}
        <Card className="p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-primary-500">{stats.total}</div>
            <div className="text-sm text-gray-600">Total Documents</div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-500">{stats.pending}</div>
            <div className="text-sm text-gray-600">Pending Review</div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-500">{stats.approved}</div>
            <div className="text-sm text-gray-600">Approved</div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-red-500">{stats.rejected}</div>
            <div className="text-sm text-gray-600">Rejected</div>
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Upload Section */}
        <div className="lg:col-span-1">
          <Card className="p-6">
            <h2 className="text-xl font-bold mb-4">Upload Document</h2>

            <form onSubmit={handleUpload} className="space-y-4">
              {/* Document Type Selector */}
              <div>
                <label htmlFor="documentType" className="block text-sm font-medium text-gray-700 mb-2">
                  Document Type *
                </label>
                <select
                  id="documentType"
                  value={documentType}
                  onChange={(e) => setDocumentType(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">Select a type...</option>
                  {DOCUMENT_TYPES.map((type) => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* File Upload Area */}
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                  isDragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300 bg-gray-50'
                }`}
              >
                <input
                  type="file"
                  onChange={handleFileChange}
                  accept={ALLOWED_FILE_EXTENSIONS.join(',')}
                  className="hidden"
                  id="fileInput"
                />
                <label htmlFor="fileInput" className="cursor-pointer block">
                  <svg className="w-8 h-8 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  <p className="font-medium text-gray-700">
                    {file ? file.name : 'Drop file or click to browse'}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    PDF, JPG, PNG, DOC, DOCX (Max 10MB)
                  </p>
                </label>
              </div>

              {/* Upload Button */}
              <Button
                type="submit"
                disabled={!documentType || !file || uploading}
                loading={uploading}
                className="w-full"
              >
                {uploading ? 'Uploading...' : 'Upload Document'}
              </Button>
            </form>

            {/* File Info */}
            {file && (
              <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-xs text-gray-600">
                  <span className="font-medium">File:</span> {file.name}
                </p>
                <p className="text-xs text-gray-600">
                  <span className="font-medium">Size:</span> {(file.size / 1024).toFixed(2)} KB
                </p>
              </div>
            )}
          </Card>
        </div>

        {/* Documents List */}
        <div className="lg:col-span-2">
          <Card className="p-6">
            <h2 className="text-xl font-bold mb-4">Your Documents</h2>

            {documents.length === 0 ? (
              <div className="text-center py-8">
                <svg className="w-12 h-12 mx-auto text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
                <p className="text-gray-600">No documents uploaded yet</p>
                <p className="text-sm text-gray-500">Upload your first document to get started</p>
              </div>
            ) : (
              <div className="space-y-3">
                {documents.map((doc) => (
                  <div key={doc.id} className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                          </svg>
                          <p className="font-medium text-gray-900 break-all">{doc.filename}</p>
                        </div>
                        <div className="flex flex-wrap gap-2">
                          <span className="text-xs text-gray-500">{getDocumentTypeLabel(doc.document_type)}</span>
                          <span className="text-xs text-gray-500">•</span>
                          <span className="text-xs text-gray-500">{(doc.file_size / 1024).toFixed(2)} KB</span>
                          <span className="text-xs text-gray-500">•</span>
                          <span className="text-xs text-gray-500">{new Date(doc.uploaded_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                      <div className="ml-4 flex items-center gap-2">
                        {getStatusBadge(doc.status)}
                        {doc.status === 'pending' && (
                          <button
                            onClick={() => {
                              setDocToDelete(doc);
                              setShowDeleteModal(true);
                            }}
                            disabled={deletingId === doc.id}
                            className="p-2 hover:bg-red-50 rounded-lg text-red-600 transition-colors disabled:opacity-50"
                            title="Delete pending document"
                          >
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                            </svg>
                          </button>
                        )}
                      </div>
                    </div>

                    {/* Rejection Reason */}
                    {doc.status === 'rejected' && doc.rejection_reason && (
                      <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                        <p className="font-medium mb-1">Rejection Reason:</p>
                        <p>{doc.rejection_reason}</p>
                      </div>
                    )}

                    {/* Expiration Notice */}
                    {doc.status === 'expired' && (
                      <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded text-sm text-yellow-700">
                        Document has expired. Please upload a new one.
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* Backdrop */}
          <div 
            className="absolute inset-0 bg-black/70 backdrop-blur-sm"
            onClick={() => setShowDeleteModal(false)}
          />
          
          {/* Modal */}
          <div className="relative w-full max-w-sm mx-4 bg-white rounded-lg shadow-xl max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="sticky top-0 px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-white">
              <h2 className="text-lg font-semibold text-gray-900">Delete Document</h2>
              <button
                onClick={() => setShowDeleteModal(false)}
                className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
              >
                ×
              </button>
            </div>

            {/* Content */}
            <div className="px-6 py-4 space-y-4">
          <p>Are you sure you want to delete this document? This action cannot be undone.</p>
          <p className="text-sm text-gray-600">
            <span className="font-medium">File:</span> {docToDelete?.filename}
          </p>
          <div className="flex gap-3 justify-end">
            <Button
              variant="outline"
              onClick={() => setShowDeleteModal(false)}
            >
              Cancel
            </Button>
            <Button
              variant="secondary"
              onClick={handleDelete}
              loading={deletingId === docToDelete?.id}
            >
              Delete
            </Button>
          </div>
            </div>
          </div>
        </div>
      )}
      </div>
    </Layout>
  );
}
