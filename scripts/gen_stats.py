#!/usr/bin/env python3
"""Generate stats + streak SVG cards from the GitHub GraphQL API.

Runs with the repo owner's own token, so unlike the shared public instances of
github-readme-stats this counts private contributions and never hits someone
else's rate limit. Rank formula mirrors github-readme-stats' calculateRank().
"""
import datetime as dt
import json
import os
import subprocess
import sys

USER = os.environ.get("GH_USER", "Frozensun47")


def gql(query, **variables):
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for k, v in variables.items():
        cmd += ["-f", f"{k}={v}"]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    payload = json.loads(out)
    if "errors" in payload:
        sys.exit(f"GraphQL error: {payload['errors']}")
    return payload["data"]


def fetch():
    base = gql("""
    query($login:String!){ user(login:$login){
      login name createdAt
      followers{totalCount}
      repositories(first:100, ownerAffiliations:[OWNER], isFork:false,
                   orderBy:{field:STARGAZERS,direction:DESC}){
        totalCount nodes{ stargazerCount }
      }
      pullRequests{totalCount}
      issues{totalCount}
      repositoriesContributedTo(contributionTypes:[COMMIT,PULL_REQUEST,REPOSITORY]){totalCount}
    }}""", login=USER)["user"]

    created = dt.datetime.fromisoformat(base["createdAt"].replace("Z", "+00:00"))
    today = dt.datetime.now(dt.timezone.utc)

    commits = reviews = 0
    days = {}
    # contributionsCollection covers max 1 year, so walk year by year.
    for year in range(created.year, today.year + 1):
        frm = max(created, dt.datetime(year, 1, 1, tzinfo=dt.timezone.utc))
        to = min(today, dt.datetime(year, 12, 31, 23, 59, 59, tzinfo=dt.timezone.utc))
        if frm >= to:
            continue
        c = gql("""
        query($login:String!,$from:DateTime!,$to:DateTime!){
          user(login:$login){ contributionsCollection(from:$from,to:$to){
            totalCommitContributions
            restrictedContributionsCount
            totalPullRequestReviewContributions
            contributionCalendar{ weeks{ contributionDays{ date contributionCount } } }
          }}}""",
                login=USER, **{"from": frm.isoformat().replace("+00:00", "Z"),
                               "to": to.isoformat().replace("+00:00", "Z")})
        cc = c["user"]["contributionsCollection"]
        # restricted = private contributions not itemised; include them.
        commits += cc["totalCommitContributions"] + cc["restrictedContributionsCount"]
        reviews += cc["totalPullRequestReviewContributions"]
        for w in cc["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                days[d["date"]] = days.get(d["date"], 0) + d["contributionCount"]

    stars = sum(n["stargazerCount"] for n in base["repositories"]["nodes"])
    return {
        "name": base["name"] or base["login"],
        "commits": commits,
        "reviews": reviews,
        "prs": base["pullRequests"]["totalCount"],
        "issues": base["issues"]["totalCount"],
        "stars": stars,
        "followers": base["followers"]["totalCount"],
        "contribs": base["repositoriesContributedTo"]["totalCount"],
        "repos": base["repositories"]["totalCount"],
        "days": days,
        "created": created,
    }


def streaks(days):
    """Current and longest daily-contribution streaks."""
    today = dt.date.today()
    dates = sorted(days)
    longest = run = 0
    long_end = cur_start = cur_end = None
    prev = None
    for ds in dates:
        d = dt.date.fromisoformat(ds)
        if d > today:
            break
        if days[ds] > 0:
            run = run + 1 if prev and (d - prev).days == 1 else 1
            if run > longest:
                longest, long_end = run, d
            prev = d
        else:
            prev = None
            run = 0
    # Current streak: walk backwards. Today not yet contributed doesn't break it.
    cur = 0
    d = today
    if days.get(d.isoformat(), 0) == 0:
        d -= dt.timedelta(days=1)
    cur_end = d
    while days.get(d.isoformat(), 0) > 0:
        cur += 1
        cur_start = d
        d -= dt.timedelta(days=1)
    return {
        "current": cur,
        "current_start": cur_start,
        "current_end": cur_end if cur else None,
        "longest": longest,
        "longest_end": long_end,
    }


def rank(s):
    """github-readme-stats calculateRank(). Lower percentile is better."""
    def exp_cdf(x):
        return 1 - 2 ** -x

    def log_cdf(x):
        return x / (1 + x)

    weights = {"commits": 2, "contribs": 1, "issues": 1,
               "stars": 1, "prs": 1, "reviews": 1, "followers": 1}
    medians = {"commits": 1000, "contribs": 25, "issues": 25,
               "stars": 50, "prs": 50, "reviews": 2, "followers": 10}
    cdf = {"stars": log_cdf, "followers": log_cdf}

    total = sum(weights.values())
    score = sum(
        weights[k] * cdf.get(k, exp_cdf)(s[k] / medians[k]) for k in weights
    ) / total
    percentile = (1 - score) * 100
    thresholds = [1, 12.5, 25, 37.5, 50, 62.5, 75, 87.5, 100]
    levels = ["S", "A+", "A", "A-", "B+", "B", "B-", "C+", "C"]
    level = next(l for t, l in zip(thresholds, levels) if percentile <= t)
    return level, percentile


def human(n):
    if n >= 1000:
        return f"{n/1000:.1f}k".replace(".0k", "k")
    return str(n)


ICONS = {
    "star": "M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.75.75 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z",
    "commit": "M11.93 8.5a4.002 4.002 0 0 1-7.86 0H.75a.75.75 0 0 1 0-1.5h3.32a4.002 4.002 0 0 1 7.86 0h3.32a.75.75 0 0 1 0 1.5Zm-1.43-.75a2.5 2.5 0 1 0-5 0 2.5 2.5 0 0 0 5 0Z",
    "pr": "M1.5 3.25a2.25 2.25 0 1 1 3 2.122v5.256a2.251 2.251 0 1 1-1.5 0V5.372A2.25 2.25 0 0 1 1.5 3.25Zm5.677-.177L9.573.677A.25.25 0 0 1 10 .854V2.5h1A2.5 2.5 0 0 1 13.5 5v5.628a2.251 2.251 0 1 1-1.5 0V5a1 1 0 0 0-1-1h-1v1.646a.25.25 0 0 1-.427.177L7.177 3.427a.25.25 0 0 1 0-.354Z",
    "issue": "M8 9.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z M8 0a8 8 0 1 1 0 16A8 8 0 0 1 8 0ZM1.5 8a6.5 6.5 0 1 0 13 0 6.5 6.5 0 0 0-13 0Z",
    "review": "M1.75 1h12.5c.966 0 1.75.784 1.75 1.75v8.5A1.75 1.75 0 0 1 14.25 13H8.06l-2.573 2.573A1.458 1.458 0 0 1 3 14.543V13H1.75A1.75 1.75 0 0 1 0 11.25v-8.5C0 1.784.784 1 1.75 1Z",
    "repo": "M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Z",
}


def card_stats(s, sk):
    level, pct = rank(s)
    rows = [
        ("star", "Total Stars Earned", human(s["stars"])),
        ("commit", "Total Commits", human(s["commits"])),
        ("pr", "Total PRs", human(s["prs"])),
        ("issue", "Total Issues", human(s["issues"])),
        ("review", "Code Reviews", human(s["reviews"])),
        ("repo", "Repositories", human(s["repos"])),
    ]
    # Rank ring: fraction filled = how far above the bottom the percentile sits.
    frac = max(0.0, min(1.0, 1 - pct / 100))
    circ = 2 * 3.141592653589793 * 40
    offset = circ * (1 - frac)

    body = []
    for i, (icon, label, value) in enumerate(rows):
        y = 40 + i * 26
        body.append(
            f'<g transform="translate(0,{y})" class="row">'
            f'<svg x="0" y="-11" width="15" height="15" viewBox="0 0 16 16" fill="var(--ic)">'
            f'<path d="{ICONS[icon]}"/></svg>'
            f'<text x="26" y="0" class="lbl">{label}</text>'
            f'<text x="250" y="0" class="val">{value}</text></g>')

    return f'''<svg width="480" height="220" viewBox="0 0 480 220" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="GitHub stats for {s['name']}">
<style>
  :root {{ --bg:#0d1117; --bd:#30363d; --ti:#58a6ff; --lbl:#c9d1d9; --ic:#58a6ff; --rk:#58a6ff; }}
  .title {{ font:600 17px 'Segoe UI',Ubuntu,sans-serif; fill:var(--ti); }}
  .lbl {{ font:400 13px 'Segoe UI',Ubuntu,sans-serif; fill:var(--lbl); }}
  .val {{ font:600 13px 'Segoe UI',Ubuntu,sans-serif; fill:var(--lbl); text-anchor:end; }}
  .rank {{ font:800 26px 'Segoe UI',Ubuntu,sans-serif; fill:var(--rk); text-anchor:middle; }}
  .rankpct {{ font:400 10px 'Segoe UI',Ubuntu,sans-serif; fill:var(--lbl); text-anchor:middle; opacity:.75; }}
  /* Deliberately static: GitHub serves README images through a proxy that
     does not reliably run CSS animation, so everything is drawn in its
     final state rather than animated into view. */
  .ring {{ stroke-dasharray:{circ:.1f}; stroke-dashoffset:{offset:.1f}; }}
</style>
<rect x=".5" y=".5" width="479" height="219" rx="6" fill="var(--bg)" stroke="var(--bd)"/>
<g transform="translate(25,32)"><text class="title">{s['name']}'s GitHub Stats</text>{''.join(body)}</g>
<g transform="translate(390,110)">
  <circle cx="0" cy="0" r="40" fill="none" stroke="var(--bd)" stroke-width="6"/>
  <circle cx="0" cy="0" r="40" fill="none" stroke="var(--rk)" stroke-width="6"
          stroke-linecap="round" class="ring" transform="rotate(-90)"/>
  <text class="rank" y="2">{level}</text>
  <text class="rankpct" y="18">top {pct:.1f}%</text>
</g>
</svg>'''


def card_streak(s, sk):
    def fmt(d):
        return d.strftime("%b %d, %Y") if d else "—"

    total = sum(s["days"].values())
    cur_range = (f"{fmt(sk['current_start'])} – {fmt(sk['current_end'])}"
                 if sk["current"] else "—")
    circ = 2 * 3.141592653589793 * 38
    cols = [
        (78, human(total), "Total Contributions",
         f"{fmt(s['created'].date())} – Present"),
        (240, str(sk["current"]), "Current Streak", cur_range),
        (402, str(sk["longest"]), "Longest Streak",
         f"ends {fmt(sk['longest_end'])}"),
    ]
    body = []
    for i, (x, big, label, sub) in enumerate(cols):
        mid = i == 1
        body.append(
            f'<g transform="translate({x},0)" class="col">'
            f'<text y="70" class="big{" hot" if mid else ""}">{big}</text>'
            f'<text y="96" class="lbl{" hotlbl" if mid else ""}">{label}</text>'
            f'<text y="118" class="sub">{sub}</text></g>')
    return f'''<svg width="480" height="220" viewBox="0 0 480 220" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Contribution streak for {s['name']}">
<style>
  :root {{ --bg:#0d1117; --bd:#30363d; --fg:#c9d1d9; --hot:#f78166; --dim:#8b949e; }}
  .big {{ font:700 28px 'Segoe UI',Ubuntu,sans-serif; fill:var(--fg); text-anchor:middle; }}
  .big.hot {{ font-size:32px; fill:var(--hot); }}
  .lbl {{ font:600 13px 'Segoe UI',Ubuntu,sans-serif; fill:var(--fg); text-anchor:middle; }}
  .lbl.hotlbl {{ fill:var(--hot); }}
  .sub {{ font:400 10px 'Segoe UI',Ubuntu,sans-serif; fill:var(--dim); text-anchor:middle; }}
  .ring {{ stroke-dasharray:{circ:.1f}; stroke-dashoffset:0; }}
</style>
<rect x=".5" y=".5" width="479" height="219" rx="6" fill="var(--bg)" stroke="var(--bd)"/>
<line x1="160" y1="42" x2="160" y2="178" stroke="var(--bd)"/>
<line x1="320" y1="42" x2="320" y2="178" stroke="var(--bd)"/>
<circle cx="240" cy="72" r="38" fill="none" stroke="var(--hot)" stroke-width="4"
        stroke-linecap="round" class="ring" transform="rotate(-90 240 72)" opacity=".85"/>
<g transform="translate(0,20)">{''.join(body)}</g>
</svg>'''


def card_activity(s, weeks=53):
    """Area chart of weekly contributions over the last year, from real data
    (the shared activity-graph services only see public commits)."""
    today = dt.date.today()
    start = today - dt.timedelta(days=weeks * 7 - 1)
    # Bucket into ISO weeks anchored on the start date.
    buckets = [0] * weeks
    for ds, n in s["days"].items():
        d = dt.date.fromisoformat(ds)
        if start <= d <= today:
            buckets[min(weeks - 1, (d - start).days // 7)] += n

    W, H = 840, 240
    PL, PR, PT, PB = 48, 20, 30, 42
    iw, ih = W - PL - PR, H - PT - PB
    peak = max(buckets) or 1
    # Round the axis top to a clean number.
    step = 10 ** (len(str(peak)) - 1)
    top = ((peak + step - 1) // step) * step

    def px(i):
        return PL + iw * i / (weeks - 1)

    def py(v):
        return PT + ih * (1 - v / top)

    pts = [(px(i), py(v)) for i, v in enumerate(buckets)]
    # Smooth with a simple cubic through midpoints.
    line = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(1, len(pts)):
        x0, y0 = pts[i - 1]
        x1, y1 = pts[i]
        cx = (x0 + x1) / 2
        line += f" C{cx:.1f},{y0:.1f} {cx:.1f},{y1:.1f} {x1:.1f},{y1:.1f}"
    area = line + f" L{pts[-1][0]:.1f},{PT+ih:.1f} L{pts[0][0]:.1f},{PT+ih:.1f} Z"

    grid = ticks = ""
    for f in (0, 0.25, 0.5, 0.75, 1):
        y = PT + ih * f
        grid += f'<line x1="{PL}" y1="{y:.1f}" x2="{PL+iw}" y2="{y:.1f}" stroke="var(--bd)" stroke-width="1" opacity=".5"/>'
        ticks += f'<text x="{PL-10}" y="{y+4:.1f}" class="ax" text-anchor="end">{int(top*(1-f))}</text>'

    months = ""
    seen = set()
    for i in range(weeks):
        d = start + dt.timedelta(days=i * 7)
        key = (d.year, d.month)
        if d.day <= 7 and key not in seen:
            seen.add(key)
            months += f'<text x="{px(i):.1f}" y="{PT+ih+20}" class="ax" text-anchor="middle">{d.strftime("%b")}</text>'

    total = sum(buckets)
    return f'''<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Weekly contribution activity, {total} contributions in the last year">
<style>
  :root {{ --bg:#0d1117; --bd:#30363d; --ti:#58a6ff; --ln:#3fb950; --dim:#8b949e; }}
  .title {{ font:600 15px 'Segoe UI',Ubuntu,sans-serif; fill:var(--ti); }}
  .sub {{ font:400 11px 'Segoe UI',Ubuntu,sans-serif; fill:var(--dim); }}
  .ax {{ font:400 10px 'Segoe UI',Ubuntu,sans-serif; fill:var(--dim); }}
  .ln {{ stroke:var(--ln); stroke-width:2.5; fill:none; stroke-linecap:round; stroke-linejoin:round;
        }}
  .ar {{ fill:url(#g); }}
</style>
<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="#3fb950" stop-opacity=".45"/>
  <stop offset="100%" stop-color="#3fb950" stop-opacity="0"/>
</linearGradient></defs>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="6" fill="var(--bg)" stroke="var(--bd)"/>
<text x="{PL}" y="20" class="title">Contribution Activity</text>
<text x="{W-PR}" y="20" class="sub" text-anchor="end">{total:,} in the last year · private included</text>
{grid}{ticks}{months}
<path class="ar" d="{area}"/>
<path class="ln" d="{line}"/>
</svg>'''


LANG_TOP = 8


def fetch_langs():
    """Language bytes across every repo I can see, private included."""
    totals, colors = {}, {}
    cursor, page = "null", 0
    while page < 6:
        after = "null" if cursor == "null" else f'"{cursor}"'
        d = gql("""
        query($login:String!){ user(login:$login){
          repositories(first:100, isFork:false, after:%s,
                       ownerAffiliations:[OWNER,ORGANIZATION_MEMBER,COLLABORATOR]){
            pageInfo{ hasNextPage endCursor }
            nodes{ languages(first:12, orderBy:{field:SIZE,direction:DESC}){
              edges{ size node{ name color } } } }
          }}}""" % after, login=USER)["user"]["repositories"]
        for n in d["nodes"]:
            for e in (n["languages"] or {}).get("edges", []):
                name = e["node"]["name"]
                totals[name] = totals.get(name, 0) + e["size"]
                colors[name] = e["node"]["color"] or "#8b949e"
        if not d["pageInfo"]["hasNextPage"]:
            break
        cursor = d["pageInfo"]["endCursor"]
        page += 1

    grand = sum(totals.values()) or 1
    ranked = sorted(totals.items(), key=lambda kv: -kv[1])[:LANG_TOP]
    return [(n, v / grand * 100, colors[n]) for n, v in ranked]


def card_langs(langs):
    rows_n = (len(langs) + 1) // 2
    W, H = 460, 92 + rows_n * 24
    BAR_Y, BAR_W = 46, W - 50
    seg, x = "", 25.0
    shown = sum(p for _, p, _ in langs) or 1
    for name, pct, col in langs:
        w = BAR_W * pct / shown
        seg += (f'<rect x="{x:.1f}" y="{BAR_Y}" width="{max(w,0.6):.1f}" height="9" '
                f'fill="{col}"/>')
        x += w
    rows = ""
    for i, (name, pct, col) in enumerate(langs):
        cx = 28 + (i % 2) * 215
        cy = 80 + (i // 2) * 24
        rows += (f'<g transform="translate({cx},{cy})">'
                 f'<circle cx="0" cy="-4" r="5" fill="{col}"/>'
                 f'<text x="12" y="0" class="lg">{name}</text>'
                 f'<text x="195" y="0" class="lp">{pct:.1f}%</text></g>')
    return f'''<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Most used languages">
<style>
  :root {{ --bg:#0d1117; --bd:#30363d; --ti:#58a6ff; --fg:#c9d1d9; }}
  .title {{ font:600 15px 'Segoe UI',Ubuntu,sans-serif; fill:var(--ti); }}
  .lg {{ font:400 12px 'Segoe UI',Ubuntu,sans-serif; fill:var(--fg); }}
  .lp {{ font:600 12px 'Segoe UI',Ubuntu,sans-serif; fill:var(--fg); text-anchor:end; }}
</style>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="6" fill="var(--bg)" stroke="var(--bd)"/>
<text x="25" y="30" class="title">Most Used Languages</text>
<clipPath id="r"><rect x="25" y="{BAR_Y}" width="{BAR_W}" height="9" rx="4.5"/></clipPath>
<g clip-path="url(#r)">{seg}</g>
{rows}
</svg>'''


def main():
    s = fetch()
    sk = streaks(s["days"])
    level, pct = rank(s)
    out = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "stats.svg"), "w") as f:
        f.write(card_stats(s, sk))
    with open(os.path.join(out, "streak.svg"), "w") as f:
        f.write(card_streak(s, sk))
    with open(os.path.join(out, "activity.svg"), "w") as f:
        f.write(card_activity(s))
    langs = fetch_langs()
    with open(os.path.join(out, "langs.svg"), "w") as f:
        f.write(card_langs(langs))
    print("langs=" + ", ".join(f"{n} {p:.1f}%" for n, p, _ in langs))
    print(f"rank={level} (top {pct:.1f}%) commits={s['commits']} prs={s['prs']} "
          f"issues={s['issues']} reviews={s['reviews']} stars={s['stars']} "
          f"repos={s['repos']} current_streak={sk['current']} "
          f"longest_streak={sk['longest']} total={sum(s['days'].values())}")


if __name__ == "__main__":
    main()
