# GitHub Actions Deploy Setup

Nach Repo-Push auf GitHub müssen folgende **GitHub Secrets** hinzugefügt werden:

## Secrets (Settings → Secrets and variables → Actions)

| Name | Wert | Beschreibung |
|------|------|-------------|
| `DEPLOY_HOST` | `bfr.roos.rocks` | Hetzner Host |
| `DEPLOY_USER` | `root` | SSH User (oder andere) |
| `DEPLOY_SSH_KEY` | *(siehe unten)* | Private SSH-Key |

### SSH-Key generieren/kopieren:

```bash
# SSH-Key anzeigen (auf Hetzner Host):
cat ~/.ssh/github_openclaw

# Oder neu generieren:
ssh-keygen -t ed25519 -f ~/.ssh/deploy-github -C "github-actions@hetzner"
```

Dann in GitHub → Settings → Secrets → `DEPLOY_SSH_KEY` → einfügen.

### SSH Key Permissions auf Host:

```bash
# Sicherstellen, dass der User ssh login kann:
sudo nano /etc/ssh/sshd_config
# → PubkeyAuthentication yes
# → PermitRootLogin yes (oder specific user)

# Key in authorized_keys:
cat ~/.ssh/github_openclaw.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Test:
ssh -i ~/.ssh/github_openclaw root@bfr.roos.rocks "whoami"
```

## Workflow Test

Nach Secrets-Setup: Neuer Push auf `main` → GitHub Actions triggert → Deploy sollte starten.

Logs: GitHub → Repo → Actions → Letzte Workflow-Run → Details.

