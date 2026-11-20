# Scheduled refresh (residencehome)

`scripts/refresh.sh` re-crawls Zap's store directory, merges, and commits + pushes `stores.json` and
`stores-index.json` when they change. It needs an Israeli residential IP (Zap blocks datacenter IPs and
headless browsers), so it runs on residencehome as a **user** systemd timer: 1st of each month, 04:30
(+ up to 1 h random delay), catching up after downtime (`Persistent=true`). Runtime about 20 minutes,
about 1,050 requests at 1 req/s.

Guard: if the crawl returns under 90% of last month's live stores (blocked or truncated), it exits 2
and commits nothing, so a bad crawl can't mark the roster as gone.

Install (from a clone at `~/repos/github/shopping/Israel-Online-Stores` on the host):

```
mkdir -p ~/.config/systemd/user
cp deploy/israel-online-stores-refresh.{service,timer} ~/.config/systemd/user/
systemctl --user daemon-reload && systemctl --user enable --now israel-online-stores-refresh.timer
loginctl enable-linger daniel     # user timers run without a login session
```

Run now: `systemctl --user start israel-online-stores-refresh.service`; logs: `journalctl --user -u israel-online-stores-refresh`.
Registered in Endpoint-Management `machines/residencehome/host-services.yaml` as `israel-online-stores-refresh` (2026-11-20).
