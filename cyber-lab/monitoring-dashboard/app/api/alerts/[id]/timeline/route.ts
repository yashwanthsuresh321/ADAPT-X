import { NextResponse } from 'next/server';
import { query } from '@/lib/db';

export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id: alertId } = await params;
    
    // Basic UUID validation
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(alertId)) {
      return NextResponse.json({ error: 'Invalid alert ID format' }, { status: 400 });
    }

    // 1. Get alert metadata for correlation
    const alertSql = `
      SELECT session_id, source_ip, first_seen, last_seen, created_at 
      FROM alerts 
      WHERE alert_id = $1
    `;
    const alertRes = await query(alertSql, [alertId]);
    
    if (alertRes.rows.length === 0) {
      return NextResponse.json({ error: 'Alert not found' }, { status: 404 });
    }

    const { 
      session_id: sessionId, 
      source_ip: sourceIp, 
      first_seen: firstSeen, 
      last_seen: lastSeen, 
      created_at: createdAt 
    } = alertRes.rows[0];

    let events: any[] = [];
    const isSyntheticIpSession = typeof sessionId === 'string' && sessionId.startsWith('ip_');

    // Case A: Genuine session ID exists in telemetry
    if (sessionId && !isSyntheticIpSession) {
      const telemetrySql = `
        SELECT event_id, timestamp, source, event_type, source_ip, source_port, 
               destination_ip, destination_port, protocol, action, resource, status
        FROM telemetry_events
        WHERE session_id = $1
        ORDER BY timestamp ASC, event_id ASC
      `;
      const telemetryRes = await query(telemetrySql, [sessionId]);
      events = telemetryRes.rows;
    }

    // Case B & C: Synthetic IP session (e.g. ip_10.10.10.2) or missing session ID
    if (events.length === 0) {
      let targetIp: string | null = null;
      if (sourceIp) {
        targetIp = sourceIp;
      } else if (isSyntheticIpSession) {
        targetIp = sessionId.replace(/^ip_/, '');
      }

      const start = firstSeen || createdAt;
      const end = lastSeen || createdAt;

      if (targetIp && start && end) {
        // Correlate telemetry by source_ip within the alert's active observation window
        const telemetrySql = `
          SELECT event_id, timestamp, source, event_type, source_ip, source_port, 
                 destination_ip, destination_port, protocol, action, resource, status
          FROM telemetry_events
          WHERE source_ip = $1
            AND timestamp >= $2
            AND timestamp <= $3
          ORDER BY timestamp ASC, event_id ASC
        `;
        const telemetryRes = await query(telemetrySql, [targetIp, start, end]);
        events = telemetryRes.rows;
      }
    }

    return NextResponse.json({ data: events }, { status: 200 });

  } catch (error) {
    console.error('API Error /alerts/[id]/timeline:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
