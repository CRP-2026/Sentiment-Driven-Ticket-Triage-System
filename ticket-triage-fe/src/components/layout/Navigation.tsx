import React from "react";
import { NavLink } from "react-router-dom";
import { Inbox, FlaskConical, BarChart3, ShieldCheck } from "lucide-react";

export const Navigation: React.FC = () => {
  const navItems = [
    { to: "/", label: "Hộp thư ưu tiên", icon: <Inbox className="w-4 h-4" /> },
    { to: "/tester", label: "Live Tester", icon: <FlaskConical className="w-4 h-4" /> },
    { to: "/analytics", label: "Phân tích thống kê", icon: <BarChart3 className="w-4 h-4" /> },
  ];

  return (
    <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-900 tracking-tight text-base">Ticket Triage</span>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                DogTowFaces v3.1
              </span>
            </div>
            <p className="text-[11px] text-slate-500">Sentiment-Driven Customer Support Routing</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 sm:gap-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `inline-flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs sm:text-sm font-medium transition-all ${
                  isActive
                    ? "bg-blue-600 text-white shadow-sm shadow-blue-600/30 font-semibold"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                }`
              }
            >
              {item.icon}
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  );
};
