export default function MetricsPanel({ metrics }) {
  const statusColor = metrics.status === 'connected' ? 'bg-emerald-500' : metrics.status === 'error' ? 'bg-red-500' : 'bg-amber-500';

  return (
    <div className="bg-slate-800 rounded-lg shadow-lg overflow-hidden border border-slate-700 flex flex-col h-full">
      <div className="bg-gradient-to-r from-blue-700 to-blue-800 p-6 shadow-md">
        <h2 className="text-2xl font-bold text-white">Live Metrics</h2>
        <p className="text-blue-200 text-xs uppercase tracking-widest mt-2 opacity-80">Real-time from Prometheus</p>
      </div>

      <div className="flex-1 p-6 space-y-4 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-600 scrollbar-track-slate-800">
        <div className="bg-slate-700 rounded-lg p-5 border border-slate-600 shadow-md">
          <div className="flex flex-col gap-3">
            <span className="text-gray-300 text-sm font-semibold uppercase tracking-wider">System Status</span>
            <div className="flex items-center gap-2">
              <div className={`w-4 h-4 rounded-full ${statusColor} animate-pulse`}></div>
              <span className="text-xs font-semibold text-gray-100 uppercase">{metrics.status}</span>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-700 to-blue-800 rounded-lg p-6 shadow-md border border-blue-600/30">
          <p className="text-blue-200 text-xs uppercase tracking-widest font-semibold">Total Requests</p>
          <p className="text-5xl font-bold text-white mt-4">{metrics.requests}</p>
          <p className="text-blue-300 text-xs mt-4 opacity-80">📊 Real-time tracking</p>
        </div>

        <div className="space-y-3 pt-4">
          <a href="http://localhost:9090" target="_blank" rel="noopener noreferrer" className="block bg-amber-700 hover:bg-amber-800 text-white p-4 rounded-lg text-center text-xs font-semibold uppercase tracking-wider transition shadow-md">
            📊 Prometheus
          </a>
          <a href="http://localhost:3000" target="_blank" rel="noopener noreferrer" className="block bg-emerald-700 hover:bg-emerald-800 text-white p-4 rounded-lg text-center text-xs font-semibold uppercase tracking-wider transition shadow-md">
            📈 Grafana
          </a>
          <a href="http://localhost:16686" target="_blank" rel="noopener noreferrer" className="block bg-cyan-700 hover:bg-cyan-800 text-white p-4 rounded-lg text-center text-xs font-semibold uppercase tracking-wider transition shadow-md">
            🔗 Jaeger Traces
          </a>
        </div>
      </div>
    </div>
  );
}
