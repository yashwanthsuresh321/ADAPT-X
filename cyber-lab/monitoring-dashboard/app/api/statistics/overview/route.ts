import { NextResponse } from 'next/server';
import { query } from '@/lib/db';

export async function GET() {
  try {
    const statsQuery = `
      SELECT
        COUNT(*) as total_alerts,
        SUM(CASE WHEN status = 'NEW' THEN 1 ELSE 0 END) as new_alerts,
        SUM(CASE WHEN status = 'ACKNOWLEDGED' THEN 1 ELSE 0 END) as acknowledged_alerts,
        SUM(CASE WHEN status = 'RESOLVED' THEN 1 ELSE 0 END) as resolved_alerts,
        SUM(CASE WHEN severity = 'CRITICAL' THEN 1 ELSE 0 END) as critical_alerts,
        SUM(CASE WHEN severity = 'HIGH' THEN 1 ELSE 0 END) as high_alerts,
        SUM(CASE WHEN severity = 'MEDIUM' THEN 1 ELSE 0 END) as medium_alerts,
        SUM(CASE WHEN severity = 'LOW' THEN 1 ELSE 0 END) as low_alerts,
        SUM(CASE WHEN ml_prediction = 'SUSPICIOUS' THEN 1 ELSE 0 END) as suspicious_ml,
        COUNT(DISTINCT source_ip) as unique_sources
      FROM alerts
    `;
    const res = await query(statsQuery);
    
    // Parse ints because COUNT/SUM often return strings in pg
    const raw = res.rows[0];
    const data = {
      total_alerts: parseInt(raw.total_alerts || '0'),
      new_alerts: parseInt(raw.new_alerts || '0'),
      acknowledged_alerts: parseInt(raw.acknowledged_alerts || '0'),
      resolved_alerts: parseInt(raw.resolved_alerts || '0'),
      critical_alerts: parseInt(raw.critical_alerts || '0'),
      high_alerts: parseInt(raw.high_alerts || '0'),
      medium_alerts: parseInt(raw.medium_alerts || '0'),
      low_alerts: parseInt(raw.low_alerts || '0'),
      suspicious_ml: parseInt(raw.suspicious_ml || '0'),
      unique_sources: parseInt(raw.unique_sources || '0'),
    };

    return NextResponse.json(data, { status: 200 });
  } catch (error) {
    console.error('API Error /statistics/overview:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
