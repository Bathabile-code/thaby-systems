#!/usr/bin/env python3
"""
AlwaysOn/Alwayzon site-builder: generates a personalized one-page site from a
per-client config JSON, using a single premium template. Turns "hours of hand-written
HTML" into a ~2-minute automated run per client.

Usage:
  python3 generate-site.py <config.json> [--out DIR] [--deploy REPO]

Config schema (JSON):
{
  "business": "Livewire Electrical",
  "trade": "Electrician",                 # "Electrician in Durban"
  "city": "Durban",
  "province": "KwaZulu-Natal",
  "phone_intl": "27827862266",            # digits only, no +
  "phone_display": "082 786 2266",
  "rating": "5.0",
  "accent": "#1d4ed8",                    # brand accent (hex)
  "accent_text": "blue",                  # not used in v1
  "tagline": "Safe, reliable electrical work, powering Durban.",
  "services": [
    {"icon":"⚡","title":"Installations","items":["New wiring & circuits","DB board upgrades"]},
    ...
  ],
  "areas": ["Durban CBD","Umhlanga","Berea"],
  "hero_image": "hero.png",               # copied into out/ if present
  "gallery": ["work1.png","work2.png"],   # copied into out/
  "extra_trust": [["5.0","Google rating"],["100%","SANS-compliant"]]
}

If --deploy REPO is given, runs deploy-autosite-site.sh after generating.
"""
import json, os, shutil, subprocess, sys, argparse

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{BUSINESS}} — {{TRADE}} in {{CITY}}</title>
<meta name="description" content="{{BUSINESS}} — {{RATING}}★ {{TRADE}} in {{CITY}}. {{SERVICES_SUMMARY}} {{PHONE_DISPLAY}}.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{
  --accent:{{ACCENT}}; --accent-dark:#163a9e;
  --ink:#0f172a; --label:#334155; --body:#475569; --muted:#94a3b8;
  --line:#e2e8f0; --bg:#ffffff; --dark:#0b1220; --success:#16a34a;
  --shadow:0 20px 50px -20px rgba(15,23,42,0.18);
  --head:'Space Grotesk',system-ui,sans-serif; --bodyf:'Inter',system-ui,sans-serif;
}
*{margin:0;padding:0;box-sizing:border-box;}
html{scroll-behavior:smooth;}
body{font-family:var(--bodyf);color:var(--ink);background:var(--bg);line-height:1.6;-webkit-font-smoothing:antialiased;}
h1,h2,h3{font-family:var(--head);line-height:1.15;font-weight:700;}
a{text-decoration:none;color:inherit;} img{max-width:100%;display:block;}
.wrap{max-width:1120px;margin:0 auto;padding:0 24px;}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;padding:14px 26px;border-radius:10px;font-weight:600;font-size:1rem;cursor:pointer;transition:transform .15s;border:none;}
.btn:hover{transform:translateY(-2px);}
.btn-blue{background:var(--accent);color:#fff;}
.btn-wa{background:rgba(255,255,255,0.12);color:#fff;border:1px solid rgba(255,255,255,0.35);}
.btn-outline{background:transparent;color:var(--accent);border:1.5px solid var(--accent);}
.wa-glyph{width:1.15em;height:1.15em;fill:currentColor;vertical-align:-0.15em;flex:none;}
.fab{position:fixed;right:20px;bottom:20px;z-index:90;width:58px;height:58px;border-radius:50%;background:#25d366;color:#fff;display:flex;align-items:center;justify-content:center;box-shadow:0 12px 30px -8px rgba(37,211,102,0.6);transition:transform .15s;}
.fab:hover{transform:scale(1.08);} .fab .wa-glyph{width:30px;height:30px;}
nav{position:sticky;top:0;z-index:50;background:rgba(255,255,255,0.9);backdrop-filter:blur(14px);border-bottom:1px solid var(--line);}
.nav-in{display:flex;align-items:center;justify-content:space-between;height:70px;}
.brand{font-family:var(--head);font-weight:700;font-size:1.1rem;}
.nav-links{display:flex;gap:30px;font-size:0.9rem;color:var(--label);font-weight:500;}
.nav-links a:hover{color:var(--accent);}
.hero{position:relative;min-height:88vh;display:flex;align-items:center;color:#fff;overflow:hidden;}
.hero-bg{position:absolute;inset:0;background:url('{{HERO}}') center/cover no-repeat;}
.hero-bg::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,18,32,0.55),rgba(11,18,32,0.78));}
.hero-in{position:relative;z-index:2;max-width:680px;padding:110px 0 120px;}
.pill{display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,0.14);border:1px solid rgba(255,255,255,0.3);padding:7px 14px;border-radius:999px;font-size:0.82rem;font-weight:500;margin-bottom:22px;}
.pill .dot{width:8px;height:8px;border-radius:50%;background:var(--success);box-shadow:0 0 0 3px rgba(22,163,74,0.3);}
.hero h1{font-size:clamp(2.3rem,6vw,3.9rem);font-weight:700;letter-spacing:-0.02em;text-shadow:0 2px 24px rgba(0,0,0,0.35);}
.hero h1 .accent{color:#60a5fa;} .hero p{max-width:560px;margin:22px 0 34px;font-size:1.15rem;color:rgba(255,255,255,0.92);}
.btn-row{display:flex;gap:14px;flex-wrap:wrap;}
.trust{position:relative;z-index:2;border-top:1px solid rgba(255,255,255,0.18);padding:30px 0;display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:20px;}
.trust .t .n{font-family:var(--head);font-weight:700;font-size:2rem;color:#fff;}
.trust .t .l{color:rgba(255,255,255,0.75);font-size:0.9rem;}
section{padding:90px 0;}
.eyebrow{color:var(--accent);font-size:0.8rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase;text-align:center;margin-bottom:12px;}
h2.title{text-align:center;font-size:clamp(1.9rem,4vw,2.6rem);letter-spacing:-0.02em;margin-bottom:14px;}
.sub{text-align:center;color:var(--body);max-width:620px;margin:0 auto 48px;font-size:1.05rem;}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:22px;}
.card{background:#fff;border:1px solid var(--line);border-radius:16px;padding:30px;box-shadow:var(--shadow);transition:transform .18s;}
.card:hover{transform:translateY(-5px);} .card .icon{font-size:2rem;margin-bottom:16px;}
.card h3{font-size:1.2rem;margin-bottom:8px;} .card p{color:var(--body);font-size:0.95rem;}
.card ul{color:var(--body);font-size:0.93rem;margin-top:12px;padding-left:18px;} .card li{margin-bottom:5px;}
.dark-band{background:var(--dark);color:#fff;} .dark-band .eyebrow{color:#60a5fa;}
.dark-band .sub{color:rgba(255,255,255,0.7);} .dark-band h2.title{color:#fff;}
.dark-band .grid .card{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);box-shadow:none;}
.dark-band .card h3{color:#fff;} .dark-band .card p{color:rgba(255,255,255,0.75);}
.gallery-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;}
.gallery-grid img{border-radius:14px;height:220px;width:100%;object-fit:cover;box-shadow:var(--shadow);}
@media(max-width:760px){.gallery-grid{grid-template-columns:1fr;}}
.area-pills{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;}
.pill-tag{background:#fff;border:1px solid var(--line);border-radius:5px;padding:9px 18px;color:var(--label);font-size:0.92rem;}
.contact-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:20px;}
.cc{background:#fff;border:1px solid var(--line);border-radius:16px;padding:30px;text-align:center;box-shadow:var(--shadow);}
.cc .lbl{color:var(--muted);font-size:0.78rem;font-weight:600;letter-spacing:.12em;text-transform:uppercase;}
.cc .val{font-size:1.2rem;font-weight:700;margin-top:10px;display:block;} .cc a.val:hover{color:var(--accent);}
.cta-band{text-align:center;margin-top:46px;}
footer{background:var(--dark);color:rgba(255,255,255,0.6);padding:40px 0;text-align:center;font-size:0.9rem;} footer b{color:#fff;}
@media(max-width:640px){.nav-links{display:none;}.hero{min-height:0;}.hero-in{padding:90px 0 70px;}}
</style>
</head>
<body>
<svg style="display:none" xmlns="http://www.w3.org/2000/svg">
  <symbol id="wa" viewBox="0 0 24 24">
    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
  </symbol>
</svg>
<nav>
  <div class="wrap nav-in">
    <div class="brand">{{BUSINESS}}</div>
    <div class="nav-links">
      <a href="#services">Services</a>
      <a href="#gallery">Our Work</a>
      <a href="#areas">Areas</a>
      <a href="#contact">Contact</a>
    </div>
    <a class="btn btn-blue" href="https://wa.me/{{PHONE}}">WhatsApp Us</a>
  </div>
</nav>
<header class="hero">
  <div class="hero-bg"></div>
  <div class="wrap hero-in">
    <span class="pill"><span class="dot"></span> {{TRADE}} · {{CITY}}</span>
    <h1>{{TAGLINE}}</h1>
    <p>{{SUBHEAD}}</p>
    <div class="btn-row">
      <a class="btn btn-blue" href="https://wa.me/{{PHONE}}?text={{ENQ}}">Get a Free Quote →</a>
      <a class="btn btn-wa" href="https://wa.me/{{PHONE}}"><svg class="wa-glyph"><use href="#wa"/></svg> WhatsApp {{PHONE_DISPLAY}}</a>
      <a class="btn btn-wa" href="tel:+{{PHONE}}">📞 Call: {{PHONE_DISPLAY}}</a>
    </div>
  </div>
</header>
<section class="trust-band" style="padding:34px 0;background:var(--dark);color:#fff;">
  <div class="wrap trust">{{TRUST}}</div>
</section>
<section id="services">
  <div class="wrap">
    <div class="eyebrow">What we do</div>
    <h2 class="title">Full-service {{TRADE}}</h2>
    <p class="sub">Safe, reliable work for homes and businesses in {{CITY}}.</p>
    <div class="grid">{{SERVICES}}</div>
  </div>
</section>
{{GALLERY}}
<section id="areas">
  <div class="wrap">
    <div class="eyebrow">Service area</div>
    <h2 class="title">Serving {{CITY}} &amp; surrounds</h2>
    <div class="area-pills">{{AREAS}}</div>
  </div>
</section>
<section id="contact" style="background:#f8fafc;">
  <div class="wrap">
    <div class="eyebrow">Get in touch</div>
    <h2 class="title">Message us — we reply fast</h2>
    <div class="contact-grid">
      <div class="cc"><div class="lbl">WhatsApp / Call</div><a class="val" href="https://wa.me/{{PHONE}}">{{PHONE_DISPLAY}}</a></div>
      <div class="cc"><div class="lbl">Location</div><div class="val">{{CITY}}, {{PROVINCE}}</div></div>
      <div class="cc"><div class="lbl">Response</div><div class="val">Fast · 7 days a week</div></div>
    </div>
    <div class="cta-band">
      <a class="btn btn-blue" href="https://wa.me/{{PHONE}}?text={{ENQ}}">💬 Get a Quote on WhatsApp</a>
    </div>
  </div>
</section>
<a class="fab" href="https://wa.me/{{PHONE}}?text={{ENQ}}" aria-label="Chat on WhatsApp"><svg class="wa-glyph"><use href="#wa"/></svg></a>
<footer><div class="wrap"><b>{{BUSINESS}}</b> · {{CITY}} · {{PHONE_DISPLAY}} · {{TRADE}} work you can trust</div></footer>
</body>
</html>
"""

def build_services(cfg):
    out = []
    for s in cfg.get("services", []):
        items = "".join(f"<li>{i}</li>" for i in s.get("items", []))
        inner = f"<p>{s['title']}</p>" if not items else f"<ul>{items}</ul>"
        out.append(f'<div class="card"><div class="icon">{s.get("icon","•")}</div><h3>{s["title"]}</h3>{inner}</div>')
    return "\n".join(out)

def build_trust(cfg):
    extra = cfg.get("extra_trust", [["5.0","Google rating"],["100%","Compliant"],["Same-day","Fast response"],["COC","Certified"]])
    return "".join(f'<div class="t"><div class="n">{n}</div><div class="l">{l}</div></div>' for n,l in extra)

def build_areas(cfg):
    return "".join(f'<span class="pill-tag">{a}</span>' for a in cfg.get("areas", [cfg.get("city","")]))

def build_gallery(cfg, outdir):
    imgs = cfg.get("gallery", [])
    if not imgs:
        return ""
    items = "".join(f'<img src="{p}" alt="{cfg["business"]} work">' for p in imgs)
    return f'<section id="gallery" style="background:#f8fafc;"><div class="wrap"><div class="eyebrow">Our work</div><h2 class="title">Quality you can see</h2><div class="gallery-grid">{items}</div></div></section>'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--out", default=None)
    ap.add_argument("--deploy", default=None)
    a = ap.parse_args()

    cfg = json.load(open(a.config))
    outdir = a.out or os.path.join(os.path.dirname(os.path.abspath(a.config)), "site")
    os.makedirs(outdir, exist_ok=True)

    # copy hero + gallery images
    for key in ("hero_image",):
        src = cfg.get(key)
        if src and os.path.exists(src):
            shutil.copy(src, os.path.join(outdir, os.path.basename(src)))
    for src in cfg.get("gallery", []):
        if os.path.exists(src):
            shutil.copy(src, os.path.join(outdir, os.path.basename(src)))

    services_summary = "; ".join(s["title"] for s in cfg.get("services", []))[:160]
    page = (TEMPLATE
        .replace("{{BUSINESS}}", cfg["business"])
        .replace("{{TRADE}}", cfg.get("trade","Service"))
        .replace("{{CITY}}", cfg.get("city",""))
        .replace("{{PROVINCE}}", cfg.get("province",""))
        .replace("{{PHONE}}", cfg["phone_intl"])
        .replace("{{PHONE_DISPLAY}}", cfg.get("phone_display", cfg["phone_intl"]))
        .replace("{{RATING}}", cfg.get("rating","5.0"))
        .replace("{{ACCENT}}", cfg.get("accent","#1d4ed8"))
        .replace("{{TAGLINE}}", cfg.get("tagline","Reliable professional service."))
        .replace("{{SUBHEAD}}", cfg.get("subhead", f"{cfg['business']} — trusted {cfg.get('trade','service')} in {cfg.get('city','')}. Fast, reliable, one WhatsApp away."))
        .replace("{{HERO}}", os.path.basename(cfg["hero_image"]) if cfg.get("hero_image") else "hero.png")
        .replace("{{ENQ}}", "Hi%20" + cfg["business"].replace(" ","%20") + "%2C%20I%27d%20like%20a%20quote.")
        .replace("{{SERVICES_SUMMARY}}", services_summary)
        .replace("{{SERVICES}}", build_services(cfg))
        .replace("{{TRUST}}", build_trust(cfg))
        .replace("{{AREAS}}", build_areas(cfg))
        .replace("{{GALLERY}}", build_gallery(cfg, outdir))
    )
    idx = os.path.join(outdir, "index.html")
    open(idx, "w").write(page)
    print(f"✓ Generated {idx}")

    if a.deploy:
        script = os.path.expanduser("~/.hermes/scripts/deploy-autosite-site.sh")
        print(f"→ Deploying as {a.deploy} ...")
        subprocess.run(["bash", script, a.deploy, outdir], check=False)

if __name__ == "__main__":
    main()
