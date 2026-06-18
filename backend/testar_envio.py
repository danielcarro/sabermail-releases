import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv

def _ssl_ctx():
    path = Path(__file__).resolve().parent / "ssl" / "gmail-ca-bundle.pem"
    ctx = ssl.create_default_context(cafile=str(path))
    ctx.verify_flags = ssl.VERIFY_X509_PARTIAL_CHAIN
    return ctx

# ============================================================
# CARREGA CONFIGURAÇÕES DO .ENV
# ============================================================
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print("✅ Arquivo .env carregado com sucesso!")
else:
    print(f"❌ Arquivo .env não encontrado em: {env_path}")
    exit(1)

# Configurações do .env
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "false").lower() == "true"
SMTP_USER = os.getenv("SMTP_USERNAME", "")
SMTP_PASS = os.getenv("SMTP_PASSWORD", "")
FROM_NAME = os.getenv("FROM_NAME", "NewLeads - Prospecção Inteligente")
ASSUNTO = os.getenv("SUBJECT", "Leads segmentados NewLeads - Prospecção Inteligente")
TEMPLATE_PATH = os.getenv("TEMPLATE_PATH", "./templates/rhsudeste.html")

# ============================================================
# DADOS DA EMPRESA TESTE
# ============================================================
DADOS_EMPRESA_TESTE = {
    "nome_empresa": "EMPREGUE RECURSOS HUMANOS LTDA",
    "cnpj": "12.345.678/0001-90",
    "cidade": "SÃO PAULO - SP",
    "apta": "Sim",
    "telefone": "(11) 3456-7890",
    "email": "contato@empregue.com.br",
    "email_destino": "danielcarrobr@gmail.com",  # Email que receberá o teste
    "nome_curto": "Empregue"
}

# ============================================================
# EMAILS PARA TESTE (PODE ADICIONAR MAIS)
# ============================================================
EMAILS_TESTE = [
    "danielcarrobr@gmail.com",
    "daniel.carro@yahoo.com.br"
]

# ============================================================
# CONFIGURAÇÕES DE PASTAS
# ============================================================
PASTA_RAIZ = Path(__file__).parent
PASTA_TEMPLATES = PASTA_RAIZ / "templates"

# ============================================================
# FUNÇÕES
# ============================================================

def ler_template_html():
    """Lê o arquivo HTML do template"""
    template_relativo = TEMPLATE_PATH.lstrip("./")
    template_path = PASTA_RAIZ / template_relativo
    
    if not template_path.exists():
        template_path = PASTA_TEMPLATES / Path(template_relativo).name
    
    if not template_path.exists():
        print(f"❌ Arquivo template não encontrado em: {template_path}")
        return None
    
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

def personalizar_html_teste(html_base):
    """Substitui placeholders no HTML pelos dados da empresa teste"""
    html_personalizado = html_base
    
    # Placeholders a serem substituídos
    substituicoes = {
        "{{NOME_EMPRESA}}": DADOS_EMPRESA_TESTE["nome_empresa"],
        "{{EMPRESA}}": DADOS_EMPRESA_TESTE["nome_empresa"],
        "{{CIDADE}}": DADOS_EMPRESA_TESTE["cidade"],
        "{{CNPJ}}": DADOS_EMPRESA_TESTE["cnpj"],
        "{{TELEFONE}}": DADOS_EMPRESA_TESTE["telefone"],
        "{{APTA}}": DADOS_EMPRESA_TESTE["apta"],
        "{{EMAIL}}": DADOS_EMPRESA_TESTE["email"],
        "{{nome}}": DADOS_EMPRESA_TESTE["nome_curto"],
        "{{NOME}}": DADOS_EMPRESA_TESTE["nome_curto"],
    }
    
    for placeholder, valor in substituicoes.items():
        if valor:
            html_personalizado = html_personalizado.replace(placeholder, valor)
    
    return html_personalizado

def enviar_email_teste(servidor, destinatario, html_base):
    """Envia um email de teste com os dados da empresa simulada"""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[TESTE] {ASSUNTO} - Empresa: {DADOS_EMPRESA_TESTE['nome_empresa']}"
        msg["From"] = f"{FROM_NAME} <{SMTP_USER}>"
        msg["To"] = destinatario
        
        # Personaliza o HTML com os dados da empresa teste
        html_personalizado = personalizar_html_teste(html_base)
        
        # Adiciona um aviso de TESTE no início do HTML
        aviso_teste = f"""
        <div style="background-color:#FF6B35; color:#ffffff; text-align:center; padding:12px; margin-bottom:20px; border-radius:8px; font-family:sans-serif;">
            <strong>🧪 ESTE É UM EMAIL DE TESTE - MODO DE VALIDAÇÃO 🧪</strong><br>
            Enviado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}<br>
            Template: {Path(TEMPLATE_PATH).name}<br>
            <strong>Dados da empresa simulada:</strong> {DADOS_EMPRESA_TESTE['nome_empresa']} | CNPJ: {DADOS_EMPRESA_TESTE['cnpj']}
        </div>
        """
        
        # Adiciona um rodapé informativo
        rodape_teste = f"""
        <div style="background-color:#f0f0f0; color:#666; text-align:center; padding:10px; margin-top:20px; border-radius:8px; font-family:sans-serif; font-size:12px;">
            <strong>🔍 INFORMAÇÕES DO TESTE</strong><br>
            Este email foi enviado com dados simulados para validação do template.<br>
            Os placeholders foram preenchidos com:<br>
            Nome: {DADOS_EMPRESA_TESTE['nome_empresa']}<br>
            CNPJ: {DADOS_EMPRESA_TESTE['cnpj']}<br>
            Cidade: {DADOS_EMPRESA_TESTE['cidade']}<br>
            Telefone: {DADOS_EMPRESA_TESTE['telefone']}
        </div>
        """
        
        html_com_aviso = aviso_teste + html_personalizado + rodape_teste
        parte_html = MIMEText(html_com_aviso, "html", "utf-8")
        msg.attach(parte_html)
        
        servidor.sendmail(SMTP_USER, destinatario, msg.as_string())
        return True, None
    except Exception as e:
        return False, str(e)

def salvar_preview_html(html_base):
    """Salva uma prévia do HTML com os dados da empresa teste"""
    preview_path = PASTA_RAIZ / "preview_teste.html"
    
    # Personaliza o HTML com os dados da empresa teste
    html_personalizado = personalizar_html_teste(html_base)
    
    aviso_teste = f"""
    <div style="background-color:#FF6B35; color:#ffffff; text-align:center; padding:12px; margin-bottom:20px; border-radius:8px; font-family:sans-serif;">
        <strong>🔧 VISUALIZAÇÃO DE TESTE - NÃO É UM EMAIL REAL 🔧</strong><br>
        Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}<br>
        Template: {Path(TEMPLATE_PATH).name}<br>
        <strong>Dados da empresa simulada:</strong> {DADOS_EMPRESA_TESTE['nome_empresa']}
    </div>
    """
    
    rodape_teste = f"""
    <div style="background-color:#f0f0f0; color:#666; text-align:center; padding:10px; margin-top:20px; border-radius:8px; font-family:sans-serif; font-size:12px;">
        <strong>🔍 DADOS UTILIZADOS NESTE PREVIEW</strong><br>
        Nome: {DADOS_EMPRESA_TESTE['nome_empresa']}<br>
        CNPJ: {DADOS_EMPRESA_TESTE['cnpj']}<br>
        Cidade: {DADOS_EMPRESA_TESTE['cidade']}<br>
        Telefone: {DADOS_EMPRESA_TESTE['telefone']}<br>
        Status: {DADOS_EMPRESA_TESTE['apta']}
    </div>
    """
    
    html_completo = aviso_teste + html_personalizado + rodape_teste
    
    with open(preview_path, "w", encoding="utf-8") as f:
        f.write(html_completo)
    
    return preview_path

def mostrar_configuracoes():
    """Exibe as configurações e dados do teste"""
    print("\n" + "=" * 60)
    print("📊 DADOS DA EMPRESA SIMULADA PARA TESTE")
    print("=" * 60)
    print(f"   Nome da Empresa: {DADOS_EMPRESA_TESTE['nome_empresa']}")
    print(f"   CNPJ: {DADOS_EMPRESA_TESTE['cnpj']}")
    print(f"   Cidade: {DADOS_EMPRESA_TESTE['cidade']}")
    print(f"   Telefone: {DADOS_EMPRESA_TESTE['telefone']}")
    print(f"   Status: {DADOS_EMPRESA_TESTE['apta']}")
    print(f"   Email Empresa: {DADOS_EMPRESA_TESTE['email']}")
    
    print("\n" + "=" * 60)
    print("⚙️  CONFIGURAÇÕES SMTP CARREGADAS")
    print("=" * 60)
    print(f"   SMTP_HOST: {SMTP_HOST}:{SMTP_PORT}")
    print(f"   SMTP_USER: {SMTP_USER}")
    print(f"   FROM_NAME: {FROM_NAME}")
    print(f"   TEMPLATE_PATH: {TEMPLATE_PATH}")

def main():
    print("=" * 60)
    print("🧪 NEWLEADS - MODO DE TESTE")
    print("=" * 60)
    
    # Valida credenciais
    if not SMTP_USER or SMTP_USER == "seuemail@gmail.com":
        print("\n❌ SMTP_USERNAME não configurado no arquivo .env")
        return
    
    if not SMTP_PASS or SMTP_PASS == "sua_senha_de_app_16_digitos":
        print("\n❌ SMTP_PASSWORD não configurado no arquivo .env")
        return
    
    # Mostra configurações
    mostrar_configuracoes()
    
    # Verifica template
    print("\n📄 Verificando template HTML...")
    html_template = ler_template_html()
    if not html_template:
        return
    
    print(f"✅ Template carregado com sucesso!")
    
    # Salva preview local
    preview_path = salvar_preview_html(html_template)
    print(f"\n💾 Preview salvo em: {preview_path}")
    print(f"   📂 Abra este arquivo no navegador para ver como o email ficará")
    
    # Mostra emails de teste
    print("\n" + "=" * 60)
    print("📧 EMAILS QUE RECEBERÃO O TESTE")
    print("=" * 60)
    for i, email in enumerate(EMAILS_TESTE, 1):
        print(f"   {i}. {email}")
    
    print(f"\n🏢 Dados que serão enviados:")
    print(f"   Empresa: {DADOS_EMPRESA_TESTE['nome_empresa']}")
    print(f"   CNPJ: {DADOS_EMPRESA_TESTE['cnpj']}")
    print(f"   Telefone: {DADOS_EMPRESA_TESTE['telefone']}")
    
    resposta = input(f"\n⚠️  Deseja enviar email de teste para {len(EMAILS_TESTE)} destinatário(s)? (s/N): ").lower()
    if resposta != 's':
        print("❌ Teste cancelado.")
        print("💡 Você ainda pode abrir o arquivo preview_teste.html no navegador para visualizar.")
        return
    
    # Conexão SMTP
    server = None
    try:
        print("\n🔌 Conectando ao servidor SMTP...")
        
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=_ssl_ctx())
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            server.starttls(context=_ssl_ctx())
        
        server.login(SMTP_USER, SMTP_PASS)
        print("✅ Conexão estabelecida!")
        
        enviados = 0
        falhas = 0
        
        for i, email in enumerate(EMAILS_TESTE, 1):
            print(f"\n📤 [{i}/{len(EMAILS_TESTE)}] Enviando para: {email}")
            print(f"   📊 Dados da empresa: {DADOS_EMPRESA_TESTE['nome_empresa']}")
            
            sucesso, erro = enviar_email_teste(server, email, html_template)
            
            if sucesso:
                print(f"   ✅ Enviado com sucesso!")
                enviados += 1
            else:
                print(f"   ❌ Falha: {erro}")
                falhas += 1
            
            # Pequeno delay entre envios de teste
            if i < len(EMAILS_TESTE):
                time.sleep(2)
        
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO DE TESTE")
        print("=" * 60)
        print(f"✅ Enviados com sucesso: {enviados}")
        print(f"❌ Falhas: {falhas}")
        
        if enviados > 0:
            print("\n🎉 Teste concluído! Verifique suas caixas de email:")
            for email in EMAILS_TESTE:
                print(f"   - {email}")
            print("\n   💡 Dica: Verifique a pasta SPAM se não encontrar o email.")
            print("   💡 O assunto do email começa com '[TESTE]'")
            print("   💡 Os placeholders foram preenchidos com os dados da EMPREGUE RECURSOS HUMANOS")
        
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {e}")
        print("\n   Possíveis causas:")
        print("   - Senha de App incorreta")
        print("   - Verificação em duas etapas não ativada")
        print("   - Verifique suas credenciais no arquivo .env")
        
    finally:
        if server:
            server.quit()
            print("\n🔌 Conexão SMTP encerrada.")

if __name__ == "__main__":
    import time
    main()