# PE-OPS-CONTAINERS-02 Runtime Inventory

## Live verification citations

### Repo / branch context
```bash
$ git -C /opt/elis/repo branch --show-current
feature/pe-ops-containers-01-containerise-elis-agent-runtime-boundaries
$ git -C /opt/elis/repo rev-parse HEAD
99dba92e4006655ae6130900ed93560804ebdf05
```

### Hermes service status
```bash
$ systemctl --user status elis-advisor-gateway.service --no-pager --full | sed -n '1,25p'
● elis-advisor-gateway.service - ELIS Advisor Hermes Gateway
     Loaded: loaded (/home/samurai/.config/systemd/user/elis-advisor-gateway.service; enabled; preset: enabled)
     Active: active (running) since Mon 2026-05-11 09:36:26 BST; 3 days ago
```

### Live file mtimes
```bash
$ stat -c '%y %n' /home/samurai/.hermes/profiles/elis-advisor/config.yaml /home/samurai/.hermes/profiles/elis-advisor/.env /home/samurai/.config/systemd/user/elis-advisor-gateway.service
2026-05-09 13:23:12.925223076 +0100 /home/samurai/.hermes/profiles/elis-advisor/config.yaml
2026-05-09 13:15:54.702625863 +0100 /home/samurai/.hermes/profiles/elis-advisor/.env
2026-05-09 13:35:41.256776042 +0100 /home/samurai/.config/systemd/user/elis-advisor-gateway.service
```

## Current ELIS Advisor runtime
- Hermes gateway on `elis-server`
- Discord advisor channel `1502602267931578378`
- supervisor channel `1494725349261709343`
- host profile: `elis-advisor`
- service: `elis-advisor-gateway.service`

## Planning notes
- `.env` is existence-only evidence; never copy contents
- no `/app:/app:ro` mount in final plan
- Hermes binary/source must be package-managed or build-managed, not host bind-mounted
- no broad `/home/samurai` or `/opt/elis` mount
