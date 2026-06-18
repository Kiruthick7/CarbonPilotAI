import Image from "next/image";
import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col text-slate-900 font-sans selection:bg-emerald-200">
      <header className="px-8 py-6 flex justify-between items-center bg-white/80 backdrop-blur-md sticky top-0 z-50 border-b border-slate-200/50">
        <div className="flex items-center gap-2">
          <Image src="/logo.png" unoptimized width={48} height={48} alt="CarbonPilot Logo" className="w-10 h-10 object-contain drop-shadow-md" />
          <div className="text-2xl font-black tracking-tight text-slate-800">CarbonPilot <span className="text-emerald-500">AI</span></div>
        </div>
        <Link href="/onboarding" className="bg-slate-900 text-white px-6 py-2.5 rounded-full font-semibold text-sm hover:bg-slate-800 transition-all shadow-sm hover:shadow-md">Get Started</Link>
      </header>
      
      <main className="flex-1 flex flex-col items-center justify-center text-center px-4 py-32 relative overflow-hidden">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-emerald-400/10 rounded-full blur-[100px] -z-10 pointer-events-none" />
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-blue-400/10 rounded-full blur-[80px] -z-10 pointer-events-none" />

        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-100/50 text-emerald-700 text-sm font-semibold mb-8 border border-emerald-200/50">
          <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
          Privacy-First Local Processing
        </div>

        <h1 className="text-6xl md:text-7xl font-black tracking-tight mb-8 max-w-5xl leading-[1.1] text-slate-900">
          A Local-First <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-500 to-teal-400">Sustainability</span> Intelligence Platform.
        </h1>
        <p className="text-xl md:text-2xl text-slate-500 max-w-3xl mb-12 leading-relaxed">
          Stop guessing your carbon footprint. Upload your utility bills, get deterministic action plans, and simulate your path to Net Zero with AI Copilot guidance.
        </p>
        <div className="flex gap-4 items-center">
          <Link href="/onboarding" className="bg-emerald-500 text-white px-10 py-5 rounded-full text-lg font-bold hover:bg-emerald-600 transition-all shadow-xl shadow-emerald-500/20 hover:shadow-emerald-500/40 hover:-translate-y-1 transform">
            Start Your Assessment
          </Link>
          <a href="#features" className="px-10 py-5 rounded-full text-lg font-bold text-slate-600 hover:bg-slate-100 transition-colors">
            Learn More
          </a>
        </div>
      </main>

      <section id="features" className="bg-white py-24 border-t border-slate-100">
        <div className="max-w-6xl mx-auto px-8">
          <h2 className="text-3xl font-bold text-center mb-16">How CarbonPilot Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12 text-left">
            <div className="p-8 rounded-3xl bg-slate-50 border border-slate-100 hover:shadow-xl hover:shadow-slate-200/50 transition-all group">
                <div className="w-14 h-14 bg-white rounded-2xl flex items-center justify-center shadow-sm mb-6 border border-slate-100 group-hover:scale-110 transition-transform">
                  <svg className="w-6 h-6 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
                </div>
                <h3 className="text-2xl font-bold mb-4 text-slate-800">Privacy First OCR</h3>
                <p className="text-slate-500 leading-relaxed">Your personal information never leaves your device. We extract utility data entirely locally using browser-safe OCR.</p>
            </div>
            <div className="p-8 rounded-3xl bg-slate-50 border border-slate-100 hover:shadow-xl hover:shadow-slate-200/50 transition-all group">
                <div className="w-14 h-14 bg-white rounded-2xl flex items-center justify-center shadow-sm mb-6 border border-slate-100 group-hover:scale-110 transition-transform">
                  <svg className="w-6 h-6 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" /></svg>
                </div>
                <h3 className="text-2xl font-bold mb-4 text-slate-800">Deterministic Engine</h3>
                <p className="text-slate-500 leading-relaxed">No AI hallucinations. We use strict, transparent math to calculate exact ROI and real-world carbon reduction potential.</p>
            </div>
            <div className="p-8 rounded-3xl bg-slate-50 border border-slate-100 hover:shadow-xl hover:shadow-slate-200/50 transition-all group">
                <div className="w-14 h-14 bg-white rounded-2xl flex items-center justify-center shadow-sm mb-6 border border-slate-100 group-hover:scale-110 transition-transform">
                  <svg className="w-6 h-6 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" /></svg>
                </div>
                <h3 className="text-2xl font-bold mb-4 text-slate-800">AI Context Copilot</h3>
                <p className="text-slate-500 leading-relaxed">Have questions about an action? Our embedded Copilot synthesizes local constraints and guides you step-by-step.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
