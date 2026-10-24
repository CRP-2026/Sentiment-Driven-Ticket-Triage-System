import React from "react";
import { Link } from "react-router-dom";
import { Home } from "lucide-react";

export const NotFoundPage: React.FC = () => {
  return (
    <div className="py-20 text-center space-y-4">
      <h2 className="text-4xl font-extrabold text-slate-800">404</h2>
      <p className="text-base text-slate-600">Trang bạn tìm kiếm không tồn tại.</p>
      <div>
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
        >
          <Home className="w-4 h-4" />
          <span>Về trang chủ</span>
        </Link>
      </div>
    </div>
  );
};
