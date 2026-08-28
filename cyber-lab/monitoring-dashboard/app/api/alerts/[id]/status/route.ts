import { NextResponse } from 'next/server';
import { query } from '@/lib/db';

export async function PATCH(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const { id: alertId } = await params;
    
    // Basic UUID validation
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(alertId)) {
      return NextResponse.json({ error: 'Invalid alert ID format' }, { status: 400 });
    }

    const body = await request.json();
    const { status } = body;

    if (!status || !['ACKNOWLEDGED', 'RESOLVED', 'NEW'].includes(status)) {
      return NextResponse.json({ error: 'Invalid status value' }, { status: 400 });
    }

    // Update status and updated_at
    const sql = `
      UPDATE alerts
      SET status = $1, updated_at = NOW()
      WHERE alert_id = $2
      RETURNING *
    `;
    
    const res = await query(sql, [status, alertId]);
    
    if (res.rows.length === 0) {
      return NextResponse.json({ error: 'Alert not found' }, { status: 404 });
    }

    return NextResponse.json(res.rows[0], { status: 200 });

  } catch (error) {
    console.error('API Error /alerts/[id]/status:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
