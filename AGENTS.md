# AGENTS.md — SaberMail

## Architecture

Two independent mailer systems share this repo and `.env` but are otherwise decoupled.

| System | Script | Input | Template method | Key traits |
|---|---|---|---|---|
| Generic CLI mailer | `backend/mailer.py` | JSON (`--list`, `--test`) | Jinja2 (`{{name}}`) | SSL/STARTTLS, rate limiting, dry-run, preview save |
| Campaign bulk mailer (pt-BR) | `backend/envio_newleads.py` | CSV via `backend/listas/` | `str.replace` with uppercase placeholders | Checkpoint/resume, daily limit, pause/cancel, random delay |
| Frontend Campaign tab | `frontend/app.py` | CSV via `DATA_DIR/listas/` | `str.replace` matching CSV column names (case-insensitive) | GUI with progress, IMAP bounce monitoring, auto-clean |

Supporting scripts: `testar_envio.py` (test send + HTML preview), `controle.py` (pause/cancel menu), `bounce_tracker.py` (IMAP bounce — hardcoded creds in source).

Frontend: single tkinter app at `frontend/app.py` (6 tabs: Dashboard, Campanha, Listas, Config SMTP, Relatórios, Bounce), deployable via PyInstaller.

## Commands (run from repo root)

```
python backend/mailer.py --test <email>
python backend/mailer.py --list backend/contacts/example.json
python backend/mailer.py --list contacts.json --dry-run --save-previews ./previews
python backend/envio_newleads.py
python backend/testar_envio.py
python backend/controle.py
python backend/bounce_tracker.py
python frontend/app.py
```

## Build & deploy

```
powershell -File build_exe.ps1                          # → dist/SaberMail/
ISCC.exe installer.iss                                   # → dist/SaberMail_Installer_v1.0.0.exe
```

## Critical gotchas

- **Three template systems** — do not confuse:
  - `mailer.py`: Jinja2 (`{{name}}`, `{% if %}`). Any JSON field is a variable.
  - `envio_newleads.py`: `str.replace` with exact uppercase placeholders (`{{NOME_EMPRESA}}`, `{{CIDADE}}`, `{{CNPJ}}`, `{{TELEFONE}}`, `{{APTA}}`, `{{EMAIL}}`). Unmatched ones appear verbatim.
  - `frontend/app.py` Campaign tab: `str.replace` using CSV column names as keys, matching both `{{COLUMN}}` and `{{column}}` variants.
- **SSL CA bundle**: all scripts use `backend/ssl/gmail-ca-bundle.pem` with `VERIFY_X509_PARTIAL_CHAIN`.
- **File-based signaling**: `backend/checkpoints/{pausar.txt,cancelar.txt}`. `envio_newleads.py` polls them; `controle.py` writes/removes.
- **Frontend config storage**: saved to SQLite `DATA_DIR/simpleship.db` (table `config`), NOT directly to `.env`. On load, SQLite values override `.env`.
- **Frontend first frozen run** (`%APPDATA%\SaberMail\`): copies default files from bundled `backend/` and `.env` from exe dir to AppData. Then config is stored in SQLite.
- **IMAP bounce**: frontend Bounce tab and campaign auto-bounce use `SMTP_USERNAME`/`SMTP_PASSWORD` + separate `IMAP_HOST`/`IMAP_PORT`/`IMAP_USE_SSL`. Standalone `bounce_tracker.py` has creds hardcoded in source (lines 18-19) — does not read `.env`.
- **GUI campaign output**: saves JSON log to `DATA_DIR/logs/` AND campaign to SQLite. After sending, generates `clean_<csvname>.csv` (removes bounced emails).
- **`envio_newleads.py` prompt typo**: line 568 prints `'python controles.py'` — the file is `controle.py` (no trailing 's').
- **No test framework, no CI, no linting/typechecking** — `.gitignore` references pytest/mypy dirs but nothing uses them.
- **Platform**: Windows only (`os.name == 'nt'`, `cls`, backslash paths in docs).
- **References**: `backend/instrucoes.md` (pt-BR) is the authoritative doc for the NewLeads campaign system; `README.md` covers the upstream `mailer.py`.
