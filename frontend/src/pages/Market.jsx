import { useEffect, useState } from "react";

import {
  getMarketSummary,
  getMetadata,
} from "../api";

export default function Market() {
  const [market, setMarket] = useState(null);
  const [metadata, setMetadata] = useState(null);

  const [district, setDistrict] = useState("");
  const [sector, setSector] = useState("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load dropdown metadata once
  useEffect(() => {
    async function loadMetadata() {
      try {
        const data = await getMetadata();
        setMetadata(data);
      } catch (err) {
        setError(err.message);
      }
    }

    loadMetadata();
  }, []);

  // Reload market intelligence whenever filters change
  useEffect(() => {
    async function loadMarket() {
      try {
        setLoading(true);
        setError(null);

        const data = await getMarketSummary({
          district,
          sector,
        });

        setMarket(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadMarket();
  }, [district, sector]);

  if (error) {
    return (
      <div className="page-state error-state">
        <h2>Unable to load market intelligence</h2>
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
            Market Intelligence
          </h1>

          <p className="page-description">
            Explore industry skill demand across
            Maharashtra by district and sector.
          </p>
        </div>
      </div>

      {/* FILTERS */}
      <div className="card market-filters">
        <div className="filter-group">
          <label htmlFor="district">
            District
          </label>

          <select
            id="district"
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

        <div className="filter-group">
          <label htmlFor="sector">
            Sector
          </label>

          <select
            id="sector"
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

        {(district || sector) && (
          <button
            className="secondary-button"
            onClick={() => {
              setDistrict("");
              setSector("");
            }}
          >
            Clear filters
          </button>
        )}
      </div>

      {/* LOADING */}
      {loading ? (
        <div className="page-state">
          <div className="loading-spinner"></div>

          <h2>
            Analysing market demand
          </h2>

          <p>
            Processing the selected market segment...
          </p>
        </div>
      ) : (
        <>
          {/* KPI CARDS */}
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">
                ▣
              </div>

              <div>
                <div className="stat-label">
                  Jobs Analysed
                </div>

                <div className="stat-value">
                  {market?.job_count?.toLocaleString() ?? 0}
                </div>

                <div className="stat-meta">
                  Matching selected filters
                </div>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">
                ↗
              </div>

              <div>
                <div className="stat-label">
                  Skills Tracked
                </div>

                <div className="stat-value">
                  {market?.skill_count?.toLocaleString() ?? 0}
                </div>

                <div className="stat-meta">
                  Normalised skill signals
                </div>
              </div>
            </div>
          </div>

          {/* MARKET SIGNALS */}
          <div className="section-header">
            <div>
              <p className="eyebrow">
                DEMAND SIGNALS
              </p>

              <h2>
                Most demanded skills
              </h2>
            </div>

            <span className="section-link">
              {district || sector
                ? "Filtered view"
                : "Maharashtra-wide view"}
            </span>
          </div>

          <div className="card intelligence-card">
            <div className="skill-list">
              {market?.top_skills
                ?.slice(0, 10)
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
                      <span>
                        jobs
                      </span>
                    </div>
                  </div>
                ))}

              {!market?.top_skills?.length && (
                <div className="empty-state">
                  No matching skill demand found.
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}