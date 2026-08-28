import { NextResponse } from 'next/server';
import { query } from '@/lib/db';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const severity = searchParams.get('severity');
    const status = searchParams.get('status');
    const type = searchParams.get('alert_type');
    const sourceIp = searchParams.get('source_ip');
    const page = parseInt(searchParams.get('page') || '1');
    const limit = parseInt(searchParams.get('limit') || '50');
    
    // Max limit to prevent overloading
    const safeLimit = Math.min(limit, 100);
    const offset = (Math.max(page, 1) - 1) * safeLimit;

    let sql = `
      SELECT 
        alert_id, source_ip, destination_ip, session_id, alert_type, detection_rule, 
        severity, status, ml_prediction, ml_probability, confidence, title, 
        first_seen, last_seen, occurrence_count
      FROM alerts
      WHERE 1=1
    `;
    const params: any[] = [];
    let paramIndex = 1;

    if (severity) {
      sql += ` AND severity = $${paramIndex++}`;
      params.push(severity);
    }
    if (status) {
      sql += ` AND status = $${paramIndex++}`;
      params.push(status);
    }
    if (type) {
      sql += ` AND alert_type = $${paramIndex++}`;
      params.push(type);
    }
    if (sourceIp) {
      sql += ` AND source_ip = $${paramIndex++}`;
      params.push(sourceIp);
    }

    // Add search logic if needed
    const search = searchParams.get('search');
    if (search) {
      sql += ` AND (title ILIKE $${paramIndex} OR source_ip ILIKE $${paramIndex} OR session_id ILIKE $${paramIndex} OR alert_type ILIKE $${paramIndex})`;
      params.push(`%${search}%`);
      paramIndex++;
    }

    sql += ` ORDER BY last_seen DESC LIMIT $${paramIndex++} OFFSET $${paramIndex++}`;
    params.push(safeLimit, offset);

    const res = await query(sql, params);
    
    // Count total for pagination
    let countSql = `SELECT COUNT(*) FROM alerts WHERE 1=1`;
    const countParams: any[] = [];
    let countIndex = 1;
    if (severity) { countSql += ` AND severity = $${countIndex++}`; countParams.push(severity); }
    if (status) { countSql += ` AND status = $${countIndex++}`; countParams.push(status); }
    if (type) { countSql += ` AND alert_type = $${countIndex++}`; countParams.push(type); }
    if (sourceIp) { countSql += ` AND source_ip = $${countIndex++}`; countParams.push(sourceIp); }
    if (search) {
      countSql += ` AND (title ILIKE $${countIndex} OR source_ip ILIKE $${countIndex} OR session_id ILIKE $${countIndex} OR alert_type ILIKE $${countIndex})`;
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
    console.error('API Error /alerts:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
