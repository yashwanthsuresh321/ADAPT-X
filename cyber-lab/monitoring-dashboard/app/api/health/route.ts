import { NextResponse } from 'next/server';
import { query } from '@/lib/db';

export async function GET() {
  try {
    const res = await query('SELECT 1 as connected');
    if (res.rows.length > 0 && res.rows[0].connected === 1) {
      return NextResponse.json({ status: 'healthy', database: 'connected' }, { status: 200 });
    }
    return NextResponse.json({ status: 'unhealthy', database: 'disconnected' }, { status: 500 });
  } catch (error) {
    console.error('Healthcheck DB Error:', error);
    return NextResponse.json({ status: 'unhealthy', database: 'error', error: 'Database connection failed' }, { status: 500 });
  }
}
