const API_PREFIX = "/api/v1";

function getToken() {
  return localStorage.getItem("tm_token") || "";
}

function setToken(token) {
  localStorage.setItem("tm_token", token);
}

function clearToken() {
  localStorage.removeItem("tm_token");
}

function readJsonInput(id) {
  const raw = document.getElementById(id).value.trim();
  if (!raw) {
    return {};
  }
  return JSON.parse(raw);
}

function writeOutput(id, data) {
  const box = document.getElementById(id);
  box.textContent = typeof data === "string" ? data : JSON.stringify(data, null, 2);
}

async function apiRequest(path, options = {}) {
  const method = options.method || "GET";
  const auth = options.auth !== false;
  const form = options.form === true;
  const body = options.body;

  const headers = {};
  if (auth) {
    const token = getToken();
    if (!token) {
      throw new Error("No token, please login first.");
    }
    headers.Authorization = `Bearer ${token}`;
  }
  if (!form) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(path, {
    method,
    headers,
    body: body === undefined ? undefined : (form ? body : JSON.stringify(body)),
  });
  const text = await response.text();
  let payload;
  try {
    payload = text ? JSON.parse(text) : {};
  } catch (_) {
    payload = { raw: text };
  }
  if (!response.ok) {
    const detail = payload.detail || payload.raw || response.statusText;
    throw new Error(`${response.status}: ${detail}`);
  }
  return payload;
}

async function register(email, password, username) {
  return apiRequest(`${API_PREFIX}/auth/register`, {
    method: "POST",
    auth: false,
    body: { email, password, username },
  });
}

async function login(email, password) {
  const form = new URLSearchParams();
  form.set("username", email);
  form.set("password", password);
  const data = await apiRequest(`${API_PREFIX}/auth/jwt/login`, {
    method: "POST",
    auth: false,
    form: true,
    body: form,
  });
  setToken(data.access_token);
  return data;
}

async function fetchMe() {
  return apiRequest(`${API_PREFIX}/users/me`);
}

async function fetchMyTeams() {
  return apiRequest(`${API_PREFIX}/teams`);
}

async function fetchTeam(teamId) {
  return apiRequest(`${API_PREFIX}/teams/${teamId}`);
}

async function fetchCapabilities(teamId) {
  return apiRequest(`${API_PREFIX}/teams/${teamId}/capabilities/me`);
}

function applyCapabilities(rootId, caps) {
  const root = document.getElementById(rootId);
  if (!root) {
    return;
  }
  root.querySelectorAll("[data-cap]").forEach((el) => {
    const key = el.getAttribute("data-cap");
    const allowed = Boolean(caps[key]);
    el.disabled = !allowed;
    if (!allowed) {
      el.title = `Not allowed: ${key}`;
    } else {
      el.title = "";
    }
  });
}

window.App = {
  API_PREFIX,
  getToken,
  setToken,
  clearToken,
  readJsonInput,
  writeOutput,
  apiRequest,
  register,
  login,
  fetchMe,
  fetchMyTeams,
  fetchTeam,
  fetchCapabilities,
  applyCapabilities,
};
