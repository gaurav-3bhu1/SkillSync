const API_BASE = "http://127.0.0.1:8000";

async function request(endpoint) {
  const response = await fetch(`${API_BASE}${endpoint}`);

  if (!response.ok) {
    throw new Error(
      `API request failed: ${response.status} ${response.statusText}`
    );
  }

  return response.json();
}

export async function getHealth() {
  return request("/api/health");
}

export async function getMetadata() {
  return request("/api/metadata");
}

export async function getMarketSummary({
  district = "",
  sector = "",
} = {}) {
  const params = new URLSearchParams();

  if (district) params.append("district", district);
  if (sector) params.append("sector", sector);

  const query = params.toString();

  return request(
    `/api/market/summary${query ? `?${query}` : ""}`
  );
}

export async function getSkillTrends({
  sector = "",
  limit = 10,
} = {}) {
  const params = new URLSearchParams();

  if (sector) params.append("sector", sector);
  params.append("limit", limit);

  return request(`/api/skills/trends?${params.toString()}`);
}

export async function getCourseAlignment({
  district = "",
  limit = 10,
} = {}) {
  const params = new URLSearchParams();

  if (district) params.append("district", district);
  params.append("limit", limit);

  return request(`/api/courses/alignment?${params.toString()}`);
}

export async function getDistrictIntelligence(
  district,
  limit = 20
) {
  const params = new URLSearchParams();
  params.append("limit", limit);

  return request(
    `/api/districts/${encodeURIComponent(district)}?${params.toString()}`
  );
}
export async function analyzeProfile({
  district,
  skills,
}) {
  const response = await fetch(
    `${API_BASE}/api/profile/analyze`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        district,
        skills,
      }),
    }
  );

  if (!response.ok) {
    throw new Error(
      `Profile analysis failed: ${response.status} ${response.statusText}`
    );
  }

  return response.json();
}