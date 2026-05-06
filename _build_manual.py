import html
from pathlib import Path

lines = Path(__file__).parent.joinpath(".manual-lines.txt").read_text(encoding="utf-8").splitlines()
lines = lines[4:]  # after tagline block

H2 = [
    ("Who This Is For", "who-this-is-for"),
    ("First Export: Start Here", "first-export"),
    ("What VitalPort Does", "what-vitalport-does"),
    ("Requirements", "requirements"),
    ("Setup", "setup"),
    ("Dashboard", "dashboard"),
    ("Exporting Your Data", "exporting-data"),
    ("Send Data to an Endpoint", "send-to-endpoint"),
    ("Automatic Scheduled Export", "scheduled-export"),
    ("Check If Your Data Is Working", "data-pipeline-status"),
    ("Fix Missing Data", "fix-missing-data"),
    ("Privacy", "manual-privacy"),
    ("Troubleshooting", "troubleshooting"),
    ("Support", "support"),
]
titles = [t for t, _ in H2]
slug_by_title = dict(H2)

idx = [i for i, l in enumerate(lines) if l in titles]
sections = []
for j, start in enumerate(idx):
    title = lines[start]
    slug = slug_by_title[title]
    end = idx[j + 1] if j + 1 < len(idx) else len(lines)
    sections.append((slug, title, lines[start + 1 : end]))


def esc(s: str) -> str:
    return html.escape(s)


def p(s: str) -> str:
    return "<p>" + esc(s) + "</p>"


H3_LITERALS = frozenset(
    {
        "What It Does",
        "Metrics",
        "Today's Briefing Card",
        "Sync Now",
        "Save a File (Export and Share)",
        "Export Formats",
        "JSON",
        "CSV",
        "Date Ranges",
        "Destination Types",
        "Configure a Destination",
        "Test Your Destination",
        "Schedule Options",
        "Set Up a Schedule",
        "Open Diagnostics",
        "What Diagnostics Shows",
        "Refresh Health Permissions",
    }
)


def fmt_default(slug: str, body: list[str]) -> str:
    out: list[str] = []
    i = 0
    while i < len(body):
        line = body[i].strip()
        if line.startswith("Note:"):
            out.append('<p class="manual-note">' + esc(line) + "</p>")
            i += 1
            continue

        if line == "VitalPort is designed for:":
            out.append("<p><strong>" + esc(line) + "</strong></p>")
            i += 1
            items: list[str] = []
            while i < len(body) and body[i][0].isupper() and not body[i].startswith("VitalPort is not"):
                if body[i].startswith("Note:"):
                    break
                items.append(body[i])
                i += 1
            if items:
                out.append("<ul>" + "".join("<li>" + esc(x) + "</li>" for x in items) + "</ul>")
            continue

        if line == "What It Does Not Do":
            out.append("<h3>" + esc(line) + "</h3>")
            i += 1
            items = []
            while i < len(body) and body[i] != "Requirements":
                if body[i] in titles:
                    break
                items.append(body[i])
                i += 1
            out.append("<ul>" + "".join("<li>" + esc(x) + "</li>" for x in items) + "</ul>")
            continue

        if slug == "dashboard" and line == "Sync Now":
            out.append("<h3>Sync Now</h3>")
            i += 1
            if i < len(body):
                out.append(p(body[i]))
                i += 1
            continue

        if line in H3_LITERALS:
            out.append("<h3>" + esc(line) + "</h3>")
            i += 1
            continue

        if line.startswith(
            ("Open VitalPort", "Tap Connect Health", "Tap Sync Now", "Tap Export", "From the dashboard, tap Sync Now")
        ):
            steps: list[str] = []
            while i < len(body):
                s = body[i]
                if s.startswith("Note:"):
                    break
                if s in titles:
                    break
                if not (
                    s.startswith("Open VitalPort")
                    or s.startswith("Tap ")
                    or s.startswith("From the dashboard, tap Sync Now")
                    or s.startswith("From the dashboard, tap Export")
                    or s.startswith("Leave the settings")
                    or s.startswith("From the iOS share sheet")
                    or s.startswith("You have now successfully")
                ):
                    break
                steps.append(s)
                i += 1
            if steps:
                out.append('<ol class="manual-steps">' + "".join("<li>" + esc(s) + "</li>" for s in steps) + "</ol>")
            continue

        if line == "Use this to generate a file and open it via the iOS share sheet.":
            out.append(p(line))
            i += 1
            steps = []
            while i < len(body) and body[i].startswith(
                ("From the dashboard, tap Export", "Choose your", "Tap Generate", "Tap Export and Share", "From the share sheet")
            ):
                steps.append(body[i])
                i += 1
            if steps:
                out.append('<ol class="manual-steps">' + "".join("<li>" + esc(s) + "</li>" for s in steps) + "</ol>")
            continue

        if line == "JSON File" and i + 1 < len(body) and body[i + 1].startswith("Saves to"):
            pairs: list[tuple[str, str]] = []
            while i + 1 < len(body):
                term = body[i]
                if term in ("Configure a Destination", "Test Your Destination") or term.startswith("Note:"):
                    break
                if term in titles:
                    break
                desc = body[i + 1]
                pairs.append((term, desc))
                i += 2
            if pairs:
                out.append(
                    '<dl class="manual-dl">'
                    + "".join("<dt>" + esc(t) + "</dt><dd>" + esc(d) + "</dd>" for t, d in pairs)
                    + "</dl>"
                )
            continue

        metric_terms = {
            "Steps",
            "Sleep",
            "HRV",
            "Resting Heart Rate",
            "Active Energy",
            "VO2 Max",
            "Weight",
            "Body Fat",
            "Workouts",
        }
        if slug == "dashboard" and line in metric_terms and i + 1 < len(body):
            pairs = []
            while i + 1 < len(body):
                t = body[i]
                if t in ("Today's Briefing Card", "Sync Now") or t.startswith("Note:"):
                    break
                if t not in metric_terms:
                    break
                pairs.append((t, body[i + 1]))
                i += 2
            if pairs:
                out.append(
                    '<dl class="manual-dl manual-metrics">'
                    + "".join("<dt>" + esc(t) + "</dt><dd>" + esc(d) + "</dd>" for t, d in pairs)
                    + "</dl>"
                )
            continue

        if slug == "requirements" and line in ("Device", "iOS Version", "Health Data Source", "App Version"):
            pairs = []
            while i < len(body) and body[i] in ("Device", "iOS Version", "Health Data Source", "App Version"):
                t = body[i]
                d = body[i + 1] if i + 1 < len(body) else ""
                pairs.append((t, d))
                i += 2
            out.append('<dl class="manual-dl">' + "".join("<dt>" + esc(t) + "</dt><dd>" + esc(d) + "</dd>" for t, d in pairs) + "</dl>")
            continue

        if slug == "data-pipeline-status" and line == "Last sync time":
            pairs = []
            labels = [
                "Last sync time",
                "Last successful export",
                "Last failure",
                "Records exported",
                "HTTP status",
            ]
            while i + 1 < len(body) and body[i] in labels:
                pairs.append((body[i], body[i + 1]))
                i += 2
            out.append('<dl class="manual-dl">' + "".join("<dt>" + esc(t) + "</dt><dd>" + esc(d) + "</dd>" for t, d in pairs) + "</dl>")
            continue

        if slug == "troubleshooting":
            probs = [
                "Dashboard shows no data after setup",
                "A specific metric is missing",
                "Export test fails",
                "VO2 Max not showing",
                "Scheduled export not running",
            ]
            if line in probs and i + 1 < len(body):
                out.append('<h3 class="manual-issue">' + esc(line) + "</h3>" + p(body[i + 1]))
                i += 2
                continue

        if line == "Reads your Health data on your iPhone":
            items = []
            while i < len(body):
                s = body[i]
                if s == "What It Does Not Do" or s in titles or s.startswith("Note:"):
                    break
                items.append(s)
                i += 1
            if items:
                out.append("<ul>" + "".join("<li>" + esc(x) + "</li>" for x in items) + "</ul>")
            continue

        if line == "Off" and i + 1 < len(body) and body[i + 1] == "No automatic exports":
            pairs = []
            for _t, _d in [
                ("Off", "No automatic exports"),
                ("Daily", "Exports once per day at your preferred time"),
                ("Weekly", "Exports once per week on your chosen day and time"),
            ]:
                if i + 1 < len(body) and body[i] == _t:
                    pairs.append((_t, body[i + 1]))
                    i += 2
            if pairs:
                out.append(
                    '<dl class="manual-dl">' + "".join("<dt>" + esc(t) + "</dt><dd>" + esc(d) + "</dd>" for t, d in pairs) + "</dl>"
                )
            continue

        if slug == "setup" and line == "Connect Health":
            out.append("<h3>" + esc(line) + "</h3>")
            i += 1
            continue

        if slug == "setup" and line == "VitalPort reads the following metrics when authorized:":
            out.append(p(line))
            i += 1
            items = []
            while i < len(body) and not body[i].startswith("Note:"):
                if body[i] == "Weight Units":
                    break
                items.append(body[i])
                i += 1
            if items:
                out.append("<ul>" + "".join("<li>" + esc(x) + "</li>" for x in items) + "</ul>")
            continue

        if slug == "setup" and line == "Weight Units":
            out.append("<h3>" + esc(line) + "</h3>")
            i += 1
            continue

        if slug == "exporting-data" and line == "Today" and i + 1 < len(body) and "data only" in body[i + 1]:
            pairs = []
            ranges = [
                ("Today", "Today's data only"),
                ("Last 7 Days", "Rolling 7-day window"),
                ("30 Days", "Coming soon"),
                ("90 Days", "Coming soon"),
            ]
            for t, d in ranges:
                if i + 1 < len(body) and body[i] == t:
                    pairs.append((t, body[i + 1]))
                    i += 2
            if pairs:
                out.append(
                    '<dl class="manual-dl manual-date-ranges">'
                    + "".join("<dt>" + esc(t) + "</dt><dd>" + esc(d) + "</dd>" for t, d in pairs)
                    + "</dl>"
                )
            continue

        if slug == "support" and line == "Website":
            pairs = []
            while i + 1 < len(body) and body[i].strip() in ("Website", "App Store", "App Version"):
                t, d = body[i].strip(), body[i + 1].strip()
                if t == "Website":
                    d_html = '<a href="https://' + esc(d) + '/">' + esc(d) + "</a>"
                    pairs.append((t, d_html))
                elif t == "App Store":
                    d_html = (
                        'Use the <a href="https://apps.apple.com/app/id6764275336">App Store support link</a> '
                        "on the VitalPort listing for questions, feedback, or bug reports."
                    )
                    pairs.append((t, d_html))
                else:
                    pairs.append((t, esc(d)))
                i += 2
            out.append(
                '<dl class="manual-dl">'
                + "".join("<dt>" + esc(t) + "</dt><dd>" + d + "</dd>" for t, d in pairs)
                + "</dl>"
            )
            continue

        out.append(p(line))
        i += 1
    return "".join(out)


parts: list[str] = ['<div class="manual-toc"><p class="manual-toc-label">On this page</p><ul>']
for slug, title, _ in sections:
    parts.append(f'<li><a href="#{slug}">{esc(title)}</a></li>')
parts.append("</ul></div>")

for slug, title, body in sections:
    parts.append(f'<section id="{slug}" class="manual-section">')
    parts.append(f"<h2>{esc(title)}</h2>")
    parts.append(fmt_default(slug, body))
    parts.append("</section>")

article = "\n".join(parts)
manual_dir = Path(__file__).parent.joinpath("manual")
manual_dir.joinpath("_article.html").write_text(article, encoding="utf-8")
print("wrote manual/_article.html", len(article))

MANUAL_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>User Manual | VitalPort</title>
<meta name="description" content="VitalPort user manual: export Health as JSON or CSV, destinations, schedules, diagnostics, and support.">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Bricolage+Grotesque:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  :root {{
    --graphite: #1A2B3C;
    --graphite-light: #243545;
    --steel: #4A90B8;
    --green: #5DB88A;
    --white: #F0F4F8;
    --muted: #8BA4B8;
    --surface: #111d28;
    --surface2: #0d1820;
    --border: rgba(74, 144, 184, 0.15);
  }}
  html {{ scroll-behavior: smooth; }}
  body {{
    background: var(--surface2);
    color: var(--white);
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 300;
    line-height: 1.7;
    overflow-x: hidden;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }}
  body::before {{
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
    opacity: 0.4;
  }}
  body::after {{
    content: '';
    position: fixed;
    inset: 0;
    background-image:
      linear-gradient(rgba(74,144,184,0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(74,144,184,0.04) 1px, transparent 1px);
    background-size: 64px 64px;
    pointer-events: none;
    z-index: 0;
  }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 0 2rem; position: relative; z-index: 1; }}
  nav {{
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 100;
    padding: 1.25rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    flex-wrap: wrap;
    background: rgba(13, 24, 32, 0.85);
    backdrop-filter: blur(12px);
    border-bottom: 0.5px solid var(--border);
  }}
  .nav-logo {{ display: flex; align-items: center; gap: 10px; text-decoration: none; }}
  .nav-icon {{ width: 32px; height: 32px; }}
  .nav-wordmark {{
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 500;
    font-size: 17px;
    color: var(--white);
    letter-spacing: -0.02em;
  }}
  .nav-actions {{ display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; justify-content: flex-end; }}
  .nav-cta {{
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    color: var(--green);
    text-decoration: none;
    border: 0.5px solid var(--green);
    padding: 6px 14px;
    border-radius: 2px;
    transition: background 0.2s, color 0.2s;
    letter-spacing: 0.04em;
  }}
  .nav-cta:hover {{ background: var(--green); color: var(--graphite); }}
  .nav-cta--primary {{
    background: var(--steel);
    border-color: var(--steel);
    color: var(--graphite);
  }}
  .nav-cta--primary:hover {{
    background: #5aa3ce;
    border-color: #5aa3ce;
    color: var(--graphite);
  }}
  main {{ flex: 1; padding: 7rem 0 4rem; position: relative; z-index: 1; }}
  .manual-wrap {{ max-width: 720px; margin: 0 auto; }}
  .manual-eyebrow {{
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.12em;
    color: var(--green);
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .manual-eyebrow::before {{
    content: '';
    display: inline-block;
    width: 16px;
    height: 1px;
    background: var(--green);
  }}
  h1 {{
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 600;
    font-size: clamp(2rem, 4vw, 2.75rem);
    letter-spacing: -0.03em;
    line-height: 1.15;
    color: var(--white);
    margin-bottom: 0.75rem;
  }}
  .manual-lead {{
    font-size: 1rem;
    color: var(--muted);
    line-height: 1.75;
    margin-bottom: 2rem;
  }}
  .manual-toc {{
    margin-bottom: 2.5rem;
    padding: 1.25rem 1.5rem;
    background: var(--surface);
    border: 0.5px solid var(--border);
    border-left: 3px solid var(--green);
  }}
  .manual-toc-label {{
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.1em;
    color: var(--green);
    margin-bottom: 0.75rem;
    text-transform: uppercase;
  }}
  .manual-toc ul {{
    list-style: none;
    columns: 2;
    column-gap: 2rem;
  }}
  .manual-toc li {{ margin-bottom: 0.4rem; break-inside: avoid; }}
  .manual-toc a {{
    font-size: 0.85rem;
    color: var(--steel);
    text-decoration: none;
  }}
  .manual-toc a:hover {{ color: var(--green); }}
  .manual-section {{
    margin-bottom: 1.25rem;
    padding: 1.5rem 1.5rem 1.35rem;
    background: var(--surface);
    border: 0.5px solid var(--border);
    border-left: 3px solid var(--steel);
  }}
  .manual-section h2 {{
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 600;
    font-size: 1.15rem;
    color: var(--white);
    margin-bottom: 0.85rem;
    letter-spacing: -0.02em;
  }}
  .manual-section h3 {{
    font-family: 'Bricolage Grotesque', sans-serif;
    font-weight: 600;
    font-size: 0.98rem;
    color: var(--white);
    margin: 1.1rem 0 0.5rem;
  }}
  .manual-section h3:first-child {{ margin-top: 0; }}
  .manual-section p {{
    font-size: 0.9rem;
    color: var(--muted);
    line-height: 1.65;
    margin-bottom: 0.65rem;
  }}
  .manual-section p:last-child {{ margin-bottom: 0; }}
  .manual-section ul, .manual-section ol {{
    font-size: 0.9rem;
    color: var(--muted);
    margin: 0.5rem 0 0.75rem 1.1rem;
    line-height: 1.55;
  }}
  .manual-section li {{ margin-bottom: 0.35rem; }}
  .manual-steps {{ margin-left: 1.25rem; }}
  .manual-note {{
    font-size: 0.82rem;
    color: var(--green);
    opacity: 0.95;
    border-left: 2px solid var(--green);
    padding-left: 0.75rem;
    margin-top: 0.75rem !important;
  }}
  .manual-dl {{ margin: 0.5rem 0 0.75rem; }}
  .manual-dl dt {{
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.04em;
    color: var(--white);
    margin-top: 0.65rem;
  }}
  .manual-dl dt:first-child {{ margin-top: 0; }}
  .manual-dl dd {{
    font-size: 0.88rem;
    color: var(--muted);
    margin: 0.2rem 0 0 0;
    padding-left: 0;
  }}
  .manual-dl dd a {{ color: var(--steel); }}
  .manual-dl dd a:hover {{ color: var(--green); }}
  .manual-issue {{ color: var(--steel) !important; }}
  footer {{
    padding: 2rem;
    border-top: 0.5px solid var(--border);
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1.25rem;
    position: relative;
    z-index: 1;
  }}
  .footer-block {{ display: flex; flex-direction: column; gap: 0.65rem; max-width: 420px; }}
  .footer-logo {{
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    color: var(--muted);
    opacity: 0.5;
    letter-spacing: 0.06em;
  }}
  .footer-links {{ display: flex; flex-wrap: wrap; gap: 0.65rem 1.1rem; }}
  .footer-link {{
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: var(--steel);
    text-decoration: none;
    letter-spacing: 0.04em;
    opacity: 0.9;
  }}
  .footer-link:hover {{ color: var(--green); }}
  .footer-support {{
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 0.03em;
    line-height: 1.55;
    opacity: 0.85;
    margin-top: 0.25rem;
  }}
  .footer-tagline {{
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: var(--muted);
    opacity: 0.4;
    letter-spacing: 0.04em;
    align-self: center;
  }}
  @media (max-width: 640px) {{
    nav {{ padding: 1rem 1.25rem; }}
    footer {{ flex-direction: column; align-items: flex-start; }}
    .manual-toc ul {{ columns: 1; }}
  }}
</style>
</head>
<body>

<nav>
  <a href="/" class="nav-logo">
    <svg class="nav-icon" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect width="32" height="32" rx="7" fill="#1A2B3C"/>
      <polyline points="6,7 16,22 26,7" fill="none" stroke="#4A90B8" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
      <polyline points="2,27 7,27 9.5,22 12,29 14.5,19 17,27 30,27" fill="none" stroke="#5DB88A" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
      <circle cx="16" cy="22" r="1.5" fill="#5DB88A"/>
    </svg>
    <span class="nav-wordmark">VitalPort</span>
  </a>
  <div class="nav-actions">
    <a data-vp-href="appStore" href="https://apps.apple.com/app/id6764275336" class="nav-cta nav-cta--primary">Download on the App Store</a>
    <a href="/" class="nav-cta">Home</a>
  </div>
</nav>

<main>
  <div class="container">
    <article class="manual-wrap">
      <p class="manual-eyebrow">Documentation</p>
      <h1>User Manual</h1>
      <p class="manual-lead">Export, route, and own your Health data.</p>
{article}
    </article>
  </div>
</main>

<footer>
  <div class="footer-block">
    <span class="footer-logo">VITALPORT.APP</span>
    <nav class="footer-links" aria-label="Footer">
      <a data-vp-href="appStore" href="https://apps.apple.com/app/id6764275336" class="footer-link">App Store</a>
      <a href="/manual/" class="footer-link" aria-current="page">User Manual</a>
      <a data-vp-href="privacy" href="/privacy/" class="footer-link">Privacy Policy</a>
    </nav>
    <p class="footer-support">Questions or feedback? Use the App Store support link.</p>
  </div>
  <span class="footer-tagline">Own your health data.</span>
</footer>

<script src="/site-config.js"></script>
<script>
(function () {{
  var L = window.VITALPORT_LINKS;
  if (!L) return;
  document.querySelectorAll('[data-vp-href]').forEach(function (el) {{
    var key = el.getAttribute('data-vp-href');
    if (key && L[key]) el.setAttribute('href', L[key]);
  }});
}})();
</script>
</body>
</html>
"""

full = MANUAL_TEMPLATE.format(article=article)
manual_dir.joinpath("index.html").write_text(full, encoding="utf-8")
print("wrote manual/index.html", len(full))
