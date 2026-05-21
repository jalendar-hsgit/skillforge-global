// API base URL configuration
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';

export interface DocumentUploadResponse {
  document_id: string;
  filename: string;
  document_type: string;
  status: 'pending' | 'approved' | 'rejected' | 'expired';
  uploaded_at: string;
  message: string;
}

export interface MentorDocument {
  id: string;
  mentor_id: string;
  document_type: string;
  filename: string;
  filepath: string;
  file_size: number;
  mime_type: string;
  status: 'pending' | 'approved' | 'rejected' | 'expired';
  rejection_reason?: string;
  uploaded_at: string;
  reviewed_at?: string;
  expires_at?: string;
}

export interface MentorDocumentListResponse {
  documents: MentorDocument[];
  total: number;
  pending_count: number;
  approved_count: number;
  rejected_count: number;
}

export interface PendingMentorVerification {
  mentor_id: string;
  mentor_name: string;
  mentor_email: string;
  pending_documents: MentorDocument[];
  pending_count: number;
}

export interface PendingVerificationListResponse {
  pending_verifications: PendingMentorVerification[];
  total: number;
}

export interface MentorApprovalResponse {
  approval_id: string;
  document_id: string;
  reviewer_id: string;
  action: 'approved' | 'rejected' | 'request_more';
  reason?: string;
  reviewed_at: string;
}

// Allowed document types
export const DOCUMENT_TYPES = [
  { value: 'certification', label: 'Certification' },
  { value: 'id_verification', label: 'ID Verification' },
  { value: 'degree', label: 'Degree/Diploma' },
  { value: 'experience', label: 'Experience Letter' },
  { value: 'license', label: 'Professional License' },
  { value: 'portfolio', label: 'Portfolio/Work Samples' },
  { value: 'other', label: 'Other' },
];

// Allowed file types
export const ALLOWED_FILE_TYPES = ['application/pdf', 'image/jpeg', 'image/png', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
export const ALLOWED_FILE_EXTENSIONS = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx'];

/**
 * Upload a document for mentor verification
 */
export async function uploadMentorDocument(
  file: File,
  documentType: string,
  token: string
): Promise<DocumentUploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('document_type', documentType);

  const response = await fetch(`${API_BASE}/api/v1x/mentor-documents/upload`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to upload document');
  }

  return response.json();
}

/**
 * Get mentor's uploaded documents
 */
export async function getMentorDocuments(token: string): Promise<MentorDocumentListResponse> {
  const response = await fetch(`${API_BASE}/api/v1x/mentor-documents/my-documents`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch documents');
  }

  return response.json();
}

/**
 * Delete a pending document
 */
export async function deleteMentorDocument(documentId: string, token: string): Promise<{ message: string }> {
  const response = await fetch(`${API_BASE}/api/v1x/mentor-documents/my-documents/${documentId}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete document');
  }

  return response.json();
}

/**
 * Get pending mentor verifications (admin only)
 */
export async function getPendingVerifications(token: string): Promise<PendingVerificationListResponse> {
  const response = await fetch(`${API_BASE}/api/v1x/mentor-documents/pending`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch pending verifications');
  }

  return response.json();
}

/**
 * Get document details including filepath
 */
export async function getDocumentDetails(documentId: string, token: string): Promise<MentorDocument> {
  const response = await fetch(`${API_BASE}/api/v1x/mentor-documents/details/${documentId}`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch document details');
  }

  return response.json();
}

/**
 * Approve a mentor document
 */
export async function approveMentorDocument(
  documentId: string,
  reason: string | null,
  token: string
): Promise<MentorApprovalResponse> {
  const response = await fetch(`${API_BASE}/api/v1x/mentor-documents/${documentId}/approve`, {
    method: 'PATCH',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      reason: reason || undefined,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to approve document');
  }

  return response.json();
}

/**
 * Reject a mentor document
 */
export async function rejectMentorDocument(
  documentId: string,
  reason: string,
  token: string
): Promise<MentorApprovalResponse> {
  const response = await fetch(`${API_BASE}/api/v1x/mentor-documents/${documentId}/reject`, {
    method: 'PATCH',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      reason,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to reject document');
  }

  return response.json();
}
