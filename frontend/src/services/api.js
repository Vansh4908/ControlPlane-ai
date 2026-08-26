const API_BASE_URL = "http://localhost:5000/api";

async function request(endpoint, options = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Something went wrong");
  }

  return data;
}

export async function getApplications() {
  return request("/applications");
}

export async function getPolicies() {
  return request("/policies");
}

export async function createEvaluation(payload) {
  return request("/evaluations", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}