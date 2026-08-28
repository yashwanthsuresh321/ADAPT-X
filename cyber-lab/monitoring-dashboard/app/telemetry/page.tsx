"use client";

import { useEffect, useState } from "react";
import { format } from "date-fns";
import { Activity, Search, Server, Network } from "lucide-react";

export default function TelemetryExplorer() {
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Filters
  const [source, setSource] = useState("");
  const [eventType, setEventType] = useState("");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [meta, setMeta] = useState<any>(null);

  const fetchTelemetry = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (source) params.append("source", source);
      if (eventType) params.append("event_type", eventType);
      if (search) params.append("search", search);
      params.append("page", page.toString());
      params.append("limit", "50");
      
      const res = await fetch(`/api/telemetry?${params.toString()}`);
      const data = await res.json();
      setEvents(data.data || []);
      setMeta(data.meta);
    } catch (error) {
      console.error("Failed to fetch telemetry", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTelemetry();
  }, [source, eventType, page]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchTelemetry();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Telemetry Explorer</h2>
          <p className="text-sm text-slate-400">Raw and normalized lab activity</p>
        </div>
      </div>

      <div className="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4 bg-slate-900 p-4 rounded-lg border border-slate-800">
        <form onSubmit={handleSearch} className="flex-1 flex">
          <div className="relative w-full max-w-md">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
            <input 
              type="text" 
              placeholder="Search IP, action, resource..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 w-full bg-slate-950 border border-slate-800 rounded-md px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
          <button type="submit" className="ml-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-sm font-medium rounded-md transition-colors">
            Search
          </button>
        </form>

        <div className="flex space-x-4">
          <select 
            value={source} 
            onChange={e => { setSource(e.target.value); setPage(1); }}
            className="bg-slate-950 border border-slate-800 rounded-md px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">All Sources</option>
            <option value="cowrie">Cowrie Honeypot</option>
            <option value="docker">Docker Logs</option>
          </select>

          <select 
            value={eventType} 
            onChange={e => { setEventType(e.target.value); setPage(1); }}
            className="bg-slate-950 border border-slate-800 rounded-md px-3 py-2 text-sm text-slate-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">All Types</option>
            <option value="auth_attempt">Auth Attempt</option>
            <option value="network_connection">Network Connection</option>
            <option value="command_execution">Command Execution</option>
            <option value="file_download">File Download</option>
          </select>
        </div>
      </div>

      <div className="border border-slate-800 rounded-lg overflow-hidden bg-slate-900">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950/50 text-slate-400 border-b border-slate-800 uppercase text-xs font-semibold">
              <tr>
                <th className="px-4 py-3">Timestamp</th>
                <th className="px-4 py-3">Source</th>
                <th className="px-4 py-3">Event Type</th>
                <th className="px-4 py-3">Source IP</th>
                <th className="px-4 py-3">Dest IP</th>
                <th className="px-4 py-3">Action</th>
                <th className="px-4 py-3">Resource</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50 font-mono text-xs">
              {loading ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-slate-400 font-sans">Loading telemetry...</td>
                </tr>
              ) : events.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-slate-400 font-sans">No telemetry events match the selected filters.</td>
                </tr>
              ) : (
                events.map((event) => (
                  <tr key={event.event_id} className="hover:bg-slate-800/50 transition-colors">
                    <td className="px-4 py-3 text-slate-400">{format(new Date(event.timestamp), 'yyyy-MM-dd HH:mm:ss')}</td>
                    <td className="px-4 py-3 text-slate-300">
                      <span className="flex items-center">
                        {event.source === 'cowrie' ? <Server className="h-3 w-3 mr-1 text-orange-400" /> : <Activity className="h-3 w-3 mr-1 text-blue-400" />}
                        {event.source}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-blue-400">{event.event_type}</td>
                    <td className="px-4 py-3 text-slate-300">{event.source_ip || '-'}</td>
                    <td className="px-4 py-3 text-slate-300">{event.destination_ip || '-'}</td>
                    <td className="px-4 py-3 text-slate-300">{event.action || '-'}</td>
                    <td className="px-4 py-3 text-slate-400 truncate max-w-[200px]" title={event.resource || ''}>{event.resource || '-'}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full bg-slate-950 border ${
                        event.status === 'success' ? 'border-emerald-500/30 text-emerald-400' : 
                        event.status === 'failed' ? 'border-rose-500/30 text-rose-400' : 
                        'border-slate-500/30 text-slate-400'
                      }`}>
                        {event.status || 'unknown'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        
        {/* Pagination */}
        {meta && meta.pages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 bg-slate-950 border-t border-slate-800">
            <div className="text-sm text-slate-400 font-mono">
              Page {meta.page} of {meta.pages} <span className="mx-2">|</span> {meta.total} total events
            </div>
            <div className="flex space-x-2">
              <button 
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="px-3 py-1 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-sm rounded transition-colors"
              >
                Previous
              </button>
              <button 
                onClick={() => setPage(Math.min(meta.pages, page + 1))}
                disabled={page === meta.pages}
                className="px-3 py-1 bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-sm rounded transition-colors"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
