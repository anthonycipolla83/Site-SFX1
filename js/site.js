/* SFX1 V5 — interactions. Le contenu reste lisible sans JavaScript ; ce script ajoute le confort. */
(function () {
  'use strict';
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* Éléments temporaires (onglet Portes ouvertes…) : visibles seulement entre deux dates */
  var today = new Date(); today.setHours(0, 0, 0, 0);
  function d(s) { var p = s.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
  $$('[data-show-from]').forEach(function (el) {
    var from = d(el.dataset.showFrom), until = d(el.dataset.showUntil);
    if (today < from || today > until) el.hidden = true;
  });

  /* Compte à rebours vers les portes ouvertes */
  $$('[data-countdown]').forEach(function (el) {
    var target = new Date(el.dataset.countdown).getTime();
    function tick() {
      var ms = target - Date.now();
      if (isNaN(target) || ms <= 0) {
        el.innerHTML = '';
        var past = document.querySelector('.po-past'); if (past && ms < -12 * 3600e3) past.hidden = false;
        return false;
      }
      var j = Math.floor(ms / 864e5), h = Math.floor(ms % 864e5 / 36e5), m = Math.floor(ms % 36e5 / 6e4);
      el.innerHTML = [[j, 'jours'], [h, 'heures'], [m, 'minutes']].map(function (x) { return '<span class="cd"><b>' + x[0] + '</b><small>' + x[1] + '</small></span>'; }).join('');
      el.setAttribute('aria-label', 'Plus que ' + j + ' jours avant les portes ouvertes');
      return true;
    }
    if (tick() && !reduce) setInterval(tick, 30000);
  });

  /* Idées reçues : retourner les cartes */
  $$('.myth-in').forEach(function (b) {
    b.addEventListener('click', function () { b.setAttribute('aria-expanded', String(b.getAttribute('aria-expanded') !== 'true')); });
  });

  /* Bandeau de test refermable (sans onclick en ligne) */
  $$('[data-dismiss]').forEach(function (b) { b.addEventListener('click', function () { b.parentNode.remove(); }); });

  /* Menu mobile : bouton, touche Échap, clic à l'extérieur */
  var menuBtn = $('#menuBtn'), nav = $('#mainnav');
  function closeMenu() { if (!nav) return; nav.classList.remove('open'); menuBtn && menuBtn.setAttribute('aria-expanded', 'false'); }
  if (menuBtn && nav) {
    menuBtn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      menuBtn.setAttribute('aria-expanded', String(open));
      menuBtn.setAttribute('aria-label', open ? 'Fermer le menu' : 'Ouvrir le menu');
      if (open) { var f = $('a', nav); f && f.focus(); }
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && nav.classList.contains('open')) { closeMenu(); menuBtn.focus(); } });
    document.addEventListener('click', function (e) { if (nav.classList.contains('open') && !nav.contains(e.target) && e.target !== menuBtn) closeMenu(); });
  }

  /* En-tête compact, barre de progression, retour en haut */
  var progress = $('#progress'), backTop = $('#backTop'), topbar = $('.topbar');
  function onScroll() {
    var max = document.documentElement.scrollHeight - innerHeight;
    if (progress) progress.style.width = (max > 0 ? 100 * scrollY / max : 0) + '%';
    topbar && topbar.classList.toggle('is-scrolled', scrollY > 30);
    backTop && backTop.classList.toggle('show', scrollY > 650);
  }
  addEventListener('scroll', onScroll, { passive: true }); onScroll();
  backTop && backTop.addEventListener('click', function () { scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' }); var m = $('#main'); m && m.focus({ preventScroll: true }); });

  /* Apparitions progressives, en cascade dans une même grille */
  var reveals = $$('.scroll-reveal');
  reveals.forEach(function (el) {
    var sibs = $$('.scroll-reveal', el.parentNode).filter(function (x) { return x.parentNode === el.parentNode; });
    var i = sibs.indexOf(el); if (i > 0) el.style.setProperty('--d', Math.min(i, 5) * 0.08 + 's');
  });
  if (reduce || !('IntersectionObserver' in window)) { reveals.forEach(function (x) { x.classList.add('visible'); }); }
  else {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('visible'); io.unobserve(e.target); } }); }, { threshold: .12, rootMargin: '0px 0px -40px 0px' });
    reveals.forEach(function (x) { io.observe(x); });
  }

  /* Compteurs animés */
  $$('[data-count]').forEach(function (el) {
    var target = +el.dataset.count, suffix = el.dataset.suffix || '';
    if (reduce || !('IntersectionObserver' in window)) { el.textContent = target + suffix; return; }
    el.textContent = '0' + suffix;
    var o = new IntersectionObserver(function (es) {
      if (!es[0].isIntersecting) return; o.disconnect();
      var t0 = null; function step(t) { t0 = t0 || t; var p = Math.min(1, (t - t0) / 1200); el.textContent = Math.round(target * (1 - Math.pow(1 - p, 3))) + suffix; if (p < 1) requestAnimationFrame(step); }
      requestAnimationFrame(step);
    }, { threshold: .6 }); o.observe(el);
  });

  /* Diaporama d'accueil : pause au survol ET au focus clavier, respect de la réduction des animations */
  var hero = $('.hero');
  if (hero && $$('.hero-slide', hero).length) {
    var slides = $$('.hero-slide', hero), dots = $$('.slide-dot', hero), cap = $('.hero-photo-caption', hero), bar = $('.hero-progress', hero);
    var pauseBtn = $('[data-slide-pause]', hero), idx = 0, timer = null, paused = reduce, hover = false;
    function show(i) {
      idx = (i + slides.length) % slides.length;
      slides.forEach(function (s, n) { s.classList.toggle('active', n === idx); });
      dots.forEach(function (d, n) { d.classList.toggle('active', n === idx); if (n === idx) d.setAttribute('aria-current', 'true'); else d.removeAttribute('aria-current'); });
      if (cap) cap.textContent = slides[idx].dataset.caption || '';
      restartBar();
    }
    function restartBar() { if (!bar) return; bar.classList.remove('run'); void bar.offsetWidth; if (!paused && !hover) bar.classList.add('run'); }
    function stop() { clearInterval(timer); timer = null; bar && bar.classList.remove('run'); }
    function start() { stop(); if (paused || hover) return; timer = setInterval(function () { if (!document.hidden) show(idx + 1); }, 6000); restartBar(); }
    dots.forEach(function (d) { d.addEventListener('click', function () { show(+d.dataset.slide); start(); }); });
    var nx = $('[data-slide-next]', hero), pv = $('[data-slide-prev]', hero);
    nx && nx.addEventListener('click', function () { show(idx + 1); start(); });
    pv && pv.addEventListener('click', function () { show(idx - 1); start(); });
    function syncPause() { if (!pauseBtn) return; pauseBtn.textContent = paused ? '▶' : 'Ⅱ'; pauseBtn.setAttribute('aria-label', paused ? 'Relancer le diaporama' : 'Mettre le diaporama en pause'); pauseBtn.setAttribute('aria-pressed', String(paused)); }
    pauseBtn && pauseBtn.addEventListener('click', function () { paused = !paused; syncPause(); start(); });
    hero.addEventListener('mouseenter', function () { hover = true; stop(); });
    hero.addEventListener('mouseleave', function () { hover = false; start(); });
    hero.addEventListener('focusin', function () { hover = true; stop(); });
    hero.addEventListener('focusout', function (e) { if (!hero.contains(e.relatedTarget)) { hover = false; start(); } });
    syncPause(); show(0); start();
  }

  /* Onglets accessibles (flèches, Début, Fin) — utilisés pour les degrés et les grilles */
  $$('[role="tablist"]').forEach(function (list) {
    var tabs = $$('[role="tab"]', list);
    function select(tab, focus) {
      tabs.forEach(function (t) {
        var on = t === tab; t.setAttribute('aria-selected', String(on)); t.tabIndex = on ? 0 : -1; t.classList.toggle('active', on);
        var p = document.getElementById(t.getAttribute('aria-controls')); if (p) { p.hidden = !on; if (on) { p.classList.remove('ready'); void p.offsetWidth; p.classList.add('ready'); } }
      });
      if (focus) tab.focus();
      if (list.dataset.hash && history.replaceState) history.replaceState(null, '', '#' + tab.dataset.key);
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { select(t); });
      t.addEventListener('keydown', function (e) {
        var k = e.key, n = null;
        if (k === 'ArrowRight' || k === 'ArrowDown') n = tabs[(i + 1) % tabs.length];
        if (k === 'ArrowLeft' || k === 'ArrowUp') n = tabs[(i - 1 + tabs.length) % tabs.length];
        if (k === 'Home') n = tabs[0]; if (k === 'End') n = tabs[tabs.length - 1];
        if (n) { e.preventDefault(); select(n, true); }
      });
    });
    var init = tabs[0];
    if (list.dataset.hash && location.hash) { tabs.forEach(function (t) { if ('#' + t.dataset.key === location.hash.toLowerCase()) init = t; }); }
    select(init);
  });

  /* Surlignage des cours donnés en néerlandais */
  $$('[data-nl-toggle]').forEach(function (c) { c.addEventListener('change', function () { document.body.classList.toggle('show-nl', c.checked); $$('[data-nl-toggle]').forEach(function (o) { o.checked = c.checked; }); }); });

  /* Filtres (documents, actualités) + recherche */
  $$('[data-filter-group]').forEach(function (group) {
    var target = document.getElementById(group.dataset.filterGroup);
    var items = $$('[data-cat]', target), search = $('[data-search="' + group.dataset.filterGroup + '"]'), empty = $('.empty-state', target.parentNode), cat = 'Tous', live = $('#' + group.dataset.filterGroup + '-live');
    function apply() {
      var q = search ? search.value.trim().toLowerCase() : '', shown = 0;
      items.forEach(function (it) { var ok = (cat === 'Tous' || it.dataset.cat === cat) && (!q || it.textContent.toLowerCase().indexOf(q) > -1); it.hidden = !ok; if (ok) shown++; });
      if (empty) empty.style.display = shown ? 'none' : 'block';
      if (live) live.textContent = shown + ' élément' + (shown > 1 ? 's' : '') + ' affiché' + (shown > 1 ? 's' : '');
    }
    $$('button[data-value]', group).forEach(function (b) {
      b.addEventListener('click', function () {
        cat = b.dataset.value;
        $$('button[data-value]', group).forEach(function (x) { var on = x === b; x.classList.toggle('selected', on); x.setAttribute('aria-pressed', String(on)); });
        apply();
      });
    });
    search && search.addEventListener('input', apply);
  });

  /* Vidéos YouTube : lecteur créé uniquement au clic (youtube-nocookie) */
  $$('[data-youtube-id]').forEach(function (button) {
    button.addEventListener('click', function () {
      var id = button.dataset.youtubeId; if (!/^[a-zA-Z0-9_-]{11}$/.test(id)) return;
      var stage = button.closest('[data-video-stage]'); if (!stage) return;
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0';
      f.title = button.dataset.title || 'Vidéo YouTube du Collège SFX1';
      f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
      f.allowFullscreen = true; f.referrerPolicy = 'strict-origin-when-cross-origin';
      stage.replaceChildren(f); f.focus();
    });
  });

  /* Vidéos Google Drive : lecteur créé uniquement au clic */
  $$('[data-drive-id]').forEach(function (button) {
    button.addEventListener('click', function () {
      var id = button.dataset.driveId; if (!/^[a-zA-Z0-9_-]{20,60}$/.test(id)) return;
      var stage = button.closest('[data-video-stage]'); if (!stage) return;
      var f = document.createElement('iframe');
      f.src = 'https://drive.google.com/file/d/' + id + '/preview';
      f.title = button.dataset.title || 'Vidéo du Collège SFX1';
      f.allow = 'autoplay; fullscreen'; f.allowFullscreen = true;
      stage.replaceChildren(f); f.focus();
    });
  });

  /* Carte OpenStreetMap : chargée uniquement à la demande du visiteur */
  $$('[data-map]').forEach(function (b) {
    b.addEventListener('click', function () {
      var stage = b.closest('.map-stage'); if (!stage) return;
      var f = document.createElement('iframe');
      f.src = b.dataset.map; f.title = 'Plan d’accès au Collège Saint-François-Xavier I, rue de Rome 18, Verviers'; f.loading = 'lazy';
      stage.replaceChildren(f);
    });
  });

  /* Formulaire de contact : envoi réel une fois en ligne (Netlify ou OVH).
     En test local (fichier ouvert depuis l'ordinateur), le message est préparé dans la messagerie. */
  $$('[data-contact-form]').forEach(function (f) {
    if (location.protocol !== 'file:') return;
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var g = function (n) { var x = f.elements[n]; return x ? x.value : ''; };
      var body = 'Nom : ' + g('nom') + '\nEmail : ' + g('email') + '\n\n' + g('message');
      var r = $('.form-result', f); r.hidden = false;
      r.textContent = 'Version de test locale : votre messagerie s’ouvre avec le message prêt à envoyer à ' + f.dataset.to + '. En ligne, l’envoi sera direct.';
      location.href = 'mailto:' + f.dataset.to + '?subject=' + encodeURIComponent('[Site] ' + g('sujet')) + '&body=' + encodeURIComponent(body);
      r.focus();
    });
  });

  /* Mode administrateur : crayons de modification.
     Simple raccourci d'affichage : toute modification exige une connexion autorisée dans /admin. */
  var isAdmin = false; try { isAdmin = localStorage.getItem('sfx1-admin') === '1'; } catch (e) {}
  if (isAdmin) {
    var adminUrl = function (entry) { return 'admin/#/collections/contenus/entries/' + entry; };
    $$('[data-edit]').forEach(function (s) {
      var a = document.createElement('a'); a.className = 'edit-pencil'; a.href = adminUrl(s.dataset.edit); a.target = '_blank'; a.rel = 'noopener';
      a.title = 'Modifier ce contenu'; a.innerHTML = '<span aria-hidden="true">✎</span><span class="sr-only">Modifier ce contenu</span>';
      s.classList.add('is-editable'); s.appendChild(a);
    });
    var bar = document.createElement('div'); bar.className = 'admin-bar';
    bar.innerHTML = '<span>✎ Mode administrateur</span><a href="admin/" target="_blank" rel="noopener">Ouvrir l’administration</a><button type="button">Quitter</button>';
    $('button', bar).addEventListener('click', function () { try { localStorage.removeItem('sfx1-admin'); } catch (e) {} location.reload(); });
    document.body.appendChild(bar);
  }

  /* Barre d'accès rapides (mobile) : se retire en descendant, revient en remontant,
     et disparaît quand on remplit un formulaire ou qu'on arrive en bas de page. */
  var mbar = $('.mbar');
  if (mbar) {
    var lastY = window.scrollY, typing = false;
    var upd = function () {
      var y = window.scrollY, nearEnd = (window.innerHeight + y) > (document.documentElement.scrollHeight - 160);
      var hide = typing || nearEnd || (y > lastY && y > 120);
      mbar.classList.toggle('is-off', hide);
      document.body.classList.toggle('mbar-off', hide);
      lastY = y;
    };
    window.addEventListener('scroll', upd, { passive: true });
    document.addEventListener('focusin', function (e) { if (e.target.matches('input,textarea,select')) { typing = true; upd(); } });
    document.addEventListener('focusout', function () { typing = false; setTimeout(upd, 50); });
  }

  /* Lien d'évitement : place le focus sur le contenu */
  var skip = $('.skip-link'); skip && skip.addEventListener('click', function () { var m = $('#main'); m && setTimeout(function () { m.focus(); }, 0); });
})();
