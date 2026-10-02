import { useEffect, useState } from "react";

import { getCourseAlignment } from "../api";

export default function Courses() {
  const [courses, setCourses] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadCourses() {
      try {
        setLoading(true);
        setError(null);

        const data = await getCourseAlignment({
          limit: 20,
        });

        setCourses(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    loadCourses();
  }, []);

  if (loading) {
    return (
      <div className="page-state">
        <div className="loading-spinner"></div>

        <h2>Loading course intelligence</h2>

        <p>
          Comparing training capacity with
          industry demand...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page-state error-state">
        <h2>Unable to load course alignment</h2>

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
            COURSE ALIGNMENT
          </p>

          <h1 className="page-title">
            Training ecosystem alignment
          </h1>

          <p className="page-description">
            Compare training capacity with the skills
            currently demanded by employers.
          </p>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">⌂</div>

          <div>
            <div className="stat-label">
              Training Courses
            </div>

            <div className="stat-value">
              {courses?.total_courses?.toLocaleString() ?? 0}
            </div>

            <div className="stat-meta">
              Current alignment dataset
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <div>
            <h3>Course alignment</h3>

            <p>
              Training programs ranked against
              observed skill demand.
            </p>
          </div>
        </div>

        <div className="course-list">
          {courses?.courses?.map((course, index) => (
            <div
              className="course-row"
              key={
                course.course_name ||
                index
              }
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
                {(
                  course.demand_score ??
                  0
                ).toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}