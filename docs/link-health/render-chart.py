#!/usr/bin/env python3
"""Link-health chart for the architect knowledge library (ErikEvenson/architect#298)."""
import collections
import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

S = "/tmp/claude-1001/-home-claude-claude-obsidian/cd6ab579-b890-40f4-a85e-de2f31ae1ba9/scratchpad"

rows = [l.rstrip("\n").split("\t") for l in open(f"{S}/linkcheck_full.tsv") if "\t" in l]


def verdict(c):
    if c in ("404", "410"): return "DEAD"
    if c[:1] in ("2", "3"):  return "OK"
    if c in ("403", "429"):  return "BLOCKED"
    if c == "000":           return "UNREACHABLE"
    return "OTHER"


tally = collections.Counter(verdict(c) for c, _ in rows)
dead_hosts = collections.Counter(
    re.sub(r"https?://([^/]+).*", r"\1", u) for c, u in rows if verdict(c) == "DEAD")
cats = collections.Counter()
for l in open(f"{S}/dead_by_file.tsv"):
    f = l.split("\t")[0]
    m = re.match(r"knowledge/([^/]+)/", f)
    if m: cats[m.group(1)] += 1

plt.style.use("dark_background")
fig = plt.figure(figsize=(13, 8.6))
fig.patch.set_facecolor("#0d1117")
gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.25], hspace=.42, wspace=.28)

# --- 1. the headline correction ---
ax = fig.add_subplot(gs[0, :]); ax.set_facecolor("#0d1117")
order = ["OK", "DEAD", "BLOCKED", "UNREACHABLE", "OTHER"]
colors = {"OK": "#3fb950", "DEAD": "#f85149", "BLOCKED": "#d29922",
          "UNREACHABLE": "#8b949e", "OTHER": "#58a6ff"}
vals = [tally.get(k, 0) for k in order]
left = 0
# Labels above/below the bar rather than inside it — DEAD/BLOCKED/UNREACHABLE are
# adjacent and narrow, so in-bar text collides.
for i, (k, v) in enumerate(zip(order, vals)):
    ax.barh([0], [v], left=left, color=colors[k], edgecolor="#0d1117", height=.55)
    if k == "OK":
        ax.text(left + v / 2, 0, f"OK  {v}", ha="center", va="center",
                fontsize=11, color="#0d1117", fontweight="bold")
    else:
        y = .42 if i % 2 else -.42
        ax.annotate(f"{k} {v}", xy=(left + v / 2, .28 if y > 0 else -.28),
                    xytext=(left + v / 2, y), ha="center",
                    va="bottom" if y > 0 else "top", fontsize=9.5,
                    color=colors[k], fontweight="bold",
                    arrowprops=dict(arrowstyle="-", color=colors[k], lw=.9))
    left += v
ax.barh([-1.35], [251], color="none", edgecolor="#f85149", height=.5, linestyle="--", lw=1.6)
ax.barh([-1.35], [117], color="#f85149", alpha=.4, height=.5)
ax.text(117 / 2, -1.35, "117", va="center", ha="center", fontsize=10,
        color="#ffffff", fontweight="bold")
ax.text(262, -1.35, "#298 reported 251 'failed' — it conflated dead, blocked and unreachable.\n"
                    "Only the shaded 117 need editing.",
        va="center", fontsize=9.5, color="#f85149")
ax.set_ylim(-1.9, .95)
ax.set_yticks([0, -1.35]); ax.set_yticklabels(["measured\n2026-07-26", "#298\n2026-05-14"], fontsize=9)
ax.set_xlim(0, 1780); ax.set_xlabel("URLs")
ax.set_title("architect knowledge library — external link health   ·   1,733 URLs, 429 hosts\n"
             "host-serialised measurement; 20 template placeholders excluded",
             color="#e6edf3", fontsize=12.5, pad=12)
ax.grid(axis="x", alpha=.15)

# --- 2. dead by host ---
ax2 = fig.add_subplot(gs[1, 0]); ax2.set_facecolor("#0d1117")
h = dead_hosts.most_common(11)[::-1]
ax2.barh([x[0] for x in h], [x[1] for x in h], color="#f85149", alpha=.85)
ax2.set_title("Dead links by host — vendor doc reorganisations", color="#e6edf3", fontsize=10.5)
ax2.tick_params(labelsize=8.5); ax2.grid(axis="x", alpha=.15)

# --- 3. dead by category ---
ax3 = fig.add_subplot(gs[1, 1]); ax3.set_facecolor("#0d1117")
c = cats.most_common()[::-1]
ax3.barh([x[0] for x in c], [x[1] for x in c], color="#d29922", alpha=.9)
for i, (k, v) in enumerate(c):
    ax3.text(v + 1, i, str(v), va="center", fontsize=9, color="#e6edf3")
ax3.set_title("Dead links by knowledge category\n81 of 417 files affected",
              color="#e6edf3", fontsize=10.5)
ax3.tick_params(labelsize=9); ax3.grid(axis="x", alpha=.15)

fig.text(0.5, 0.02,
         "BLOCKED = 403/429 after 3 retries (anti-bot; the link is probably fine).  "
         "UNREACHABLE = persistent timeout/DNS.  Only DEAD (404/410) needs editing.",
         ha="center", color="#8b949e", fontsize=9)
fig.savefig(f"{S}/link-health.png", dpi=135, facecolor="#0d1117", bbox_inches="tight")
print(f"  wrote link-health.png   OK={tally['OK']} DEAD={tally['DEAD']} "
      f"BLOCKED={tally['BLOCKED']} UNREACHABLE={tally['UNREACHABLE']}")
