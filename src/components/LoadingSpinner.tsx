// src/components/LoadingSpinner.tsx
export function LoadingSpinner({ message = "Loading..." }: { message?: string }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 mb-4 bg-blue-100 rounded-full">
          <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
        </div>
        <p className="text-gray-600 text-lg font-medium">{message}</p>
      </div>
    </div>
  )
}
