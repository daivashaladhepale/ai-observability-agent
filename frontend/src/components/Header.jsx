export default function Header() {
  return (
    <header className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 border-b border-slate-700 sticky top-0 z-50 shadow-lg backdrop-blur-sm">
      <div className="px-8 py-6 flex items-center justify-between">
        <div className="flex items-center gap-5">
          <div className="w-14 h-14 bg-gradient-to-br from-blue-600 to-blue-700 rounded-2xl flex items-center justify-center font-black text-white text-2xl shadow-md">
            ⚡
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-100">
              AI Observability Agent
            </h1>
            <p className="text-gray-400 text-xs uppercase tracking-widest font-semibold mt-1.5">Metrics • Traces • Intelligence</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <div className="px-5 py-3 bg-emerald-900/30 border border-emerald-700/50 rounded-full backdrop-blur-sm">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></div>
              <span className="text-xs font-semibold text-emerald-300 uppercase tracking-wider">Live • Prod Ready</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
