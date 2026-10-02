import {
  Bell,
  Search,
} from "lucide-react";

export default function Topbar() {
  return (
    <header className="topbar">
      <div className="topbar-search">
        <Search size={18} />

        <input
          type="text"
          placeholder="Search skills, courses, districts..."
        />
      </div>

      <div className="topbar-actions">
        <button className="icon-button">
          <Bell size={19} />
        </button>

        <div className="user-menu">
          <div className="avatar">
            G
          </div>

          <div className="user-info">
            <strong>SkillSync User</strong>
            <span>Administrator</span>
          </div>
        </div>
      </div>
    </header>
  );
}