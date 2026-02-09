/* calendar-mcp docs — shared JavaScript */
(function () {
  'use strict';

  var STORAGE_KEY = 'calendar-mcp-dark-mode';
  var html = document.documentElement;

  // Unicode icons
  var MOON = '\u{1F319}';  // crescent moon
  var SUN  = '\u2600\uFE0F'; // sun

  // ---- Dark-mode toggle ----
  var toggle = document.createElement('button');
  toggle.className = 'dark-mode-toggle';
  toggle.id = 'dark-mode-toggle';
  toggle.setAttribute('title', 'Toggle dark mode');
  document.body.appendChild(toggle);

  function setTheme(isDark) {
    if (isDark) {
      html.setAttribute('data-theme', 'dark');
      toggle.textContent = SUN;
      toggle.setAttribute('aria-label', 'Switch to light mode');
    } else {
      html.removeAttribute('data-theme');
      toggle.textContent = MOON;
      toggle.setAttribute('aria-label', 'Switch to dark mode');
    }
  }

  // Determine initial theme: localStorage > OS preference > light
  var stored = localStorage.getItem(STORAGE_KEY);
  var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

  if (stored === 'dark') {
    setTheme(true);
  } else if (stored === 'light') {
    setTheme(false);
  } else {
    setTheme(prefersDark);
  }

  // Toggle on click
  toggle.addEventListener('click', function () {
    var isDark = html.getAttribute('data-theme') === 'dark';
    var newIsDark = !isDark;
    setTheme(newIsDark);
    localStorage.setItem(STORAGE_KEY, newIsDark ? 'dark' : 'light');
  });

  // Listen for OS preference changes (only when no manual choice stored)
  if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
      if (!localStorage.getItem(STORAGE_KEY)) {
        setTheme(e.matches);
      }
    });
  }

  // ---- External links open in new tabs ----
  var links = document.querySelectorAll('a[href]');
  var currentHost = window.location.hostname;
  for (var i = 0; i < links.length; i++) {
    var link = links[i];
    try {
      var url = new URL(link.href, window.location.href);
      if (url.hostname && url.hostname !== currentHost && url.protocol.indexOf('http') === 0) {
        link.setAttribute('target', '_blank');
        link.setAttribute('rel', 'noopener noreferrer');
      }
    } catch (e) {
      // skip malformed URLs
    }
  }
})();
