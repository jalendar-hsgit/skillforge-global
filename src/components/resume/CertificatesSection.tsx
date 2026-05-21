import { useState } from 'react';
import { Button } from '@/components/Button';
import { Card } from '@/components/Card';
import { Input } from '@/components/Input';

interface Certificate {
  id: number;
  name: string;
  issuer: string;
  issue_date: string;
  expiry_date?: string;
  credential_id?: string;
  credential_url?: string;
}

interface CertificatesSectionProps {
  resumeId: number;
  certificates: Certificate[];
  onUpdate: () => void;
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001';

export default function CertificatesSection({
  resumeId,
  certificates,
  onUpdate,
}: CertificatesSectionProps) {
  const [editingId, setEditingId] = useState<number | null>(null);
  const [showForm, setShowForm] = useState(false);

  const handleAdd = () => {
    setEditingId(null);
    setShowForm(true);
  };

  const handleEdit = (id: number) => {
    setEditingId(id);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this certificate?')) return;

    try {
      const response = await fetch(
        `/api/session/v1x/certificates?id=${id}`,
        {
          method: 'DELETE',
          credentials: 'include',
        }
      );

      if (response.ok) {
        onUpdate();
      }
    } catch (error) {
      console.error('Error deleting certificate:', error);
      alert('Failed to delete certificate');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-black bg-gradient-to-r from-forgePurple via-neuralBlue to-forgePurple bg-clip-text text-transparent tracking-tight">Certificates & Licenses</h2>
          <p className="text-techGray/80 mt-1">
            List professional certifications, licenses, and training programs.
          </p>
        </div>
        <Button onClick={handleAdd} variant="primary">
          + Add Certificate
        </Button>
      </div>

      {certificates.length === 0 && !showForm && (
        <Card className="p-8 text-center">
          <div className="text-4xl mb-3">🏆</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No certificates yet</h3>
          <p className="text-gray-600 mb-4">
            Add certifications to stand out from other candidates.
          </p>
          <Button onClick={handleAdd} variant="primary">
            Add Certificate
          </Button>
        </Card>
      )}

      {certificates.map((cert) => (
        <Card key={cert.id} className="p-6">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-lg font-bold text-gray-900">{cert.name}</h3>
              <p className="text-md text-gray-700 font-medium">{cert.issuer}</p>
              <p className="text-sm text-gray-500 mt-1">
                Issued: {cert.issue_date}
                {cert.expiry_date && ` • Expires: ${cert.expiry_date}`}
              </p>
              {cert.credential_id && (
                <p className="text-sm text-gray-600 mt-1">
                  Credential ID: {cert.credential_id}
                </p>
              )}
              {cert.credential_url && (
                <a
                  href={cert.credential_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-600 hover:text-blue-800 mt-2 inline-block"
                >
                  🔗 View Credential
                </a>
              )}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => handleEdit(cert.id)}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                Edit
              </button>
              <button
                onClick={() => handleDelete(cert.id)}
                className="text-red-600 hover:text-red-800 text-sm font-medium"
              >
                Delete
              </button>
            </div>
          </div>
        </Card>
      ))}

      {showForm && (
        <CertificateForm
          resumeId={resumeId}
          certificateId={editingId}
          onClose={() => {
            setShowForm(false);
            setEditingId(null);
          }}
          onSave={() => {
            setShowForm(false);
            setEditingId(null);
            onUpdate();
          }}
        />
      )}
    </div>
  );
}

// Form Component
interface CertificateFormProps {
  resumeId: number;
  certificateId: number | null;
  onClose: () => void;
  onSave: () => void;
}

function CertificateForm({ resumeId, certificateId, onClose, onSave }: CertificateFormProps) {
  const [formData, setFormData] = useState({
    name: '',
    issuer: '',
    issue_date: '',
    expiry_date: '',
    credential_id: '',
    credential_url: '',
  });
  const [saving, setSaving] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      const url = certificateId
        ? `/api/session/v1x/certificates?id=${certificateId}`
        : `/api/session/v1x/certificates?resumeId=${resumeId}`;

      const response = await fetch(url, {
        method: certificateId ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          name: formData.name,
          issuing_organization: formData.issuer,
          issue_date: formData.issue_date,
          expiry_date: formData.expiry_date,
          credential_id: formData.credential_id,
          credential_url: formData.credential_url,
        }),
      });

      if (response.ok) {
        onSave();
      } else {
        alert('Failed to save certificate');
      }
    } catch (error) {
      console.error('Error saving certificate:', error);
      alert('Failed to save certificate');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Card className="p-6">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-900">
            {certificateId ? 'Edit' : 'Add'} Certificate
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Certificate Name <span className="text-red-500">*</span>
          </label>
          <Input
            type="text"
            value={formData.name}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setFormData({ ...formData, name: e.target.value })
            }
            placeholder="AWS Certified Solutions Architect"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Issuing Organization <span className="text-red-500">*</span>
          </label>
          <Input
            type="text"
            value={formData.issuer}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setFormData({ ...formData, issuer: e.target.value })
            }
            placeholder="Amazon Web Services"
            required
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Issue Date <span className="text-red-500">*</span>
            </label>
            <Input
              type="month"
              value={formData.issue_date}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setFormData({ ...formData, issue_date: e.target.value })
              }
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Expiration Date (if applicable)
            </label>
            <Input
              type="month"
              value={formData.expiry_date}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setFormData({ ...formData, expiry_date: e.target.value })
              }
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Credential ID</label>
          <Input
            type="text"
            value={formData.credential_id}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setFormData({ ...formData, credential_id: e.target.value })
            }
            placeholder="ABC-123-XYZ"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Credential URL</label>
          <Input
            type="url"
            value={formData.credential_url}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              setFormData({ ...formData, credential_url: e.target.value })
            }
            placeholder="https://..."
          />
        </div>

        <div className="flex gap-3 pt-4">
          <Button type="submit" variant="primary" disabled={saving}>
            {saving ? 'Saving...' : 'Save'}
          </Button>
          <Button type="button" onClick={onClose} variant="secondary">
            Cancel
          </Button>
        </div>
      </form>
    </Card>
  );
}
