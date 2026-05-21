import React, { useEffect } from "react";
import { useRouter } from "next/router";
import Layout from "@/components/Layout";

export default function GitHubCallback() {
  const router = useRouter();
  const { code, state, error } = router.query;

  useEffect(() => {
    if (error) {
      console.error("GitHub OAuth error:", error);
      router.push("/github-integration?error=" + error);
      return;
    }

    if (code) {
      // Send code to backend to exchange for access token
      const exchangeCode = async () => {
        try {
          const response = await fetch(
            `${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8001"}/api/v1x/github/connect`,
            {
              method: "POST",
              credentials: "include",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ code })
            }
          );
          
          if (response.ok) {
            // Redirect back to GitHub integration page
            router.push("/github-integration?success=true");
          } else {
            router.push("/github-integration?error=connection_failed");
          }
        } catch (error) {
          console.error("Failed to exchange GitHub code:", error);
          router.push("/github-integration?error=exchange_failed");
        }
      };

      exchangeCode();
    }
  }, [code, error, router]);

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 pt-20 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block">
            <div className="w-12 h-12 border-4 border-slate-700 border-t-blue-500 rounded-full animate-spin mb-4"></div>
          </div>
          <p className="text-white text-lg">Connecting your GitHub account...</p>
        </div>
      </div>
    </Layout>
  );
}
