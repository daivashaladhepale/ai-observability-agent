import { useState, useEffect } from 'react';
import './index.css';
import ChatPanel from './components/ChatPanel';
import MetricsPanel from './components/MetricsPanel';
import Header from './components/Header';

function App() {
  const [metrics, setMetrics] = useState({
    requests: 0,
    avgLatency: 0,
    status: 'connecting'
  });

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/metrics', {
          headers: {
            'Accept': 'text/plain'
          }
        });
        const text = await response.text();
        
        const requestsMatch = text.match(/llm_requests_total\{.*?\}\s([\d.]+)/);
        setMetrics(prev => ({
          ...prev,
          requests: requestsMatch ? parseInt(requestsMatch[1]) : 0,
          status: 'connected'
        }));
      } catch (error) {
        console.error('Error fetching metrics:', error);
        setMetrics(prev => ({ ...prev, status: 'error' }));
      }
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-950 flex flex-col">
      <Header />
      <div className="flex-1 px-6 py-6 overflow-hidden">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-full">
          <div className="lg:col-span-3 flex flex-col">
            <ChatPanel />
          </div>
          
          <div className="lg:col-span-1 flex flex-col">
            <MetricsPanel metrics={metrics} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
