(function () {
  const KEY = 'ccs-theme';
  const isLight = localStorage.getItem(KEY) === 'light';

  // Apply theme immediately before paint to avoid flash
  if (isLight) document.documentElement.classList.add('light-mode-pre');

  function applyTheme(light) {
    document.body.classList.toggle('light-mode', light);
    const btn = document.querySelector('.dark-mode-toggle');
    if (btn) {
      btn.innerHTML = light ? '🌙' : '☀️';
      btn.title = light ? 'Switch to Dark Mode' : 'Switch to Light Mode';
    }
  }

  function createToggle() {
    if (document.querySelector('.dark-mode-toggle')) return;
    const navLinks = document.querySelector('.nav-links');
    if (!navLinks) return;

    const btn = document.createElement('button');
    btn.className = 'dark-mode-toggle';
    btn.innerHTML = isLight ? '🌙' : '☀️';
    btn.title = isLight ? 'Switch to Dark Mode' : 'Switch to Light Mode';
    btn.setAttribute('aria-label', 'Toggle theme');
    btn.onclick = () => {
      const nowLight = !document.body.classList.contains('light-mode');
      localStorage.setItem(KEY, nowLight ? 'light' : 'dark');
      applyTheme(nowLight);
    };

    // Insert before the last child (logout button)
    navLinks.insertBefore(btn, navLinks.lastElementChild);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      applyTheme(isLight);
      createToggle();
    });
  } else {
    applyTheme(isLight);
    createToggle();
  }
})();