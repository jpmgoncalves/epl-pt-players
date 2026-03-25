#!/usr/bin/env python3
"""Build index.html from CSV data + logos."""
import csv
from collections import OrderedDict

CSV_PATH = "Portuguese EPL Players by Season.csv"
OUTPUT_PATH = "index.html"

# Club name → (logo file, brand color)
CLUBS = {
    "Arsenal":                  ("logos/arsenal.svg",              "#EF0107"),
    "Aston Villa":              ("logos/astonvilla.svg",           "#670E36"),
    "Bolton Wanderers":         ("logos/boltonwanderers.png",      "#263B7B"),
    "Bradford City":            ("logos/bradford.png",             "#7A1A2E"),
    "Brentford":                ("logos/brentford.svg",            "#E30613"),
    "Burnley":                  ("logos/burnley.svg",              "#6C1D45"),
    "Charlton Athletic":        ("logos/charltonathl.png",         "#D4021D"),
    "Chelsea":                  ("logos/chelseafc.svg",            "#034694"),
    "Everton":                  ("logos/everton.svg",              "#003399"),
    "Fulham":                   ("logos/fulham.svg",               "#CC0000"),
    "Leeds United":             ("logos/leeds.svg",                "#1D428A"),
    "Leicester City":           ("logos/leicester.png",            "#003090"),
    "Liverpool":                ("logos/liverpool.svg",            "#C8102E"),
    "Manchester City":          ("logos/mancity.svg",              "#6CABDD"),
    "Manchester United":        ("logos/manutd.svg",               "#DA020E"),
    "Middlesbrough":            ("logos/middlesbrough.png",        "#E41B17"),
    "Newcastle United":         ("logos/newcastleufc.svg",         "#241F20"),
    "Norwich City":             ("logos/norwhich.png",             "#FFF200"),
    "Nottingham Forest":        ("logos/nottinghamforest.svg",     "#DD0000"),
    "Portsmouth":               ("logos/portsmouth.png",           "#001489"),
    "Queens Park Rangers":      ("logos/queenparkrangers.png",     "#1D5BA4"),
    "Reading":                  ("logos/reading.png",              "#004494"),
    "Southampton":              ("logos/southampton.png",          "#D71920"),
    "Swansea City":             ("logos/swansea.png",              "#121212"),
    "Tottenham Hotspur":        ("logos/tottenham.svg",            "#132257"),
    "Watford":                  ("logos/watford.png",              "#FBEE23"),
    "West Bromwich Albion":     ("logos/westbromwichalbion.png",   "#122F67"),
    "West Ham United":          ("logos/westham.svg",              "#7A263A"),
    "Wolverhampton Wanderers":  ("logos/wolves.svg",              "#FDB913"),
}

# ── Read CSV ──────────────────────────────────────────────────────────
rows = []
with open(CSV_PATH, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        rows.append(r)

# Group by season → club → [players]
seasons = OrderedDict()
for r in rows:
    s = r["Season"]
    c = r["Club"]
    n = r["Name"]
    seasons.setdefault(s, OrderedDict())
    seasons[s].setdefault(c, [])
    seasons[s][c].append(n)

# Compute stats
unique_players = set(r["Name"] for r in rows)
unique_clubs = set(r["Club"] for r in rows)
total_seasons = len(seasons)
total_unique_players = len(unique_players)
total_unique_clubs = len(unique_clubs)

# Sort seasons descending (most recent first)
sorted_seasons = sorted(seasons.keys(), key=lambda s: s[:4], reverse=True)

# All clubs that appear, sorted
all_clubs_sorted = sorted(unique_clubs)


# ── Helpers ───────────────────────────────────────────────────────────
def club_logo(club):
    return CLUBS.get(club, ("", "#888"))[0]

def club_color(club):
    return CLUBS.get(club, ("", "#888"))[1]

def ordinal(n):
    """1→1st, 2→2nd etc."""
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    return f"{n}" + {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


# ── Build dropdown items ──────────────────────────────────────────────
dropdown_items = ['        <div class="pl-dropdown-item selected" data-value="all"><span>All Clubs</span></div>']
for club in all_clubs_sorted:
    logo = club_logo(club)
    img = f'<img src="{logo}" alt="">' if logo else ""
    dropdown_items.append(
        f'        <div class="pl-dropdown-item" data-value="{club}">'
        f'{img}<span>{club}</span></div>'
    )
dropdown_html = "\n".join(dropdown_items)


# ── Build season entries ──────────────────────────────────────────────
entries = []
for idx, season in enumerate(sorted_seasons):
    clubs_in_season = seasons[season]
    total_players = sum(len(ps) for ps in clubs_in_season.values())
    num_clubs = len(clubs_in_season)

    club_names = list(clubs_in_season.keys())
    data_clubs = ",".join(club_names)
    delay = f"{idx * 0.02:.2f}s"

    # Mark the most recent season as notable
    notable = " notable" if idx == 0 else ""

    player_sfx = "player" if total_players == 1 else "players"
    club_sfx = "club" if num_clubs == 1 else "clubs"

    club_sections = []
    for club, players in clubs_in_season.items():
        logo = club_logo(club)
        color = club_color(club)
        player_count = len(players)
        p_sfx = "player" if player_count == 1 else "players"

        chips = []
        for i, player in enumerate(players):
            ord_num = ordinal(i + 1)
            chips.append(
                f'            <div class="pl-player">'
                f'<span class="pl-player-num">{ord_num}</span>'
                f'<span class="pl-player-name">{player}</span></div>'
            )
        chips_html = "\n".join(chips)

        img_tag = f'<img src="{logo}" alt="" style="width:20px;height:20px;object-fit:contain">' if logo else ""

        club_sections.append(f"""          <div class="pl-club-section">
            <div class="pl-club-section-head">
              <div class="pl-club-accent" style="background:{color}"></div>
              {img_tag}
              <span class="pl-club-section-name">{club}</span>
              <span class="pl-club-player-count">{player_count} {p_sfx}</span>
            </div>
            <div class="pl-club-players">
{chips_html}
            </div>
          </div>""")

    club_sections_html = "\n".join(club_sections)

    entries.append(f"""      <div class="pl-entry{notable}" data-clubs="{data_clubs}" style="animation-delay:{delay}">
        <div class="pl-card">
          <div class="pl-card-top">
            <span class="pl-season">{season}</span>
            <div class="pl-card-summary">
              <span>{total_players} {player_sfx}</span>
              <span class="pl-card-summary-sep"></span>
              <span>{num_clubs} {club_sfx}</span>
            </div>
          </div>
          <div class="pl-club-sections">
{club_sections_html}
          </div>
        </div>
      </div>""")

entries_html = "\n".join(entries)


# ── Full HTML ─────────────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-YE712X5P2E"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-YE712X5P2E');
</script>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Portuguese Players — Premier League</title>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800;900&family=Barlow:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --pl-bg:#faf9fa; --pl-white:#ffffff; --pl-purple:#37003c; --pl-purple-80:#541e5d;
    --pl-purple-10:#ebe5eb; --pl-purple-5:#f5f2f5; --pl-magenta:#e90052;
    --pl-green:#00ff87; --pl-cyan:#05f0ff; --pl-text:#37003c;
    --pl-text-mid:rgba(55,0,60,0.6); --pl-text-dim:rgba(55,0,60,0.4);
    --pl-border:#e5e5e5; --pl-border-strong:#d0c9d0;
    --pl-radius:4px; --pl-radius-l:8px;
    --font-display:'Barlow Condensed',system-ui,sans-serif;
    --font-body:'Barlow',system-ui,sans-serif;
  }}
  *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
  html{{scroll-behavior:smooth}}
  body{{background:var(--pl-bg);color:var(--pl-text);font-family:var(--font-body);font-size:15px;line-height:1.5;min-height:100vh}}

  .pl-utility-bar{{background:var(--pl-purple);padding:0 32px;height:36px;display:flex;align-items:center}}
  .pl-utility-bar-links{{display:flex;gap:24px}}
  .pl-utility-bar a{{font-size:12px;font-weight:500;color:rgba(255,255,255,0.7);text-decoration:none}}
  .pl-utility-bar a:hover{{color:white}}

  .pl-nav{{background:var(--pl-white);border-bottom:1px solid var(--pl-border);height:64px;display:flex;align-items:center;padding:0 32px;position:sticky;top:0;z-index:100;box-shadow:0 1px 4px rgba(55,0,60,0.08)}}
  .pl-nav-inner{{max-width:1100px;width:100%;margin:0 auto;display:flex;align-items:center;justify-content:space-between}}
  .pl-nav-brand{{display:flex;align-items:center;gap:10px}}
  .pl-nav-wordmark{{font-family:var(--font-display);font-weight:800;font-size:16px;letter-spacing:0.05em;text-transform:uppercase;color:var(--pl-purple);line-height:1.1}}
  .pl-nav-wordmark span{{display:block;font-size:10px;font-weight:600;color:var(--pl-magenta);letter-spacing:0.12em}}
  .pl-nav-tag{{background:var(--pl-purple);color:var(--pl-white);font-family:var(--font-display);font-weight:700;font-size:11px;letter-spacing:0.1em;text-transform:uppercase;padding:6px 14px;border-radius:var(--pl-radius)}}

  .pl-hero{{background:linear-gradient(100deg,var(--pl-purple) 0%,#6a1a8a 35%,#3b82c4 65%,var(--pl-cyan) 100%);padding:52px 32px 48px;position:relative;overflow:hidden}}
  .pl-hero::after{{content:'';position:absolute;top:-50%;right:-10%;width:50%;height:200%;background:linear-gradient(135deg,transparent 40%,rgba(255,255,255,0.05) 50%,transparent 60%);pointer-events:none}}
  .pl-hero-inner{{max-width:1100px;margin:0 auto;position:relative}}
  .pl-hero-kicker{{font-family:var(--font-display);font-size:11px;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;color:var(--pl-green);margin-bottom:12px;display:block}}
  .pl-hero-h1{{font-family:var(--font-display);font-weight:900;font-size:clamp(36px,5.5vw,72px);line-height:1;letter-spacing:-0.01em;text-transform:uppercase;color:var(--pl-white);margin-bottom:12px}}
  .pl-hero-desc{{font-size:15px;color:rgba(255,255,255,0.75);max-width:480px;line-height:1.6;margin-bottom:32px}}
  .pl-hero-stats{{display:flex;gap:2px;flex-wrap:wrap;max-width:680px}}
  .pl-hero-stat{{flex:1;min-width:110px;background:rgba(255,255,255,0.12);border:1px solid rgba(255,255,255,0.2);padding:14px 16px}}
  .pl-hero-stat-num{{font-family:var(--font-display);font-weight:900;font-size:26px;color:var(--pl-white);display:block;line-height:1}}
  .pl-hero-stat-sub{{font-family:var(--font-display);font-weight:700;font-size:11px;color:var(--pl-green);display:block;margin-top:2px;line-height:1.3}}
  .pl-hero-stat-label{{font-size:10px;font-weight:600;color:rgba(255,255,255,0.5);text-transform:uppercase;letter-spacing:0.08em;margin-top:3px;display:block}}

  .pl-filter-bar{{background:var(--pl-white);border-bottom:1px solid var(--pl-border);position:sticky;top:64px;z-index:90}}
  .pl-filter-inner{{max-width:1100px;margin:0 auto;padding:0 32px;height:56px;display:flex;align-items:center;gap:12px}}
  .pl-filter-label{{font-family:var(--font-display);font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:var(--pl-text-dim);flex-shrink:0}}
  .pl-filter-result{{font-family:var(--font-display);font-size:12px;font-weight:700;letter-spacing:0.06em;color:var(--pl-text-dim);background:var(--pl-purple-10);padding:4px 10px;border-radius:2px;white-space:nowrap}}

  .pl-dropdown{{position:relative;flex-shrink:0}}
  .pl-dropdown-btn{{display:inline-flex;align-items:center;gap:8px;background:var(--pl-white);border:1px solid var(--pl-border-strong);border-radius:var(--pl-radius);padding:7px 12px;font-family:var(--font-display);font-weight:700;font-size:13px;letter-spacing:0.04em;color:var(--pl-purple);cursor:pointer;min-width:210px;justify-content:space-between;transition:border-color 0.15s,background 0.15s;user-select:none}}
  .pl-dropdown-btn:hover{{border-color:var(--pl-purple-80);background:var(--pl-purple-5)}}
  .pl-dropdown-btn.open{{border-color:var(--pl-purple);background:var(--pl-purple-5)}}
  .pl-dropdown-arrow{{width:0;height:0;border-left:4px solid transparent;border-right:4px solid transparent;border-top:5px solid var(--pl-purple);transition:transform 0.2s;flex-shrink:0}}
  .pl-dropdown-btn.open .pl-dropdown-arrow{{transform:rotate(180deg)}}
  .pl-dropdown-menu{{position:absolute;top:calc(100% + 4px);left:0;background:var(--pl-white);border:1px solid var(--pl-border-strong);border-radius:var(--pl-radius-l);box-shadow:0 8px 24px rgba(55,0,60,0.12);min-width:260px;max-height:380px;overflow-y:auto;z-index:200;display:none}}
  .pl-dropdown-menu.open{{display:block}}
  .pl-dropdown-menu::-webkit-scrollbar{{width:4px}}
  .pl-dropdown-menu::-webkit-scrollbar-thumb{{background:var(--pl-purple-10);border-radius:2px}}
  .pl-dropdown-item{{display:flex;align-items:center;gap:8px;padding:9px 16px;font-family:var(--font-display);font-size:13px;font-weight:600;letter-spacing:0.03em;color:var(--pl-text);cursor:pointer;transition:background 0.1s;border-bottom:1px solid var(--pl-border)}}
  .pl-dropdown-item:last-child{{border-bottom:none}}
  .pl-dropdown-item:hover{{background:var(--pl-purple-5)}}
  .pl-dropdown-item.selected{{background:var(--pl-purple);color:var(--pl-white)}}
  .pl-dropdown-item.selected:hover{{background:var(--pl-purple-80)}}
  .pl-dropdown-item-dot{{width:8px;height:8px;border-radius:50%;flex-shrink:0}}
  .pl-dropdown-item img{{width:18px;height:18px;object-fit:contain;flex-shrink:0}}

  .pl-section-head{{max-width:1100px;margin:0 auto;padding:28px 32px 16px;display:flex;align-items:center;justify-content:space-between;gap:16px}}
  .pl-section-title{{font-family:var(--font-display);font-weight:900;font-size:22px;letter-spacing:0.02em;text-transform:uppercase;color:var(--pl-purple)}}
  .pl-section-count{{font-family:var(--font-display);font-size:12px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:var(--pl-text-dim);background:var(--pl-purple-10);padding:4px 10px;border-radius:2px}}

  main{{max-width:1100px;margin:0 auto;padding:0 32px 80px}}

  .pl-timeline{{position:relative;padding-left:52px}}
  .pl-timeline::before{{content:'';position:absolute;left:16px;top:8px;bottom:8px;width:2px;background:linear-gradient(180deg,transparent 0%,var(--pl-magenta) 3%,var(--pl-border) 6%,var(--pl-border) 94%,transparent 100%)}}

  .pl-entry{{position:relative;margin-bottom:8px;opacity:0;transform:translateY(8px);animation:plFadeUp 0.3s ease forwards}}
  @keyframes plFadeUp{{to{{opacity:1;transform:translateY(0)}}}}
  .pl-entry::before{{content:'';position:absolute;left:-38px;top:20px;width:12px;height:12px;border-radius:50%;background:var(--pl-white);border:2px solid var(--pl-border-strong);z-index:2;transition:transform 0.2s,background 0.2s,border-color 0.2s}}
  .pl-entry:hover::before{{transform:scale(1.3);background:var(--pl-magenta);border-color:var(--pl-magenta)}}
  .pl-entry.notable::before{{background:var(--pl-magenta);border-color:var(--pl-magenta);box-shadow:0 0 0 4px rgba(233,0,82,0.12)}}
  .pl-entry.hidden{{display:none}}

  .pl-card{{background:var(--pl-white);border:1px solid var(--pl-border);border-left:3px solid transparent;border-radius:var(--pl-radius-l);overflow:hidden;transition:border-left-color 0.2s,box-shadow 0.2s}}
  .pl-card:hover{{border-left-color:var(--pl-magenta);box-shadow:0 2px 16px rgba(55,0,60,0.08)}}
  .pl-card-top{{display:flex;align-items:center;justify-content:space-between;padding:14px 20px 12px;gap:12px;flex-wrap:wrap}}
  .pl-season{{font-family:var(--font-display);font-weight:900;font-size:20px;letter-spacing:0.02em;color:var(--pl-purple);line-height:1}}
  .pl-card-summary{{font-size:12px;color:var(--pl-text-dim);display:flex;align-items:center;gap:6px}}
  .pl-card-summary-sep{{width:3px;height:3px;border-radius:50%;background:var(--pl-border-strong)}}

  .pl-club-sections{{border-top:1px solid var(--pl-border)}}
  .pl-club-section{{border-bottom:1px solid var(--pl-border);transition:background 0.12s}}
  .pl-club-section:last-child{{border-bottom:none}}
  .pl-club-section:hover{{background:var(--pl-purple-5)}}
  .pl-club-section-head{{display:flex;align-items:center;gap:8px;padding:9px 20px 7px}}
  .pl-club-accent{{width:3px;height:22px;border-radius:2px;flex-shrink:0}}
  .pl-club-section-name{{font-family:var(--font-display);font-size:13px;font-weight:800;letter-spacing:0.06em;text-transform:uppercase;color:var(--pl-purple)}}
  .pl-club-player-count{{margin-left:auto;font-family:var(--font-display);font-size:11px;font-weight:600;color:var(--pl-text-dim);letter-spacing:0.05em}}
  .pl-club-players{{display:flex;flex-wrap:wrap;gap:5px;padding:0 20px 10px 31px}}

  /* PLAYER CHIP */
  .pl-player{{display:inline-flex;align-items:stretch;background:var(--pl-bg);border:1px solid var(--pl-border);border-radius:var(--pl-radius);overflow:hidden;font-size:13px;font-weight:500;color:var(--pl-text);transition:background 0.12s,border-color 0.12s}}
  .pl-player:hover{{background:var(--pl-purple-10);border-color:var(--pl-border-strong)}}
  .pl-player-num{{display:inline-flex;align-items:center;gap:0;background:var(--pl-purple-10);color:var(--pl-purple);font-family:var(--font-display);font-size:12px;font-weight:800;padding:4px 6px 4px 8px;border-right:1px solid var(--pl-border-strong);line-height:1;flex-shrink:0}}
  .pl-player-num sup{{font-size:8px;font-weight:700;vertical-align:super}}
  .pl-player-name{{padding:4px 8px;display:inline-flex;align-items:center}}

  .pl-footer{{background:var(--pl-purple);padding:32px}}
  .pl-footer-inner{{max-width:1100px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px}}
  .pl-footer-brand{{font-family:var(--font-display);font-size:14px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:rgba(255,255,255,0.7);display:flex;align-items:center;gap:8px}}
  .pl-footer-dot{{width:6px;height:6px;border-radius:50%;background:var(--pl-green)}}
  .pl-footer-note{{font-size:12px;color:rgba(255,255,255,0.4)}}

  ::-webkit-scrollbar{{width:5px}}
  ::-webkit-scrollbar-track{{background:var(--pl-bg)}}
  ::-webkit-scrollbar-thumb{{background:var(--pl-purple-10);border-radius:3px}}
  ::-webkit-scrollbar-thumb:hover{{background:var(--pl-purple-80)}}

  @media(max-width:640px){{
    .pl-utility-bar,.pl-nav,.pl-hero,.pl-section-head,main,.pl-footer{{padding-left:16px;padding-right:16px}}
    .pl-filter-inner{{padding:0 16px}}
    .pl-timeline{{padding-left:36px}}
    .pl-timeline::before{{left:10px}}
    .pl-entry::before{{left:-27px}}
    .pl-utility-bar{{display:none}}
    .pl-club-players{{padding-left:20px}}
  }}

  .pl-footer-links {{ display: flex; align-items: center; gap: 8px; }}
  .pl-footer-link {{ font-size: 12px; font-weight: 600; color: rgba(255,255,255,0.65); text-decoration: none; transition: color 0.15s; }}
  .pl-footer-link:hover {{ color: var(--pl-green); }}
  .pl-footer-link--dim {{ color: rgba(255,255,255,0.35); }}
  .pl-footer-link--dim:hover {{ color: rgba(255,255,255,0.6); }}
  .pl-footer-link-sep {{ color: rgba(255,255,255,0.25); font-size: 12px; }}
</style>
</head>
<body>

<div class="pl-utility-bar">
  <div class="pl-utility-bar-links">
    <a href="#">Premier League</a><a href="#">Shop</a><a href="#">About Us</a><a href="#">Football &amp; Community</a><a href="#">Media</a>
  </div>
</div>

<nav class="pl-nav">
  <div class="pl-nav-inner">
    <div class="pl-nav-brand">
      <img src="logos/pl-logo.png" alt="Premier League" style="height:44px;width:auto;object-fit:contain">
      <div class="pl-nav-wordmark">Premier League<span>\U0001f1f5\U0001f1f9 Portuguese Players</span></div>
    </div>
    <div class="pl-nav-tag">Heritage Archive</div>
  </div>
</nav>

<section class="pl-hero">
  <div class="pl-hero-inner">
    <span class="pl-hero-kicker">Since 1995/96</span>
    <h1 class="pl-hero-h1">Portuguese Players<br>in the Premier League</h1>
    <p class="pl-hero-desc">A comprehensive season-by-season record of every Portuguese player to appear in the Premier League — from pioneers to present day.</p>
    <div class="pl-hero-stats">
      <div class="pl-hero-stat">
        <span class="pl-hero-stat-num">{total_seasons}</span>
        <span class="pl-hero-stat-label">Seasons</span>
      </div>
      <div class="pl-hero-stat">
        <span class="pl-hero-stat-num">{total_unique_players}</span>
        <span class="pl-hero-stat-label">Unique Players</span>
      </div>
      <div class="pl-hero-stat">
        <span class="pl-hero-stat-num">{total_unique_clubs}</span>
        <span class="pl-hero-stat-label">Clubs</span>
      </div>
    </div>
  </div>
</section>

<div class="pl-filter-bar">
  <div class="pl-filter-inner">
    <span class="pl-filter-label">Filter by Club</span>
    <div class="pl-dropdown">
      <div class="pl-dropdown-btn" id="dropdownBtn">
        <span id="dropdownLabel">All Clubs</span>
        <span class="pl-dropdown-arrow"></span>
      </div>
      <div class="pl-dropdown-menu" id="dropdownMenu">
{dropdown_html}
      </div>
    </div>
    <span class="pl-filter-result" id="filterResult">{total_seasons} seasons shown</span>
  </div>
</div>

<div class="pl-section-head">
  <h2 class="pl-section-title">Season-by-Season Timeline</h2>
  <span class="pl-section-count" id="sectionCount">{total_seasons} seasons &middot; most recent first</span>
</div>

<main>
  <div class="pl-timeline" id="timeline">
{entries_html}
  </div>
</main>

<footer class="pl-footer">
  <div class="pl-footer-inner">
    <div class="pl-footer-brand"><div class="pl-footer-dot"></div>Premier League &mdash; Portuguese Players Archive</div>
    <div class="pl-footer-links">
      <a href="https://joaopmgoncalves.com/" target="_blank" rel="noopener" class="pl-footer-link">Made by Jo&atilde;o Gon&ccedil;alves</a>
      <span class="pl-footer-link-sep">&middot;</span>
      <a href="https://github.com/jpmgoncalves/epl-pt-players" target="_blank" rel="noopener" class="pl-footer-link pl-footer-link--dim">Public Repository</a>
    </div>
    <p class="pl-footer-note">Data sourced from official records. Includes Portuguese players who made at least one PL appearance.</p>
  </div>
</footer>

<script>
const btn=document.getElementById('dropdownBtn'),menu=document.getElementById('dropdownMenu'),label=document.getElementById('dropdownLabel'),filterResult=document.getElementById('filterResult'),sectionCount=document.getElementById('sectionCount'),entries=document.querySelectorAll('.pl-entry');
btn.addEventListener('click',e=>{{e.stopPropagation();btn.classList.toggle('open');menu.classList.toggle('open')}});
document.addEventListener('click',()=>{{btn.classList.remove('open');menu.classList.remove('open')}});
menu.querySelectorAll('.pl-dropdown-item').forEach(item=>{{
  item.addEventListener('click',e=>{{
    e.stopPropagation();
    const value=item.dataset.value,text=item.querySelector('span:last-child')?.textContent.trim()||item.textContent.trim();
    menu.querySelectorAll('.pl-dropdown-item').forEach(i=>i.classList.remove('selected'));
    item.classList.add('selected');label.textContent=text;
    btn.classList.remove('open');menu.classList.remove('open');
    let shown=0;
    entries.forEach(entry=>{{
      const clubs=(entry.dataset.clubs||'').split(',').map(s=>s.trim());
      const match=value==='all'||clubs.includes(value);
      entry.classList.toggle('hidden',!match);
      if(match)shown++;
    }});
    const sfx=shown===1?' season':' seasons';
    filterResult.textContent=shown+sfx+' shown';
    sectionCount.textContent=shown+sfx+' \u00b7 most recent first';
  }});
}});
</script>
</body>
</html>"""

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Built {OUTPUT_PATH}")
print(f"   {total_seasons} seasons, {total_unique_players} unique players, {total_unique_clubs} clubs")
print(f"   {len(rows)} total player-season entries")
