import { useEffect, useState } from "react";

import {
  getMetadata,
  getDistrictIntelligence,
} from "../api";

export default function Districts() {
  const [metadata, setMetadata] = useState(null);
  const [district, setDistrict] = useState("");
  const [data, setData] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadMetadata() {
      try {
        const data = await getMetadata();

        setMetadata(data);

        if (data?.districts?.length > 0) {
          setDistrict(data.districts[0]);
        }
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    }

    loadMetadata();
  }, []);

  useEffect(() => {
    if (!district) {
      return;
    }

    async function loadDistrict() {
      try {
        setLoading(true);
        setError(null);

        const result =
          await getDistrictIntelligence(
            district,
            20
          );

        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadDistrict();
  }, [district]);

  if (loading) {
    return (
      <div className="page-state">

        <div className="loading-spinner"></div>

        <h2>
          Loading district intelligence
        </h2>

        <p>
          Analysing local workforce signals...
        </p>

      </div>
    );
  }

  if (error) {
    return (
      <div className="page-state error-state">

        <h2>
          Unable to load district intelligence
        </h2>

        <p>
          {error}
        </p>

        <button
          className="primary-button"
          onClick={() =>
            window.location.reload()
          }
        >
          Retry
        </button>

      </div>
    );
  }

  return (
    <div>

      {/* HEADER */}

      <div className="page-header">

        <div>

          <p className="eyebrow">
            DISTRICT PLANNING
          </p>

          <h1 className="page-title">
            Local workforce intelligence
          </h1>

          <p className="page-description">
            Identify demand, supply and priority
            skills at district level.
          </p>

        </div>

        {/* DISTRICT SELECTOR */}

        <select
          value={district}
          onChange={(event) =>
            setDistrict(event.target.value)
          }
          style={{
            minWidth: "220px",
            padding: "12px 14px",
            borderRadius: "8px",
            border: "1px solid #dbe2ea",
            background: "white",
          }}
        >

          {metadata?.districts?.map(
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

      </div>

      {/* KPI */}

      <div className="stats-grid">

        <div className="stat-card">

          <div className="stat-icon">
            ◇
          </div>

          <div>

            <div className="stat-label">
              District
            </div>

            <div className="stat-value">
              {data?.district ||
                district}
            </div>

            <div className="stat-meta">
              Current view
            </div>

          </div>

        </div>

        <div className="stat-card">

          <div className="stat-icon">
            ▣
          </div>

          <div>

            <div className="stat-label">
              Skills
            </div>

            <div className="stat-value">
              {data?.total_skills ?? "..."}
            </div>

            <div className="stat-meta">
              Local skill signals
            </div>

          </div>

        </div>

      </div>

      {/* SKILLS */}

      <div
        className="card"
        style={{
          marginTop: "28px",
          padding: "22px",
        }}
      >

        <div className="card-header">

          <div>

            <h3>
              District skill priorities
            </h3>

            <p>
              Local demand and supply signals
            </p>

          </div>

        </div>

        <div className="trend-list">

          {data?.skills?.map(
            (skill, index) => (
              <div
                className="trend-row"
                key={
                  skill.skill_id ||
                  skill.skill ||
                  index
                }
              >

                <div className="trend-rank">
                  {String(index + 1).padStart(
                    2,
                    "0"
                  )}
                </div>

                <div className="trend-info">

                  <strong>
                    {skill.skill}
                  </strong>

                  <span>
                    {skill.skill_family ||
                      skill.skill_sector ||
                      "Skill"}
                  </span>

                </div>

                <div className="trend-value">

                  {(
                    skill.job_count ??
                    skill.demand_job_count ??
                    0
                  ).toLocaleString()}

                  <span>
                    jobs
                  </span>

                </div>

              </div>
            )
          )}

        </div>

      </div>

    </div>
  );
}