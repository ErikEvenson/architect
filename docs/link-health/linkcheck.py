#!/usr/bin/env python3
"""Link-health check for the architect knowledge library (ErikEvenson/architect#298).

Read-only. Produces a number worth acting on, which means separating real link rot
from measurement artifacts. A naive run at concurrency 8 returned 12x 429 and 10x
000 on a 60-URL sample purely because 182 of the URLs share one host — reporting
that as rot would send someone editing links that are fine.

Design:
  * Grouped by host; one worker per host, URLs within a host strictly serial with a
    delay. Parallelism comes from breadth across hosts, never depth within one.
  * HEAD first, ranged GET fallback (several vendor doc sites reject HEAD).
  * 429/000/5xx are RETRIED with backoff, and only a persistent failure counts.
  * Verdicts separate DEAD (404/410 — actionable) from BLOCKED (403/429 after
    retries — anti-bot, not necessarily rot) from UNREACHABLE (timeouts).
    #298 conflated these, which is why its 251 overstates what needs editing.
"""
import collections
import concurrent.futures as cf
import subprocess
import sys
import time
import urllib.parse

URLS = sys.argv[1] if len(sys.argv) > 1 else "/tmp/arch_urls.txt"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/tmp/linkcheck_results.tsv"
HOST_WORKERS = int(sys.argv[3]) if len(sys.argv) > 3 else 12
PER_HOST_DELAY = 1.1
UA = "Mozilla/5.0 (compatible; architect-knowledge-link-check/1.0)"


def curl(url, head=True, timeout=20):
    cmd = ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}",
           "--max-time", str(timeout), "-L", "--max-redirs", "5", "-A", UA]
    cmd += ["-I"] if head else ["-r", "0-2048"]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 8)
        return (r.stdout or "000").strip()[-3:]
    except Exception:
        return "000"


def probe(url):
    """Return final status after retries. Retries only ambiguous codes."""
    for attempt in range(3):
        code = curl(url, head=True)
        if code in ("000", "403", "405", "501"):
            code = curl(url, head=False, timeout=25)
        if code not in ("429", "000", "500", "502", "503", "504"):
            return code
        time.sleep(1.5 * (attempt + 1) ** 2)   # 1.5s, 6s, 13.5s
    return code


def host_of(u):
    try:
        return urllib.parse.urlparse(u).netloc.lower()
    except Exception:
        return "?"


urls = [l.strip() for l in open(URLS) if l.strip().startswith("http")]
by_host = collections.defaultdict(list)
for u in urls:
    by_host[host_of(u)].append(u)
print(f"  {len(urls)} URLs across {len(by_host)} hosts; {HOST_WORKERS} host-workers, "
      f"{PER_HOST_DELAY}s between requests to the same host", flush=True)

results = []


def do_host(item):
    host, hurls = item
    out = []
    for i, u in enumerate(hurls):
        if i:
            time.sleep(PER_HOST_DELAY)
        out.append((probe(u), u))
    return out


done = 0
with cf.ThreadPoolExecutor(max_workers=HOST_WORKERS) as ex:
    futs = {ex.submit(do_host, it): it[0] for it in
            sorted(by_host.items(), key=lambda kv: -len(kv[1]))}
    for f in cf.as_completed(futs):
        try:
            results.extend(f.result())
        except Exception as e:
            print(f"  host {futs[f]} errored: {e}", flush=True)
        done += 1
        if done % 25 == 0:
            print(f"  hosts done {done}/{len(by_host)}", flush=True)

with open(OUT, "w") as fh:
    for code, u in sorted(results):
        fh.write(f"{code}\t{u}\n")


def verdict(c):
    if c in ("404", "410"):
        return "DEAD (actionable — fix or remove)"
    if c.startswith("2") or c.startswith("3"):
        return "OK"
    if c in ("403", "429"):
        return "BLOCKED (anti-bot; link may be fine)"
    if c == "000":
        return "UNREACHABLE (timeout/DNS)"
    return f"OTHER {c}"


tally = collections.Counter(verdict(c) for c, _ in results)
print("\n  === RESULTS ===")
for k, v in tally.most_common():
    print(f"    {v:5d}  {k}")
dead = sorted(u for c, u in results if c in ("404", "410"))
print(f"\n  DEAD links: {len(dead)}")
for u in dead[:25]:
    print(f"    {u}")
if len(dead) > 25:
    print(f"    ... and {len(dead)-25} more (full list in {OUT})")
