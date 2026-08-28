import { NextResponse } from 'next/server';
import { query } from '@/lib/db';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const source = searchParams.get('source');
    const eventType = searchParams.get('event_type');
    const sourceIp = searchParams.get('source_ip');
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '50');
    
    const safeLimit = Math.min(limit, 100);
    const offset = (Math.max(page, 1) - 1) * safeLimit;

    let sql = `
      SELECT 
        event_id, timestamp, source, event_type, source_ip, source_port, 
        destination_ip, destination_port, protocol, action, resource, status, session_id
      FROM telemetry_events
      WHERE 1=1
    `;
    const params: any[] = [];
    let paramIndex = 1;

    if (source) {
      sql += ` AND source = $${paramIndex++}`;
      params.push(source);
    }
    if (eventType) {
      sql += ` AND event_type = $${paramIndex++}`;
      params.push(eventType);
    }
    if (sourceIp) {
      sql += ` AND source_ip = $${paramIndex++}`;
      params.push(sourceIp);
    }

    const search = searchParams.get('search');
    if (search) {
      sql += ` AND (source_ip ILIKE $${paramIndex} OR action ILIKE $${paramIndex} OR resource ILIKE $${paramIndex})`;
      params.push(`%${search}%`);
      paramIndex++;
    }

    sql += ` ORDER BY timestamp DESC LIMIT $${paramIndex++} OFFSET $${paramIndex++}`;
    params.push(safeLimit, offset);

    const res = await query(sql, params);
    
    let countSql = `SELECT COUNT(*) FROM telemetry_events WHERE 1=1`;
    const countParams: any[] = [];
    let countIndex = 1;
    if (source) { countSql += ` AND source = $${countIndex++}`; countParams.push(source); }
    if (eventType) { countSql += ` AND event_type = $${countIndex++}`; countParams.push(eventType); }
    if (sourceIp) { countSql += ` AND source_ip = $${countIndex++}`; countParams.push(sourceIp); }
    if (search) {
      countSql += ` AND (source_ip ILIKE $${countIndex} OR action ILIKE $${countIndex} OR resource ILIKE $${countIndex})`;
      countParams.push(`%${search}%`);
    }
    
    const countRes = await query(countSql, countParams);
    const total = parseInt(countRes.rows[0].count);

    return NextResponse.json({
      data: res.rows,
      meta: {
        total,
        page,
        limit: safeLimit,
        pages: Math.ceil(total / safeLimit)
      }
    }, { status: 200 });

  } catch (error) {
    console.error('API Error /telemetry:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
