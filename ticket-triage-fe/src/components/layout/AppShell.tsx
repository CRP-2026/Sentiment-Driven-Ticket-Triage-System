import React from "react";
import { Outlet } from "react-router-dom";
import { Navigation } from "./Navigation";

export const AppShell: React.FC = () => {
  return (
    <div className="app-shell min-h-screen md:flex">
      <Navigation />
      <div className="app-workspace min-w-0 flex-1">
        <main className="app-main w-full px-4 py-5 sm:px-6 lg:px-8 lg:py-7">
          <Outlet />
        </main>
        <footer className="app-footer px-5 py-4 text-xs">
        Đồ án Quản trị dự án phần mềm — Nhóm DogTowFaces (Học phần 2026) | Phiên bản 3.1
        </footer>
      </div>
    </div>
  );
};
