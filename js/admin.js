const API = 'http://127.0.0.1:5000/api';

// ── AUTH GUARD ─────────────────────────────────────────
function requireAdmin() {
  const admin = localStorage.getItem('ccs_admin');
  if (!admin) {
    window.location.href = '/login-register/admin-login.html';
    return null;
  }
  return JSON.parse(admin);
}

// ── SET ACTIVE NAV LINK ────────────────────────────────
function setActiveNav() {
  const page = window.location.pathname.split('/').pop();
  document.querySelectorAll('.admin-nav-links a').forEach(a => {
    a.classList.toggle('active', a.getAttribute('href') === page);
  });
}

// ── LOGOUT ─────────────────────────────────────────────
async function adminLogout() {
  try {
    await fetch(API + '/admin/logout', { method: 'POST', credentials: 'include' });
  } catch {}
  localStorage.removeItem('ccs_admin');
  window.location.href = '/login-register/admin-login.html';
}

// ── TOAST NOTIFICATION ─────────────────────────────────
function showToast(msg, type = 'success') {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = msg;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

// ── MODAL HELPERS ──────────────────────────────────────
function openModal(id)  { document.getElementById(id).classList.remove('hidden'); }
function closeModal(id) { document.getElementById(id).classList.add('hidden'); }

// ── FORMAT DATE ────────────────────────────────────────
function formatDate(dateStr) {
  if (!dateStr) return '—';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-PH', { year: 'numeric', month: 'short', day: 'numeric' });
}

// ── SIMPLE PIE CHART (Canvas) ──────────────────────────
function drawPieChart(canvasId, data, colors) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const total = data.reduce((s, d) => s + d.value, 0);
  if (total === 0) {
    ctx.fillStyle = 'rgba(255,255,255,0.05)';
    ctx.beginPath();
    ctx.arc(canvas.width/2, canvas.height/2, Math.min(canvas.width, canvas.height)/2 - 4, 0, Math.PI*2);
    ctx.fill();
    return;
  }
  let startAngle = -Math.PI / 2;
  const cx = canvas.width / 2, cy = canvas.height / 2;
  const r  = Math.min(cx, cy) - 4;

  data.forEach((item, i) => {
    const slice = (item.value / total) * Math.PI * 2;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.arc(cx, cy, r, startAngle, startAngle + slice);
    ctx.closePath();
    ctx.fillStyle = colors[i % colors.length];
    ctx.fill();
    startAngle += slice;
  });
}
