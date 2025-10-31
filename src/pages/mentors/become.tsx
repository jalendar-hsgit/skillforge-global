import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import Card from '@/components/Card';
import Button from '@/components/Button';
import Input from '@/components/Input';
import { API_BASE } from '@/lib/apiBase';

interface EligibilityResponse {
  eligible: boolean;
  requirements: {
    completed_paths: number;
    quiz_average: number;
  };
  reasons?: string[];
}

export default function BecomeMentorPage() {
  const router = useRouter();
  
  const [loading, setLoading] = useState(false);
  const [checkingEligibility, setCheckingEligibility] = useState(true);
  const [eligibility, setEligibility] = useState<EligibilityResponse | null>(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // Form state
  const [bio, setBio] = useState('');
  const [expertise, setExpertise] = useState<string[]>([]);
  const [newExpertise, setNewExpertise] = useState('');
  const [hourlyRate, setHourlyRate] = useState<number>(40);

  const availableSkills = [
    'Python', 'JavaScript', 'TypeScript', 'React', 'Node.js',
    'FastAPI', 'Django', 'PostgreSQL', 'MongoDB', 'AWS',
    'Docker', 'Git', 'HTML/CSS', 'Next.js', 'Vue.js'
  ];

  useEffect(() => {
    checkEligibility();
  }, []);

  const checkEligibility = async () => {
    try {
      const response = await fetch(
        `${API_BASE}/api/v1x/mentors/eligibility`,
        { credentials: 'include' }
      );

      if (response.status === 401) {
        router.push('/login?redirect=/mentors/become');
        return;
      }

      if (!response.ok) throw new Error('Failed to check eligibility');

      const data = await response.json();
      setEligibility(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setCheckingEligibility(false);
    }
  };

  const toggleExpertise = (skill: string) => {
    if (expertise.includes(skill)) {
      setExpertise(expertise.filter(s => s !== skill));
    } else {
      setExpertise([...expertise, skill]);
    }
  };

  const addCustomExpertise = () => {
    if (newExpertise.trim() && !expertise.includes(newExpertise.trim())) {
      setExpertise([...expertise, newExpertise.trim()]);
      setNewExpertise('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (expertise.length === 0) {
      setError('Please select at least one area of expertise');
      return;
    }

    if (bio.length < 100) {
      setError('Bio must be at least 100 characters');
      return;
    }

    try {
      setLoading(true);
      setError('');

      const response = await fetch(`${API_BASE}/api/v1x/mentors/apply`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          bio,
          expertise,
          hourly_rate: hourlyRate
        })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to submit application');
      }

      setSuccess(true);
      setTimeout(() => {
        router.push('/mentors/dashboard');
      }, 2000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (checkingEligibility) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Checking eligibility...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white py-12">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Become a Mentor
            </h1>
            <p className="text-xl text-gray-600">
              Share your knowledge and help others on their learning journey
            </p>
          </div>

          {/* Eligibility Check */}
          {eligibility && !eligibility.eligible && (
            <Card className="mb-8 bg-yellow-50 border-yellow-200">
              <div className="flex items-start gap-4">
                <svg
                  className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-1"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
                <div>
                  <h3 className="text-lg font-semibold text-yellow-900 mb-2">
                    Not Eligible Yet
                  </h3>
                  <p className="text-yellow-800 mb-4">
                    To become a mentor, you need to:
                  </p>
                  <ul className="list-disc list-inside space-y-2 text-yellow-800">
                    {eligibility.reasons?.map((reason, index) => (
                      <li key={index}>{reason}</li>
                    ))}
                  </ul>
                  <div className="mt-4 pt-4 border-t border-yellow-300">
                    <p className="text-sm text-yellow-800">
                      Current Progress:
                    </p>
                    <ul className="mt-2 space-y-1 text-sm text-yellow-800">
                      <li>
                        ✓ Completed Paths: {eligibility.requirements.completed_paths}
                      </li>
                      <li>
                        ✓ Quiz Average: {eligibility.requirements.quiz_average.toFixed(1)}%
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </Card>
          )}

          {/* Success Message */}
          {success && (
            <Card className="mb-8 bg-green-50 border-green-200">
              <div className="flex items-center gap-4">
                <svg
                  className="w-8 h-8 text-green-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <div>
                  <h3 className="text-lg font-semibold text-green-900">
                    Application Submitted!
                  </h3>
                  <p className="text-green-800">
                    Your application is under review. We'll notify you soon.
                  </p>
                </div>
              </div>
            </Card>
          )}

          {/* Error Message */}
          {error && (
            <Card className="mb-8 bg-red-50 border-red-200">
              <p className="text-red-700">{error}</p>
            </Card>
          )}

          {/* Application Form */}
          {eligibility?.eligible && !success && (
            <Card>
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Bio */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tell us about yourself *
                  </label>
                  <textarea
                    value={bio}
                    onChange={(e) => setBio(e.target.value)}
                    rows={6}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Share your experience, teaching style, and what makes you a great mentor..."
                    required
                    minLength={100}
                  />
                  <p className="mt-1 text-sm text-gray-500">
                    {bio.length} / 100 characters minimum
                  </p>
                </div>

                {/* Expertise */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Areas of Expertise *
                  </label>
                  <div className="flex flex-wrap gap-2 mb-4">
                    {availableSkills.map(skill => (
                      <button
                        key={skill}
                        type="button"
                        onClick={() => toggleExpertise(skill)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                          expertise.includes(skill)
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {skill}
                      </button>
                    ))}
                  </div>

                  {/* Custom Expertise */}
                  <div className="flex gap-2">
                    <Input
                      type="text"
                      value={newExpertise}
                      onChange={(e) => setNewExpertise(e.target.value)}
                      placeholder="Add custom skill..."
                      className="flex-grow"
                    />
                    <Button
                      type="button"
                      onClick={addCustomExpertise}
                      variant="outline"
                    >
                      Add
                    </Button>
                  </div>

                  {/* Selected Expertise */}
                  {expertise.length > 0 && (
                    <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                      <p className="text-sm font-medium text-gray-700 mb-2">
                        Selected ({expertise.length}):
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {expertise.map(skill => (
                          <span
                            key={skill}
                            className="px-3 py-1 bg-blue-600 text-white rounded-full text-sm flex items-center gap-2"
                          >
                            {skill}
                            <button
                              type="button"
                              onClick={() => toggleExpertise(skill)}
                              className="hover:text-red-200"
                            >
                              ×
                            </button>
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Hourly Rate */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Hourly Rate (USD) *
                  </label>
                  <div className="flex items-center gap-4">
                    <span className="text-2xl font-bold text-gray-900">$</span>
                    <input
                      type="range"
                      min="20"
                      max="200"
                      step="5"
                      value={hourlyRate}
                      onChange={(e) => setHourlyRate(Number(e.target.value))}
                      className="flex-grow"
                    />
                    <span className="text-2xl font-bold text-blue-600 w-20">
                      ${hourlyRate}
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-gray-500">
                    Recommended: $30-$80 for beginners, $80-$150 for experienced mentors
                  </p>
                </div>

                {/* Submit Button */}
                <div className="pt-6 border-t border-gray-200">
                  <Button
                    type="submit"
                    variant="primary"
                    disabled={loading || expertise.length === 0 || bio.length < 100}
                    className="w-full"
                  >
                    {loading ? 'Submitting...' : 'Submit Application'}
                  </Button>
                </div>
              </form>
            </Card>
          )}

          {/* Requirements Info */}
          <Card className="mt-8 bg-blue-50 border-blue-200">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">
              Why These Requirements?
            </h3>
            <ul className="space-y-2 text-blue-800">
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold">✓</span>
                <span>
                  <strong>Completed Paths:</strong> Ensures you have comprehensive knowledge
                  in at least one area
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold">✓</span>
                <span>
                  <strong>80%+ Quiz Average:</strong> Demonstrates strong understanding
                  of the material you'll be teaching
                </span>
              </li>
            </ul>
          </Card>
        </div>
      </div>
    </Layout>
  );
}
