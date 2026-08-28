import { NextResponse } from 'next/server';
import { query } from '@/lib/db';

export async function GET() {
  try {
    const statsQuery = `
      SELECT source_ip, COUNT(*) as count
      FROM alerts
      WHERE source_ip IS NOT NULL
      GROUP BY source_ip
      ORDER BY count DESC
      LIMIT 10
    `;
    const res = await query(statsQuery);
    
    const data = res.rows.map(r => ({
      source_ip: r.source_ip,
      count: parseInt(r.count || '0')
    }));

    return NextResponse.json(data, { status: 200 });
  } catch (error) {
    console.error('API Error /statistics/sources:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
