# -*- coding: utf-8 -*-
import json, html, os, re

import os
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BASE = "https://lexvdufroid.fr"
PHONE = "+33757832626"
DATE = "2026-10-14"

def e(s):
    return html.escape(s, quote=False)

def a(s):
    return html.escape(s, quote=True)

PAGEFILES = set()
RENAMED = {}

def fname(t):
    typ = t.get("type", "installation")
    return t.get("file") or f"{typ}-climatisation-{t.get('town', t['slug'])}.html"

def resolve(h):
    """Un lien interne vers une page qui n'existe pas (encore) est redirigé vers la page renommée de la même ville."""
    if h.startswith("../") or h in PAGEFILES or not PAGEFILES:
        return h
    return RENAMED.get(h, h)

def url(t):
    return f"{BASE}/zones/{fname(t)}"

def jsonld(t):
    u = url(t)
    img = f"{BASE}/images/{t['hero']}"
    n = t["name"]
    faq = [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in t["faq"]]
    g = [
        {"@type": "Place", "@id": u + "#place", "name": n,
         "address": {"@type": "PostalAddress", "addressLocality": n, "postalCode": t.get("cp", ""), "addressRegion": "Île-de-France", "addressCountry": "FR"}},
        {"@type": ["HVACBusiness", "LocalBusiness", "Organization"], "@id": BASE + "/#business", "name": "Le XV du Froid",
         "url": BASE + "/", "telephone": PHONE, "email": "contact@lexvdufroid.fr",
         "address": {"@type": "PostalAddress", "addressRegion": "Île-de-France", "addressCountry": "FR"},
         "logo": {"@type": "ImageObject", "@id": BASE + "/#logo", "url": BASE + "/images/logo-xv-du-froid-site.png",
                  "contentUrl": BASE + "/images/logo-xv-du-froid-site.png", "caption": "Le XV du Froid", "inLanguage": "fr-FR"},
         "image": {"@id": BASE + "/#logo"},
         "areaServed": t["areas"] + ["Yvelines", "Île-de-France"],
         "slogan": "La force du bleu, l’expertise du froid",
         "contactPoint": {"@type": "ContactPoint", "telephone": PHONE, "contactType": "customer service", "areaServed": "FR-IDF", "availableLanguage": ["fr-FR"]}},
        {"@type": "WebSite", "@id": BASE + "/#website", "url": BASE + "/", "name": "Le XV du Froid", "publisher": {"@id": BASE + "/#business"}, "inLanguage": "fr-FR"},
        {"@type": "ImageObject", "@id": img, "url": img, "contentUrl": img, "caption": t["hero_alt"], "inLanguage": "fr-FR"},
        {"@type": "WebPage", "@id": u + "#webpage", "url": u, "name": t["title"], "description": t["meta"],
         "isPartOf": {"@id": BASE + "/#website"}, "about": {"@id": BASE + "/#business"},
         "mainEntity": {"@id": u + "#service"}, "primaryImageOfPage": {"@id": img}, "breadcrumb": {"@id": u + "#breadcrumb"},
         "datePublished": t.get("date", DATE) + "T00:00:00+02:00", "dateModified": t.get("date", DATE) + "T12:00:00+02:00", "inLanguage": "fr-FR",
         "keywords": t["kw"]},
        {"@type": "Service", "@id": u + "#service", "name": t["h1"].rstrip("."), "serviceType": t.get("service_type", "Installation de climatisation"),
         "provider": {"@id": BASE + "/#business"}, "areaServed": {"@id": u + "#place"},
         "availableChannel": {"@type": "ServiceChannel", "serviceUrl": BASE + "/contact.html",
                              "servicePhone": {"@type": "ContactPoint", "telephone": PHONE, "contactType": "devis climatisation"}},
         "description": t["meta"]},
        {"@type": "FAQPage", "@id": u + "#faq", "mainEntity": faq},
        {"@type": "BreadcrumbList", "@id": u + "#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Nos zones", "item": BASE + "/zones.html"},
            {"@type": "ListItem", "position": 3, "name": t["crumb"], "item": u}]},
    ]
    s = json.dumps({"@context": "https://schema.org", "@graph": g}, ensure_ascii=False, indent=2)
    return "\n".join("      " + l for l in s.splitlines())

def paras(ps):
    return "".join(f"<p>{e(p)}</p>" for p in ps)

def ul(items, cls):
    return f'<ul class="{cls}">' + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>"

def block(b, t):
    k = b[0]
    if k == "text":      # ("text", eyebrow, h2, [paras])
        _, ey, h2, ps = b
        return f'''          <section class="local-soft-panel local-text-panel">
            <div class="local-section-head">
              <p class="lp-eyebrow">{e(ey)}</p>
              <h2>{e(h2)}</h2>
            </div>
            <div>{paras(ps)}</div>
          </section>'''
    if k == "list":      # ("list", eyebrow, h2, intro, [(strong, text)])
        _, ey, h2, intro, items = b
        li = "".join(f"<li><strong>{e(x)}</strong> {e(y)}</li>" for x, y in items)
        return f'''          <section class="local-soft-panel local-text-panel">
            <div class="local-section-head">
              <p class="lp-eyebrow">{e(ey)}</p>
              <h2>{e(h2)}</h2>
              <p>{e(intro)}</p>
            </div>
            <div><ul class="local-text-list">{li}</ul></div>
          </section>'''
    if k == "photo":     # ("photo", img, alt, tag, h2, [paras], [checks], reverse)
        _, img, alt, tag, h2, ps, checks, rev = b
        cls = "local-photo-block local-photo-block-rev" if rev else "local-photo-block"
        return f'''          <section class="{cls}">
            <figure><img src="../images/{img.replace(".png",".webp")}" alt="{a(alt)}" width="1200" height="900" loading="lazy" /></figure>
            <div>
              <span class="lp-service-tag">{e(tag)}</span>
              <h2>{e(h2)}</h2>
              {paras(ps)}
              {ul(checks, "local-checks") if checks else ""}
            </div>
          </section>'''
    if k == "price":     # ("price", eyebrow, h2, [paras])
        _, ey, h2, ps = b
        return f'''          <section class="local-price">
            <div>
              <p class="lp-eyebrow">{e(ey)}</p>
              <h2>{e(h2)}</h2>
            </div>
            <div>{paras(ps[:-1])}<p class="local-plain-note">{e(ps[-1])}</p></div>
          </section>'''
    if k == "editorial": # ("editorial", eyebrow, h2, [paras], note_title, note_text)
        _, ey, h2, ps, nt, ntext = b
        return f'''          <section class="local-editorial">
            <div class="local-editorial-copy">
              <p class="lp-eyebrow">{e(ey)}</p>
              <h2>{e(h2)}</h2>
              {paras(ps)}
            </div>
            <div class="local-text-note">
              <strong>{e(nt)}</strong>
              <p>{e(ntext)}</p>
            </div>
          </section>'''
    if k == "faq":       # ("faq", eyebrow, h2)
        _, ey, h2 = b
        items = "\n".join(f"              <details>\n                <summary>{e(q)}</summary>\n                <p>{e(r)}</p>\n              </details>" for q, r in t["faq"])
        return f'''          <section class="local-faq">
            <div class="local-section-head">
              <p class="lp-eyebrow">{e(ey)}</p>
              <h2>{e(h2)}</h2>
            </div>
            <div class="lp-accordion">
{items}
            </div>
          </section>'''
    if k == "zone":      # ("zone", eyebrow, h2, para, cta)
        _, ey, h2, p, cta = b
        return f'''          <section class="local-districts-v2">
            <div class="local-section-head">
              <p class="lp-eyebrow">{e(ey)}</p>
              <h2>{e(h2)}</h2>
            </div>
            <div class="local-area-text">
              <p>{e(p)}</p>
              <a class="lp-arrow" href="../contact.html">{e(cta)}</a>
            </div>
          </section>'''
    if k == "links":     # ("links", eyebrow, h2, intro, [(href, label)])
        _, ey, h2, intro, items = b
        li = "".join(f'<li><a href="{a(h)}">{e(l)}</a></li>' for h, l in items)
        return f'''          <section class="local-soft-panel local-text-panel">
            <div class="local-section-head">
              <p class="lp-eyebrow">{e(ey)}</p>
              <h2>{e(h2)}</h2>
              <p>{e(intro)}</p>
            </div>
            <div><ul class="local-text-list">{li}</ul></div>
          </section>'''
    raise ValueError(k)

FOOT = [("versailles", "Versailles"), ("saint-germain-en-laye", "Saint-Germain-en-Laye"), ("poissy", "Poissy"),
        ("mantes-la-jolie", "Mantes-la-Jolie"), ("rambouillet", "Rambouillet"), ("sartrouville", "Sartrouville"),
        ("velizy-villacoublay", "Vélizy-Villacoublay"), ("montigny-le-bretonneux", "Montigny-le-Bretonneux")]

def page(t):
    n = t["name"]
    u = url(t)
    near = ", ".join(f'<a href="{resolve(x[0])}">{e(x[1])}</a>' for x in t["near"])
    body = "\n\n".join(block(b, t) for b in t["blocks"])
    ic = t.get("card")
    card = ""
    if ic:
        card = f'''          <div class="local-intro-card">
            <strong>{e(ic[0])}</strong>
            {ul(ic[1], "")[:-5].replace('<ul class="">', '<ul>')}</ul>
            <a class="btn btn-red" href="../contact.html">{e(ic[2])}</a>
          </div>'''
    foot1 = "".join(f'<li><a href="{resolve("installation-climatisation-" + s + ".html")}">{e(x)}</a></li>' for s, x in FOOT[:4])
    foot2 = "".join(f'<li><a href="{resolve("installation-climatisation-" + s + ".html")}">{e(x)}</a></li>' for s, x in FOOT[4:])
    pts = "".join(f"<li>{e(p)}</li>" for p in t["points"])
    return f'''<!doctype html>
<html lang="fr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{e(t['title'])}</title>
    <meta name="description" content="{a(t['meta'])}" />
    <meta name="keywords" content="{a(', '.join(t['kw']))}" />
    <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1" />
    <link rel="canonical" href="{u}" />
    <meta property="og:locale" content="fr_FR" />
    <meta property="og:title" content="{a(t['title'])}" />
    <meta property="og:description" content="{a(t['meta'])}" />
    <meta property="og:url" content="{u}" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="Le XV du Froid" />
    <meta property="og:image" content="{BASE}/images/{t['hero']}" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{a(t['title'])}" />
    <meta name="twitter:description" content="{a(t['meta'])}" />
    <meta name="twitter:image" content="{BASE}/images/{t['hero']}" />
    <link rel="icon" type="image/png" href="../images/favicon-32.png" />
    <link rel="apple-touch-icon" href="../images/favicon-180.png" />
    <link rel="stylesheet" href="../styles.css?v=paris-1-json-seo-1" />
    <link rel="stylesheet" href="../virage.css?v=virage-2" />
    <script type="application/ld+json">
{jsonld(t)}
    </script>
  </head>
  <body>
    <header class="site-header">
      <a class="logo" href="../index.html" aria-label="Accueil Le XV du Froid">
        <img class="logo-mark" src="../images/logo-xv-du-froid-header.avif" alt="Logo Le XV du Froid" width="660" height="297" />
        <span class="logo-text"><strong>LE <span class="xv">XV</span> DU <span class="froid">FROID</span></strong><small>« La force du bleu, l’expertise du froid »</small></span>
      </a>
      <input class="menu-toggle" type="checkbox" id="menu-toggle" aria-label="Ouvrir le menu" />
      <label class="hamburger" for="menu-toggle" aria-hidden="true"><span></span><span></span><span></span></label>
      <nav class="nav" aria-label="Navigation principale">
        <a href="../index.html">Accueil</a>
        <a class="active" href="../climatisation.html">Installation</a>
        <a href="../entretien.html">Entretien</a>
        <a href="../depannage.html">Dépannage</a>
        <a href="../zones.html">Nos zones</a>
        <a href="../a-propos.html">À propos</a>
        <a href="../blog.html">Blog</a>
        <a href="../contact.html">Contact</a>
      <a href="../leasing-pompe-a-chaleur.html">Leasing PAC</a>
      <a class="nav-cta" href="tel:{PHONE}">☎ 07 57 83 26 26</a>
      </nav>
    </header>

    <nav class="breadcrumb" aria-label="Fil d’Ariane">
      <a href="../index.html">Accueil</a>
      <a href="../zones.html">Nos zones</a>
      <span>{e(t['crumb'])}</span>
    </nav>

    <main class="lp seo-page local-page local-page-v2">
      <section class="lp-hero local-hero">
        <div class="lp-wrap lp-hero-split">
          <div class="lp-hero-copy">
            <p class="lp-eyebrow lp-eyebrow-invert">{e(t['eyebrow'])}</p>
            <h1>{e(t['h1'])}</h1>
            <p class="lp-hero-lead">{e(t['lead'])}</p>
            <div class="lp-actions">
              <a class="btn btn-red" href="tel:{PHONE}"><span>☎</span><strong>07 57 83 26 26</strong></a>
              <a class="btn btn-outline-dark" href="../contact.html">{e(t.get('cta', 'Demander un devis'))}</a>
            </div>
            <ul class="lp-hero-points">{pts}</ul>
          </div>
          <figure class="lp-hero-media">
            <img src="../images/{t["hero"].replace(".png",".webp")}" alt="{a(t['hero_alt'])}" width="1200" height="945" fetchpriority="high" />
            <figcaption>{e(t['caption'])}</figcaption>
          </figure>
        </div>
      </section>

      <section class="local-intro">
        <div class="lp-wrap local-intro-grid">
          <div>
            <p class="lp-eyebrow">{e(t['intro'][0])}</p>
            <h2>{e(t['intro'][1])}</h2>
            {paras(t['intro'][2])}
          </div>
{card}
        </div>
      </section>

      <section class="lp-section">
        <div class="lp-wrap local-flow">
{body}

          <section class="local-next">
            <div>
              <p class="lp-eyebrow">À lire aussi</p>
              <h2>{e(t['next_h2'])}</h2>
            </div>
            <p class="local-link-line">{e(t['next_p'])} {near}.</p>
          </section>
        </div>
      </section>

      <section class="vg-ticket-band" aria-label="Devis clair avant travaux">
        <div class="vg-ticket-copy">
          <p class="lp-eyebrow">Transparence</p>
          <h2>Un devis clair avant toute intervention.</h2>
          <p>Vous savez ce qui est prévu, pourquoi c’est nécessaire et à quel tarif avant que le technicien commence. Puis contrôles et essais avant son départ.</p>
          <div class="vg-ticket-actions">
            <a class="btn btn-red" href="tel:{PHONE}"><span>☎</span><strong>07 57 83 26 26</strong></a>
            <a class="btn btn-outline-dark" href="../contact.html">Demander un devis</a>
          </div>
        </div>
        <div class="vg-ticket" aria-hidden="true">
            <div class="vg-ticket-top"><b>Le XV du Froid</b><span>{e(n)}</span></div>
            <div class="vg-ticket-main"><strong>Devis clair<br>avant travaux</strong><span>Diagnostic sur place, essais avant notre départ</span></div>
            <div class="vg-ticket-bar"></div>
            <div class="vg-ticket-foot">Appelez le 07 57 83 26 26</div>
          </div>
      </section>
</main>

    <footer class="footer">
      <div class="footer-main">
        <div class="footer-brand">
          <a class="logo footer-logo" href="../index.html" aria-label="Accueil Le XV du Froid">
            <img class="logo-mark" loading="lazy" src="../images/logo-xv-du-froid-header.avif" alt="Logo Le XV du Froid" width="660" height="297" />
            <span class="logo-text"><strong>LE <span class="xv">XV</span> DU <span class="froid">FROID</span></strong><small>« La force du bleu, l’expertise du froid »</small></span>
          </a>
          <p>{e(t['foot'])}</p>
          <a class="footer-phone" href="tel:{PHONE}">07 57 83 26 26</a>
        </div>
        <div><h3>Yvelines (78)</h3><ul>{foot1}</ul></div>
        <div><h3>Yvelines (suite)</h3><ul>{foot2}</ul></div>
        <div><h3>Services</h3><ul><li><a href="../climatisation.html">Installation</a></li><li><a href="../contact.html">Devis</a></li><li><a href="../zones.html">Nos zones</a></li><li><a href="../blog.html">Blog</a></li></ul></div>
      </div>
      <div class="footer-bottom"><span>© 2026 Le XV du Froid.</span><span>{e(t['crumb'])}</span></div>
    </footer>
    <a class="floating-call" href="tel:{PHONE}" aria-label="Appeler Le XV du Froid"><span>☎</span><strong>Appeler</strong></a>
    <script src="../menu.js?v=menu-1" defer></script>
</body>
</html>
'''

def write_all(towns):
    for t in towns:
        out = page(t).replace("­", "")
        path = os.path.join(REPO, "zones", fname(t))
        with open(path, "w", encoding="utf-8") as f:
            f.write(out)
        print("écrit", fname(t))
