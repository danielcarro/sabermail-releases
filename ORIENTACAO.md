# ORIENTAÇÃO — Reestruturação simple-mailship

## Objetivo

Reorganizar o repositório em **backend/** e **frontend/** e gerar instaladores `.exe` para Windows.

---

## Status atual (15/jun/2026)

### ✅ Fase 1 — Reorganização (CONCLUÍDA)
- Todos os scripts `.py` movidos para `backend/`
- Pastas de dados (`templates/`, `listas/`, `contacts/`, `logs/`, `checkpoints/`) movidas para `backend/`
- `.env.example`, `requirements.txt`, `instrucoes.md` movidos para `backend/`
- Paths dos scripts ajustados para encontrar `.env` na raiz (`Path(__file__).parent.parent`)
- `.env` na raiz atualizado com `TEMPLATE_PATH=./backend/templates/...`
- `.gitignore` atualizado para a nova estrutura
- `AGENTS.md` atualizado com paths `backend/` e `frontend/`

### ✅ Fase 2 — Frontend (CONCLUÍDA)
- App único integrado: `frontend/app.py` com 5 abas (Dashboard, Campanha, Listas, Config SMTP, Bounce)
- Arquivos antigos de app individual removidos
- IMAP config (`IMAP_HOST`, `IMAP_PORT`, `IMAP_USE_SSL`) adicionado ao `.env`, SMTP tab e Bounce tab
- Bug de geometry corrigido: `"900+100+50"` → `"900x600+100+50"`

### ✅ Fase 3 — Build .exe + Instalador (CONCLUÍDA)
- `build_exe.ps1` usa `--onedir` com `pyinstaller` para gerar `dist/SimpleMailShip/` (exe + `_internal/` DLLs + `backend/` + `.env`)
- Bug `ModuleNotFoundError: No module named 'encodings'` corrigido via rebuild com `base_library.zip` incluso
- `installer.iss` (Inno Setup) gera instalador Windows em `dist/SimpleMailShip_Installer_v1.0.0.exe`
- Instalador: instala em `{autopf}\SimpleMailShip`, cria atalhos (Iniciar + Área de Trabalho), suporta desinstalação
- Dados do usuário em `%APPDATA%\SimpleMailShip\` (listas, logs, templates, checkpoints) — persistente entre atualizações
- `.exe` verificado: abre sem crash

## Arquitetura final

```
simple-mailship/
├── backend/                  ← scripts Python + dados
│   ├── mailer.py, envio_newleads.py, testar_envio.py, controle.py, bounce_tracker.py
│   ├── templates/, listas/, contacts/, logs/, checkpoints/
│   └── .env.example, requirements.txt, instrucoes.md
├── frontend/
│   ├── app.py                ← app integrado (5 abas, tkinter)
│   └── requirements.txt
├── dist/
│   ├── SimpleMailShip/       ← pasta portátil (exe + DLLs + backend/ + .env)
│   └── SimpleMailShip_Installer_v1.0.0.exe  ← instalador Windows
├── build_exe.ps1             ← build .exe com PyInstaller
├── installer.iss             ← script Inno Setup
├── .env                      ← SMTP + IMAP (junto do .exe ou na raiz)
├── .gitignore
├── AGENTS.md
├── ORIENTACAO.md             ← este arquivo
└── README.md
```

## Tecnologias escolhidas

| Camada | Tecnologia | Motivo |
|---|---|---|
| GUI | `tkinter` (stdlib) | Zero dependência extra, suporte nativo no PyInstaller |
| Build .exe | `PyInstaller` | Empacota Python + dependências em .exe único |
| SO alvo | Windows 10/11 | Todos os scripts usam `os.name == 'nt'` |

## Passos a seguir (ordem)

### Fase 1 — Reorganização

1. Criar pasta `backend/`
2. Mover todos os `.py`, pastas de dados e `requirements.txt` para `backend/`
3. Criar `.env` na raiz que aponte os paths para `backend/` (ex: `TEMPLATE_PATH=./backend/templates/...`)
4. Atualizar paths dentro dos scripts (se necessário)
5. Mover `instrucoes.md` para `backend/instrucoes.md` (pertence ao sistema NewLeads)
6. Atualizar `AGENTS.md` com a nova estrutura

### ✅ Fase 2 — Frontend (CONCLUÍDA)
- App único integrado: `frontend/app.py` com 5 abas (Dashboard, Campanha, Listas, Config SMTP, Bounce)
- Arquivos antigos de app individual removidos

### ✅ Fase 3 — Build .exe (CONCLUÍDA)
- `build_exe.ps1` usa `--onedir` para criar `dist/SimpleMailShip/` com exe + DLLs + backend/ + .env
- `installer.iss` (Inno Setup) para gerar instalador Windows completo
- Dados do usuário em `%APPDATA%\SimpleMailShip\`

---

**Status: Projeto completo.** O instalador foi gerado e verificado. Próximos passos opcionais: testar instalação em máquina limpa, adicionar suporte a locale pt-BR na GUI, e implementar auto-update.
