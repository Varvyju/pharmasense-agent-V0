const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function handle(res) {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json();
}

export async function getPatients() {
  const res = await fetch(`${BASE_URL}/api/patients`);
  return handle(res);
}

export async function getPatient(patientId) {
  const res = await fetch(`${BASE_URL}/api/patients/${patientId}`);
  return handle(res);
}

export async function getKnowledgeBase() {
  const res = await fetch(`${BASE_URL}/api/knowledge-base`);
  return handle(res);
}

export async function analyzePatient(patientId) {
  const res = await fetch(`${BASE_URL}/api/agent/analyze/${patientId}`, {
    method: "POST",
  });
  return handle(res);
}
