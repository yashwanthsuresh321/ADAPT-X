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

    // 1. Get the session_id for the alert
    const alertSql = `SELECT session_id FROM alerts WHERE alert_id = $1`;
    const alertRes = await query(alertSql, [alertId]);
    
    if (alertRes.rows.length === 0) {
      return NextResponse.json({ error: 'Alert not found' }, { status: 404 });
    }

    const sessionId = alertRes.rows[0].session_id;

    if (!sessionId) {
      return NextResponse.json({ data: [] }, { status: 200 }); // No session to correlate
    }

    // 2. Fetch all telemetry events for that session
    const telemetrySql = `
      SELECT event_id, timestamp, source, event_type, source_ip, source_port, 
             destination_ip, destination_port, protocol, action, resource, status, raw_event
      FROM telemetry_events
      WHERE session_id = $1
      ORDER BY timestamp ASC
    `;
    
    const telemetryRes = await query(telemetrySql, [sessionId]);

    return NextResponse.json({ data: telemetryRes.rows }, { status: 200 });

  } catch (error) {
    console.error('API Error /alerts/[id]/timeline:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
