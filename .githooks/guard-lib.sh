#!/usr/bin/env bash
# Shared guard library for .githooks/{pre-commit,commit-msg}.
#
# THIS REPO IS PUBLIC. Two classes of leak matter, and they need DIFFERENT scan
# scopes — which is the whole reason this library exists rather than one flat list:
#
#   CLIENT DATA  — client/site/system names. Scanned everywhere EXCEPT
#                  `knowledge/**` and `mkdocs.yml`, because a vendor in the
#                  79-vendor knowledge library legitimately collides with a client
#                  name, and without the exemption every library commit would be
#                  blocked. Patterns are confidential and live in the GITIGNORED
#                  `client-patterns.local` (see the .example).
#
#   CREDENTIALS  — keys, tokens, private keys. Scanned in EVERY file, with NO
#                  exemptions. A leaked AWS key inside a knowledge doc is exactly
#                  as compromised as one in source, and unlike vendor names there
#                  is no false-positive reason to exempt anything. The previous
#                  hooks had ZERO credential patterns, which left the only PUBLIC
#                  repo of the three with the weakest guard of the three.
#
# Also fixes a maintenance hazard: the old `.git/hooks/pre-commit` and
# `.git/hooks/commit-msg` each carried their own copy of the pattern list, so
# editing one silently left the other stale.
#
# Activate with:  git config core.hooksPath .githooks   (per-clone; hook paths are
# not versioned, so a fresh clone has NO guard until this is run).

set -uo pipefail

RED=$'\033[31m'; YEL=$'\033[33m'; GRN=$'\033[32m'; DIM=$'\033[2m'; NC=$'\033[0m'

HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLIENT_PATTERNS_FILE="$HOOKS_DIR/client-patterns.local"

# ---------- credential patterns (versioned; safe to publish) ----------
# Shapes only — no secret is embedded here.
CRED_PATTERNS=(
  '\b(AKIA|ASIA|ABIA|ACCA)[0-9A-Z]{16}\b'                    # AWS access key id
  '(aws_secret_access_key|aws_session_token)[[:space:]]*[:=]' # AWS secret assignment
  '\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b'               # GitHub token
  '\bgithub_pat_[A-Za-z0-9_]{50,}\b'                         # GitHub fine-grained PAT
  '\bxox[baprs]-[0-9A-Za-z-]{10,}\b'                         # Slack
  '\b(sk|rk)_live_[0-9A-Za-z]{20,}\b'                        # Stripe live
  '\bAIza[0-9A-Za-z_-]{35}\b'                                # Google API key
  '\bsk-ant-[A-Za-z0-9_-]{20,}\b'                            # Anthropic
  '\bsk-[A-Za-z0-9]{48}\b'                                   # OpenAI
  '\bnpm_[A-Za-z0-9]{36}\b'                                  # npm
  '\bpypi-AgEIcHlwaS5vcmc[A-Za-z0-9_-]{20,}'                 # PyPI
  '\bglpat-[A-Za-z0-9_-]{20,}\b'                             # GitLab PAT
  '\bdop_v1_[a-f0-9]{64}\b'                                  # DigitalOcean
  '-----BEGIN( RSA| EC| DSA| OPENSSH| PGP)? PRIVATE KEY'     # private key block
  '\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}'  # JWT
  '(password|passwd|secret|api[_-]?key|apikey|access[_-]?token|auth[_-]?token|client[_-]?secret)[[:space:]]*[:=][[:space:]]*["'"'"'][^"'"'"'[:space:]]{12,}["'"'"']'
  # Inline password in a connection URI. Requires >=8 chars and excludes shell/k8s
  # substitutions via CRED_BENIGN — `postgres://u:$(PGPASSWORD)@h` is how this repo
  # legitimately writes them, and flagging that would block every k8s manifest.
  '(postgres|postgresql|mysql|mongodb|redis|amqp|amqps)(\+[a-z]+)?://[^:@/[:space:]]+:[^@/[:space:]]{8,}@'
)

# NOTE: every grep below passes the pattern via `-e`. The private-key pattern
# starts with `-----`, which grep parses as options otherwise — that pattern
# silently never matched until a branch test caught it.

# Values that match a credential shape but are demonstrably not secrets. Kept
# tight on purpose: a permissive allowlist is how a real key slips through.
# `\$[A-Za-z_]` covers a BARE shell variable — `password="$POSTGRES_PASSWORD"` is
# how scripts/create-secrets.sh correctly avoids embedding a secret, and flagging
# it would train a --no-verify habit. `(prod|dev|staging)[-_]password` covers the
# documentation placeholders the knowledge library uses.
CRED_BENIGN='(changeme|placeholder|example|redacted|dummy|sample|your[_-]|xxxx|\$\{|\$\(|\$[A-Za-z_]|<[A-Za-z_]|notarealsecret|fake|test[_-]?(key|token|secret)|(prod|dev|staging|local)[-_]password|ENC\[|\*{4,})'

# ---------- allowlist for ACCEPTED pre-existing findings ----------
# Keyed by `<path>:<sha256 of the matched line>`, so editing the line re-flags it.
# A whole-file exemption would silently cover a real key added later; a line hash
# cannot. Versioned deliberately — an accepted finding is by definition not secret.
ALLOWLIST_FILE="$HOOKS_DIR/credential-allowlist"

is_allowlisted() {  # is_allowlisted <path> <line-text>
  [ -f "$ALLOWLIST_FILE" ] || return 1
  local key
  key="$1:$(printf '%s' "$2" | sha256sum | cut -d' ' -f1)"
  grep -qxF "$key" "$ALLOWLIST_FILE" 2>/dev/null
}

# ---------- forbidden paths ----------
FORBIDDEN_PATHS=(
  '(^|/)\.env$'  '(^|/)\.env\.[^/]+$'  '(^|/)credentials\.json$'
  '(^|/)kubeconfig(\.ya?ml)?$'  '(^|/)id_(rsa|dsa|ecdsa|ed25519)$'
  '\.pem$' '\.p12$' '\.pfx$' '\.jks$' '\.keystore$'
  '(^|/)service-account.*\.json$'  '(^|/)\.npmrc$'  '(^|/)\.pypirc$'
  '(^|/)terraform\.tfstate(\.backup)?$'  '(^|/)secrets?\.ya?ml$'
)

# ---------- helpers ----------

# Client patterns are OPTIONAL-but-warned: a missing file must not silently
# disable the client-data guard, which is this repo's #1 rule.
client_regex() {
  if [ ! -f "$CLIENT_PATTERNS_FILE" ]; then
    printf '%s' ""
    return 1
  fi
  grep -vE '^\s*(#|$)' "$CLIENT_PATTERNS_FILE" | paste -sd'|' -
}

warn_missing_client_patterns() {
  printf '%s\n' "${YEL}WARNING: $CLIENT_PATTERNS_FILE is missing — the CLIENT-DATA guard is OFF.${NC}" >&2
  printf '%s\n' "${DIM}  cp .githooks/client-patterns.local.example .githooks/client-patterns.local${NC}" >&2
  printf '%s\n' "${DIM}  Credential scanning still applies. This repo is PUBLIC; do not commit${NC}" >&2
  printf '%s\n' "${DIM}  engagement content until the client list is in place.${NC}" >&2
}

# is_exempt_from_client_scan <path>
# knowledge/** and mkdocs.yml only. Credential scanning never consults this.
is_exempt_from_client_scan() {
  case "$1" in
    knowledge/*|mkdocs.yml) return 0 ;;
    *) return 1 ;;
  esac
}

# scan_text_for_credentials <label> <text>  -> 0 clean, 1 hit
scan_text_for_credentials() {
  local label="$1" text="$2" pat hits rc=0
  for pat in "${CRED_PATTERNS[@]}"; do
    hits="$(printf '%s' "$text" | grep -inE -e "$pat" 2>/dev/null | grep -ivE -e "$CRED_BENIGN" || true)"
    [ -z "$hits" ] && continue
    # Drop lines whose exact content is allowlisted for this path.
    local kept="" line body
    while IFS= read -r line; do
      body="${line#*:}"
      is_allowlisted "$label" "$body" || kept="${kept}${line}"$'\n'
    done <<< "$hits"
    if [ -n "${kept//[$'\n\t ']/}" ]; then
      printf '%s\n' "${RED}BLOCKED: possible CREDENTIAL in $label${NC}" >&2
      printf '%s\n' "$kept" | grep -v '^$' | head -3 | sed 's/^/    /' >&2
      rc=1
    fi
  done
  return $rc
}

# scan_text_for_client_data <label> <text>  -> 0 clean, 1 hit
# Prints line numbers and a redacted marker, never the matched name — a hook
# transcript is less protected than the pattern file.
scan_text_for_client_data() {
  local label="$1" text="$2" combined hits
  combined="$(client_regex)" || return 0
  [ -z "$combined" ] && return 0
  hits="$(printf '%s' "$text" | grep -inE -e "$combined" 2>/dev/null || true)"
  if [ -n "$hits" ]; then
    printf '%s\n' "${RED}BLOCKED: possible CLIENT DATA in $label${NC}" >&2
    printf '%s\n' "$hits" | head -5 | cut -d: -f1 \
      | sed 's/^/    line /;s/$/: [redacted — matched a confidential client pattern]/' >&2
    return 1
  fi
  return 0
}
