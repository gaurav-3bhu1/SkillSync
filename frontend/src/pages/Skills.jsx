import { useEffect, useState } from "react";

import { getSkillTrends } from "../api";

export default function Skills() {
  const [skills, setSkills] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadSkills() {
      try {
        setLoading(true);
        setError(null);

        const data = await getSkillTrends({
          limit: 20,
        });

        setSkills(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadSkills();
  }, []);

  if (loading) {
    return (
      <div className="page-state">
        <div className="loading-spinner"></div>

        <h2>Loading skill intelligence</h2>

        <p>
          Analysing skill demand signals...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-state error-state">
        <h2>Unable to load skill intelligence</h2>

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
      <div className="page-header">
        <div>
          <p className="eyebrow">
            SKILL INTELLIGENCE
          </p>

          <h1 className="page-title">
            Emerging skill signals
          </h1>

          <p className="page-description">
            Demand, supply and training indicators
            for individual skills.
          </p>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div>
            <h3>Current skill signals</h3>

            <p>
              Normalised demand signals from the
              current labour-market dataset.
            </p>
          </div>
        </div>

        <div className="trend-list">
          {skills?.skills?.map((skill, index) => (
            <div
              className="trend-row"
              key={
                skill.skill_id ||
                skill.skill ||
                index
              }
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
                {(
                  skill.demand_job_count ??
                  skill.job_count ??
                  0
                ).toLocaleString()}

                <span>
                  jobs
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}