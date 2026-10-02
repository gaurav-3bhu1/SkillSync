import { useEffect, useState } from "react";
import {
  Activity,
  BarChart3,
  BookOpen,
  Building2,
  ChevronRight,
  GraduationCap,
  LayoutDashboard,
  Map,
  Search,
  ShieldCheck,
  TrendingUp,
  Users,
  Plus,
  X,
  Sparkles
} from "lucide-react";
import Market from "./pages/Market";
import { analyzeProfile, getMetadata } from "./api";

import "./App.css";

const API = "http://127.0.0.1:8000";

function App() {
  const [page, setPage] = useState("overview");
  const [market, setMarket] = useState(null);
  const [skills, setSkills] = useState([]);
  const [courses, setCourses] = useState([]);
  const [district, setDistrict] = useState(null);
  const [metadata, setMetadata] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    try {
      setLoading(true);

      const [
        marketResponse,
        skillsResponse,
        coursesResponse,
        metadataResponse,
      ] = await Promise.all([
        fetch(`${API}/api/market/summary`),
        fetch(`${API}/api/skills/trends?limit=10`),
        fetch(`${API}/api/courses/alignment?limit=10`),
        fetch(`${API}/api/metadata`),
      ]);

      setMarket(await marketResponse.json());

      const skillData = await skillsResponse.json();
      setSkills(skillData.skills || []);

      const courseData = await coursesResponse.json();
      setCourses(courseData.courses || []);

      setMetadata(await metadataResponse.json());
    } catch (error) {
      console.error("Dashboard loading failed:", error);
    } finally {
      setLoading(false);
    }
  }

  async function loadDistrict(name) {
    try {
      const response = await fetch(
        `${API}/api/districts/${encodeURIComponent(name)}?limit=20`
      );

      const data = await response.json();
      setDistrict(data);
    } catch (error) {
      console.error("District loading failed:", error);
    }
  }

  function navigate(target) {
    setPage(target);

    if (target === "districts" && metadata?.districts?.length) {
      loadDistrict(metadata.districts[0]);
    }
  }

  const filteredSkills = skills.filter((item) =>
    String(item.skill || "")
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  const filteredCourses = courses.filter((item) =>
    String(item.course_name || "")
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  return (
    <div className="app-shell">
      <Sidebar page={page} navigate={navigate} />

      <main className="main-content">
        <header className="topbar">
          <div>
            <div className="breadcrumb">
              SkillSync <ChevronRight size={14} /> Intelligence Platform
            </div>
            <h1>{getPageTitle(page)}</h1>
          </div>

          <div className="topbar-actions">
            <div className="search-box">
              <Search size={17} />
              <input
                placeholder="Search skills, courses..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>

            <div className="status-pill">
              <span className="status-dot" />
              System Online
            </div>
          </div>
        </header>

        {loading ? (
          <Loading />
        ) : (
          <>
            {page === "overview" && (
              <Overview
                market={market}
                skills={skills}
                courses={courses}
                metadata={metadata}
                navigate={navigate}
              />
            )}

            {page === "market" && (
              <Market />
            )}

            {page === "skills" && (
              <SkillsPage />
            )}

            {page === "courses" && (
              <CoursesPage />
            )}

            {page === "districts" && (
              <DistrictPage
                metadata={metadata}
                district={district}
                loadDistrict={loadDistrict}
              />
            )}
            {page === "profile" && (
              <ProfilePage />
            )}
          </>
        )}
      </main>
    </div>
  );
}

function Sidebar({ page, navigate }) {
  const items = [
    {
      id: "overview",
      label: "Overview",
      icon: LayoutDashboard,
    },
    {
      id: "market",
      label: "Market Intelligence",
      icon: BarChart3,
    },
    {
      id: "skills",
      label: "Skill Intelligence",
      icon: TrendingUp,
    },
    {
      id: "courses",
      label: "Course Alignment",
      icon: GraduationCap,
    },
    {
      id: "districts",
      label: "District Planning",
      icon: Map,
    },
    {
      id: "profile",
      label: "My Skill Profile",
      icon: Users,
    },
  ];

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">
          <Activity size={23} />
        </div>

        <div>
          <div className="brand-name">SkillSync</div>
          <div className="brand-subtitle">Labour Intelligence</div>
        </div>
      </div>

      <div className="nav-label">PLATFORM</div>

      <nav>
        {items.map((item) => {
          const Icon = item.icon;

          return (
            <button
              key={item.id}
              className={`nav-item ${
                page === item.id ? "active" : ""
              }`}
              onClick={() => navigate(item.id)}
            >
              <Icon size={19} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="sidebar-bottom">
        <div className="data-card">
          <div className="data-card-icon">
            <ShieldCheck size={18} />
          </div>

          <div>
            <strong>Data Engine</strong>
            <span>Connected to API</span>
          </div>
        </div>

        <div className="sidebar-footer">
          SkillSync Prototype
          <br />
          Maharashtra Labour Intelligence
        </div>
      </div>
    </aside>
  );
}

function Overview({
  market,
  skills,
  courses,
  metadata,
  navigate,
}) {
  const totalJobs = market?.job_count || 0;
  const skillCount = market?.skill_count || 0;
  const districtCount = metadata?.districts?.length || 0;
  const courseCount = courses.length;

  return (
    <section>
      <div className="hero">
        <div>
          <div className="eyebrow">
            LABOUR MARKET INTELLIGENCE
          </div>

          <h2>
            Turning labour-market signals
            <br />
            into training decisions.
          </h2>

          <p>
            SkillSync connects industry demand, skills,
            training capacity and district-level intelligence
            into one decision-support platform.
          </p>

          <button
            className="primary-button"
            onClick={() => navigate("market")}
          >
            Explore Market Intelligence
            <ChevronRight size={17} />
          </button>
        </div>

        <div className="hero-graphic">
          <div className="orbit orbit-one" />
          <div className="orbit orbit-two" />

          <div className="hero-core">
            <Activity size={35} />
          </div>
        </div>
      </div>

      <div className="stats-grid">
        <StatCard
          icon={<Building2 />}
          label="Jobs Analysed"
          value={formatNumber(totalJobs)}
          detail="Across Maharashtra"
        />

        <StatCard
          icon={<TrendingUp />}
          label="Skills Tracked"
          value={formatNumber(skillCount)}
          detail="Normalised skill signals"
        />

        <StatCard
          icon={<GraduationCap />}
          label="Training Programs"
          value={formatNumber(courseCount)}
          detail="Current alignment view"
        />

        <StatCard
          icon={<Map />}
          label="Districts Covered"
          value={formatNumber(districtCount)}
          detail="District-level intelligence"
        />
      </div>

      <div className="section-header">
        <div>
          <div className="eyebrow">INTELLIGENCE SNAPSHOT</div>
          <h3>Current market signals</h3>
        </div>

        <button
          className="text-button"
          onClick={() => navigate("skills")}
        >
          View all skills <ChevronRight size={16} />
        </button>
      </div>

      <div className="content-grid">
        <div className="panel">
          <PanelHeader
            title="Top demanded skills"
            subtitle="Based on analysed job demand"
          />

          <div className="skill-list">
            {skills.slice(0, 6).map((skill, index) => (
              <SkillRow
                key={skill.skill_id || index}
                skill={skill}
                rank={index + 1}
              />
            ))}
          </div>
        </div>

        <div className="panel">
          <PanelHeader
            title="Training alignment"
            subtitle="Current course intelligence"
          />

          {courses.slice(0, 5).map((course, index) => (
            <CourseRow
              key={course.course_name || index}
              course={course}
            />
          ))}
        </div>
      </div>
    </section>
  );
}

function MarketPage({ market, metadata }) {
  return (
    <section>
      <div className="page-intro">
        <div>
          <div className="eyebrow">MARKET INTELLIGENCE</div>
          <h2>Industry demand landscape</h2>
          <p>
            Analyse job demand and the skills employers are
            requesting across the available dataset.
          </p>
        </div>
      </div>

      <div className="stats-grid compact">
        <StatCard
          icon={<Building2 />}
          label="Jobs Analysed"
          value={formatNumber(market?.job_count)}
          detail="Current dataset"
        />

        <StatCard
          icon={<TrendingUp />}
          label="Unique Skills"
          value={formatNumber(market?.skill_count)}
          detail="Normalised signals"
        />

        <StatCard
          icon={<Map />}
          label="Districts"
          value={formatNumber(metadata?.districts?.length)}
          detail="Covered locations"
        />
      </div>

      <div className="panel">
        <PanelHeader
          title="Skill demand distribution"
          subtitle="Top skills by job count"
        />

        <div className="large-skill-list">
          {(market?.top_skills || []).map((skill, index) => (
            <SkillBar
              key={skill.skill || index}
              skill={skill}
              max={
                market?.top_skills?.[0]?.job_count || 1
              }
              rank={index + 1}
            />
          ))}
        </div>
      </div>
    </section>
  );
}

function SkillsPage() {
  const [skills, setSkills] = useState([]);
  const [metadata, setMetadata] = useState(null);

  const [sector, setSector] = useState("");
  const [limit, setLimit] = useState(20);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadMetadata() {
      try {
        const response = await fetch(
          `${API}/api/metadata`
        );

        const data = await response.json();

        setMetadata(data);
      } catch (error) {
        setError(error.message);
      }
    }

    loadMetadata();
  }, []);

  useEffect(() => {
    async function loadSkills() {
      try {
        setLoading(true);
        setError(null);

        const params = new URLSearchParams();

        if (sector) {
          params.append("sector", sector);
        }

        params.append("limit", limit);

        const response = await fetch(
          `${API}/api/skills/trends?${params.toString()}`
        );

        if (!response.ok) {
          throw new Error(
            `Skill API failed: ${response.status}`
          );
        }

        const data = await response.json();

        setSkills(data.skills || []);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    }

    loadSkills();
  }, [sector, limit]);

  if (error) {
    return (
      <div className="page-state error-state">
        <h2>
          Unable to load skill intelligence
        </h2>

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
    <section>
      <div className="page-intro">
        <div>
          <div className="eyebrow">
            SKILL INTELLIGENCE
          </div>

          <h2>
            Emerging skill signals
          </h2>

          <p>
            Analyse demand, supply and training
            indicators for individual skills.
          </p>
        </div>
      </div>

      {/* FILTERS */}

      <div className="card market-filters">

        <div className="filter-group">
          <label htmlFor="skill-sector">
            Sector
          </label>

          <select
            id="skill-sector"
            value={sector}
            onChange={(event) =>
              setSector(event.target.value)
            }
          >
            <option value="">
              All sectors
            </option>

            {metadata?.sectors?.map((item) => (
              <option
                key={item}
                value={item}
              >
                {item}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="skill-limit">
            Skills shown
          </label>

          <select
            id="skill-limit"
            value={limit}
            onChange={(event) =>
              setLimit(Number(event.target.value))
            }
          >
            <option value={10}>Top 10</option>
            <option value={20}>Top 20</option>
            <option value={50}>Top 50</option>
          </select>
        </div>

        {sector && (
          <button
            className="secondary-button"
            onClick={() => setSector("")}
          >
            Clear filter
          </button>
        )}

      </div>

      {loading ? (
        <div className="page-state">
          <div className="loading-spinner" />

          <h2>
            Analysing skill signals
          </h2>

          <p>
            Processing current market and training
            indicators...
          </p>
        </div>
      ) : (
        <>
          {/* SUMMARY */}

          <div className="stats-grid compact">

            <StatCard
              icon={<TrendingUp />}
              label="Skills Analysed"
              value={formatNumber(skills.length)}
              detail={
                sector
                  ? `Filtered to ${sector}`
                  : "Current intelligence view"
              }
            />

            <StatCard
              icon={<Building2 />}
              label="Total Job Demand"
              value={formatNumber(
                skills.reduce(
                  (total, skill) =>
                    total +
                    Number(
                      skill.demand_job_count ||
                      skill.job_count ||
                      0
                    ),
                  0
                )
              )}
              detail="Across returned skill signals"
            />

            <StatCard
              icon={<GraduationCap />}
              label="Training Capacity"
              value={formatNumber(
                skills.reduce(
                  (total, skill) =>
                    total +
                    Number(
                      skill.allocated_skill_seats ||
                      skill.training_capacity ||
                      0
                    ),
                  0
                )
              )}
              detail="Allocated seat proxy"
            />

          </div>

          {/* TABLE */}

          <div className="panel">

            <PanelHeader
              title="Skill demand intelligence"
              subtitle={
                sector
                  ? `Signals for ${sector}`
                  : "Current skill demand and training indicators"
              }
            />

            {skills.length ? (
              <div className="table-wrapper">

                <table>

                  <thead>
                    <tr>
                      <th>Skill</th>
                      <th>Sector</th>
                      <th>Job Demand</th>
                      <th>Districts</th>
                      <th>Trend</th>
                      <th>Supply</th>
                    </tr>
                  </thead>

                  <tbody>

                    {skills.map((item, index) => (
                      <tr
                        key={
                          item.skill_id ||
                          item.skill ||
                          index
                        }
                      >

                        <td>
                          <strong>
                            {item.skill}
                          </strong>

                          <small>
                            {item.skill_family ||
                              "Skill"}
                          </small>
                        </td>

                        <td>
                          <span className="tag">
                            {item.skill_sector ||
                              "Unclassified"}
                          </span>
                        </td>

                        <td>
                          {formatNumber(
                            item.demand_job_count ||
                            item.job_count
                          )}
                        </td>

                        <td>
                          {formatNumber(
                            item.demand_district_count
                          )}
                        </td>

                        <td>
                          <TrendBadge
                            value={
                              item.skill_demand_trend_signal ||
                              "N/A"
                            }
                          />
                        </td>

                        <td>
                          <SupplyBadge
                            value={
                              item.training_capacity_signal ||
                              "N/A"
                            }
                          />
                        </td>

                      </tr>
                    ))}

                  </tbody>

                </table>

              </div>
            ) : (
              <div className="empty-state">
                No skill signals found for the
                selected sector.
              </div>
            )}

          </div>
        </>
      )}
    </section>
  );
}

function CoursesPage() {
  const [courses, setCourses] = useState([]);
  const [metadata, setMetadata] = useState(null);

  const [district, setDistrict] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadMetadata() {
      try {
        const response = await fetch(`${API}/api/metadata`);
        const data = await response.json();
        setMetadata(data);
      } catch (error) {
        setError(error.message);
      }
    }

    loadMetadata();
  }, []);

  useEffect(() => {
    async function loadCourses() {
      try {
        setLoading(true);
        setError(null);

        const params = new URLSearchParams();

        if (district) {
          params.append("district", district);
        }

        params.append("limit", "20");

        const response = await fetch(
          `${API}/api/courses/alignment?${params.toString()}`
        );

        if (!response.ok) {
          throw new Error(
            `Course API failed: ${response.status}`
          );
        }

        const data = await response.json();

        setCourses(data.courses || []);
      } catch (error) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    }

    loadCourses();
  }, [district]);

  if (error) {
    return (
      <div className="page-state error-state">
        <h2>Unable to load course intelligence</h2>
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
    <section>
      <div className="page-intro">
        <div>
          <div className="eyebrow">
            COURSE ALIGNMENT
          </div>

          <h2>
            Training ecosystem alignment
          </h2>

          <p>
            Compare training capacity with the skills
            currently demanded by employers.
          </p>
        </div>
      </div>

      {/* FILTERS */}

      <div className="card market-filters">
        <div className="filter-group">
          <label htmlFor="course-district">
            District
          </label>

          <select
            id="course-district"
            value={district}
            onChange={(event) =>
              setDistrict(event.target.value)
            }
          >
            <option value="">
              All districts
            </option>

            {metadata?.districts?.map((item) => (
              <option
                key={item}
                value={item}
              >
                {item}
              </option>
            ))}
          </select>
        </div>

        {district && (
          <button
            className="secondary-button"
            onClick={() => setDistrict("")}
          >
            Clear filter
          </button>
        )}
      </div>

      {loading ? (
        <div className="page-state">
          <div className="loading-spinner" />

          <h2>
            Analysing training alignment
          </h2>

          <p>
            Comparing courses with market demand...
          </p>
        </div>
      ) : (
        <>
          {/* SUMMARY */}

          <div className="stats-grid compact">
            <StatCard
              icon={<GraduationCap />}
              label="Training Courses"
              value={formatNumber(courses.length)}
              detail={
                district
                  ? `Available in ${district}`
                  : "Current alignment view"
              }
            />

            <StatCard
              icon={<TrendingUp />}
              label="Demand Signals"
              value={formatNumber(
                courses.reduce(
                  (total, course) =>
                    total +
                    Number(course.demand_score || 0),
                  0
                )
              )}
              detail="Aggregated demand score"
            />

            <StatCard
              icon={<Building2 />}
              label="Training Providers"
              value={formatNumber(
                courses.reduce(
                  (total, course) =>
                    total +
                    Number(course.iti_count || 0),
                  0
                )
              )}
              detail="ITI-course availability"
            />
          </div>

          {/* TABLE */}

          <div className="panel">
            <PanelHeader
              title="Course alignment"
              subtitle={
                district
                  ? `Training courses relevant to ${district}`
                  : "Training courses mapped against industry demand"
              }
            />

            {courses.length ? (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>Course</th>
                      <th>ITIs</th>
                      <th>Skills</th>
                      <th>Demand Score</th>
                      <th>Placement</th>
                      <th>High Demand Skills</th>
                    </tr>
                  </thead>

                  <tbody>
                    {courses.map((course, index) => (
                      <tr
                        key={
                          course.course_name ||
                          index
                        }
                      >
                        <td>
                          <strong>
                            {course.course_name}
                          </strong>
                        </td>

                        <td>
                          {formatNumber(
                            course.iti_count
                          )}
                        </td>

                        <td>
                          {formatNumber(
                            course.skill_count
                          )}
                        </td>

                        <td>
                          <strong>
                            {formatNumber(
                              course.demand_score
                            )}
                          </strong>
                        </td>

                        <td>
                          {formatPercent(
                            course.average_placement_rate_pct
                          )}
                        </td>

                        <td>
                          <div className="mini-tags">
                            {(
                              course.high_demand_skills ||
                              []
                            )
                              .slice(0, 3)
                              .map((skill) => (
                                <span
                                  className="tag"
                                  key={skill}
                                >
                                  {skill}
                                </span>
                              ))}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="empty-state">
                No training courses found for the
                selected district.
              </div>
            )}
          </div>
        </>
      )}
    </section>
  );
}

function DistrictPage({
  metadata,
  district,
  loadDistrict,
}) {
  const districts = metadata?.districts || [];

  const skills =
    district?.skills ||
    district?.priority_skills ||
    district?.high_priority_skills ||
    [];

  return (
    <section>
      <div className="page-intro district-heading">
        <div>
          <div className="eyebrow">
            DISTRICT PLANNING
          </div>

          <h2>
            Local workforce intelligence
          </h2>

          <p>
            Identify demand, supply and priority skills
            at district level.
          </p>
        </div>

        <select
          value={
            district?.district ||
            district?.location ||
            districts[0] ||
            ""
          }
          onChange={(event) =>
            loadDistrict(event.target.value)
          }
        >
          {districts.map((item) => (
            <option
              key={item}
              value={item}
            >
              {item}
            </option>
          ))}
        </select>
      </div>

      {district ? (
        <>
          {/* DISTRICT SUMMARY */}

          <div className="stats-grid compact">

            <StatCard
              icon={<Map />}
              label="District"
              value={
                district.district ||
                district.location ||
                "Selected"
              }
              detail="Current planning view"
            />

            <StatCard
              icon={<Building2 />}
              label="Jobs"
              value={formatNumber(
                district.total_jobs ||
                district.district_total_jobs
              )}
              detail="Local demand"
            />

            <StatCard
              icon={<TrendingUp />}
              label="Skills Analysed"
              value={formatNumber(
                district.total_skills ||
                skills.length
              )}
              detail="District skill signals"
            />

            <StatCard
              icon={<GraduationCap />}
              label="Priority Skills"
              value={formatNumber(
                skills.filter(
                  (item) =>
                    item.priority_band ===
                    "HIGH_PRIORITY"
                ).length
              )}
              detail="High-priority signals"
            />

          </div>

          {/* SKILL PRIORITIES */}

          <div className="panel">

            <PanelHeader
              title="District skill priorities"
              subtitle="Demand and supply signals"
            />

            {skills.length ? (
              <div className="table-wrapper">

                <table>

                  <thead>
                    <tr>
                      <th>Skill</th>
                      <th>Demand</th>
                      <th>Supply</th>
                      <th>Trend</th>
                      <th>Priority</th>
                    </tr>
                  </thead>

                  <tbody>

                    {skills
                      .slice(0, 20)
                      .map((skill, index) => {

                        const demand =
                          skill.demand_job_count ??
                          skill.job_count ??
                          0;

                        const supply =
                          skill.allocated_skill_seats ??
                          0;

                        const priority =
                          skill.priority_band ||
                          skill.supply_status ||
                          "MONITOR";

                        return (
                          <tr
                            key={
                              skill.skill_id ||
                              skill.skill ||
                              index
                            }
                          >

                            <td>
                              <strong>
                                {skill.skill}
                              </strong>

                              <small>
                                {skill.skill_family ||
                                  skill.skill_sector ||
                                  "Skill"}
                              </small>
                            </td>

                            <td>
                              {formatNumber(demand)}
                              <small>
                                jobs
                              </small>
                            </td>

                            <td>
                              {formatNumber(supply)}
                              <small>
                                allocated seats
                              </small>
                            </td>

                            <td>
                              <TrendBadge
                                value={
                                  skill
                                    .district_skill_trend_signal ||
                                  skill
                                    .skill_demand_trend_signal ||
                                  "N/A"
                                }
                              />
                            </td>

                            <td>
                              <span
                                className={
                                  `priority-badge ` +
                                  getPriorityClass(
                                    priority
                                  )
                                }
                              >
                                {formatPriority(
                                  priority
                                )}
                              </span>
                            </td>

                          </tr>
                        );
                      })}

                  </tbody>

                </table>

              </div>
            ) : (
              <div className="empty-state">
                No district skill signals were returned.
              </div>
            )}

          </div>
        </>
      ) : (
        <div className="empty-state">
          Select a district to view workforce intelligence.
        </div>
      )}
    </section>
  );
}

function DistrictResults({ data }) {
  const skills =
    data.skills ||
    data.priority_skills ||
    data.high_priority_skills ||
    [];

  return (
    <>
      <div className="stats-grid compact">
        <StatCard
          icon={<Map />}
          label="District"
          value={data.district || data.location || "Selected"}
          detail="Current view"
        />

        <StatCard
          icon={<Building2 />}
          label="Jobs"
          value={formatNumber(
            data.total_jobs || data.district_total_jobs
          )}
          detail="Local demand"
        />

        <StatCard
          icon={<TrendingUp />}
          label="Priority Skills"
          value={formatNumber(skills.length)}
          detail="Current signals"
        />
      </div>

      <div className="panel">
        <PanelHeader
          title="District skill priorities"
          subtitle="Demand and supply signals"
        />

        {skills.length ? (
          <div className="skill-list">
            {skills.slice(0, 20).map((skill, index) => (
              <SkillRow
                key={skill.skill_id || skill.skill || index}
                skill={skill}
                rank={index + 1}
              />
            ))}
          </div>
        ) : (
          <div className="empty-state">
            No priority skills were returned for this district.
          </div>
        )}
      </div>
    </>
  );
}

function StatCard({ icon, label, value, detail }) {
  return (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>

      <div className="stat-content">
        <span>{label}</span>
        <strong>{value}</strong>
        <small>{detail}</small>
      </div>
    </div>
  );
}

function SkillRow({ skill, rank }) {
  return (
    <div className="skill-row">
      <div className="rank">{String(rank).padStart(2, "0")}</div>

      <div className="skill-main">
        <strong>{skill.skill}</strong>
        <span>
          {skill.skill_family || skill.skill_sector || "Skill"}
        </span>
      </div>

      <div className="skill-demand">
        <strong>
          {formatNumber(
            skill.demand_job_count ||
              skill.job_count ||
              skill.demand_count
          )}
        </strong>
        <span>jobs</span>
      </div>
    </div>
  );
}

function SkillBar({ skill, max, rank }) {
  const width = Math.max(
    5,
    ((skill.job_count || 0) / max) * 100
  );

  return (
    <div className="skill-bar-row">
      <div className="skill-bar-label">
        <span className="bar-rank">{rank}</span>
        <strong>{skill.skill}</strong>
        <span>
          {formatNumber(skill.job_count)} jobs
        </span>
      </div>

      <div className="bar-track">
        <div
          className="bar-fill"
          style={{ width: `${width}%` }}
        />
      </div>

      <span className="percentage">
        {formatPercent(skill.demand_percentage)}
      </span>
    </div>
  );
}

function CourseRow({ course }) {
  return (
    <div className="course-row">
      <div className="course-icon">
        <BookOpen size={18} />
      </div>

      <div className="course-info">
        <strong>{course.course_name}</strong>
        <span>
          {formatNumber(course.skill_count)} skills
        </span>
      </div>

      <span className="course-score">
        {formatNumber(course.demand_score)}
      </span>
    </div>
  );
}

function PanelHeader({ title, subtitle }) {
  return (
    <div className="panel-header">
      <div>
        <h3>{title}</h3>
        <p>{subtitle}</p>
      </div>
    </div>
  );
}

function TrendBadge({ value }) {
  const text = value || "N/A";

  return (
    <span className="trend-badge">
      <TrendingUp size={13} />
      {text}
    </span>
  );
}

function SupplyBadge({ value }) {
  return (
    <span className="supply-badge">
      {value || "N/A"}
    </span>
  );
}

function getPriorityClass(priority) {
  const value = String(priority)
    .toUpperCase()
    .replaceAll(" ", "_");

  if (value.includes("HIGH")) {
    return "priority-high";
  }

  if (
    value.includes("DEMAND") ||
    value.includes("GAP")
  ) {
    return "priority-medium";
  }

  return "priority-low";
}


function formatPriority(priority) {
  return String(priority || "MONITOR")
    .replaceAll("_", " ")
    .replace("HIGH PRIORITY", "HIGH PRIORITY");
}

function ProfilePage() {
  const [skills, setSkills] = useState([]);
  const [skillInput, setSkillInput] = useState("");
  const [district, setDistrict] = useState("");
  const [metadata, setMetadata] = useState({
    districts: [],
  });

  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [metadataLoading, setMetadataLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadMetadata() {
      try {
        setMetadataLoading(true);

        const data = await getMetadata();

        setMetadata(data);

        if (
          !district &&
          data.districts &&
          data.districts.length > 0
        ) {
          setDistrict(data.districts[0]);
        }
      } catch (err) {
        setError(
          "Unable to load district information."
        );
      } finally {
        setMetadataLoading(false);
      }
    }

    loadMetadata();
  }, []);

  function addSkill() {
    const value = skillInput.trim();

    if (!value) {
      return;
    }

    const exists = skills.some(
      (skill) =>
        skill.toLowerCase() === value.toLowerCase()
    );

    if (exists) {
      setSkillInput("");
      return;
    }

    setSkills((current) => [
      ...current,
      value,
    ]);

    setSkillInput("");
    setAnalysis(null);
    setError("");
  }

  function removeSkill(skillToRemove) {
    setSkills((current) =>
      current.filter(
        (skill) => skill !== skillToRemove
      )
    );

    setAnalysis(null);
  }

  function handleSkillKeyDown(event) {
    if (event.key === "Enter") {
      event.preventDefault();
      addSkill();
    }
  }

  async function analyzeSkills() {
    if (!district) {
      setError("Please select a preferred district.");
      return;
    }

    if (skills.length === 0) {
      setError(
        "Add at least one current skill before analysis."
      );
      return;
    }

    try {
      setLoading(true);
      setError("");
      setAnalysis(null);

      const result = await analyzeProfile({
        district,
        skills,
      });

      setAnalysis(result);
    } catch (err) {
      setError(
        err.message ||
        "Unable to analyze your skill profile."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-content">

      <div className="page-eyebrow">
        PERSONAL INTELLIGENCE
      </div>

      <div className="page-heading">
        <h2>My Skill Profile</h2>

        <p>
          Tell SkillSync what you already know.
          We'll identify relevant skill gaps and
          training paths.
        </p>
      </div>

      <div className="profile-grid">

        <section className="panel profile-form">

          <div className="panel-header">
            <div>
              <h3>Profile details</h3>
              <p>
                Help us understand your current
                context
              </p>
            </div>
          </div>

          <label className="form-label">
            PREFERRED DISTRICT
          </label>

          <select
            className="form-select"
            value={district}
            onChange={(event) => {
              setDistrict(event.target.value);
              setAnalysis(null);
            }}
            disabled={metadataLoading}
          >
            <option value="">
              Select district
            </option>

            {metadata.districts?.map(
              (item) => (
                <option
                  key={item}
                  value={item}
                >
                  {item}
                </option>
              )
            )}
          </select>

        </section>

        <section className="panel profile-form">

          <div className="panel-header">
            <div>
              <h3>Current skills</h3>
              <p>
                Add skills you already have
              </p>
            </div>
          </div>

          <div className="skill-input-row">

            <input
              className="form-input"
              value={skillInput}
              onChange={(event) =>
                setSkillInput(
                  event.target.value
                )
              }
              onKeyDown={
                handleSkillKeyDown
              }
              placeholder="e.g. Java, SQL, Python"
            />

            <button
              className="primary-button"
              onClick={addSkill}
            >
              <Plus size={16} />
              Add Skill
            </button>

          </div>

          {skills.length > 0 ? (

            <div className="profile-skill-list">

              {skills.map((skill) => (
                <div
                  className="profile-skill"
                  key={skill}
                >
                  <span>{skill}</span>

                  <button
                    onClick={() =>
                      removeSkill(skill)
                    }
                    aria-label={`Remove ${skill}`}
                  >
                    <X size={14} />
                  </button>
                </div>
              ))}

            </div>

          ) : (

            <p className="empty-state">
              No skills added yet.
            </p>

          )}

        </section>

      </div>

      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}

      <section className="panel profile-summary">

        <div className="profile-summary-content">

          <div>

            <div className="page-eyebrow">
              PROFILE ANALYSIS
            </div>

            <h3>
              {analysis
                ? `Skill intelligence for ${analysis.district}`
                : "Build your skill profile"}
            </h3>

            <p>
              {analysis
                ? `Analysis based on ${analysis.current_skills.length} current skills and local labour-market demand.`
                : district
                  ? `Planning recommendations will be aligned with ${district}.`
                  : "Select a district and add your current skills to begin."
              }
            </p>

          </div>

          <button
            className="primary-button analyze-button"
            onClick={analyzeSkills}
            disabled={
              loading ||
              !district ||
              skills.length === 0
            }
          >
            <Sparkles size={16} />

            {loading
              ? "Analyzing..."
              : "Analyze Skill Gap"}
          </button>

        </div>

      </section>

      {analysis && (

        <div className="profile-results">

          <section className="panel">

            <div className="panel-header">

              <div>
                <h3>Skill Gaps</h3>

                <p>
                  Skills currently demanded in{" "}
                  {analysis.district} that are
                  not in your profile.
                </p>
              </div>

              <span className="result-count">
                {analysis.skill_gaps.length}
              </span>

            </div>

            {analysis.skill_gaps.length === 0 ? (

              <div className="success-state">
                No skill gaps were identified
                from the current dataset.
              </div>

            ) : (

              <div className="skill-gap-list">

                {analysis.skill_gaps.map(
                  (gap) => (

                    <div
                      className="skill-gap-row"
                      key={gap.skill}
                    >

                      <div className="skill-gap-main">

                        <strong>
                          {gap.skill}
                        </strong>

                        <span>
                          {gap.reason}
                        </span>

                      </div>

                      <div className="skill-gap-demand">

                        <strong>
                          {gap.demand_percentage.toFixed(
                            1
                          )}%
                        </strong>

                        <span>
                          demand
                        </span>

                      </div>

                      <span
                        className={`priority-badge priority-${gap.priority.toLowerCase()}`}
                      >
                        {gap.priority}
                      </span>

                    </div>

                  )
                )}

              </div>

            )}

          </section>

          <section className="panel">

            <div className="panel-header">

              <div>
                <h3>
                  Recommended Training
                </h3>

                <p>
                  Training options matching
                  identified skill gaps.
                </p>
              </div>

              <span className="result-count">
                {
                  analysis
                    .recommended_courses
                    .length
                }
              </span>

            </div>

            {analysis.recommended_courses
              .length === 0 ? (

              <div className="empty-state">
                No matching training
                recommendations were found
                for this profile and district.
              </div>

            ) : (

              <div className="course-recommendation-list">

                {analysis.recommended_courses.map(
                  (course, index) => (

                    <div
                      className="course-recommendation"
                      key={`${course.course_name}-${course.iti_name}-${index}`}
                    >

                      <div>
                        <strong>
                          {course.course_name}
                        </strong>

                        <span>
                          {course.iti_name}
                        </span>

                        <small>
                          {course.matched_skills.join(
                            ", "
                          )}
                        </small>
                      </div>

                      <div className="placement-rate">
                        {course.placement_rate_pct > 0 ? (
                          <>
                            <strong>
                              {course.placement_rate_pct.toFixed(1)}%
                            </strong>
                            <span>placement</span>
                          </>
                        ) : (
                          <>
                            <strong>Recommended</strong>
                            <span>learning path</span>
                          </>
                        )}
                      </div>
                  </div>

                  )
                )}

              </div>

            )}

          </section>

        </div>

      )}

    </div>
  );
}

function Loading() {
  return (
    <div className="loading-screen">
      <div className="loading-spinner" />
      <strong>Loading SkillSync intelligence...</strong>
      <span>Connecting to the data engine</span>
    </div>
  );
}

function getPageTitle(page) {
  const titles = {
    overview: "Intelligence Overview",
    market: "Market Intelligence",
    skills: "Skill Intelligence",
    courses: "Course Alignment",
    districts: "District Planning",
    profile: "My Skill Profile",
  };

  return titles[page];
}

function formatNumber(value) {
  if (value === undefined || value === null) {
    return "0";
  }

  return new Intl.NumberFormat("en-IN").format(
    Number(value) || 0
  );
}

function formatPercent(value) {
  if (value === undefined || value === null) {
    return "0%";
  }

  return `${Number(value).toFixed(1)}%`;
}

export default App;