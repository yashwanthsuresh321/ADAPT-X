import { NextResponse } from 'next/server';
import { query } from '@/lib/db';

export async function GET() {
  try {
    const statsQuery = `
      SELECT severity, COUNT(*) as count
      FROM alerts
      GROUP BY severity
      ORDER BY 
        CASE severity 
          WHEN 'CRITICAL' THEN 1 
          WHEN 'HIGH' THEN 2 
          WHEN 'MEDIUM' THEN 3 
          WHEN 'LOW' THEN 4 
          ELSE 5 
        END
    `;
    const res = await query(statsQuery);
    
    const data = res.rows.map(r => ({
      severity: r.severity,
      count: parseInt(r.count || '0')
    }));

    // Ensure all severities exist even if 0
    const fullData = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(sev => {
      const found = data.find(d => d.severity === sev);
      return found || { severity: sev, count: 0 };
    });

    return NextResponse.json(fullData, { status: 200 });
  } catch (error) {
    console.error('API Error /statistics/severity:', error);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
