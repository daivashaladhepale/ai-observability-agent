import { useState } from 'react';

export default function ChatPanel() {
  const [messages, setMessages] = useState([
    { id: 1, text: 'Hey there! 👋 Ask me anything , or what\'s on your mind!', sender: 'agent', timestamp: new Date() }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      text: input,
      sender: 'user',
      timestamp: new Date()
    };
    setMessages([...messages, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch(`http://127.0.0.1:8000/chat?q=${encodeURIComponent(input)}`);
      const data = await response.json();

      const agentMessage = {
        id: messages.length + 2,
        text: data.response,
        sender: 'agent',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, agentMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        id: messages.length + 2,
        text: 'Oops! Let me think about that... could you try again?',
        sender: 'agent',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-800 rounded-lg shadow-lg overflow-hidden border border-slate-700 flex flex-col h-full">
      <div className="bg-gradient-to-r from-blue-700 to-blue-800 p-6 shadow-md">
        <h2 className="text-2xl font-bold text-white">Chat with AI Agent</h2>
        <p className="text-blue-200 text-xs uppercase tracking-widest mt-2 opacity-80">Fully instrumented with observability</p>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-750" style={{scrollbarWidth: 'thin'}}>
        {messages.map(msg => (
          <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-md px-5 py-4 rounded-lg ${ 
              msg.sender === 'user'
                ? 'bg-blue-700 text-white rounded-br-none shadow-md'
                : 'bg-slate-700 text-white rounded-bl-none shadow-md'
            }`}>
              <p className="text-sm leading-relaxed font-medium">{msg.text}</p>
              <span className="text-xs opacity-70 mt-3 block">
                {msg.timestamp.toLocaleTimeString()}
              </span>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-700 text-white px-5 py-4 rounded-lg rounded-bl-none shadow-md">
              <div className="flex space-x-3">
                <div className="w-3 h-3 bg-white rounded-full animate-bounce"></div>
                <div className="w-3 h-3 bg-white rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                <div className="w-3 h-3 bg-white rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      <form onSubmit={sendMessage} className="p-6 border-t border-slate-700 bg-slate-750 backdrop-blur-sm">
        <div className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me anything..."
            disabled={loading}
            className="flex-1 px-5 py-3 bg-slate-700 text-white placeholder-slate-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 focus:ring-offset-0 disabled:opacity-50 border border-slate-600 transition"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-8 py-3 bg-blue-700 hover:bg-blue-800 text-white rounded-lg font-semibold disabled:opacity-50 transition shadow-md"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}
