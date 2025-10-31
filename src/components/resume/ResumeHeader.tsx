import { Input } from '@/components/Input';

interface Resume {
  full_name?: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin?: string;
  github?: string;
  website?: string;
}

interface ResumeHeaderProps {
  resume: Resume;
  updateResume: (updates: Partial<Resume>) => void;
}

export default function ResumeHeader({ resume, updateResume }: ResumeHeaderProps) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Header & Contact Information</h2>
        <p className="text-gray-600">
          Add your basic information and contact details that will appear at the top of your resume.
        </p>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Full Name <span className="text-red-500">*</span>
          </label>
          <Input
            type="text"
            value={resume.full_name || ''}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              updateResume({ full_name: e.target.value })
            }
            placeholder="John Doe"
            className="w-full"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email <span className="text-red-500">*</span>
            </label>
            <Input
              type="email"
              value={resume.email || ''}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                updateResume({ email: e.target.value })
              }
              placeholder="john.doe@example.com"
              className="w-full"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Phone
            </label>
            <Input
              type="tel"
              value={resume.phone || ''}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                updateResume({ phone: e.target.value })
              }
              placeholder="+1 (555) 123-4567"
              className="w-full"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Location
          </label>
          <Input
            type="text"
            value={resume.location || ''}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
              updateResume({ location: e.target.value })
            }
            placeholder="San Francisco, CA"
            className="w-full"
          />
        </div>

        <div className="border-t border-gray-200 pt-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Links (Optional)</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                LinkedIn Profile
              </label>
              <Input
                type="url"
                value={resume.linkedin || ''}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  updateResume({ linkedin: e.target.value })
                }
                placeholder="https://linkedin.com/in/johndoe"
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                GitHub Profile
              </label>
              <Input
                type="url"
                value={resume.github || ''}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  updateResume({ github: e.target.value })
                }
                placeholder="https://github.com/johndoe"
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Personal Website/Portfolio
              </label>
              <Input
                type="url"
                value={resume.website || ''}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  updateResume({ website: e.target.value })
                }
                placeholder="https://johndoe.com"
                className="w-full"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex gap-3">
          <span className="text-2xl">💡</span>
          <div>
            <h4 className="font-semibold text-blue-900 mb-1">Pro Tips:</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Use a professional email address</li>
              <li>• Include your city and state (no full address needed)</li>
              <li>• Make sure your LinkedIn profile is complete and up-to-date</li>
              <li>• Only add links that showcase your professional work</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
