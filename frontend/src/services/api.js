const API_BASE = "http://127.0.0.1:8000/api";

async function request(endpoint) {
  const response = await fetch(`${API_BASE}${endpoint}`);

  if (!response.ok) {
    throw new Error(
      `API request failed: ${response.status}`
    );
  }

  return response.json();
}

export async function getHealth() {
  return request("/health");
}

export async function getMetadata() {
  return request("/metadata");
}

export async function getMarketSummary(
  district = null,
  sector = null
) {
  const params = new URLSearchParams();

  if (district) {
    params.set("district", district);
  }

  if (sector) {
    params.set("sector", sector);
  }

  const query = params.toString();

  return request(
    `/market/summary${query ? `?${query}` : ""}`
  );
}

export async function getSkillTrends(
  sector = null,
  limit = 10
) {
  const params = new URLSearchParams();

  if (sector) {
    params.set("sector", sector);
  }

  params.set("limit", limit);

  return request(`/skills/trends?${params.toString()}`);
}

export async function getCourseAlignment(
  district = null,
  limit = 10
) {
  const params = new URLSearchParams();

  if (district) {
    params.set("district", district);
  }

  params.set("limit", limit);

  return request(
    `/courses/alignment?${params.toString()}`
  );
}

export async function getDistrictIntelligence(
  district,
  limit = 20
) {
  const params = new URLSearchParams();
  params.set("limit", limit);

  return request(
    `/districts/${encodeURIComponent(district)}?${params.toString()}`
  );
}