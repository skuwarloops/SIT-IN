// ── Community dropdown ──────────────────────────────────
const toggle = document.getElementById('communityToggle');
const menu   = document.getElementById('communityMenu');

toggle.addEventListener('click', e => {
  e.preventDefault();
  menu.classList.toggle('open');
});

document.addEventListener('click', e => {
  if (!toggle.contains(e.target) && !menu.contains(e.target)) {
    menu.classList.remove('open');
  }
});

// ── Mobile hamburger ────────────────────────────────────
const hamburger = document.getElementById('hamburger');
const navLinks  = document.getElementById('nav-links');

hamburger.addEventListener('click', () => {
  navLinks.classList.toggle('open');
});

// ── Active nav on scroll ────────────────────────────────
const links = document.querySelectorAll('.nav-link');
window.addEventListener('scroll', () => {
  links.forEach(l => l.classList.remove('active'));
  const scrollY = window.scrollY;
  if (scrollY < 300) {
    document.querySelector('[href="#"]')?.classList.add('active');
  } else {
    document.querySelector('[href="#about"]')?.classList.add('active');
  }
});
