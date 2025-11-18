import { useEffect, useState } from "react";
import Head from "next/head";
import Link from "next/link";
import { API_BASE } from "@/lib/apiBase";

type Health = { status?: string } | null;

type Me = { id: string; email: string; full_name?: string } | null;

export default function StatusPage() {
  const [backend, setBackend] = useState<Health>(null);
  const [me, setMe] = useState<Me>(null);
  const [errors, setErrors] = useState<string[]>([]);

  useEffect(() => {
    const run = async () => {
      try {
        const r = await fetch(`${API_BASE}/healthz`, { credentials: "include" });
        const ok = r.ok;
        setBackend({ status: ok ? "ok" : `error:${r.status}` });
      } catch (e: any) {
        setErrors((prev) => [...prev, `Backend health error: ${e?.message || e}`]);
      }

      try {
        const r = await fetch("/api/session/me", { credentials: "include" });
        if (r.ok) setMe(await r.json());
        else setMe(null);
      } catch (e: any) {
        setErrors((prev) => [...prev, `Auth check error: ${e?.message || e}`]);
      }
    };
    run();
  }, []);

  return (
    <>
      <Head>
        <title>Status • SkillForge</title>
      </Head>
      <main className="min-h-screen px-6 py-10 max-w-3xl mx-auto">
        <h1 className="text-2xl font-semibold mb-4">System Status</h1>
        <div className="space-y-4">
          <section className="p-4 border rounded">
            <h2 className="font-medium mb-2">Frontend</h2>
            <ul className="text-sm list-disc pl-5">
              <li>Environment: {process.env.NODE_ENV}</li>
              <li>API Base: {API_BASE}</li>
            </ul>
          </section>

          <section className="p-4 border rounded">
            <h2 className="font-medium mb-2">Backend</h2>
            <p className="text-sm">Health: {backend?.status || "unknown"}</p>
          </section>

          <section className="p-4 border rounded">
            <h2 className="font-medium mb-2">Auth</h2>
            {me ? (
              <div className="text-sm">
                <div>User: {me.email}</div>
                {me.full_name && <div>Name: {me.full_name}</div>}
              </div>
            ) : (
              <div className="text-sm">Not authenticated</div>
            )}
          </section>

          {errors.length > 0 && (
            <section className="p-4 border rounded bg-yellow-50">
              <h2 className="font-medium mb-2">Notes</h2>
              <ul className="text-sm list-disc pl-5">
                {errors.map((e, i) => (
                  <li key={i}>{e}</li>
                ))}
              </ul>
            </section>
          )}

          <div className="pt-2">
            <Link href="/">
              <span className="text-blue-600 hover:underline">← Back to Home</span>
            </Link>
          </div>
        </div>
      </main>
    </>
  );
}
