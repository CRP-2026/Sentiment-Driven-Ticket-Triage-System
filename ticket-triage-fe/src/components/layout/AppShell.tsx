import React from "react";
import { Outlet } from "react-router-dom";
import { Navigation } from "./Navigation";

export const AppShell: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navigation />
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <Outlet />
      </main>
      <footer className="border-t border-slate-200 bg-white py-4 text-center text-xs text-slate-500">
        Đồ án Quản trị dự án phần mềm — Nhóm DogTowFaces (Học phần 2026) | Phiên bản Version 3.1
      </footer>
    </div>
  );
};
