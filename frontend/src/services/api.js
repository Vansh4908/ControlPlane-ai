const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://localhost:5000/api";

async function request(endpoint, options = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(data.error || data.message || `Request failed with status ${response.status}`);
    }

    return data;
  } catch (err) {
    if (err.name === "TypeError" && err.message === "Failed to fetch") {
      throw new Error("Failed to fetch response from backend service. Please check network connection or backend server status.");
    }
    throw err;
  }
}

export async function getApplications() {
  return request("/applications");
}

export async function getPolicies() {
  return request("/policies");
}

export async function createEvaluation(payload) {
  if (payload instanceof FormData) {
    try {
      const response = await fetch(`${API_BASE_URL}/evaluations`, {
        method: "POST",
        body: payload,
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.error || data.message || "Failed to submit evaluation");
      }
      return data;
    } catch (err) {
      if (err.name === "TypeError" && err.message === "Failed to fetch") {
        throw new Error("Failed to fetch response from backend service. Please check network connection or backend server status.");
      }
      throw err;
    }
  }

  return request("/evaluations", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getReviewQueue() {
  return request("/evaluations/review");
}

export async function submitHumanReview(evaluationId, payload) {
  return request(`/evaluations/${evaluationId}/review`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getAuditLogs(evaluationId) {
  return request(`/evaluations/${evaluationId}/audit`);
}

export async function getEvaluationHistory() {
  return request("/evaluations/history");
}