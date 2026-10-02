import { useEffect, useState } from "react";

import {
  getMarketSummary,
  getSkillTrends,
  getCourseAlignment,
  getMetadata,
} from "../api";

export default function Overview() {
  const [market, setMarket] = useState(null);
  const [skills, setSkills] = useState(null);
  const [courses, setCourses] = useState(null);
  const [metadata, setMetadata] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        setError(null);

        const [
          marketData,
          skillData,
          courseData,
          metadataData,
        ] = await Promise.all([
          getMarketSummary(),
          getSkillTrends({ limit: 5 }),
          getCourseAlignment({ limit: 5 }),
          getMetadata(),
        ]);

        setMarket(marketData);
        setSkills(skillData);
        setCourses(courseData);
        setMetadata(metadataData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  if (loading) {
    return (
      <div className="page-state">
        <div className="loading-spinner"></div>

        <h2>Loading intelligence</h2>

        <p>
          Connecting to the SkillSync data engine...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-state error-state">
        <h2>Unable to load intelligence</h2>

        <p>{error}</p>

        <button
          className="primary-button"
          onClick={() => window.location.reload()}
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div>
      {/* PAGE HEADER */}
      <div className="page-header">
        <div>
          <p className="eyebrow">
            LABOUR MARKET INTELLIGENCE
          </p>

          <h1 className="page-title">
            Intelligence Overview
          </h1>

          <p className="page-description">
            Maharashtra skill demand, training capacity
            and workforce alignment.
          </p>
        </div>
      </div>

      {/* HERO */}
      <div className="overview-hero">
        <div className="hero-content">
          <p className="hero-eyebrow">
            SKILLSYNC INTELLIGENCE PLATFORM
          </p>

          <h2>
            Turning labour-market signals
            <br />
            into training decisions.
          </h2>

          <p>
            SkillSync connects industry demand, skills,
            training capacity and district-level
            intelligence into one decision-support
            platform.
          </p>
        </div>

        <div className="hero-orbit">
          <div className="hero-orbit-ring ring-one"></div>
          <div className="hero-orbit-ring ring-two"></div>

          <div className="hero-core">
            <span>⌁</span>
          </div>
        </div>
      </div>

      {/* KPI CARDS */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">▣</div>

          <div>
            <div className="stat-label">
              Jobs Analysed
            </div>

            <div className="stat-value">
              {market?.job_count?.toLocaleString() ?? "..."}
            </div>

            <div className="stat-meta">
              Across Maharashtra
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">↗</div>

          <div>
            <div className="stat-label">
              Skills Tracked
            </div>

            <div className="stat-value">
              {market?.skill_count?.toLocaleString() ?? "..."}
            </div>

            <div className="stat-meta">
              Normalised skill signals
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">⌂</div>

          <div>
            <div className="stat-label">
              Training Courses
            </div>

            <div className="stat-value">
              {courses?.total_courses?.toLocaleString() ?? "..."}
            </div>

            <div className="stat-meta">
              Current alignment view
            </div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">◇</div>

          <div>
            <div className="stat-label">
              Districts Covered
            </div>

            <div className="stat-value">
              {metadata?.districts?.length ?? "..."}
            </div>

            <div className="stat-meta">
              District-level intelligence
            </div>
          </div>
        </div>
      </div>

      {/* SNAPSHOT HEADER */}
      <div className="section-header">
        <div>
          <p className="eyebrow">
            INTELLIGENCE SNAPSHOT
          </p>

          <h2>Current market signals</h2>
        </div>

        <span className="section-link">
          Live from data engine
        </span>
      </div>

      {/* TWO COLUMN INTELLIGENCE */}
      <div className="overview-grid">
        {/* TOP SKILLS */}
        <div className="card intelligence-card">
          <div className="card-header">
            <div>
              <h3>Top demanded skills</h3>

              <p>
                Based on analysed job demand
              </p>
            </div>
          </div>

          <div className="skill-list">
            {market?.top_skills
              ?.slice(0, 5)
              .map((item, index) => (
                <div
                  className="skill-row"
                  key={item.skill}
                >
                  <div className="skill-rank">
                    {String(index + 1).padStart(2, "0")}
                  </div>

                  <div className="skill-info">
                    <strong>
                      {item.skill}
                    </strong>

                    <span>
                      Industry demand
                    </span>
                  </div>

                  <div className="skill-demand">
                    {item.job_count?.toLocaleString()}
                    <span>jobs</span>
                  </div>
                </div>
              ))}
          </div>
        </div>

        {/* TRAINING ALIGNMENT */}
        <div className="card intelligence-card">
          <div className="card-header">
            <div>
              <h3>Training alignment</h3>

              <p>
                Current course intelligence
              </p>
            </div>
          </div>

          <div className="course-list">
            {courses?.courses
              ?.slice(0, 5)
              .map((course) => (
                <div
                  className="course-row"
                  key={course.course_name}
                >
                  <div className="course-icon">
                    ◫
                  </div>

                  <div className="course-info">
                    <strong>
                      {course.course_name}
                    </strong>

                    <span>
                      {course.skill_count ?? 0} skills
                    </span>
                  </div>

                  <div className="course-demand">
                    {course.demand_score?.toLocaleString?.() ??
                      course.demand_score ??
                      0}
                  </div>
                </div>
              ))}
          </div>
        </div>
      </div>

      {/* SKILL SIGNALS */}
      <div className="card trend-card">
        <div className="card-header">
          <div>
            <p className="eyebrow">
              SKILL INTELLIGENCE
            </p>

            <h3>Current skill signals</h3>

            <p>
              Normalised demand signals from the
              current labour-market dataset.
            </p>
          </div>
        </div>

        <div className="trend-list">
          {skills?.skills
            ?.slice(0, 5)
            .map((skill, index) => (
              <div
                className="trend-row"
                key={skill.skill_id || skill.skill}
              >
                <div className="trend-rank">
                  {String(index + 1).padStart(2, "0")}
                </div>

                <div className="trend-info">
                  <strong>
                    {skill.skill}
                  </strong>

                  <span>
                    {skill.skill_family ||
                      skill.skill_sector ||
                      "Skill signal"}
                  </span>
                </div>

                <div className="trend-value">
                  {skill.demand_job_count?.toLocaleString?.() ??
                    skill.demand_job_count ??
                    skill.job_count?.toLocaleString?.() ??
                    skill.job_count ??
                    0}

                  <span>jobs</span>
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  );
}