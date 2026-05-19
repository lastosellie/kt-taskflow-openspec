// JWT localStorage 유틸리티
const TOKEN_KEY = "tf_token";
const USER_KEY  = "tf_user";

export const Auth = {
  save(token, user) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },
  token()  { return localStorage.getItem(TOKEN_KEY); },
  user()   { const u = localStorage.getItem(USER_KEY); return u ? JSON.parse(u) : null; },
  clear()  { localStorage.removeItem(TOKEN_KEY); localStorage.removeItem(USER_KEY); },
  check()  { if (!this.token()) { location.href = "/static/login.html"; } },
};

// API fetch 래퍼 (Authorization 자동 주입, 401 → 로그인 리다이렉트)
export async function api(path, options = {}) {
  const token = Auth.token();
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(path, { ...options, headers });

  if (res.status === 401) {
    Auth.clear();
    location.href = "/static/login.html";
    return;
  }

  const data = await res.json().catch(() => null);
  if (!res.ok) throw { status: res.status, detail: data };
  return data;
}

// 채팅 5초 폴링 (exponential backoff)
export function startPolling(teamId, onMessages, onError) {
  let lastSince = new Date().toISOString();
  let interval  = 5000;
  let timer     = null;

  async function poll() {
    try {
      const msgs = await api(`/teams/${teamId}/messages?since=${encodeURIComponent(lastSince)}`);
      if (msgs && msgs.length > 0) {
        lastSince = msgs[msgs.length - 1].created_at;
        onMessages(msgs);
      }
      interval = 5000; // 성공 시 정상 간격 복원
    } catch (err) {
      interval = Math.min(interval * 2, 60000); // 실패 시 최대 60초까지 backoff
      if (onError) onError(err);
    }
    timer = setTimeout(poll, interval);
  }

  poll();
  return () => clearTimeout(timer); // stop 함수 반환
}
