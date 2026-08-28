"use client";

import { useEffect, useState } from "react";
import { formatDistanceToNow, format } from "date-fns";
import Link from "next/link";
import { AlertTriangle, ChevronRight, ShieldAlert, AlertCircle, Info, RefreshCw } from "lucide-react";

export default function AlertQueue() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Filters
  const [severity, setSeverity] = useState("");
  const [status, setStatus] = useState("NEW");

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (severity) params.append("severity", severity);
      if (status) params.append("status", status);
      
      const res = await fetch(`/api/alerts?${params.toString()}`);
      const data = await res.json();
      setAlerts(data.data || []);
    } catch (error) {
      console.error("Failed to fetch alerts", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [severity, status]);

  const getSeverityIcon = (sev: string) => {
    switch (sev) {
      case 'CRITICAL': return <AlertTriangle className="h-5 w-5 text-rose-500" />;
      case 'HIGH': return <ShieldAlert className="h-5 w-5 text-orange-500" />;
      case 'MEDIUM': return <AlertCircle className="h-5 w-5 text-yellow-500" />;
      case 'LOW': return <Info className="h-5 w-5 text-blue-500" />;
      default: return <Info className="h-5 w-5 text-slate-500" />;
    }
  };

  const getStatusBadge = (stat: string) => {
    switch (stat) {
      case 'NEW': return <span className="px-2 py-1 text-xs rounded-full bg-rose-500/10 text-rose-500 border border-rose-500/20">NEW</span>;
      case 'ACKNOWLEDGED': return <span className="px-2 py-1 text-xs rounded-full bg-blue-500/10 text-blue-500 border border-blue-500/20">ACKNOWLEDGED</span>;
      case 'RESOLVED': return <span className="px-2 py-1 text-xs rounded-full bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">RESOLVED</span>;
      default: return <span className="px-2 py-1 text-xs rounded-full bg-slate-500/10 text-slate-500 border border-slate-500/20">{stat}</span>;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Alert Queue</h2>
          <p className="text-sm text-slate-400">Manage and investigate security detections</p>
        </div>
        
        <div className="flex items-center space-x-4">
          <select 
            value={severity} 
            onChange={e => setSeverity(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-md px-3 py-2 text-sm text-slate-200"
          >
            <option value="">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>

          <select 
            value={status} 
            onChange={e => setStatus(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-md px-3 py-2 text-sm text-slate-200"
          >
            <option value="">All Statuses</option>
            <option value="NEW">New</option>
            <option value="ACKNOWLEDGED">Acknowledged</option>
            <option value="RESOLVED">Resolved</option>
          </select>
          
          <button 
            onClick={fetchAlerts}
            className="flex items-center px-4 py-2 bg-slate-800 hover:bg-slate-700 text-sm font-medium rounded-md transition-colors"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      <div className="border border-slate-800 rounded-lg overflow-hidden bg-slate-900">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-950/50 text-slate-400 border-b border-slate-800 uppercase text-xs font-semibold">
            <tr>
              <th className="px-4 py-3 w-12">Sev</th>
              <th className="px-4 py-3">Alert</th>
              <th className="px-4 py-3">Source IP</th>
              <th className="px-4 py-3">ML Prediction</th>
              <th className="px-4 py-3 text-right">Occurrences</th>
              <th className="px-4 py-3">Last Seen</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3 w-12"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50">
            {loading ? (
              <tr>
                <td colSpan={8} className="px-4 py-8 text-center text-slate-400">Loading alerts...</td>
              </tr>
            ) : alerts.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-4 py-8 text-center text-slate-400">No alerts match the selected filters.</td>
              </tr>
            ) : (
              alerts.map((alert) => (
                <tr key={alert.alert_id} className="hover:bg-slate-800/50 transition-colors group">
                  <td className="px-4 py-3 flex justify-center">
                    {getSeverityIcon(alert.severity)}
                  </td>
                  <td className="px-4 py-3">
                    <div className="font-medium text-slate-200">{alert.title}</div>
                    <div className="text-xs text-slate-500 mt-1">{alert.alert_type}</div>
                  </td>
                  <td className="px-4 py-3 font-mono text-xs">{alert.source_ip || 'N/A'}</td>
                  <td className="px-4 py-3">
                    {alert.ml_prediction ? (
                      <div className="flex flex-col">
                        <span className={alert.ml_prediction === 'SUSPICIOUS' ? 'text-rose-400' : 'text-slate-400'}>
                          {alert.ml_prediction}
                        </span>
                        <span className="text-xs text-slate-500">
                          {alert.ml_probability ? (alert.ml_probability * 100).toFixed(1) + '%' : ''}
                        </span>
                      </div>
                    ) : (
                      <span className="text-slate-500">N/A</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right font-mono text-slate-400">{alert.occurrence_count}</td>
                  <td className="px-4 py-3 text-slate-400">
                    <div title={format(new Date(alert.last_seen), 'PPpp')}>
                      {formatDistanceToNow(new Date(alert.last_seen), { addSuffix: true })}
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    {getStatusBadge(alert.status)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link href={`/alerts/${alert.alert_id}`} className="inline-flex items-center justify-center p-2 rounded-md hover:bg-slate-700 text-slate-400 hover:text-white transition-colors">
                      <ChevronRight className="h-4 w-4" />
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
