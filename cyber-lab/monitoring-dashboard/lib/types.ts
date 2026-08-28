export interface Alert {
  alert_id: string;
  source_ip: string | null;
  destination_ip: string | null;
  session_id: string | null;
  alert_type: string;
  detection_rule: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status: 'NEW' | 'ACKNOWLEDGED' | 'RESOLVED';
  ml_prediction: string | null;
  ml_probability: number | null;
  confidence: number | null;
  title: string;
  description: string | null;
  evidence: any;
  behavior_sequence: any;
  feature_snapshot: any;
  first_seen: Date;
  last_seen: Date;
  created_at: Date;
  updated_at: Date;
  occurrence_count: number;
}

export interface TelemetryEvent {
  event_id: string;
  timestamp: Date;
  source: string;
  event_type: string;
  source_ip: string | null;
  source_port: number | null;
  destination_ip: string | null;
  destination_port: number | null;
  protocol: string | null;
  action: string | null;
  resource: string | null;
  status: string | null;
  session_id: string | null;
  raw_event: any;
}
