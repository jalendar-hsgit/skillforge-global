import { useState, useEffect } from 'react';
import Layout from '@/components/Layout';
import { Button } from '@/components/Button';
import { User, Mail, Phone, MapPin, Building2, FileText, Save, Camera, AlertCircle } from 'lucide-react';
import { useRouter } from 'next/router';

interface SellerProfile {
  id: number;
  user_id: number;
  email: string;
  name: string;
  store_name: string;
  store_description: string;
  store_logo_url?: string;
  store_banner_url?: string;
  phone: string;
  address: string;
  city: string;
  state: string;
  country: string;
  zip_code: string;
  business_name: string;
  business_registration?: string;
  tax_id?: string;
  bank_account_name?: string;
  bank_account_number?: string;
  bank_routing_number?: string;
  return_policy?: string;
  shipping_info?: string;
  verification_status: string;
  is_verified: boolean;
  total_products: number;
  total_sales: number;
  total_revenue: number;
  average_rating: number;
  created_at: string;
}

export default function SellerAccountPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [profile, setProfile] = useState<SellerProfile | null>(null);
  const [formData, setFormData] = useState<Partial<SellerProfile>>({});
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [activeTab, setActiveTab] = useState('profile');

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/seller/profile`,
        {
          credentials: 'include',
        }
      );

      if (response.status === 401) {
        router.push('/auth/login?redirect=/marketplace/seller/account');
        return;
      }

      if (!response.ok) {
        setError('Failed to load seller profile');
        return;
      }

      const data = await response.json();
      setProfile(data);
      setFormData(data);
    } catch (error) {
      console.error('Error fetching profile:', error);
      setError('Error loading profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage('');
    setError('');

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || ''}/api/v1x/marketplace/seller/profile`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify(formData),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        setError(errorData.detail || 'Failed to save profile');
        return;
      }

      const updatedProfile = await response.json();
      setProfile(updatedProfile);
      setEditMode(false);
      setMessage('Profile updated successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Error saving profile:', error);
      setError('Error saving profile. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-slate-900 mb-2">Seller Account</h1>
            <p className="text-slate-600">Manage your seller profile, store information, and business settings</p>
          </div>

          {/* Messages */}
          {message && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700 flex items-center gap-2">
              <AlertCircle size={20} />
              {message}
            </div>
          )}

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 flex items-center gap-2">
              <AlertCircle size={20} />
              {error}
            </div>
          )}

          {/* Tabs */}
          <div className="flex gap-4 mb-8 border-b border-slate-200">
            <button
              onClick={() => setActiveTab('profile')}
              className={`px-4 py-3 font-medium border-b-2 transition ${
                activeTab === 'profile'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              <User size={20} className="inline mr-2" />
              Profile
            </button>
            <button
              onClick={() => setActiveTab('store')}
              className={`px-4 py-3 font-medium border-b-2 transition ${
                activeTab === 'store'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              <Building2 size={20} className="inline mr-2" />
              Store Info
            </button>
            <button
              onClick={() => setActiveTab('business')}
              className={`px-4 py-3 font-medium border-b-2 transition ${
                activeTab === 'business'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              <FileText size={20} className="inline mr-2" />
              Business
            </button>
            <button
              onClick={() => setActiveTab('banking')}
              className={`px-4 py-3 font-medium border-b-2 transition ${
                activeTab === 'banking'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-slate-600 hover:text-slate-900'
              }`}
            >
              💳 Banking
            </button>
          </div>

          {/* Profile Content */}
          {profile && (
            <div className="bg-white rounded-lg shadow-md p-8">
              {/* Profile Tab */}
              {activeTab === 'profile' && (
                <div className="space-y-6">
                  <div className="flex items-center gap-6 mb-8">
                    <div className="w-24 h-24 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center text-white text-4xl">
                      {profile.store_logo_url ? (
                        <img
                          src={profile.store_logo_url}
                          alt="Logo"
                          className="w-full h-full rounded-full object-cover"
                        />
                      ) : (
                        <User size={48} />
                      )}
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-slate-900">{profile.store_name || profile.name}</h2>
                      <p className="text-slate-600">Seller ID: {profile.id}</p>
                      <p className={`text-sm font-medium mt-2 ${profile.is_verified ? 'text-green-600' : 'text-yellow-600'}`}>
                        {profile.is_verified ? '✓ Verified' : '⏳ Pending Verification'}
                      </p>
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <p className="text-sm text-slate-600 mb-1">Total Products</p>
                      <p className="text-2xl font-bold text-blue-600">{profile.total_products}</p>
                    </div>
                    <div className="bg-green-50 p-4 rounded-lg">
                      <p className="text-sm text-slate-600 mb-1">Total Sales</p>
                      <p className="text-2xl font-bold text-green-600">{profile.total_sales}</p>
                    </div>
                    <div className="bg-purple-50 p-4 rounded-lg">
                      <p className="text-sm text-slate-600 mb-1">Revenue</p>
                      <p className="text-2xl font-bold text-purple-600">${profile.total_revenue?.toFixed(2) || '0.00'}</p>
                    </div>
                    <div className="bg-yellow-50 p-4 rounded-lg">
                      <p className="text-sm text-slate-600 mb-1">Rating</p>
                      <p className="text-2xl font-bold text-yellow-600">{profile.average_rating?.toFixed(1) || 'N/A'}</p>
                    </div>
                  </div>

                  {/* Personal Info Form */}
                  <div className="border-t pt-6">
                    <h3 className="text-lg font-bold text-slate-900 mb-4">Personal Information</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2 flex items-center gap-2">
                          <User size={16} /> Full Name
                        </label>
                        <input
                          type="text"
                          name="name"
                          value={formData.name || ''}
                          onChange={handleInputChange}
                          disabled={!editMode}
                          className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2 flex items-center gap-2">
                          <Mail size={16} /> Email
                        </label>
                        <input
                          type="email"
                          name="email"
                          value={formData.email || ''}
                          disabled
                          className="w-full px-4 py-2 border border-slate-300 rounded-lg bg-slate-100 cursor-not-allowed"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2 flex items-center gap-2">
                          <Phone size={16} /> Phone
                        </label>
                        <input
                          type="tel"
                          name="phone"
                          value={formData.phone || ''}
                          onChange={handleInputChange}
                          disabled={!editMode}
                          className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2 flex items-center gap-2">
                          <MapPin size={16} /> Country
                        </label>
                        <input
                          type="text"
                          name="country"
                          value={formData.country || ''}
                          onChange={handleInputChange}
                          disabled={!editMode}
                          className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Store Tab */}
              {activeTab === 'store' && (
                <div className="space-y-6">
                  <h3 className="text-lg font-bold text-slate-900">Store Information</h3>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Store Name</label>
                    <input
                      type="text"
                      name="store_name"
                      value={formData.store_name || ''}
                      onChange={handleInputChange}
                      disabled={!editMode}
                      className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Store Description</label>
                    <textarea
                      name="store_description"
                      value={formData.store_description || ''}
                      onChange={handleInputChange}
                      disabled={!editMode}
                      rows={4}
                      className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Return Policy</label>
                    <textarea
                      name="return_policy"
                      value={formData.return_policy || ''}
                      onChange={handleInputChange}
                      disabled={!editMode}
                      rows={3}
                      className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Shipping Information</label>
                    <textarea
                      name="shipping_info"
                      value={formData.shipping_info || ''}
                      onChange={handleInputChange}
                      disabled={!editMode}
                      rows={3}
                      className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
                    />
                  </div>
                </div>
              )}

              {/* Business Tab */}
              {activeTab === 'business' && (
                <div className="space-y-6">
                  <h3 className="text-lg font-bold text-slate-900">Business Information</h3>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Business Name</label>
                    <input
                      type="text"
                      name="business_name"
                      value={formData.business_name || ''}
                      onChange={handleInputChange}
                      disabled={!editMode}
                      className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Business Registration Number</label>
                    <input
                      type="text"
                      name="business_registration"
                      value={formData.business_registration || ''}
                      onChange={handleInputChange}
                      disabled={!editMode}
                      className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Tax ID</label>
                    <input
                      type="text"
                      name="tax_id"
                      value={formData.tax_id || ''}
                      onChange={handleInputChange}
                      disabled={!editMode}
                      className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-2">City</label>
                      <input
                        type="text"
                        name="city"
                        value={formData.city || ''}
                        onChange={handleInputChange}
                        disabled={!editMode}
                        className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-2">State</label>
                      <input
                        type="text"
                        name="state"
                        value={formData.state || ''}
                        onChange={handleInputChange}
                        disabled={!editMode}
                        className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-2">ZIP Code</label>
                      <input
                        type="text"
                        name="zip_code"
                        value={formData.zip_code || ''}
                        onChange={handleInputChange}
                        disabled={!editMode}
                        className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-2">Address</label>
                      <input
                        type="text"
                        name="address"
                        value={formData.address || ''}
                        onChange={handleInputChange}
                        disabled={!editMode}
                        className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
                      />
                    </div>
                  </div>
                </div>
              )}

              {/* Banking Tab */}
              {activeTab === 'banking' && (
                <div className="space-y-6">
                  <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 mb-6">
                    <p className="text-blue-700 text-sm">
                      🔒 Bank information is encrypted and secure. Your details are used only for payouts.
                    </p>
                  </div>

                  <h3 className="text-lg font-bold text-slate-900">Bank Account Information</h3>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Account Holder Name</label>
                    <input
                      type="text"
                      name="bank_account_name"
                      value={formData.bank_account_name || ''}
                      onChange={handleInputChange}
                      disabled={!editMode}
                      className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Account Number</label>
                    <input
                      type="password"
                      name="bank_account_number"
                      value={formData.bank_account_number || ''}
                      onChange={handleInputChange}
                      disabled={!editMode}
                      className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Routing Number</label>
                    <input
                      type="password"
                      name="bank_routing_number"
                      value={formData.bank_routing_number || ''}
                      onChange={handleInputChange}
                      disabled={!editMode}
                      className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 disabled:bg-slate-100"
                    />
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-4 mt-8 border-t pt-6">
                {!editMode ? (
                  <Button
                    onClick={() => setEditMode(true)}
                    className="flex items-center gap-2"
                  >
                    Edit Profile
                  </Button>
                ) : (
                  <>
                    <Button
                      onClick={handleSave}
                      disabled={saving}
                      className="flex items-center gap-2 bg-green-600 hover:bg-green-700"
                    >
                      <Save size={18} />
                      {saving ? 'Saving...' : 'Save Changes'}
                    </Button>
                    <Button
                      onClick={() => {
                        setEditMode(false);
                        setFormData(profile);
                      }}
                      variant="outline"
                    >
                      Cancel
                    </Button>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
