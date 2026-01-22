import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { useRouter } from 'next/router';
import { Upload, X, Save, AlertCircle, CheckCircle } from 'lucide-react';
import { useAuthCheck } from '@/lib/protectedRoute';

interface ProductFormData {
  name: string;
  description: string;
  product_type: string;
  category: string;
  price: number;
  original_price?: number;
  tags: string[];
  requirements: string[];
  features: string[];
  status: string;
  visibility: string;
}

interface UploadedFiles {
  thumbnail?: string;
  content?: string;
  preview?: string;
}

export default function CreateProduct() {
  const router = useRouter();
  const { isAuthorized, loading: authLoading } = useAuthCheck('seller');
  const [formData, setFormData] = useState<ProductFormData>({
    name: '',
    description: '',
    product_type: 'resource',
    category: 'other',
    price: 0,
    tags: [],
    requirements: [],
    features: [],
    status: 'draft',
    visibility: 'public',
  });

  const [uploadedFiles, setUploadedFiles] = useState<UploadedFiles>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [tagInput, setTagInput] = useState('');
  const [requirementInput, setRequirementInput] = useState('');
  const [featureInput, setFeatureInput] = useState('');
  const [uploading, setUploading] = useState(false);

  const productTypes = ['course', 'template', 'bundle', 'resource', 'tool', 'consultation'];
  const categories = ['programming', 'design', 'business', 'marketing', 'education', 'health', 'other'];

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'price' || name === 'original_price' ? parseFloat(value) : value
    }));
  };

  const addTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tagInput.trim()]
      }));
      setTagInput('');
    }
  };

  const removeTag = (index: number) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter((_, i) => i !== index)
    }));
  };

  const addRequirement = () => {
    if (requirementInput.trim() && !formData.requirements.includes(requirementInput.trim())) {
      setFormData(prev => ({
        ...prev,
        requirements: [...prev.requirements, requirementInput.trim()]
      }));
      setRequirementInput('');
    }
  };

  const removeRequirement = (index: number) => {
    setFormData(prev => ({
      ...prev,
      requirements: prev.requirements.filter((_, i) => i !== index)
    }));
  };

  const addFeature = () => {
    if (featureInput.trim() && !formData.features.includes(featureInput.trim())) {
      setFormData(prev => ({
        ...prev,
        features: [...prev.features, featureInput.trim()]
      }));
      setFeatureInput('');
    }
  };

  const removeFeature = (index: number) => {
    setFormData(prev => ({
      ...prev,
      features: prev.features.filter((_, i) => i !== index)
    }));
  };

  const handleFileUpload = async (
    e: React.ChangeEvent<HTMLInputElement>,
    fileType: 'thumbnail' | 'content' | 'preview'
  ) => {
    if (!e.target.files || !e.target.files[0]) return;

    const file = e.target.files[0];
    setUploading(true);
    setError('');

    try {
      // First, create the product if it doesn't exist
      if (!router.query.productId) {
        const res = await fetch(
          `/api/session/v1x/seller/products`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(formData),
          }
        );

        if (res.ok) {
          const product = await res.json();
          // Redirect to edit page
          router.push(`/marketplace/seller/edit-product?productId=${product.id}`);
          return;
        }
      }

      // Upload file
      const formDataUpload = new FormData();
      formDataUpload.append('file', file);

      const uploadUrl = `/api/session/v1x/seller/products/${router.query.productId}/upload-${fileType}`;

      const uploadRes = await fetch(uploadUrl, {
        method: 'POST',
        credentials: 'include',
        body: formDataUpload,
      });

      if (uploadRes.ok) {
        const uploadData = await uploadRes.json();
        setUploadedFiles(prev => ({
          ...prev,
          [fileType]: uploadData[`${fileType}_url`]
        }));
        setSuccess(`${fileType} uploaded successfully!`);
        setTimeout(() => setSuccess(''), 3000);
      } else {
        const errorData = await uploadRes.json();
        setError(errorData.detail || `Failed to upload ${fileType}`);
      }
    } catch (err: any) {
      setError(err.message || `Error uploading ${fileType}`);
    } finally {
      setUploading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const submitData = {
        ...formData,
        thumbnail_url: uploadedFiles.thumbnail,
        content_url: uploadedFiles.content,
        preview_url: uploadedFiles.preview,
      };

      const url = router.query.productId
        ? `/api/session/v1x/seller/products/${router.query.productId}`
        : `/api/session/v1x/seller/products`;

      const res = await fetch(url, {
        method: router.query.productId ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(submitData),
      });

      if (res.ok) {
        setSuccess('Product saved successfully!');
        setTimeout(() => {
          router.push('/marketplace/seller/products');
        }, 1500);
      } else {
        const errorData = await res.json();
        setError(errorData.detail || 'Failed to save product');
      }
    } catch (err: any) {
      setError(err.message || 'Error saving product');
    } finally {
      setLoading(false);
    }
  };

  if (authLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">Loading...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (!isAuthorized) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 text-yellow-800 dark:text-yellow-200">
            You must be a seller to access this page. Please contact support if you need seller access.
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-white dark:bg-gray-900">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
            {router.query.productId ? 'Edit Product' : 'Create New Product'}
          </h1>

          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded-lg flex gap-3">
              <AlertCircle className="text-red-600 dark:text-red-400" size={20} />
              <p className="text-red-600 dark:text-red-400">{error}</p>
            </div>
          )}

          {success && (
            <div className="mb-6 p-4 bg-green-50 dark:bg-green-900 border border-green-200 dark:border-green-700 rounded-lg flex gap-3">
              <CheckCircle className="text-green-600 dark:text-green-400" size={20} />
              <p className="text-green-600 dark:text-green-400">{success}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Basic Information */}
            <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-lg">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Basic Information</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Product Name *
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter product name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Description *
                  </label>
                  <textarea
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    required
                    rows={5}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Describe your product in detail"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Product Type
                    </label>
                    <select
                      name="product_type"
                      value={formData.product_type}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {productTypes.map(type => (
                        <option key={type} value={type}>{type.charAt(0).toUpperCase() + type.slice(1)}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Category
                    </label>
                    <select
                      name="category"
                      value={formData.category}
                      onChange={handleInputChange}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {categories.map(cat => (
                        <option key={cat} value={cat}>{cat.charAt(0).toUpperCase() + cat.slice(1)}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            </div>

            {/* Pricing */}
            <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-lg">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Pricing</h2>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Price ($) *
                  </label>
                  <input
                    type="number"
                    name="price"
                    value={formData.price}
                    onChange={handleInputChange}
                    step="0.01"
                    min="0"
                    required
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="0.00"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Original Price ($)
                  </label>
                  <input
                    type="number"
                    name="original_price"
                    value={formData.original_price || ''}
                    onChange={handleInputChange}
                    step="0.01"
                    min="0"
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="For discount display"
                  />
                </div>
              </div>
            </div>

            {/* Files */}
            <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-lg">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Product Files</h2>

              {!router.query.productId && (
                <p className="text-amber-600 dark:text-amber-400 mb-4 flex gap-2">
                  <AlertCircle size={20} />
                  Save basic info first, then you can upload files
                </p>
              )}

              <div className="space-y-4 opacity-75">
                {/* Thumbnail */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Thumbnail Image {uploadedFiles.thumbnail && '✓'}
                  </label>
                  <div className="flex items-center gap-4">
                    <label className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700 disabled:opacity-50">
                      <Upload size={18} />
                      {uploading ? 'Uploading...' : 'Upload'}
                      <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => handleFileUpload(e, 'thumbnail')}
                        disabled={!router.query.productId || uploading}
                        className="hidden"
                      />
                    </label>
                    {uploadedFiles.thumbnail && (
                      <span className="text-sm text-green-600 dark:text-green-400">Uploaded</span>
                    )}
                  </div>
                </div>

                {/* Content */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Content File {uploadedFiles.content && '✓'}
                  </label>
                  <div className="flex items-center gap-4">
                    <label className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700 disabled:opacity-50">
                      <Upload size={18} />
                      {uploading ? 'Uploading...' : 'Upload'}
                      <input
                        type="file"
                        onChange={(e) => handleFileUpload(e, 'content')}
                        disabled={!router.query.productId || uploading}
                        className="hidden"
                      />
                    </label>
                    {uploadedFiles.content && (
                      <span className="text-sm text-green-600 dark:text-green-400">Uploaded</span>
                    )}
                  </div>
                </div>

                {/* Preview */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Preview File {uploadedFiles.preview && '✓'}
                  </label>
                  <div className="flex items-center gap-4">
                    <label className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700 disabled:opacity-50">
                      <Upload size={18} />
                      {uploading ? 'Uploading...' : 'Upload'}
                      <input
                        type="file"
                        onChange={(e) => handleFileUpload(e, 'preview')}
                        disabled={!router.query.productId || uploading}
                        className="hidden"
                      />
                    </label>
                    {uploadedFiles.preview && (
                      <span className="text-sm text-green-600 dark:text-green-400">Uploaded</span>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Tags */}
            <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-lg">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Tags</h2>

              <div className="flex gap-2 mb-4">
                <input
                  type="text"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Add a tag and press Enter"
                />
                <button
                  type="button"
                  onClick={addTag}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Add
                </button>
              </div>

              <div className="flex flex-wrap gap-2">
                {formData.tags.map((tag, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-200 rounded-full flex items-center gap-2"
                  >
                    {tag}
                    <X size={16} className="cursor-pointer" onClick={() => removeTag(idx)} />
                  </span>
                ))}
              </div>
            </div>

            {/* Requirements */}
            <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-lg">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Requirements</h2>

              <div className="flex gap-2 mb-4">
                <input
                  type="text"
                  value={requirementInput}
                  onChange={(e) => setRequirementInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addRequirement())}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Add a requirement"
                />
                <button
                  type="button"
                  onClick={addRequirement}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Add
                </button>
              </div>

              <ul className="space-y-2">
                {formData.requirements.map((req, idx) => (
                  <li
                    key={idx}
                    className="flex items-center justify-between p-2 bg-white dark:bg-gray-700 rounded border border-gray-200 dark:border-gray-600"
                  >
                    <span className="text-gray-900 dark:text-white">{req}</span>
                    <X
                      size={16}
                      className="cursor-pointer text-red-600 dark:text-red-400"
                      onClick={() => removeRequirement(idx)}
                    />
                  </li>
                ))}
              </ul>
            </div>

            {/* Features */}
            <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-lg">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Key Features</h2>

              <div className="flex gap-2 mb-4">
                <input
                  type="text"
                  value={featureInput}
                  onChange={(e) => setFeatureInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addFeature())}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Add a feature"
                />
                <button
                  type="button"
                  onClick={addFeature}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Add
                </button>
              </div>

              <ul className="space-y-2">
                {formData.features.map((feature, idx) => (
                  <li
                    key={idx}
                    className="flex items-center justify-between p-2 bg-white dark:bg-gray-700 rounded border border-gray-200 dark:border-gray-600"
                  >
                    <span className="text-gray-900 dark:text-white">✓ {feature}</span>
                    <X
                      size={16}
                      className="cursor-pointer text-red-600 dark:text-red-400"
                      onClick={() => removeFeature(idx)}
                    />
                  </li>
                ))}
              </ul>
            </div>

            {/* Status */}
            <div className="bg-gray-50 dark:bg-gray-800 p-6 rounded-lg">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Status</h2>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Status
                  </label>
                  <select
                    name="status"
                    value={formData.status}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="draft">Draft</option>
                    <option value="published">Published</option>
                    <option value="archived">Archived</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Visibility
                  </label>
                  <select
                    name="visibility"
                    value={formData.visibility}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="public">Public</option>
                    <option value="private">Private</option>
                    <option value="listed">Listed</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Submit */}
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={loading}
                className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
              >
                <Save size={20} />
                {loading ? 'Saving...' : 'Save Product'}
              </button>
              <button
                type="button"
                onClick={() => router.back()}
                className="px-6 py-3 bg-gray-300 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-400 dark:hover:bg-gray-600 font-medium"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </Layout>
  );
}
