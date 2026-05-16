// Dark Mode Toggle Functionality
class DarkModeManager {
    constructor() {
        this.storageKey = 'sit-in-dark-mode';
        this.init();
    }

    init() {
        // Check localStorage for saved preference
        const isDark = localStorage.getItem(this.storageKey) === 'true';
        if (isDark) {
            this.enableDarkMode();
        }
        
        // Create toggle button
        this.createToggleButton();
        
        // Listen for system preference changes
        if (window.matchMedia) {
            window.matchMedia('(prefers-color-scheme: dark)').addListener((e) => {
                if (!localStorage.getItem(this.storageKey)) {
                    if (e.matches) {
                        this.enableDarkMode();
                    } else {
                        this.disableDarkMode();
                    }
                }
            });
        }
    }

    enableDarkMode() {
        document.body.classList.add('dark-mode');
        localStorage.setItem(this.storageKey, 'true');
        this.updateToggleIcon();
    }

    disableDarkMode() {
        document.body.classList.remove('dark-mode');
        localStorage.setItem(this.storageKey, 'false');
        this.updateToggleIcon();
    }

    toggle() {
        if (document.body.classList.contains('dark-mode')) {
            this.disableDarkMode();
        } else {
            this.enableDarkMode();
        }
    }

    createToggleButton() {
        // Find navbar and add toggle button
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;

        const button = document.createElement('button');
        button.className = 'dark-mode-toggle';
        button.innerHTML = '🌙'; // Moon icon initially
        button.title = 'Toggle dark mode';
        button.onclick = () => this.toggle();

        // Insert at the end of navbar, before last item
        const navLinks = navbar.querySelector('.nav-links');
        if (navLinks) {
            navLinks.insertBefore(button, navLinks.lastChild);
        }

        this.updateToggleIcon();
    }

    updateToggleIcon() {
        const toggle = document.querySelector('.dark-mode-toggle');
        if (!toggle) return;
        
        if (document.body.classList.contains('dark-mode')) {
            toggle.innerHTML = '☀️'; // Sun icon in dark mode
        } else {
            toggle.innerHTML = '🌙'; // Moon icon in light mode
        }
    }
}

// Initialize dark mode when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.darkModeManager = new DarkModeManager();
});

// Shortcut function for toggling
function toggleDarkMode() {
    if (window.darkModeManager) {
        window.darkModeManager.toggle();
    }
}
