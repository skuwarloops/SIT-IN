const API = 'http://127.0.0.1:5000/api';

// ── LOGIN TYPE TOGGLE ──────────────────────────────────
let currentLoginType = 'student';

function setLoginType(type) {
  currentLoginType = type;
  document.getElementById('student-login-fields').style.display = type === 'student' ? 'block' : 'none';
  document.getElementById('admin-login-fields').style.display   = type === 'admin'   ? 'block' : 'none';
  document.getElementById('btn-student-login').classList.toggle('active', type === 'student');
  document.getElementById('btn-admin-login').classList.toggle('active',   type === 'admin');
  clearErrors();
}

// ── TAB SWITCHING ──────────────────────────────────────
const tabs    = document.querySelectorAll('.tab');
const forms   = document.querySelectorAll('.form');
const success = document.getElementById('success');

function switchTab(name) {
  tabs.forEach(t => t.classList.toggle('active', t.dataset.tab === name));
  forms.forEach(f => f.classList.toggle('active', f.id === name));
  success.classList.add('hidden');
  clearErrors();
}

tabs.forEach(t => t.addEventListener('click', () => switchTab(t.dataset.tab)));
document.querySelectorAll('[data-switch]').forEach(l => {
  l.addEventListener('click', e => { e.preventDefault(); switchTab(l.dataset.switch); });
});

// ── HELPERS ────────────────────────────────────────────
function setError(el, errEl, msg) {
  if (errEl) errEl.textContent = msg;
  if (el)    el.classList.toggle('invalid', !!msg);
}

function clearErrors() {
  document.querySelectorAll('.error').forEach(e => e.textContent = '');
  document.querySelectorAll('input, select').forEach(i => i.classList.remove('invalid'));
  document.getElementById('login-server-err').innerHTML = '';
  document.getElementById('reg-server-err').innerHTML   = '';
  // clear login type-specific fields
  const loginIdErr = document.getElementById('login-id-number-err');
  if (loginIdErr) loginIdErr.textContent = '';
  const loginUnErr = document.getElementById('login-username-err');
  if (loginUnErr) loginUnErr.textContent = '';
}

function serverErr(id, msg) {
  document.getElementById(id).innerHTML = '<div class="server-error">' + msg + '</div>';
}

function showSuccess(msg) {
  forms.forEach(f => f.classList.remove('active'));
  success.classList.remove('hidden');
  document.getElementById('success-msg').textContent = msg;
}

function setBtn(id, loading, label) {
  const b = document.getElementById(id);
  b.disabled    = loading;
  b.textContent = loading ? 'Please wait...' : label;
}

// ── LOGIN ──────────────────────────────────────────────
document.getElementById('login').addEventListener('submit', async e => {
  e.preventDefault();
  clearErrors();

  if (currentLoginType === 'admin') {
    // ── ADMIN LOGIN
    const username = document.getElementById('login-username');
    const pass     = document.getElementById('login-admin-password');
    let ok = true;

    if (!username.value.trim()) {
      setError(username, document.getElementById('login-username-err'), 'Username is required.');
      ok = false;
    }
    if (!pass.value) {
      setError(pass, document.getElementById('login-admin-password-err'), 'Password is required.');
      ok = false;
    }
    if (!ok) return;

    setBtn('login-btn', true, 'Login');
    try {
      const res  = await fetch(API + '/admin/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ username: username.value.trim(), password: pass.value })
      });
      const data = await res.json();
      if (data.success) {
        localStorage.setItem('ccs_admin', JSON.stringify(data.admin));
        window.location.href = '/admin/home.html';
      } else {
        serverErr('login-server-err', data.message || 'Invalid admin credentials.');
      }
    } catch {
      serverErr('login-server-err', 'Cannot connect to server. Make sure app.py is running.');
    }
    setBtn('login-btn', false, 'Login');

  } else {
    // ── STUDENT LOGIN
    const idNum = document.getElementById('login-id-number');
    const pass  = document.getElementById('login-password');
    let ok = true;

    if (!idNum.value.trim()) {
      setError(idNum, document.getElementById('login-id-number-err'), 'Student ID is required.');
      ok = false;
    }
    if (!pass.value) {
      setError(pass, document.getElementById('login-password-err'), 'Password is required.');
      ok = false;
    }
    if (!ok) return;

    setBtn('login-btn', true, 'Login');
    try {
      const res  = await fetch(API + '/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ id_number: idNum.value.trim(), password: pass.value })
      });
      const data = await res.json();
      if (data.success) {
        localStorage.setItem('ccs_user', JSON.stringify(data.user));
        window.location.href = '/page/dashboard.html';
      } else {
        if (data.errors && data.errors.id_number)
          setError(idNum, document.getElementById('login-id-number-err'), data.errors.id_number);
        if (data.errors && data.errors.password)
          setError(pass, document.getElementById('login-password-err'), data.errors.password);
        if (!data.errors)
          serverErr('login-server-err', 'Login failed. Please try again.');
      }
    } catch {
      serverErr('login-server-err', 'Cannot connect to server. Make sure app.py is running.');
    }
    setBtn('login-btn', false, 'Login');
  }
});

// ── REGISTER ───────────────────────────────────────────
document.getElementById('register').addEventListener('submit', async e => {
  e.preventDefault();
  clearErrors();

  const idNumber    = document.getElementById('reg-id-number');
  const lastname    = document.getElementById('reg-lastname');
  const firstname   = document.getElementById('reg-firstname');
  const middlename  = document.getElementById('reg-middlename');
  const email       = document.getElementById('reg-email');
  const course      = document.getElementById('reg-course');
  const level       = document.getElementById('reg-level');
  const pass        = document.getElementById('reg-password');
  const conf        = document.getElementById('reg-confirm');
  let ok = true;

  if (!idNumber.value.trim())    { setError(idNumber,  document.getElementById('reg-id-number-err'), 'Student ID is required.');          ok = false; }
  if (!lastname.value.trim())    { setError(lastname,  document.getElementById('reg-lastname-err'),  'Last name is required.');           ok = false; }
  if (!firstname.value.trim())   { setError(firstname, document.getElementById('reg-firstname-err'), 'First name is required.');          ok = false; }
  if (!email.value.trim())       { setError(email,     document.getElementById('reg-email-err'),     'Email is required.');               ok = false; }
  if (!course.value)             { setError(course,    document.getElementById('reg-course-err'),    'Please select a course.');          ok = false; }
  if (!level.value)              { setError(level,     document.getElementById('reg-level-err'),     'Please select a year level.');      ok = false; }
  if (pass.value.length < 6)    { setError(pass,       document.getElementById('reg-password-err'),  'At least 6 characters required.');  ok = false; }
  if (pass.value !== conf.value) { setError(conf,       document.getElementById('reg-confirm-err'),   'Passwords do not match.');          ok = false; }
  if (!ok) return;

  setBtn('reg-btn', true, 'Create Account');
  try {
    const res  = await fetch(API + '/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({
        id_number:  idNumber.value.trim(),
        lastname:   lastname.value.trim(),
        firstname:  firstname.value.trim(),
        middlename: middlename.value.trim(),
        email:      email.value.trim(),
        address:    document.getElementById('reg-address').value.trim(),
        course:     course.value,
        level:      level.value,
        password:   pass.value,
        confirm:    conf.value
      })
    });
    const data = await res.json();

    if (data.success) {
      showSuccess(data.message);
      setTimeout(() => switchTab('login'), 1800);
    } else {
      if (data.errors) {
        if (data.errors.id_number) setError(idNumber,  document.getElementById('reg-id-number-err'), data.errors.id_number);
        if (data.errors.lastname)  setError(lastname,  document.getElementById('reg-lastname-err'),  data.errors.lastname);
        if (data.errors.firstname) setError(firstname, document.getElementById('reg-firstname-err'), data.errors.firstname);
        if (data.errors.email)     setError(email,     document.getElementById('reg-email-err'),     data.errors.email);
        if (data.errors.course)    setError(course,    document.getElementById('reg-course-err'),    data.errors.course);
        if (data.errors.level)     setError(level,     document.getElementById('reg-level-err'),     data.errors.level);
        if (data.errors.password)  setError(pass,      document.getElementById('reg-password-err'),  data.errors.password);
        if (data.errors.confirm)   setError(conf,      document.getElementById('reg-confirm-err'),   data.errors.confirm);
      }
    }
  } catch {
    serverErr('reg-server-err', 'Cannot connect to server. Make sure app.py is running.');
  }
  setBtn('reg-btn', false, 'Create Account');
});