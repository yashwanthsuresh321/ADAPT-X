import { NextResponse } from 'next/server';
import { query } from '@/lib/db';

export async function GET() {
  try {
    const statsQuery = `
      SELECT alert_type, COUNT(*) as count
      FROM alerts
      GROUP BY alert_type
      ORDER BY count DESC
    `;
    const res = await query(statsQuery);
    
    const data = res.rows.map(r => ({
      alert_type: r.alert_type,
      count: parseInt(r.count || '0')
    }));

    return NextResponse.json(data, { status: 200 });
  } catch (error) {
    console.error('API Error /statistics/types:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
