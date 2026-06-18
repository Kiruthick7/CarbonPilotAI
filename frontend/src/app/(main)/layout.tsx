"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { TrustModal } from "@/components/TrustModal";

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [isTrustModalOpen, setIsTrustModalOpen] = useState(false);

  const getLinkClass = (path: string) => {
    const isActive = pathname === path;
    return `p-3 rounded-lg font-medium transition-colors ${
      isActive ? "bg-green-100 text-green-800" : "hover:bg-gray-100"
    }`;
  };

  return (
    <div className="flex h-screen bg-gray-50 text-gray-900 overflow-hidden">
      <aside className="hidden md:flex w-64 bg-white border-r shadow-sm relative flex-col">
        <div className="p-6">
          <Link href="/">
            <div className="flex items-center gap-2 cursor-pointer group">
              <Image
                src="/logo.png"
                unoptimized
                width={36}
                height={36}
                alt="CarbonPilot Logo"
                className="w-9 h-9 object-contain drop-shadow-sm"
              />
              <h1 className="text-2xl font-bold text-green-600 group-hover:text-green-700 transition-colors">
                CarbonPilot AI
              </h1>
            </div>
          </Link>
        </div>
        <nav className="mt-6 flex flex-col space-y-2 px-4">
          <Link href="/dashboard" className={getLinkClass("/dashboard")}>
            Dashboard
          </Link>
          <Link href="/actions" className={getLinkClass("/actions")}>
            Action Plan
          </Link>
          <Link href="/simulator" className={getLinkClass("/simulator")}>
            Ask the AI
          </Link>
          <Link href="/" className={getLinkClass("/")}>
            Exit
          </Link>
        </nav>

        <div className="absolute bottom-6 left-6 right-6">
          <button
            onClick={() => setIsTrustModalOpen(true)}
            className="w-full flex items-center justify-center gap-2 p-3 text-sm font-semibold text-emerald-700 bg-emerald-50 rounded-xl hover:bg-emerald-100 transition-colors"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
              />
            </svg>
            Trust & Privacy
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto p-4 md:p-8 pb-24 md:pb-8">
        {children}
      </main>

      <TrustModal
        isOpen={isTrustModalOpen}
        onClose={() => setIsTrustModalOpen(false)}
      />

      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)] z-50 flex justify-around items-center p-2 pb-safe">
        <Link
          href="/"
          className={`flex flex-col items-center p-2 rounded-lg transition-colors ${pathname === "/" ? "text-emerald-600" : "text-gray-500 hover:bg-gray-50"}`}
        >
          <svg
            className="w-6 h-6 mb-1"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
            />
          </svg>
          <span className="text-[10px] font-bold">Exit</span>
        </Link>
        <Link
          href="/dashboard"
          className={`flex flex-col items-center p-2 rounded-lg transition-colors ${pathname === "/dashboard" ? "text-emerald-600" : "text-gray-500 hover:bg-gray-50"}`}
        >
          <svg
            className="w-6 h-6 mb-1"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
            />
          </svg>
          <span className="text-[10px] font-bold">Dashboard</span>
        </Link>
        <Link
          href="/actions"
          className={`flex flex-col items-center p-2 rounded-lg transition-colors ${pathname === "/actions" ? "text-emerald-600" : "text-gray-500 hover:bg-gray-50"}`}
        >
          <svg
            className="w-6 h-6 mb-1"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
            />
          </svg>
          <span className="text-[10px] font-bold">Actions</span>
        </Link>
        <Link
          href="/simulator"
          className={`flex flex-col items-center p-2 rounded-lg transition-colors ${pathname === "/simulator" ? "text-emerald-600" : "text-gray-500 hover:bg-gray-50"}`}
        >
          <svg
            className="w-6 h-6 mb-1"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 10V3L4 14h7v7l9-11h-7z"
            />
          </svg>
          <span className="text-[10px] font-bold">Simulator</span>
        </Link>
        <button
          onClick={() => setIsTrustModalOpen(true)}
          className={`flex flex-col items-center p-2 rounded-lg transition-colors text-gray-500 hover:bg-gray-50`}
        >
          <svg
            className="w-6 h-6 mb-1"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
            />
          </svg>
          <span className="text-[10px] font-bold">Trust</span>
        </button>
      </nav>

      <div className="fixed bottom-6 right-6 w-80 h-96 bg-white rounded-2xl shadow-2xl border flex-col overflow-hidden hidden">
        <div className="bg-green-600 text-white p-4 font-bold">AI Copilot</div>
        <div className="flex-1 p-4 bg-gray-50 overflow-y-auto">
          <div className="text-sm text-gray-600">
            How can I help you optimize your footprint today?
          </div>
        </div>
        <div className="p-3 bg-white border-t">
          <input
            type="text"
            placeholder="Ask anything..."
            className="w-full border rounded p-2 text-sm"
          />
        </div>
      </div>
    </div>
  );
}
