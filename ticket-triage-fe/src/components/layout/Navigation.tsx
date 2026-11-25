import React from "react";
import { NavLink } from "react-router-dom";
import { Inbox, FlaskConical, BarChart3, ShieldCheck } from "lucide-react";
import { useHealth } from "../../api/hooks";

export const Navigation: React.FC = () => {
  const { data: health, isError: isHealthError } = useHealth();

  const navItems = [
    { to: "/", label: "Hộp thư ưu tiên", icon: <Inbox className="w-[18px] h-[18px]" /> },
    { to: "/tester", label: "Kiểm thử trực tiếp", icon: <FlaskConical className="w-[18px] h-[18px]" /> },
    { to: "/analytics", label: "Phân tích thống kê", icon: <BarChart3 className="w-[18px] h-[18px]" /> },
  ];

  let dotClass = "";
  let statusText = "Đang theo dõi hàng đợi";
  let statusTitle: string | undefined;

  if (isHealthError) {
    dotClass = "is-error";
    statusText = "Mất kết nối máy chủ";
  } else if (health) {
    statusTitle = `Mô hình: ${health.model_name} (v${health.version})`;
    if (!health.model_loaded && !health.is_mock) {
      dotClass = "is-warn";
      statusText = `Model chưa sẵn sàng · Hàng đợi: ${health.queue_size}`;
    } else if (health.is_mock) {
      dotClass = "is-mock";
      statusText = `Chế độ Mock · Hàng đợi: ${health.queue_size}`;
    } else {
      statusText = `Trực tuyến · Hàng đợi: ${health.queue_size}`;
    }
  }

  return (
    <aside className="app-sidebar">
      <div className="app-brand">
        <div className="app-brand-mark"><ShieldCheck className="w-5 h-5" /></div>
        <div className="min-w-0">
          <div className="text-[15px] font-bold tracking-tight text-slate-900">Phân loại ticket</div>
          <div className="text-[10px] font-medium text-slate-500">DogTwoFaces v3.1</div>
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
      <div className="app-sidebar-foot" title={statusTitle}>
        <span className={`app-live-dot ${dotClass}`} />
        <span>{statusText}</span>
      </div>
    </aside>
  );
};
