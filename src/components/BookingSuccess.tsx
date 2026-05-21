import { useRouter } from 'next/router';
import { Button } from './Button';
import { Card } from './Card';

export interface BookingSuccessProps {
  sessionId: number;
  mentorName: string;
  scheduledAt: string;
  topic: string;
  price: number;
}

export function BookingSuccess({
  sessionId,
  mentorName,
  scheduledAt,
  topic,
  price
}: BookingSuccessProps) {
  const router = useRouter();

  const date = new Date(scheduledAt);
  const formattedDate = date.toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  });
  const formattedTime = date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  });

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-blue-50">
      <Card className="max-w-md w-full mx-4 text-center space-y-6 p-8">
        {/* Success Icon */}
        <div className="flex justify-center">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center">
            <svg className="w-12 h-12 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        </div>

        <h2 className="text-3xl font-bold text-gray-900">Booking Confirmed!</h2>

        <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg space-y-3">
          <div className="text-left">
            <p className="text-sm text-gray-600">Mentor</p>
            <p className="font-semibold text-gray-900">{mentorName}</p>
          </div>
          <hr className="border-blue-200" />
          <div className="text-left">
            <p className="text-sm text-gray-600">Topic</p>
            <p className="font-semibold text-gray-900">{topic}</p>
          </div>
          <hr className="border-blue-200" />
          <div className="text-left">
            <p className="text-sm text-gray-600">Date & Time</p>
            <p className="font-semibold text-gray-900">{formattedDate}</p>
            <p className="font-semibold text-gray-900 text-lg text-blue-600">{formattedTime}</p>
          </div>
          <hr className="border-blue-200" />
          <div className="text-left">
            <p className="text-sm text-gray-600">Session Cost</p>
            <p className="font-bold text-2xl text-blue-600">${price.toFixed(2)}</p>
          </div>
          <hr className="border-blue-200" />
          <div className="text-left bg-yellow-50 p-2 rounded">
            <p className="text-xs text-gray-600">Session ID</p>
            <p className="font-mono text-sm text-gray-900">{sessionId}</p>
          </div>
        </div>

        <div className="space-y-3 pt-4">
          <p className="text-gray-600 text-sm">
            A confirmation email has been sent to your email address with all the details.
          </p>

          <p className="text-sm text-blue-600 font-medium">
            The mentor will review your booking and confirm within 24 hours.
          </p>

          <div className="grid grid-cols-2 gap-3">
            <Button
              onClick={() => router.push('/mentors')}
              className="bg-gray-200 hover:bg-gray-300 text-gray-900 font-medium py-2 px-4 rounded-md transition-colors"
            >
              Back to Mentors
            </Button>
            <Button
              onClick={() => router.push('/dashboard')}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition-colors"
            >
              Go to Dashboard
            </Button>
          </div>
        </div>

        <hr className="border-gray-200" />

        <p className="text-xs text-gray-500">
          You can view and manage your bookings in your dashboard or navigate to your profile page.
        </p>
      </Card>
    </div>
  );
}
