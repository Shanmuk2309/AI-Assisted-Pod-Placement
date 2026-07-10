const SCENARIO_API = "http://localhost:8000";
const ADVISOR_API = "http://localhost:8001";

async function handleResponse(response) {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || data.error || data.message || "Request failed");
  }
  return data;
}

export async function generateScenarios(count) {
  const response = await fetch(
    `${SCENARIO_API}/scenarios/generate?count=${count}`,
    { method: "POST" }
  );
  return handleResponse(response);
}

export async function getScenarioCount() {
  const response = await fetch(`${SCENARIO_API}/scenarios/count`);
  return handleResponse(response);
}

export async function generateDataset() {
  const response = await fetch(`${SCENARIO_API}/dataset/generate`, {
    method: "POST",
  });
  return handleResponse(response);
}

export async function getDatasetStatus() {
  const response = await fetch(`${SCENARIO_API}/dataset/status`);
  return handleResponse(response);
}

export async function listScenarios() {
  const response = await fetch(`${SCENARIO_API}/scenarios`);
  return handleResponse(response);
}

export async function clearScenarios() {
  const response = await fetch(`${SCENARIO_API}/scenarios/clear`, {
    method: "DELETE",
  });
  return handleResponse(response);
}

export async function recommendDataset(scenario) {
  const response = await fetch(`${SCENARIO_API}/dataset/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(scenario),
  });
  return handleResponse(response);
}

export async function recommendBaseline(scenarioId) {
  const response = await fetch(
    `${ADVISOR_API}/recommend/baseline/${scenarioId}`
  );

  return handleResponse(response);
}
export async function recommendBaselineBody(scenario) {
  const response = await fetch(`${ADVISOR_API}/recommend/baseline`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(scenario),
  });
  return handleResponse(response);
}

export async function recommendMLBody(scenario) {
  const response = await fetch(`${ADVISOR_API}/recommend/ml`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(scenario),
  });
  return handleResponse(response);
}
export async function recommendML(scenarioId) {
  const response = await fetch(
    `${ADVISOR_API}/recommend/ml/${scenarioId}`
  );

  return handleResponse(response);
}