"use client";

import { useEffect, useState } from "react";
import { format } from "date-fns";
import Link from "next/link";
import { ArrowLeft, ShieldAlert, CheckCircle2, AlertTriangle, Info, Clock, Check, Shield, Server, Network, Activity, ListOrdered, Layers } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function AlertInvestigation({ params }: { params: Promise<{ id: string }> }) {
  const [alertId, setAlertId] = useState<string>('');
  const [alert, setAlert] = useState<any>(null);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    async function resolveParams() {
      const p = await params;
      setAlertId(p.id);
    }
    resolveParams();
  }, [params]);

  useEffect(() => {
    if (!alertId) return;
    async function fetchData() {
      try {
        const [alertRes, timelineRes] = await Promise.all([
          fetch(`/api/alerts/${alertId}`),
          fetch(`/api/alerts/${alertId}/timeline`)
        ]);
        
        if (alertRes.ok) setAlert(await alertRes.json());
        if (timelineRes.ok) {
          const tData = await timelineRes.json();
          setTimeline(tData.data || []);
        }
      } catch (error) {
        console.error("Failed to fetch alert details", error);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [alertId]);

  const updateStatus = async (newStatus: string) => {
    setUpdating(true);
    try {
      const res = await fetch(`/api/alerts/${alertId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
      if (res.ok) {
        const updated = await res.json();
        setAlert({ ...alert, status: updated.status, updated_at: updated.updated_at });
      }
    } catch (error) {
      console.error("Failed to update status", error);
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-full text-slate-400">Loading investigation data...</div>;
  }

  if (!alert) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-slate-400">
        <AlertTriangle className="h-12 w-12 text-slate-600 mb-4" />
        <h2 className="text-xl">Alert Not Found</h2>
        <Link href="/alerts" className="mt-4 text-blue-500 hover:underline">Return to Queue</Link>
      </div>
    );
  }

  const getSeverityColor = (sev: string) => {
    switch (sev) {
      case 'CRITICAL': return 'text-rose-500 bg-rose-500/10 border-rose-500/20';
      case 'HIGH': return 'text-orange-500 bg-orange-500/10 border-orange-500/20';
      case 'MEDIUM': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
      case 'LOW': return 'text-blue-500 bg-blue-500/10 border-blue-500/20';
      default: return 'text-slate-500 bg-slate-500/10 border-slate-500/20';
    }
  };

  const renderEvidence = (evidence: any) => {
    if (!evidence) return <div className="text-slate-500 text-sm">No structured evidence available.</div>;
    return (
      <div className="space-y-4">
        {Object.entries(evidence).map(([key, value]) => (
          <div key={key} className="border border-slate-800 rounded-md p-3 bg-slate-950/50">
            <h4 className="text-xs font-semibold uppercase text-slate-400 mb-2">{key.replace(/_/g, ' ')}</h4>
            {typeof value === 'object' && value !== null ? (
              <ul className="space-y-1">
                {Object.entries(value).map(([subKey, subVal]) => (
                  <li key={subKey} className="text-sm flex justify-between">
                    <span className="text-slate-500">{subKey.replace(/_/g, ' ')}</span>
                    <span className="font-mono text-slate-300">{String(subVal)}</span>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="text-sm font-mono text-slate-300">{String(value)}</div>
            )}
          </div>
        ))}
      </div>
    );
  };

  const renderFeatureSnapshot = (snapshot: any) => {
    if (!snapshot || typeof snapshot !== 'object' || Object.keys(snapshot).length === 0) {
      return <div className="text-slate-500 text-sm py-2">No behavioral feature snapshot available for this alert.</div>;
    }

    const formatValue = (val: any): string => {
      if (val === null || val === undefined) return 'N/A';
      if (typeof val === 'number') {
        return Number.isInteger(val) ? val.toLocaleString() : val.toFixed(2);
      }
      if (typeof val === 'boolean') return val ? 'True' : 'False';
      if (typeof val === 'object') return JSON.stringify(val);
      return String(val);
    };

    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
        {Object.entries(snapshot).map(([key, val]) => (
          <div key={key} className="bg-slate-950/60 border border-slate-800 rounded-md p-3">
            <div className="text-xs text-slate-500 uppercase font-semibold tracking-wider">
              {key.replace(/_/g, ' ')}
            </div>
            <div className="text-lg font-mono font-medium text-slate-200 mt-1">
              {formatValue(val)}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderBehaviorSequence = (sequence: any) => {
    if (!sequence || (Array.isArray(sequence) && sequence.length === 0)) {
      return <div className="text-slate-500 text-sm py-2">No behavior sequence recorded for this alert.</div>;
    }

    const items = Array.isArray(sequence) ? sequence : [sequence];

    return (
      <div className="space-y-3">
        <div className="flex flex-wrap gap-2 max-h-72 overflow-y-auto pr-2 border border-slate-800/80 rounded-md p-3 bg-slate-950/40">
          {items.map((item: any, idx: number) => {
            const text = typeof item === 'string' ? item : JSON.stringify(item);
            const dotIndex = text.indexOf('.');
            const service = dotIndex !== -1 ? text.substring(0, dotIndex) : null;
            const action = dotIndex !== -1 ? text.substring(dotIndex + 1) : text;

            return (
              <div 
                key={idx} 
                className="flex items-center text-xs font-mono bg-slate-900 border border-slate-800 rounded px-2.5 py-1 text-slate-300 hover:border-slate-700 transition-colors"
                title={`Step ${idx + 1}: ${text}`}
              >
                <span className="text-slate-500 mr-1.5 font-sans font-semibold">#{idx + 1}</span>
                {service && <span className="text-blue-400 mr-1">{service}.</span>}
                <span className="text-slate-200">{action}</span>
              </div>
            );
          })}
        </div>
        <div className="text-xs text-slate-500">
          Recorded sequence length: <span className="font-mono text-slate-400">{items.length} steps</span>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center space-x-2 text-sm text-slate-400">
        <Link href="/alerts" className="hover:text-white flex items-center transition-colors">
          <ArrowLeft className="h-4 w-4 mr-1" /> Back to Queue
        </Link>
      </div>

      {/* Header */}
      <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-4">
        <div>
          <div className="flex items-center space-x-3 mb-2">
            <span className={`px-2.5 py-1 text-xs font-bold rounded border ${getSeverityColor(alert.severity)}`}>
              {alert.severity}
            </span>
            <span className="px-2.5 py-1 text-xs font-semibold rounded bg-slate-800 text-slate-300 border border-slate-700">
              {alert.status}
            </span>
            {alert.confidence && (
              <span className="text-sm text-slate-400 ml-2">
                Confidence: <span className="font-mono text-slate-200">{(alert.confidence * 100).toFixed(1)}%</span>
              </span>
            )}
          </div>
          <h2 className="text-3xl font-bold tracking-tight text-white">{alert.title}</h2>
          <p className="text-slate-400 mt-1 flex items-center space-x-4">
            <span>ID: <span className="font-mono text-xs">{alert.alert_id.split('-')[0]}</span></span>
            <span>Created: {format(new Date(alert.created_at), 'PP p')}</span>
          </p>
        </div>
        
        <div className="flex space-x-3">
          {alert.status === 'NEW' && (
            <button 
              onClick={() => updateStatus('ACKNOWLEDGED')}
              disabled={updating}
              className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md transition-colors disabled:opacity-50"
            >
              <Check className="h-4 w-4 mr-2" />
              Acknowledge
            </button>
          )}
          {alert.status !== 'RESOLVED' && (
            <button 
              onClick={() => updateStatus('RESOLVED')}
              disabled={updating}
              className="flex items-center px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-md transition-colors disabled:opacity-50"
            >
              <CheckCircle2 className="h-4 w-4 mr-2" />
              Resolve
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Core Info */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader className="border-b border-slate-800 pb-4">
              <CardTitle className="text-lg flex items-center">
                <Shield className="h-5 w-5 mr-2 text-blue-500" />
                Detection Analysis
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <h4 className="text-sm font-medium text-slate-400 mb-3">Deterministic Rules</h4>
                  <div className="flex items-start space-x-2">
                    <CheckCircle2 className="h-4 w-4 text-emerald-500 mt-0.5 shrink-0" />
                    <div>
                      <div className="text-sm font-medium text-slate-200">{alert.detection_rule}</div>
                      <div className="text-xs text-slate-500 mt-0.5">Primary rule triggered</div>
                    </div>
                  </div>
                  {alert.alert_type !== alert.detection_rule && (
                    <div className="flex items-start space-x-2 mt-3">
                      <CheckCircle2 className="h-4 w-4 text-emerald-500 mt-0.5 shrink-0" />
                      <div>
                        <div className="text-sm font-medium text-slate-200">{alert.alert_type}</div>
                        <div className="text-xs text-slate-500 mt-0.5">Correlated behavior</div>
                      </div>
                    </div>
                  )}
                </div>
                <div>
                  <h4 className="text-sm font-medium text-slate-400 mb-3">AI / ML Model</h4>
                  {alert.ml_prediction ? (
                    <div className="flex items-start space-x-2">
                      <Activity className={`h-4 w-4 mt-0.5 shrink-0 ${alert.ml_prediction === 'SUSPICIOUS' ? 'text-rose-500' : 'text-emerald-500'}`} />
                      <div>
                        <div className="text-sm font-medium text-slate-200">Classified as {alert.ml_prediction}</div>
                        <div className="text-xs text-slate-500 mt-0.5">
                          Probability: {alert.ml_probability ? (alert.ml_probability * 100).toFixed(1) + '%' : 'N/A'}
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-sm text-slate-500">No ML correlation for this alert.</div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-900 border-slate-800">
            <CardHeader className="border-b border-slate-800 pb-4">
              <CardTitle className="text-lg flex items-center">
                <Layers className="h-5 w-5 mr-2 text-purple-400" />
                Behavioral Evidence
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              {renderEvidence(alert.evidence)}
            </CardContent>
          </Card>

          <Card className="bg-slate-900 border-slate-800">
            <CardHeader className="border-b border-slate-800 pb-4">
              <CardTitle className="text-lg flex items-center">
                <Activity className="h-5 w-5 mr-2 text-emerald-400" />
                Feature Snapshot
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              {renderFeatureSnapshot(alert.feature_snapshot)}
            </CardContent>
          </Card>

          <Card className="bg-slate-900 border-slate-800">
            <CardHeader className="border-b border-slate-800 pb-4">
              <CardTitle className="text-lg flex items-center">
                <ListOrdered className="h-5 w-5 mr-2 text-indigo-400" />
                Behavior Sequence
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              {renderBehaviorSequence(alert.behavior_sequence)}
            </CardContent>
          </Card>
          
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader className="border-b border-slate-800 pb-4">
              <CardTitle className="text-lg flex items-center">
                <Clock className="h-5 w-5 mr-2 text-slate-400" />
                Chronological Event Timeline
              </CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              {timeline.length === 0 ? (
                <div className="text-slate-500 text-sm text-center py-4">No correlated telemetry events found for this session.</div>
              ) : (
                <div className="relative border-l border-slate-800 ml-3 space-y-6">
                  {timeline.map((event: any, index: number) => (
                    <div key={event.event_id} className="relative pl-6">
                      <div className="absolute -left-1.5 mt-1.5 h-3 w-3 rounded-full bg-blue-500 ring-4 ring-slate-900"></div>
                      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-baseline mb-1">
                        <h4 className="text-sm font-medium text-slate-200">{event.event_type}</h4>
                        <time className="text-xs text-slate-500 font-mono">{format(new Date(event.timestamp), 'HH:mm:ss.SSS')}</time>
                      </div>
                      <div className="text-xs text-slate-400 mt-1 flex items-center space-x-2">
                        <span className="font-mono bg-slate-800 px-1.5 py-0.5 rounded">{event.action || 'unknown'}</span>
                        <span>&rarr;</span>
                        <span className="font-mono bg-slate-800 px-1.5 py-0.5 rounded">{event.resource || 'unknown'}</span>
                        <span className={`px-1.5 py-0.5 rounded ${event.status === 'success' ? 'text-emerald-400' : 'text-rose-400'}`}>{event.status}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column - Metadata */}
        <div className="space-y-6">
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader className="border-b border-slate-800 pb-4">
              <CardTitle className="text-lg">Network Context</CardTitle>
            </CardHeader>
            <CardContent className="pt-6 space-y-4">
              <div>
                <span className="text-xs text-slate-500 uppercase font-semibold">Source IP</span>
                <div className="flex items-center mt-1">
                  <Network className="h-4 w-4 mr-2 text-slate-400" />
                  <span className="font-mono text-sm">{alert.source_ip || 'N/A'}</span>
                </div>
              </div>
              <div>
                <span className="text-xs text-slate-500 uppercase font-semibold">Target Environment</span>
                <div className="flex items-center mt-1">
                  <Server className="h-4 w-4 mr-2 text-slate-400" />
                  <span className="font-mono text-sm text-slate-300">ADAPT-X Cyber Lab</span>
                </div>
              </div>
              <div>
                <span className="text-xs text-slate-500 uppercase font-semibold">Session ID</span>
                <div className="mt-1 font-mono text-xs text-slate-400 break-all">{alert.session_id || 'N/A'}</div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-slate-900 border-slate-800">
            <CardHeader className="border-b border-slate-800 pb-4">
              <CardTitle className="text-lg">Alert Lifecycle</CardTitle>
            </CardHeader>
            <CardContent className="pt-6 space-y-4">
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-500">First Seen</span>
                <span className="font-mono text-slate-300">{format(new Date(alert.first_seen), 'MMM d, HH:mm:ss')}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-500">Last Seen</span>
                <span className="font-mono text-slate-300">{format(new Date(alert.last_seen), 'MMM d, HH:mm:ss')}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-slate-500">Occurrences</span>
                <span className="font-mono font-medium text-slate-200 bg-slate-800 px-2 py-0.5 rounded-full">{alert.occurrence_count}</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}