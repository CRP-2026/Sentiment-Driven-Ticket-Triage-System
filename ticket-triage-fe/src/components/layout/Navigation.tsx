import React from "react";
import { NavLink } from "react-router-dom";
import { Inbox, FlaskConical, BarChart3, ShieldCheck } from "lucide-react";

export const Navigation: React.FC = () => {
  const navItems = [
    { to: "/", label: "Hộp thư ưu tiên", icon: <Inbox className="w-[18px] h-[18px]" /> },
    { to: "/tester", label: "Kiểm thử trực tiếp", icon: <FlaskConical className="w-[18px] h-[18px]" /> },
    { to: "/analytics", label: "Phân tích thống kê", icon: <BarChart3 className="w-[18px] h-[18px]" /> },
  ];

  return (
    <aside className="app-sidebar">
      <div className="app-brand">
        <div className="app-brand-mark"><ShieldCheck className="w-5 h-5" /></div>
        <div className="min-w-0">
          <div className="text-[15px] font-bold tracking-tight text-slate-900">Phân loại ticket</div>
          <div className="text-[10px] font-medium text-slate-500">DogTowFaces v3.1</div>
        </div>
      </div>
      <nav className="app-nav-groups">
        {[
          { label: "CHUNG", items: navItems.slice(0, 1) },
          { label: "CÔNG CỤ", items: navItems.slice(1) },
        ].map((group) => (
          <section className="app-nav-group" key={group.label}>
            <div className="app-nav-caption">{group.label}</div>
            <div className="app-nav-list">
              {group.items.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === "/"}
                  className={({ isActive }) => `app-nav-link ${isActive ? "is-active" : ""}`}
                >
                  {item.icon}
                  <span>{item.label}</span>
                </NavLink>
              ))}
            </div>
          </section>
        ))}
      </nav>
      <div className="app-sidebar-foot">
        <span className="app-live-dot" />
        <span>Đang theo dõi hàng đợi</span>
      </div>
    </aside>
  );
};
