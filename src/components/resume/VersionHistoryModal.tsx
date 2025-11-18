import { useEffect, useMemo, useState } from 'react';
import { X, Save, RotateCcw, History, GitCompare, Plus } from 'lucide-react';
import { Button } from '@/components/Button';
import { API_BASE } from '@/lib/apiBase';

interface VersionItem {
  id: number;
  version_number: number;
  version_name: string;
  description?: string;
  ats_score?: number;
  word_count?: number;
  skill_count?: number;
  created_at: string;
}

interface VersionHistoryModalProps {
  resumeId: number;
  isOpen: boolean;
  onClose: () => void;
  onRestored?: () => void;
  onCompareClick?: (baseVersionId?: number, comparedVersionId?: number) => void;
}

export default function VersionHistoryModal({ resumeId, isOpen, onClose, onRestored, onCompareClick }: VersionHistoryModalProps) {
  const [versions, setVersions] = useState<VersionItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [newName, setNewName] = useState('');
  const [restoringId, setRestoringId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [bestVersionId, setBestVersionId] = useState<number | null>(null);

  useEffect(() => {
    if (isOpen) {
      setNewName('');
      fetchVersions();
      fetchBestVersion();
    }
  }, [isOpen, resumeId]);

  const sortedVersions = useMemo(() => {
    return [...versions].sort((a, b) => b.version_number - a.version_number);
  }, [versions]);

  const fetchVersions = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await fetch(`/api/session/v1x/resume-comparison/versions/${resumeId}`, { credentials: 'include' });
      if (!res.ok) {
        let detail = '';
        const ct = res.headers.get('content-type') || '';
        try {
          if (ct.includes('application/json')) {
            const j = await res.json();
            detail = (j && (j.detail || j.message)) ? `: ${j.detail || j.message}` : '';
          } else {
            const t = await res.text();
            detail = t ? `: ${t}` : '';
          }
        } catch (_) { /* ignore parse errors */ }
        throw new Error(`Failed to load versions (${res.status})${detail}`);
      }
      const data = await res.json();
      setVersions(data);
    } catch (e: any) {
      setError(e?.message || 'Failed to load versions');
    } finally {
      setLoading(false);
    }
  };

  const fetchBestVersion = async () => {
    try {
      const res = await fetch(`/api/session/v1x/resume-comparison/best-version/${resumeId}?metric=ats_score`, { credentials: 'include' });
      if (!res.ok) return; // optional enhancement; ignore errors silently
      const data = await res.json();
      if (data?.id) setBestVersionId(data.id as number);
    } catch (_) {
      // ignore best-version fetch errors
    }
  };

  const saveNewVersion = async () => {
    const name = newName.trim() || `Version ${sortedVersions.length + 1}`;
    try {
      setSaving(true);
      const res = await fetch(`/api/session/v1x/resume-comparison/versions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          resume_id: resumeId,
          version_name: name,
          description: `Snapshot created on ${new Date().toLocaleString()}`,
        }),
      });
      if (!res.ok) {
        let detail = '';
        try {
          const ct = res.headers.get('content-type') || '';
          if (ct.includes('application/json')) {
            const j = await res.json();
            detail = (j && (j.detail || j.message)) ? `: ${j.detail || j.message}` : '';
          } else {
            const t = await res.text();
            detail = t ? `: ${t}` : '';
          }
        } catch (_) {}
        throw new Error(`Failed to save version (${res.status})${detail}`);
      }
      setNewName('');
      await fetchVersions();
    } catch (e: any) {
      setError(e?.message || 'Failed to save version');
    } finally {
      setSaving(false);
    }
  };

  const restoreVersion = async (versionId: number) => {
    try {
      const confirmRestore = window.confirm('Restore this version? This will replace current resume content.');
      if (!confirmRestore) return;
      setRestoringId(versionId);
      const res = await fetch(`/api/session/v1x/resume-comparison/versions/${versionId}/restore`, {
        method: 'POST',
        credentials: 'include',
      });
      if (!res.ok) {
        let detail = '';
        try {
          const ct = res.headers.get('content-type') || '';
          if (ct.includes('application/json')) {
            const j = await res.json();
            detail = (j && (j.detail || j.message)) ? `: ${j.detail || j.message}` : '';
          } else {
            const t = await res.text();
            detail = t ? `: ${t}` : '';
          }
        } catch (_) {}
        throw new Error(`Failed to restore version (${res.status})${detail}`);
      }
      onRestored?.();
    } catch (e: any) {
      setError(e?.message || 'Failed to restore version');
    } finally {
      setRestoringId(null);
    }
  };

  const deleteVersion = async (versionId: number) => {
    try {
      const confirmDelete = window.confirm('Delete this version? This cannot be undone.');
      if (!confirmDelete) return;
      setDeletingId(versionId);
      const res = await fetch(`/api/session/v1x/resume-comparison/versions/${versionId}`, {
        method: 'DELETE',
        credentials: 'include',
      });
      if (!res.ok) {
        let detail = '';
        try {
          const ct = res.headers.get('content-type') || '';
          if (ct.includes('application/json')) {
            const j = await res.json();
            detail = (j && (j.detail || j.message)) ? `: ${j.detail || j.message}` : '';
          } else {
            const t = await res.text();
            detail = t ? `: ${t}` : '';
          }
        } catch (_) {}
        throw new Error(`Failed to delete version (${res.status})${detail}`);
      }
      await fetchVersions();
      await fetchBestVersion();
    } catch (e: any) {
      setError(e?.message || 'Failed to delete version');
    } finally {
      setDeletingId(null);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-gradient-to-b from-deepTech via-deepTech/95 to-deepTech/90 rounded-2xl w-full max-w-3xl shadow-2xl border border-white/15 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-white/5">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-500/20 border border-blue-400/30">
              <History className="w-5 h-5 text-blue-300" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">Version History</h2>
              <p className="text-xs text-white/60">Save snapshots and restore previous versions</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg">
            <X className="w-5 h-5 text-white/70" />
          </button>
        </div>

        {/* New version row */}
        <div className="px-6 py-4 border-b border-white/10 bg-white/5">
          <div className="flex items-center gap-3">
            <input
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="Version name (e.g., Final Draft)"
              className="flex-1 px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
            />
            <Button onClick={saveNewVersion} disabled={saving} className="bg-blue-500/20 border-blue-400/50 hover:bg-blue-500/30">
              <Plus className="w-4 h-4 mr-1.5" /> Save Version
            </Button>
          </div>
        </div>

        {/* Body */}
        <div className="max-h-[60vh] overflow-y-auto">
          {loading ? (
            <div className="p-6 text-center text-white/70">Loading versions…</div>
          ) : error ? (
            <div className="p-6 text-center text-red-200">{error}</div>
          ) : sortedVersions.length === 0 ? (
            <div className="p-10 text-center text-white/70">
              <p>No versions yet. Create your first snapshot.</p>
            </div>
          ) : (
            <ul className="divide-y divide-white/10">
              {sortedVersions.map((v) => (
                <li key={v.id} className="px-6 py-4 flex items-center justify-between hover:bg-white/5">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-white font-semibold">{v.version_name || `v${v.version_number}`}</span>
                      <span className="text-xs text-white/50">(v{v.version_number})</span>
                      {bestVersionId === v.id && (
                        <span className="ml-2 text-[10px] px-2 py-0.5 rounded-full bg-amber-400/20 text-amber-200 border border-amber-400/40 uppercase tracking-wide">Best</span>
                      )}
                    </div>
                    <div className="text-xs text-white/50 mt-0.5">
                      {new Date(v.created_at).toLocaleString()} • ATS: {typeof v.ats_score === 'number' ? v.ats_score.toFixed(0) : 'N/A'} • Words: {v.word_count ?? '—'} • Skills: {v.skill_count ?? '—'}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      onClick={() => restoreVersion(v.id)}
                      variant="secondary"
                      data-testid={`btn-restore-${v.id}`}
                      disabled={restoringId === v.id || deletingId === v.id}
                      className="px-3 py-1.5 text-sm bg-emerald-500/20 border-emerald-400/50 hover:bg-emerald-500/30 disabled:opacity-50"
                    >
                      <RotateCcw className="w-3.5 h-3.5 mr-1.5" /> {restoringId === v.id ? 'Restoring…' : 'Restore'}
                    </Button>
                    <Button onClick={() => {
                      const idx = sortedVersions.findIndex(sv => sv.id === v.id);
                      const base = idx >= 0 && idx + 1 < sortedVersions.length ? sortedVersions[idx + 1].id : undefined;
                      onCompareClick?.(base, v.id);
                    }} variant="secondary" data-testid={`btn-compare-${v.id}`} className="px-3 py-1.5 text-sm">
                      <GitCompare className="w-3.5 h-3.5 mr-1.5" /> Compare
                    </Button>
                    <Button
                      onClick={() => deleteVersion(v.id)}
                      variant="secondary"
                      data-testid={`btn-delete-${v.id}`}
                      disabled={deletingId === v.id || restoringId === v.id}
                      className="px-3 py-1.5 text-sm bg-red-500/20 border-red-400/50 hover:bg-red-500/30 disabled:opacity-50"
                    >
                      {deletingId === v.id ? 'Deleting…' : 'Delete'}
                    </Button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
