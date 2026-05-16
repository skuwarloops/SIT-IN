// ── Tab switching ──────────────────────────────────────────
const tabs   = document.querySelectorAll('.tab');
const forms  = document.querySelectorAll('.form');
const success = document.getElementById('success');
const successMsg = document.getElementById('success-msg');

function switchTab(name) {
  tabs.forEach(t => t.classList.toggle('active', t.dataset.tab === name));
  forms.forEach(f => f.classList.toggle('active', f.id === name));
  success.classList.add('hidden');
  clearErrors();
}

tabs.forEach(tab => tab.addEventListener('click', () => switchTab(tab.dataset.tab)));

// Switch links inside forms
document.querySelectorAll('[data-switch]').forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    switchTab(link.dataset.switch);
  });
});

// ── Helpers ────────────────────────────────────────────────
function setError(inputEl, errEl, msg) {
  errEl.textContent = msg;
  if (msg) inputEl.classList.add('invalid');
  else      inputEl.classList.remove('invalid');
}

function clearErrors() {
  document.querySelectorAll('.error').forEach(e => e.textContent = '');
  document.querySelectorAll('input').forEach(i => i.classList.remove('invalid'));
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function showSuccess(msg) {
  forms.forEach(f => f.classList.remove('active'));
  success.classList.remove('hidden');
  successMsg.textContent = msg;
}

// ── Simple in-memory "database" ────────────────────────────
const users = [];   // { name, email, password }

// ── Login ──────────────────────────────────────────────────
const loginForm     = document.getElementById('login');
const loginEmail    = document.getElementById('login-email');
const loginPassword = document.getElementById('login-password');
const loginEmailErr = document.getElementById('login-email-err');
const loginPassErr  = document.getElementById('login-password-err');

loginForm.addEventListener('submit', e => {
  e.preventDefault();
  let valid = true;

  if (!loginEmail.value.trim()) {
    setError(loginEmail, loginEmailErr, 'Email is required.'); valid = false;
  } else if (!isValidEmail(loginEmail.value.trim())) {
    setError(loginEmail, loginEmailErr, 'Enter a valid email.'); valid = false;
  } else {
    setError(loginEmail, loginEmailErr, '');
  }

  if (!loginPassword.value) {
    setError(loginPassword, loginPassErr, 'Password is required.'); valid = false;
  } else {
    setError(loginPassword, loginPassErr, '');
  }

  if (!valid) return;

  const user = users.find(u =>
    u.email === loginEmail.value.trim() && u.password === loginPassword.value
  );

  if (!user) {
    setError(loginPassword, loginPassErr, 'Incorrect email or password.');
    return;
  }

  showSuccess(`Welcome back, ${user.name}! You are now logged in.`);
  loginForm.reset();
});

// ── Register ───────────────────────────────────────────────
const regForm    = document.getElementById('register');
const regName    = document.getElementById('reg-name');
const regEmail   = document.getElementById('reg-email');
const regPass    = document.getElementById('reg-password');
const regConfirm = document.getElementById('reg-confirm');
const regNameErr = document.getElementById('reg-name-err');
const regEmailErr= document.getElementById('reg-email-err');
const regPassErr = document.getElementById('reg-password-err');
const regConfErr = document.getElementById('reg-confirm-err');

regForm.addEventListener('submit', e => {
  e.preventDefault();
  let valid = true;

  if (!regName.value.trim()) {
    setError(regName, regNameErr, 'Name is required.'); valid = false;
  } else {
    setError(regName, regNameErr, '');
  }

  if (!regEmail.value.trim()) {
    setError(regEmail, regEmailErr, 'Email is required.'); valid = false;
  } else if (!isValidEmail(regEmail.value.trim())) {
    setError(regEmail, regEmailErr, 'Enter a valid email.'); valid = false;
  } else if (users.find(u => u.email === regEmail.value.trim())) {
    setError(regEmail, regEmailErr, 'Email is already registered.'); valid = false;
  } else {
    setError(regEmail, regEmailErr, '');
  }

  if (regPass.value.length < 6) {
    setError(regPass, regPassErr, 'At least 6 characters required.'); valid = false;
  } else {
    setError(regPass, regPassErr, '');
  }

  if (regConfirm.value !== regPass.value) {
    setError(regConfirm, regConfErr, 'Passwords do not match.'); valid = false;
  } else {
    setError(regConfirm, regConfErr, '');
  }

  if (!valid) return;

  users.push({
    name: regName.value.trim(),
    email: regEmail.value.trim(),
    password: regPass.value
  });

  showSuccess(`Account created for ${regName.value.trim()}! You can now login.`);
  regForm.reset();

  // Auto-switch to login after 1.5s
  setTimeout(() => switchTab('login'), 1500);
});
