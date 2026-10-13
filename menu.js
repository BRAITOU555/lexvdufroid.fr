/* Menu mobile : se referme au clic sur un lien, en dehors du menu ou sur Échap. */
(function () {
  var toggle = document.getElementById('menu-toggle');
  var nav = document.querySelector('.site-header .nav');
  var burger = document.querySelector('.site-header .hamburger');
  if (!toggle || !nav) return;
  function sync() {
    toggle.setAttribute('aria-expanded', toggle.checked ? 'true' : 'false');
    document.documentElement.classList.toggle('menu-open', toggle.checked);
  }
  function close() { if (toggle.checked) { toggle.checked = false; sync(); } }
  toggle.addEventListener('change', sync);
  nav.addEventListener('click', function (e) { if (e.target.closest('a')) close(); });
  document.addEventListener('click', function (e) {
    if (toggle.checked && e.target !== toggle && !nav.contains(e.target) && !(burger && burger.contains(e.target))) close();
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
  window.addEventListener('resize', function () { if (window.innerWidth > 980) close(); });
  sync();
})();
