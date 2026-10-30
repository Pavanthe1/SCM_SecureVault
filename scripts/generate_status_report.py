import csv, html, json, os, urllib.request
from datetime import datetime, timezone

repo = os.environ["GITHUB_REPOSITORY"]
token = os.environ["GITHUB_TOKEN"]
api = f"https://api.github.com/repos/{repo}"

def get(path):
    req = urllib.request.Request(api + path, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "SecureVault-SAR"
    })
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())

def date(v):
    return (v or "—").replace("T", " ").replace("Z", " UTC")

def table(headers, rows):
    h = "<tr>" + "".join(f"<th>{html.escape(str(x))}</th>" for x in headers) + "</tr>"
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(x if x is not None else '—'))}</td>" for x in row) + "</tr>" for row in rows)
    return "<table>" + h + (body or f'<tr><td colspan="{len(headers)}">No records found</td></tr>') + "</table>"

commits = get("/commits?per_page=100")
all_issues = get("/issues?state=all&per_page=100")
issues = [x for x in all_issues if "pull_request" not in x]
pulls = get("/pulls?state=all&per_page=100")
tags = get("/tags?per_page=100")
runs = get("/actions/runs?per_page=100").get("workflow_runs", [])

commit_rows = [[c["sha"][:12], c["commit"]["message"].splitlines()[0],
                (c.get("author") or {}).get("login", c["commit"]["author"]["name"]),
                date(c["commit"]["author"]["date"])] for c in commits]
issue_rows = [[i["number"], i["title"], i["state"], i["user"]["login"],
               date(i["created_at"]), date(i["updated_at"])] for i in issues]
pull_rows = [[p["number"], p["title"], p["state"], p["user"]["login"], date(p["updated_at"])] for p in pulls]
tag_rows = [[t["name"], t["commit"]["sha"][:12]] for t in tags]
run_rows = [[r["name"], r["status"], r.get("conclusion") or "—", r["head_branch"], date(r["updated_at"])] for r in runs[:30]]

def csvfile(name, headers, rows):
    with open(name, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(headers); w.writerows(rows)

csvfile("status_accounting_commits.csv", ["Commit ID","Message","Author","Date"], commit_rows)
csvfile("status_accounting_issues.csv", ["Issue #","Title","State","Author","Created","Updated"], issue_rows)

open_issues = sum(i["state"] == "open" for i in issues)
closed_issues = sum(i["state"] == "closed" for i in issues)
successful = sum(r.get("conclusion") == "success" for r in runs)
failed = sum(r.get("conclusion") == "failure" for r in runs)
latest_tag = tags[0]["name"] if tags else "No tags"
latest_commit = commits[0]["sha"][:12] if commits else "—"

report = f"""<!doctype html><html><head><meta charset="utf-8"><title>Secure-Vault Status Accounting Report</title>
<style>body{{font:15px Arial;margin:32px;background:#f5f7fa;color:#202938}}h1,h2{{color:#173b5e}}table{{border-collapse:collapse;width:100%;margin:12px 0 28px;background:white}}th,td{{border:1px solid #ccd5df;padding:8px;text-align:left}}th{{background:#e7eef5}}.box{{background:white;padding:14px;border:1px solid #ccd5df;border-radius:8px}}.note{{color:#596777;font-size:13px}}</style>
</head><body><h1>Secure-Vault — Status Accounting Report</h1>
<div class="box"><b>Repository:</b> {html.escape(repo)}<br><b>Generated:</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}<br>
<b>Latest commit:</b> {latest_commit}<br><b>Latest tag:</b> {html.escape(latest_tag)}<br>
<b>Commits retrieved:</b> {len(commits)} | <b>Open issues:</b> {open_issues} | <b>Closed issues:</b> {closed_issues}<br>
<b>Successful workflow runs:</b> {successful} | <b>Failed workflow runs:</b> {failed}</div>
<p class="note">This report summarizes records returned by GitHub at generation time. A commit does not prove that a feature works; functional status needs test or verification evidence.</p>
<h2>1. Commit history</h2>{table(["Commit ID","Message","Author","Date"], commit_rows[:50])}
<h2>2. Issues — pending and completed work</h2>{table(["Issue #","Title","State","Author","Created","Updated"], issue_rows)}
<h2>3. Pull requests</h2>{table(["PR #","Title","State","Author","Updated"], pull_rows)}
<h2>4. Tags / version baselines</h2>{table(["Tag","Commit"], tag_rows)}
<h2>5. GitHub Actions workflow runs</h2>{table(["Workflow","Status","Conclusion","Branch","Updated"], run_rows)}
</body></html>"""
with open("status_accounting_report.html", "w", encoding="utf-8") as f:
    f.write(report)
print("Status accounting report generated.")
