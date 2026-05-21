import Link from "next/link";

export default function NotFoundPage() {
  return (
    <main className="min-h-screen flex items-center justify-center p-8">
      <div className="max-w-md text-center">
        <h1 className="text-4xl font-bold mb-2">404</h1>
        <p className="text-gray-600 mb-6">We couldn't find that page.</p>
        <Link href="/">
          <span className="inline-block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Go Home</span>
        </Link>
      </div>
    </main>
  );
}
