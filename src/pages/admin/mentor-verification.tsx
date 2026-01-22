'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useProtectedPage } from '@/lib/useProtectedPage';
import { useToast } from '@/components/Toast';
import { LoadingSpinner } from '@/components/LoadingSpinner';
import Layout from '@/components/Layout';
import {
  getPendingVerifications,
  approveMentorDocument,
  rejectMentorDocument,
  MentorDocument,
  PendingMentorVerification,
} from '@/lib/api/mentorVerificationApi';
import Button from '@/components/Button';
import Card from '@/components/Card';

type DocumentAction = 'approve' | 'reject' | 'preview' | null;

export default function AdminMentorVerificationPage() {
  const router = useRouter();
  const { user, loading: authLoading, isAuthorized } = useProtectedPage('admin');
  const { addToast } = useToast();

  const [pendingVerifications, setPendingVerifications] = useState<PendingMentorVerification[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState<string | null>(null);

  // Modal states
  const [selectedDocument, setSelectedDocument] = useState<MentorDocument | null>(null);
  const [currentAction, setCurrentAction] = useState<DocumentAction>(null);
  const [approvalNote, setApprovalNote] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');
  const [showModal, setShowModal] = useState(false);

  // Redirect if not authenticated or not admin
  useEffect(() => {
    if (authLoading) return; // Wait for auth to load
    
    if (!isAuthorized) {
      return; // useProtectedPage already handles redirect
    }

    // Once auth is confirmed, load data
    loadPendingVerifications();
  }, [isAuthorized, authLoading]);

  const loadPendingVerifications = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      if (!token) throw new Error('No auth token');
      const response = await getPendingVerifications(token);
      setPendingVerifications(response.pending_verifications);
    } catch (error: any) {
      addToast({
        type: 'error',
        message: 'Failed to load pending verifications: ' + (error.message || 'Unknown error'),
      });
    } finally {
      setLoading(false);
    }
  };

  const openApproveModal = (doc: MentorDocument) => {
    setSelectedDocument(doc);
    setCurrentAction('approve');
    setApprovalNote('');
    setShowModal(true);
  };

  const openRejectModal = (doc: MentorDocument) => {
    setSelectedDocument(doc);
    setCurrentAction('reject');
    setRejectionReason('');
    setShowModal(true);
  };

  const openPreviewModal = (doc: MentorDocument) => {
    setSelectedDocument(doc);
    setCurrentAction('preview');
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedDocument(null);
    setCurrentAction(null);
    setApprovalNote('');
    setRejectionReason('');
  };

  const handleApprove = async () => {
    if (!selectedDocument) return;

    try {
      setProcessingId(selectedDocument.id);
      const token = localStorage.getItem('token');
      if (!token) throw new Error('No auth token');
      await approveMentorDocument(selectedDocument.id, approvalNote || null, token);
      addToast({
        type: 'success',
        message: 'Document approved successfully',
      });
      closeModal();
      await loadPendingVerifications();
    } catch (error: any) {
      addToast({
        type: 'error',
        message: 'Approval failed: ' + (error.message || 'Unknown error'),
      });
    } finally {
      setProcessingId(null);
    }
  };

  const handleReject = async () => {
    if (!selectedDocument || !rejectionReason) {
      addToast({
        type: 'error',
        message: 'Please provide a rejection reason',
      });
      return;
    }

    try {
      setProcessingId(selectedDocument.id);
      const token = localStorage.getItem('token');
      if (!token) throw new Error('No auth token');
      await rejectMentorDocument(selectedDocument.id, rejectionReason, token);
      addToast({
        type: 'success',
        message: 'Document rejected successfully',
      });
      closeModal();
      await loadPendingVerifications();
    } catch (error: any) {
      addToast({
        type: 'error',
        message: 'Rejection failed: ' + (error.message || 'Unknown error'),
      });
    } finally {
      setProcessingId(null);
    }
  };

  if (authLoading) {
    return <LoadingSpinner message="Loading admin dashboard..." />;
  }

  // Don't render if not authorized (useProtectedPage handles redirect)
  if (!isAuthorized) {
    return null;
  }

  if (loading) {
    return <LoadingSpinner message="Loading mentor verifications..." />;
  }

  const totalPendingDocuments = pendingVerifications.reduce((sum, v) => sum + v.pending_count, 0);

  return (
    <Layout maxWidth="7xl">
      <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Mentor Verification Dashboard</h1>
        <p className="text-gray-600">Review and approve mentor verification documents.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <Card className="p-4">
          <div className="flex items-center">
            <div className="text-3xl font-bold text-primary-500 mr-4">{pendingVerifications.length}</div>
            <div>
              <div className="text-sm font-medium text-gray-600">Mentors Pending</div>
              <div className="text-xs text-gray-500">Waiting for approval</div>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center">
            <div className="text-3xl font-bold text-yellow-500 mr-4">{totalPendingDocuments}</div>
            <div>
              <div className="text-sm font-medium text-gray-600">Documents Pending</div>
              <div className="text-xs text-gray-500">Total across all mentors</div>
            </div>
          </div>
        </Card>
      </div>

      {/* Pending Verifications List */}
      {pendingVerifications.length === 0 ? (
        <Card className="p-12 text-center">
          <svg className="w-16 h-16 mx-auto text-green-500 mb-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          <h3 className="text-lg font-semibold mb-2">All Clear!</h3>
          <p className="text-gray-600">No pending mentor verifications at this time.</p>
        </Card>
      ) : (
        <div className="space-y-6">
          {pendingVerifications.map((mentor) => (
            <Card key={mentor.mentor_id} className="p-6">
              {/* Mentor Header */}
              <div className="mb-4 pb-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center">
                      <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-gray-900">{mentor.mentor_name}</h3>
                      <p className="text-sm text-gray-600">{mentor.mentor_email}</p>
                    </div>
                  </div>
                  <div className="inline-block px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
                    {mentor.pending_count} Pending
                  </div>
                </div>
              </div>

              {/* Documents List */}
              <div className="space-y-3">
                {mentor.pending_documents.map((doc) => (
                  <div key={doc.id} className="p-4 bg-gray-50 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-start gap-3 flex-1">
                        <svg className="w-5 h-5 text-gray-400 mt-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                        </svg>
                        <div className="flex-1">
                          <p className="font-medium text-gray-900 break-all">{doc.filename}</p>
                          <div className="flex flex-wrap gap-3 mt-1">
                            <span className="text-xs text-gray-600 bg-white px-2 py-1 rounded">
                              {doc.document_type.replace(/_/g, ' ').toUpperCase()}
                            </span>
                            <span className="text-xs text-gray-500">{(doc.file_size / 1024).toFixed(2)} KB</span>
                            <span className="text-xs text-gray-500">{new Date(doc.uploaded_at).toLocaleDateString()}</span>
                          </div>
                        </div>
                      </div>
                      <span className="inline-block px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800">
                        PENDING
                      </span>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-2 justify-end">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => openPreviewModal(doc)}
                      >
                        Preview
                      </Button>
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => openApproveModal(doc)}
                        disabled={processingId === doc.id}
                      >
                        <svg className="w-4 h-4 mr-2 inline" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        Approve
                      </Button>
                      <Button
                        size="sm"
                        variant="secondary"
                        onClick={() => openRejectModal(doc)}
                        disabled={processingId === doc.id}
                      >
                        <svg className="w-4 h-4 mr-2 inline" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                        </svg>
                        Reject
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Modal for Actions */}
      {showModal && selectedDocument && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          {/* Backdrop */}
          <div 
            className="absolute inset-0 bg-black/70 backdrop-blur-sm"
            onClick={closeModal}
          />
          
          {/* Modal */}
          <div className="relative w-full max-w-md mx-4 bg-white rounded-lg shadow-xl max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="sticky top-0 px-6 py-4 border-b border-gray-200 flex items-center justify-between bg-white">
              <h2 className="text-lg font-semibold text-gray-900">
                {currentAction === 'approve'
                  ? 'Approve Document'
                  : currentAction === 'reject'
                    ? 'Reject Document'
                    : 'Preview Document'}
              </h2>
              <button
                onClick={closeModal}
                className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
              >
                ×
              </button>
            </div>

            {/* Content */}
            <div className="px-6 py-4 space-y-4">
              {/* Document Info */}
              <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                <p className="text-xs text-gray-600">
                  <span className="font-medium">File:</span> {selectedDocument.filename}
                </p>
                <p className="text-xs text-gray-600 mt-1">
                  <span className="font-medium">Type:</span> {selectedDocument.document_type.replace(/_/g, ' ')}
                </p>
                <p className="text-xs text-gray-600 mt-1">
                  <span className="font-medium">Size:</span> {(selectedDocument.file_size / 1024).toFixed(2)} KB
                </p>
              </div>

              {/* Preview */}
              {currentAction === 'preview' && (
                <div className="bg-gray-100 rounded-lg p-4 text-center">
                  <svg className="w-12 h-12 mx-auto text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                  <p className="text-sm text-gray-600">
                    Document preview not yet available. Download and view: {selectedDocument.filename}
                  </p>
                  <p className="text-xs text-gray-500 mt-2">
                    File path: {selectedDocument.filepath}
                  </p>
                </div>
              )}

              {/* Approval Form */}
              {currentAction === 'approve' && (
                <div>
                  <label htmlFor="approvalNote" className="block text-sm font-medium text-gray-700 mb-2">
                    Optional Note
                  </label>
                  <textarea
                    id="approvalNote"
                    value={approvalNote}
                    onChange={(e) => setApprovalNote(e.target.value)}
                    placeholder="Add an optional note for the mentor (optional)"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    rows={4}
                  />
                </div>
              )}

              {/* Rejection Form */}
              {currentAction === 'reject' && (
                <div>
                  <label htmlFor="rejectionReason" className="block text-sm font-medium text-gray-700 mb-2">
                    Rejection Reason *
                  </label>
                  <textarea
                    id="rejectionReason"
                    value={rejectionReason}
                    onChange={(e) => setRejectionReason(e.target.value)}
                    placeholder="Explain why this document is being rejected..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    rows={4}
                  />
                  {!rejectionReason && (
                    <p className="text-xs text-red-600 mt-1">Rejection reason is required</p>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              {currentAction !== 'preview' && (
                <div className="flex gap-3 justify-end">
                  <Button variant="outline" onClick={closeModal}>
                    Cancel
                  </Button>
                  {currentAction === 'approve' && (
                    <Button
                      onClick={handleApprove}
                      loading={processingId === selectedDocument.id}
                    >
                      Approve Document
                    </Button>
                  )}
                  {currentAction === 'reject' && (
                    <Button
                      variant="secondary"
                      onClick={handleReject}
                      loading={processingId === selectedDocument.id}
                      disabled={!rejectionReason}
                    >
                      Reject Document
                    </Button>
                  )}
                </div>
              )}

              {currentAction === 'preview' && (
                <div className="flex gap-3 justify-end">
                  <Button variant="outline" onClick={closeModal}>
                    Close
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
      </div>
    </Layout>
  );
}
