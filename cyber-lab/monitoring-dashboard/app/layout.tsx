import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import { Activity, AlertTriangle, LayoutDashboard, Shield, Database } from "lucide-react";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "ADAPT-X Security Operations Center",
  description: "AI-Driven Adaptive Cyber Deception",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} bg-slate-950 text-slate-50 flex h-screen overflow-hidden`}>
        {/* Sidebar */}
        <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col">
          <div className="h-16 flex items-center px-6 border-b border-slate-800">
            <Shield className="w-6 h-6 text-blue-500 mr-2" />
            <span className="font-bold text-lg tracking-tight">ADAPT-X SOC</span>
          </div>
          
          <div className="flex-1 overflow-y-auto py-4">
            <nav className="space-y-1 px-3">
              <Link href="/" className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-slate-300 hover:bg-slate-800 hover:text-white group">
                <LayoutDashboard className="w-5 h-5 mr-3 text-slate-400 group-hover:text-blue-500" />
                Overview
              </Link>
              <Link href="/alerts" className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-slate-300 hover:bg-slate-800 hover:text-white group">
                <AlertTriangle className="w-5 h-5 mr-3 text-slate-400 group-hover:text-rose-500" />
                Alerts
              </Link>
              <Link href="/telemetry" className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-slate-300 hover:bg-slate-800 hover:text-white group">
                <Activity className="w-5 h-5 mr-3 text-slate-400 group-hover:text-emerald-500" />
                Telemetry
              </Link>
            </nav>
          </div>
          
          <div className="p-4 border-t border-slate-800">
            <div className="flex items-center text-sm text-slate-400">
              <Database className="w-4 h-4 mr-2" />
              <span className="flex-1">System Status</span>
              <span className="flex h-2 w-2 rounded-full bg-emerald-500"></span>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 flex flex-col h-screen overflow-hidden">
          <header className="h-16 flex items-center justify-between px-8 border-b border-slate-800 bg-slate-950">
            <h1 className="text-xl font-semibold">Security Operations Center</h1>
            <div className="text-sm text-slate-400">Live Environment</div>
          </header>
          <div className="flex-1 overflow-y-auto p-8">
            {children}
          </div>
        </main>
      </body>
    </html>
  );
}
