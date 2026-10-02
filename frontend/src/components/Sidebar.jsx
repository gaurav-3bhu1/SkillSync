import {
  LayoutDashboard,
  BriefcaseBusiness,
  BrainCircuit,
  GraduationCap,
  MapPinned,
  UserRound,
} from "lucide-react";

import { NavLink } from "react-router-dom";

const navigation = [
  {
    label: "Overview",
    path: "/overview",
    icon: LayoutDashboard,
  },
  {
    label: "Market Intelligence",
    path: "/market",
    icon: BriefcaseBusiness,
  },
  {
    label: "Skill Intelligence",
    path: "/skills",
    icon: BrainCircuit,
  },
  {
    label: "Course Alignment",
    path: "/courses",
    icon: GraduationCap,
  },
  {
    label: "District Intelligence",
    path: "/districts",
    icon: MapPinned,
  },
  {
    label: "My Skill Profile",
    path: "/profile",
    icon: UserRound,
  },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">
          S
        </div>

        <div>
          <div className="brand-name">
            SkillSync
          </div>

          <div className="brand-subtitle">
            Labour Intelligence
          </div>
        </div>
      </div>

      <div className="nav-section">
        <div className="nav-label">
          PLATFORM
        </div>

        <nav className="nav-list">
          {navigation.map((item) => {
            const Icon = item.icon;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `nav-item ${
                    isActive ? "active" : ""
                  }`
                }
              >
                <Icon size={19} strokeWidth={1.8} />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      <div className="sidebar-footer">
        <div className="system-status">
          <span className="status-dot" />
          <span>Intelligence engine active</span>
        </div>

        <div className="sidebar-version">
          SkillSync v1.0
        </div>
      </div>
    </aside>
  );
}