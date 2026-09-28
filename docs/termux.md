# Running the backend on an Android phone (Termux + Debian)

Replaces the Render `wkai-backend` service. The backend runs in Debian under
`proot-distro` inside Termux; Postgres stays on Neon and Redis on Upstash, so
sessions carry over. `deploy/termux/run.sh` replaces Render's restart-on-exit;
`~/wkaictl.sh` starts it in the background and on boot.

```
Termux (Android app)
 ├─ ~/wkaictl.sh          start / stop / logs, tmux session "wkai", wake-lock
 └─ proot-distro: Debian
     └─ /root/wkai
         └─ deploy/termux/run.sh   restarts the backend on exit 1, stops on exit 0
```

## 0. Before you start

- **Stop the Render service first** (Render → `wkai-backend` → Suspend). Two
  backends share nothing in-process: rate-limit counters live in process
  memory (`wkai-backend/.env.example` notes the effective cap multiplies per
  instance) and WebSocket rooms are per-process, so students on different
  instances can't see each other.
- Phone: Android 7+, 64-bit (arm64, e.g. Pixel 10a) preferred, ~2 GB free
  storage, and on charger if it is meant to run 24/7.
- Install **Termux** and **Termux:Boot** from **F-Droid** (or their GitHub
  releases). The Play Store Termux is outdated and breaks `pkg`. Both apps
  must come from the same source.

## 1. Android settings (do these once — the difference between hours and weeks of uptime)

1. Settings → Apps → Termux → Battery → **Unrestricted** (disable battery
   optimisation). Same for Termux:Boot.
2. Open **Termux:Boot** once so Android registers it.
3. **Android 12+: phantom process killer.** Android kills background
   child processes (which is exactly what proot + node are). Either:
   - Android 14+: Developer options → **Disable child process restrictions**, or
   - Android 12/13, from a PC with USB debugging:
     ```bash
     adb shell "settings put global settings_enable_monitor_phantom_procs false"
     ```
4. Lock Termux in the recent-apps screen so a swipe doesn't kill it.

## 2. Termux: install Debian

In Termux (**not** inside Debian — `tmux` lives here):

```bash
pkg update -y && pkg upgrade -y
pkg install -y proot-distro tmux git
proot-distro install debian
```

## 3. Debian: get the code and install

```bash
proot-distro login debian
```

Now inside Debian (prompt changes to `root@localhost`):

```bash
cd ~
git clone --filter=blob:none --sparse https://github.com/Dinaltium/wkai.git
cd wkai
git sparse-checkout set wkai-backend deploy
bash deploy/termux/setup-debian.sh
```

The repo is private: when git asks for a password, paste a GitHub
**personal access token** (GitHub → Settings → Developer settings → Tokens,
`repo` read access), not your GitHub password.

## 4. Debian: configure `.env`

```bash
nano ~/wkai/wkai-backend/.env
```

Copy **every** variable from Render → `wkai-backend` → Environment:

| Variable | Value |
|---|---|
| `DATABASE_URL` | same Neon URL as Render |
| `REDIS_URL` | same Upstash URL as Render (`rediss://…`) |
| `GROQ_API_KEY` | as on Render |
| `CLOUDINARY_CLOUD_NAME` / `CLOUDINARY_API_KEY` / `CLOUDINARY_API_SECRET` | as on Render (needed for file sharing) |
| `STUDENT_JOIN_TOKEN_SECRET` | **exactly** as on Render, or existing tokens break |
| `CORS_ALLOWED_ORIGINS` | as on Render (keep your Vercel domains) |
| `PG_POOL_MAX` | `3` — a phone doesn't need 20 Postgres connections |

Save with Ctrl-O, Enter, Ctrl-X. Never run `> .env` — that truncates the
file to zero bytes; if you already did, restore with
`cp .env.example .env` and fill it in again.

## 5. First run, in the foreground

Still in Debian:

```bash
cd ~/wkai && bash deploy/termux/run.sh
```

Wait for `[WKAI] Server running on http://localhost:4000` plus the LAN-access
line. From a laptop on the same Wi-Fi, open `http://<phone-ip>:4000/health`.
Stop with Ctrl-C, then leave Debian:

```bash
exit
```

## 6. Termux: run in the background + start on boot

Back in plain Termux:

```bash
bash $PREFIX/var/lib/proot-distro/containers/debian/rootfs/root/wkai/deploy/termux/wkaictl.sh install
bash ~/wkaictl.sh start
```

(Older `proot-distro` versions keep Debian at
`$PREFIX/var/lib/proot-distro/installed-rootfs/debian/` instead; use that
prefix if the path above doesn't exist.)

Day to day:

```bash
bash ~/wkaictl.sh status     # running / stopped
bash ~/wkaictl.sh logs       # follow the log (Ctrl-C stops following, not the backend)
bash ~/wkaictl.sh attach     # live console; detach with Ctrl-b then d
bash ~/wkaictl.sh restart    # e.g. after git pull
bash ~/wkaictl.sh stop
```

A persistent Termux notification with "wake lock held" means the CPU is kept
awake with the screen off — that's intended.

## 7. Updating

### Automatic (recommended)

With `AUTO_UPDATE=true` in `wkai-backend/.env`, `run.sh` starts
`deploy/termux/autoupdate.sh` beside the backend. Every 5 minutes it checks
GitHub; when `main` has new commits it fast-forwards them, runs `npm ci`
only if `wkai-backend/package.json`/`package-lock.json` changed, applies
migrations, and restarts the backend. Merge a PR → the phone is running it
within ~5 minutes.

If a commit fails (`npm ci` or `db:migrate`), the phone rolls back to the
commit it was running, keeps the backend up on the old code, and skips that
commit until a newer one lands. Everything is logged with an `[autoupdate]`
prefix in the backend log.

One-time setup, because the repo is private and the updater can't type a
password. Inside Debian:

```bash
cd ~/wkai
git config credential.helper store
git pull
```

At the password prompt paste a **fine-grained personal access token** (GitHub
→ Settings → Developer settings → Fine-grained tokens) scoped to **only**
`Dinaltium/wkai` with **Contents: Read-only**. `credential.helper store`
saves it in plain text in `~/.git-credentials`, which is why it should be
read-only and limited to this one repo. Then add to `wkai-backend/.env`:

```
AUTO_UPDATE=true
```

and `bash ~/wkaictl.sh restart` from Termux.

Notes:
- The phone checkout must not have local commits; if it has diverged from
  `main` the updater logs it and does nothing.
- Changes to `deploy/termux/run.sh` itself take effect on the next
  `bash ~/wkaictl.sh restart` (or reboot), not on the automatic restart.
- `AUTO_UPDATE_INTERVAL_SEC` (default 300) and `AUTO_UPDATE_BRANCH`
  (default `main`) tune it.

### Manual

```bash
proot-distro login debian -- bash -c "cd ~/wkai && git pull && cd wkai-backend && npm ci --no-audit --no-fund && npm run db:migrate"
bash ~/wkaictl.sh restart
```

## What changes compared to Render

| | Render | Phone |
|---|---|---|
| Restart on crash / watchdog | platform | `deploy/termux/run.sh` (exit 1 → restart with backoff up to 5 min; exit 0 → stay down) |
| Start command | `npm run start` | same, via `run.sh` (migrates once, then loops `node src/index.js`) |
| Logs | Render dashboard | `/root/wkai-logs/backend.log` in Debian, rotated at 20 MB |
| Health / API | public URL | `http://<phone-ip>:4000` on the same Wi-Fi only |

The API is no longer reachable from the internet. If the Vercel frontend
needs it remotely, put a tunnel (e.g. `ngrok http 4000`, Cloudflare Tunnel)
or Tailscale in front of port 4000 and set that public URL as
`VITE_BACKEND_URL`.

## Troubleshooting

- **Backend stops when the screen turns off** → step 1 wasn't fully applied
  (battery optimisation or phantom process killer).
- **`tmux: command not found` inside Debian** → expected: `tmux` is a Termux
  package, not a Debian one. `exit` to Termux and `pkg install tmux`.
- **`bash\r: No such file or directory`** → scripts checked out with Windows
  line endings; fix with `sed -i 's/\r$//' deploy/termux/*.sh`
  (`deploy/termux/.gitattributes` prevents this on fresh clones).
- **Empty `.env`** → `> .env` truncates it; restore with
  `cp .env.example .env` and re-fill from Render.
