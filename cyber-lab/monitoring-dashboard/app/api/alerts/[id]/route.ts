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

    const sql = `
      SELECT *
      FROM alerts
      WHERE alert_id = $1
    `;
    
    const res = await query(sql, [alertId]);
    
    if (res.rows.length === 0) {
      return NextResponse.json({ error: 'Alert not found' }, { status: 404 });
    }

    return NextResponse.json(res.rows[0], { status: 200 });

  } catch (error) {
    console.error('API Error /alerts/[id]:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
