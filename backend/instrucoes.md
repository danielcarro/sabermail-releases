# 🚀 NewLeads - Sistema de Disparo de Email Marketing

Sistema profissional para disparo de emails em massa com suporte a **retomada automática**, **logs detalhados**, **controle de limite diário** e **pausa/cancelamento** de campanhas.

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Como Usar](#-como-usar)
- [Comandos Rápidos](#-comandos-rápidos)
- [Controle da Campanha](#-controle-da-campanha)
- [Logs e Relatórios](#-logs-e-relatórios)
- [Recuperação de Falhas](#-recuperação-de-falhas)
- [Limites e Boas Práticas](#-limites-e-boas-práticas)
- [Solução de Problemas](#-solução-de-problemas)
- [Personalização do Template](#-personalização-do-template)

---

## ✨ Funcionalidades

- ✅ **Envio em massa** de emails com template HTML personalizado
- ✅ **Intervalo aleatório** entre 2-5 segundos (evita bloqueio)
- ✅ **Limite diário** configurável (padrão: 500 emails/dia)
- ✅ **Checkpoint automático** - retoma de onde parou em caso de falha
- ✅ **Pausar/Retomar** campanha a qualquer momento
- ✅ **Cancelamento** seguro da campanha
- ✅ **Logs detalhados** em JSON por campanha
- ✅ **Recuperação** após queda de internet/energia
- ✅ **Placeholders** para personalização por empresa
- ✅ **Preview local** antes do envio

---

## 📦 Pré-requisitos

| Requisito | Versão | Comando para verificar |
|-----------|--------|------------------------|
| **Python** | 3.7+ | `python --version` |
| **Pip** | 20.0+ | `pip --version` |
| **Conta Gmail** | Qualquer | com verificação em duas etapas |

---

## 🔧 Instalação

### 1. Clone ou baixe o projeto

```bash
# Crie a pasta do projeto
mkdir C:\projetos\simple-mailship
cd C:\projetos\simple-mailship
2. Instale as dependências
bash
pip install python-dotenv
3. Crie a estrutura de pastas
bash
mkdir templates
mkdir listas
mkdir logs
mkdir checkpoints
⚙️ Configuração
1. Configure o arquivo .env
Crie o arquivo .env na raiz do projeto:

env
# ==== Gmail SMTP settings ====
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_SSL=false

# Your full Gmail address and App Password
SMTP_USERNAME=seuemail@gmail.com
SMTP_PASSWORD=SUA_SENHA_DE_APP_16_DIGITOS

# From display name and subject
FROM_NAME=NewLeads - Prospecção Inteligente
SUBJECT=Leads segmentados NewLeads - Prospecção Inteligente

# Path to your HTML email template
TEMPLATE_PATH=./templates/rhsudeste.html

# Optional reply-to address
REPLY_TO=

# Rate limit (emails per minute)
RATE_PER_MIN=12
2. Gerar Senha de App do Gmail
Acesse Google Account Security

Ative Verificação em duas etapas (2FA)

Vá em Senhas de app (App Passwords)

Selecione:

App: "Email"

Dispositivo: "Windows Computador"

Clique em Gerar

Copie a senha de 16 caracteres (ex: abcd efgh ijkl mnop)

Cole no campo SMTP_PASSWORD do .env sem espaços

3. Prepare o template HTML
Coloque seu template HTML na pasta templates/ com nome rhsudeste.html (ou conforme configurado no .env)

Placeholders disponíveis:

{{NOME_EMPRESA}} - Nome da empresa

{{CNPJ}} - CNPJ da empresa

{{CIDADE}} - Cidade

{{TELEFONE}} - Telefone

{{APTA}} - Status (Sim/Não)

{{EMAIL}} - Email da empresa

4. Prepare a lista de leads (CSV)
Coloque seu arquivo CSV na pasta listas/ com o formato:

csv
CNPJ,Razao Social,Fundacao,Cidade,Apta,Telefone,Email
00.000.000/0001-00,EMPRESA EXEMPLO LTDA,1990-01-01,SAO PAULO,Sim,(11) 99999-9999,contato@empresa.com
📁 Estrutura do Projeto
text
C:\projetos\simple-mailship\
│
├── .env                          ← Configurações SMTP
├── envio_newleads.py             ← Script principal de envio
├── testar_envio.py               ← Script para testar antes de enviar
├── controles.py                  ← Controle de pausa/cancelamento
├── preview_teste.html            ← Preview gerado automaticamente
│
├── templates\                    ← Templates HTML
│   └── rhsudeste.html
│
├── listas\                       ← Arquivos CSV com leads
│   └── sua_lista.csv
│
├── logs\                         ← Logs de cada campanha
│   └── campanha_20250115_143022.json
│
└── checkpoints\                  ← Pontos de recuperação
    ├── campanha_atual.json
    ├── pausar.txt                ← Crie para pausar
    └── cancelar.txt              ← Crie para cancelar
🚀 Como Usar
Passo 1: Teste antes de enviar
bash
python testar_envio.py
O script irá:

Carregar as configurações do .env

Gerar um preview local (preview_teste.html)

Enviar emails de teste para os endereços configurados

Adicionar um banner de TESTE para identificação

Passo 2: Execute a campanha principal
bash
python envio_newleads.py
O script irá:

Verificar limite diário

Listar os CSVs disponíveis

Perguntar qual arquivo usar

Mostrar resumo da campanha

Solicitar confirmação

Iniciar os envios

📌 Comandos Rápidos
Comando	Descrição
python testar_envio.py	Testa envio para emails pessoais
python envio_newleads.py	Inicia campanha principal
python controles.py	Abre menu de controle
Ctrl+C (durante envio)	Salva checkpoint e sai
🎮 Controle da Campanha
Durante o envio (em outro terminal):
bash
python controles.py
Menu de controle:

text
========================================
🎮 CONTROLE DA CAMPANHA
========================================
1. Pausar campanha
2. Continuar campanha
3. Cancelar campanha
4. Verificar status
5. Sair
Manual (criando arquivos):
Ação	Como fazer
Pausar	Crie o arquivo checkpoints/pausar.txt
Continuar	Delete o arquivo checkpoints/pausar.txt
Cancelar	Crie o arquivo checkpoints/cancelar.txt
📊 Logs e Relatórios
Cada campanha gera um arquivo JSON na pasta logs/:

json
{
  "data_inicio": "2025-01-15T14:30:22",
  "total_emails": 150,
  "sucessos": 148,
  "falhas": 2,
  "envios": [
    {
      "timestamp": "2025-01-15T14:30:25",
      "email": "empresa1@email.com",
      "empresa": "EMPRESA TESTE LTDA",
      "status": "sucesso",
      "erro": null
    }
  ]
}
Visualizar relatório rapidamente:
bash
# No PowerShell
Get-Content logs\campanha_*.json | ConvertFrom-Json | Format-List
🔄 Recuperação de Falhas
Queda de internet/energia:
O script salva checkpoint automático a cada lote (50 emails)

Ao reiniciar, execute novamente:

bash
python envio_newleads.py
O script detectará o checkpoint e perguntará:

text
🔄 Recuperando campanha anterior...
Deseja continuar de onde parou? (s/N):
Interrupção manual (Ctrl+C):
O script salva o checkpoint automaticamente

Pode ser retomado normalmente

⚠️ Limites e Boas Práticas
Configuração	Valor padrão	Recomendação
Limite diário	500 emails	Não exceder para evitar bloqueio
Intervalo entre emails	2-5 segundos	Mantenha entre 3-8 segundos
Emails por lote	50	Checkpoint a cada lote
Pausa entre lotes	60 minutos	Para respeitar limite diário
Limites do Gmail:
Conta gratuita: 500 emails/dia

Google Workspace: 2.000 emails/dia

Máximo por minuto: ~20 emails

🔧 Solução de Problemas
Erro: authentication failed
text
❌ ERRO CRÍTICO: authentication failed
Solução:

Verifique se usou Senha de App (não a senha normal)

Verifique se a verificação em 2 etapas está ativa

Regere uma nova senha de app

Erro: Connection timeout
text
❌ ERRO CRÍTICO: [Errno 110] Connection timed out
Solução:

Verifique sua conexão com a internet

Verifique se firewall não está bloqueando a porta 587

Tente usar porta 465 com SMTP_USE_SSL=true

Erro: Template não encontrado
text
❌ Arquivo template não encontrado!
Solução:

Verifique se o arquivo existe em templates/rhsudeste.html

Verifique o TEMPLATE_PATH no arquivo .env

Erro: CSV não encontrado
text
❌ Nenhum arquivo CSV encontrado
Solução:

Coloque seus arquivos .csv na pasta listas/

Verifique se o arquivo tem extensão .csv

🎨 Personalização do Template
Placeholders disponíveis:
Placeholder	Descrição	Origem no CSV
{{NOME_EMPRESA}}	Nome da empresa	Razao Social
{{CNPJ}}	CNPJ	CNPJ
{{CIDADE}}	Cidade	Cidade
{{TELEFONE}}	Telefone	Telefone
{{APTA}}	Status	Apta
{{EMAIL}}	Email	Email
Exemplo de uso no HTML:
html
<p>Olá, <strong>{{NOME_EMPRESA}}</strong>!</p>
<p>Sua empresa localizada em <strong>{{CIDADE}}</strong> foi selecionada.</p>
<p>CNPJ: {{CNPJ}} | Telefone: {{TELEFONE}}</p>
📞 Suporte
Se encontrar problemas:

Verifique os logs em logs/

Verifique o checkpoint em checkpoints/campanha_atual.json

Execute o modo de teste primeiro

📄 Licença
Este software é de uso interno. Não compartilhe suas credenciais SMTP ou listas de leads.

Desenvolvido para NewLeads - Prospecção Inteligente