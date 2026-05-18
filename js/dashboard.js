const API = 'http://127.0.0.1:5000/api';

// ── AUTH CHECK ─────────────────────────────────────────
const stored = localStorage.getItem('ccs_user');
if (!stored) {
  window.location.href = '/login-register/index.html';
}

const user = JSON.parse(stored);

// ── POPULATE STUDENT INFO PANEL ────────────────────────
document.getElementById('si-name').textContent     = user.fullname    || '—';
document.getElementById('si-course').textContent   = user.course      || '—';
document.getElementById('si-year').textContent     = user.level       || '—';
document.getElementById('si-email').textContent    = user.email       || '—';
document.getElementById('si-address').textContent  = user.address     || 'Not set';
document.getElementById('si-sessions').textContent = user.remaining_session ?? '—';

// Navbar user
document.getElementById('nav-username').textContent = user.firstname || user.fullname.split(',')[0].trim();
document.getElementById('nav-avatar').textContent   = (user.lastname || user.fullname).charAt(0).toUpperCase();

// Profile picture initials fallback
const initialsEl = document.getElementById('profile-initials');
if (initialsEl) {
  const initials = ((user.firstname || '').charAt(0) + (user.lastname || '').charAt(0)).toUpperCase();
  initialsEl.textContent = initials || user.fullname.charAt(0).toUpperCase();
}

// Profile picture — load from localStorage if previously set
const savedPic = localStorage.getItem('ccs_profile_pic_' + user.id);
if (savedPic) {
  const picEl = document.getElementById('profile-pic-display');
  picEl.innerHTML = `<img src="${savedPic}" alt="Profile"/>`;
}

// Profile picture file input (triggered via dropdown)
const picInput = document.getElementById('profile-pic-input');
const changePhotoTrigger = document.getElementById('change-photo-trigger');
if (changePhotoTrigger && picInput) {
  changePhotoTrigger.addEventListener('click', (e) => {
    e.preventDefault();
    picInput.click();
  });
  picInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (ev) => {
      const dataUrl = ev.target.result;
      const picEl = document.getElementById('profile-pic-display');
      picEl.innerHTML = `<img src="${dataUrl}" alt="Profile"/>`;
      localStorage.setItem('ccs_profile_pic_' + user.id, dataUrl);
    };
    reader.readAsDataURL(file);
  });
}

// User dropdown toggle
const userDropdownToggle = document.getElementById('userDropdownToggle');
const userDropdownMenu   = document.getElementById('userDropdownMenu');
if (userDropdownToggle && userDropdownMenu) {
  userDropdownToggle.addEventListener('click', (e) => {
    e.preventDefault();
    userDropdownMenu.classList.toggle('open');
  });
  document.addEventListener('click', (e) => {
    if (!userDropdownToggle.contains(e.target) && !userDropdownMenu.contains(e.target)) {
      userDropdownMenu.classList.remove('open');
    }
  });
}

// ── LOAD ANNOUNCEMENTS ─────────────────────────────────
async function loadAnnouncements() {
  const panel = document.getElementById('ann-panel');
  try {
    const res  = await fetch(API + '/admin/announcements', { credentials: 'include' });
    const data = await res.json();
    const anns = data.announcements || [];

    if (anns.length === 0) {
      panel.innerHTML = '<div class="ann-empty">No announcements yet.</div>';
      return;
    }

    panel.innerHTML = anns.map(a => `
      <div class="ann-item">
        <div class="ann-item-meta">${a.author} | ${formatDate(a.created)}</div>
        <div class="ann-item-text">${a.content}</div>
      </div>`).join('');
  } catch {
    panel.innerHTML = '<div class="ann-empty">Could not load announcements.</div>';
  }
}

function formatDate(d) {
  if (!d) return '—';
  return new Date(d).toLocaleDateString('en-PH', { year: 'numeric', month: 'short', day: 'numeric' });
}

function timeAgo(d) {
  if (!d) return '';
  const diff = Math.floor((Date.now() - new Date(d)) / 1000);
  if (diff < 60)   return 'Just now';
  if (diff < 3600) return Math.floor(diff / 60) + 'm ago';
  if (diff < 86400) return Math.floor(diff / 3600) + 'h ago';
  return formatDate(d);
}

// ── LOGOUT ─────────────────────────────────────────────
document.getElementById('logout-btn').addEventListener('click', async () => {
  try { await fetch(API + '/logout', { method: 'POST', credentials: 'include' }); } catch {}
  localStorage.removeItem('ccs_user');
  window.location.href = '/login-register/index.html';
});

// ══════════════════════════════════════════════════════
//  NOTIFICATION SYSTEM
// ══════════════════════════════════════════════════════

const NOTIF_ICONS = {
  announcement: '📢',
  sitin:        '✅',
  reservation:  '📋',
  info:         '🔔',
};

let lastUnreadCount = 0;
let notifOpen = false;

// ── Toast pop-up ───────────────────────────────────────
function showToast(type, title, message) {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <div class="toast-icon">${NOTIF_ICONS[type] || '🔔'}</div>
    <div class="toast-body">
      <div class="toast-title">${title}</div>
      <div class="toast-msg">${message}</div>
    </div>
    <button class="toast-close" onclick="dismissToast(this.parentElement)">×</button>
  `;
  container.appendChild(toast);
  // Auto-dismiss after 6 seconds
  setTimeout(() => dismissToast(toast), 6000);
}

function dismissToast(el) {
  if (!el || el.classList.contains('hiding')) return;
  el.classList.add('hiding');
  setTimeout(() => el && el.remove(), 300);
}

// ── Render notification list in dropdown ───────────────
function renderNotifList(notifications) {
  const list = document.getElementById('notif-list');
  if (!notifications.length) {
    list.innerHTML = '<div class="notif-empty">No notifications yet.</div>';
    return;
  }
  list.innerHTML = notifications.map(n => `
    <div class="notif-item ${n.is_read ? '' : 'unread'}" data-id="${n.id}" onclick="markOneRead(${n.id}, this)">
      <div class="notif-dot ${n.is_read ? 'read' : ''}"></div>
      <div class="notif-icon-circle ${n.type}">${NOTIF_ICONS[n.type] || '🔔'}</div>
      <div class="notif-body">
        <div class="n-title">${n.title}</div>
        <div class="n-msg">${n.message}</div>
        <div class="n-time">${timeAgo(n.created)}</div>
      </div>
    </div>
  `).join('');
}

// ── Update badge count ─────────────────────────────────
function updateBadge(count) {
  const badge = document.getElementById('notif-badge');
  if (count > 0) {
    badge.textContent = count > 99 ? '99+' : count;
    badge.style.display = 'flex';
  } else {
    badge.style.display = 'none';
  }
}

// ── Poll the server for new notifications ──────────────
async function pollNotifications() {
  try {
    const res  = await fetch(`${API}/notifications/${user.id}`, { credentials: 'include' });
    const data = await res.json();
    if (!data.success) return;

    const notifications = data.notifications || [];
    const unreadCount   = notifications.filter(n => !n.is_read).length;

    // Show toast only for genuinely new notifications since last poll
    if (unreadCount > lastUnreadCount) {
      const newest = notifications.find(n => !n.is_read);
      if (newest) showToast(newest.type, newest.title, newest.message);
    }

    lastUnreadCount = unreadCount;
    updateBadge(unreadCount);

    // Re-render dropdown list if it's open
    if (notifOpen) renderNotifList(notifications);

    // Store for dropdown open rendering
    window._cachedNotifs = notifications;
  } catch (e) {
    // Silently fail — don't break the page if notifications are unavailable
  }
}

// ── Mark a single notification as read ────────────────
async function markOneRead(nid, el) {
  try {
    await fetch(`${API}/notifications/${nid}/read`, { method: 'POST', credentials: 'include' });
    el.classList.remove('unread');
    el.querySelector('.notif-dot').classList.add('read');
    lastUnreadCount = Math.max(0, lastUnreadCount - 1);
    updateBadge(lastUnreadCount);
  } catch {}
}

// ── Mark all as read ───────────────────────────────────
document.getElementById('notif-mark-all').addEventListener('click', async () => {
  try {
    await fetch(`${API}/notifications/${user.id}/mark-read`, { method: 'POST', credentials: 'include' });
    document.querySelectorAll('.notif-item.unread').forEach(el => {
      el.classList.remove('unread');
      el.querySelector('.notif-dot').classList.add('read');
    });
    lastUnreadCount = 0;
    updateBadge(0);
  } catch {}
});

// ── Bell click — open/close dropdown ──────────────────
const notifBell     = document.getElementById('notif-bell');
const notifDropdown = document.getElementById('notif-dropdown');

notifBell.addEventListener('click', (e) => {
  e.stopPropagation();
  notifOpen = !notifOpen;
  notifDropdown.classList.toggle('open', notifOpen);
  if (notifOpen && window._cachedNotifs) {
    renderNotifList(window._cachedNotifs);
  }
});

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
  if (!notifBell.contains(e.target) && !notifDropdown.contains(e.target)) {
    notifOpen = false;
    notifDropdown.classList.remove('open');
  }
});

// ── START POLLING ──────────────────────────────────────
// Poll immediately on load, then every 15 seconds
pollNotifications();
setInterval(pollNotifications, 15000);

// ── INIT ───────────────────────────────────────────────
loadAnnouncements();
// ══════════════════════════════════════════════════════
//  SIT-IN SUMMARY + SESSIONS TABLE
// ══════════════════════════════════════════════════════

function fmtTime(dt) {
  if (!dt || dt === '—') return '—';
  // If already HH:MM format, return as-is
  if (/^\d{1,2}:\d{2}$/.test(dt.trim())) return dt.trim();
  // Otherwise try parsing as full datetime
  const d = new Date(dt);
  if (isNaN(d.getTime())) return '—';
  try { return d.toLocaleTimeString('en-PH', { hour: '2-digit', minute: '2-digit' }); }
  catch { return '—'; }
}

function fmtDuration(mins) {
  if (mins == null || mins === 0 || mins === '—') return '—';
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
}

async function loadSitInSummary() {
  try {
    const res  = await fetch(API + '/student/sit-in-summary', { credentials: 'include' });
    const data = await res.json();
    if (data.error) return;

    const s = data.summary;
    document.getElementById('sum-total-hours').textContent = (s.total_hours && s.total_hours > 0) ? s.total_hours + 'h' : '—';
    document.getElementById('sum-sessions').textContent    = s.total_sessions ?? 0;
    document.getElementById('sum-avg').textContent         = fmtDuration(s.avg_duration_minutes);
    document.getElementById('sum-longest').textContent     = fmtDuration(s.longest_session_minutes);

    const tbody = document.getElementById('sum-table-body');
    if (!data.sessions || data.sessions.length === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="sum-empty">No sessions recorded yet.</td></tr>';
      return;
    }

    tbody.innerHTML = data.sessions.map(s => `
      <tr>
        <td>${s.date || '—'}</td>
        <td>${s.lab || '—'}</td>
        <td>${s.pc_number || '—'}</td>
        <td>${fmtTime(s.time_in)}</td>
        <td>${fmtTime(s.time_out)}</td>
        <td>${fmtDuration(s.duration_minutes)}</td>
        <td><span class="sum-badge ${s.status === 'Active' ? 'sum-badge-active' : 'sum-badge-done'}">${s.status}</span></td>
      </tr>`).join('');
  } catch (e) {
    document.getElementById('sum-table-body').innerHTML =
      '<tr><td colspan="7" class="sum-empty">Could not load sessions.</td></tr>';
  }
}

loadSitInSummary();