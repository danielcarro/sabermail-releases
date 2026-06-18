import imaplib
import email
from email.header import decode_header
import re
from pathlib import Path
import json
from datetime import datetime
import time

# ============================================================
# CONFIGURAÇÕES DA CAIXA DE BOUNCE
# ============================================================
# Configure uma conta de e-mail EXCLUSIVA para receber bounces
# Ex: bounce@seudominio.com.br ou uma conta Gmail secundária

IMAP_SERVER = "imap.gmail.com"  # Para Gmail: imap.gmail.com
IMAP_PORT = 993
IMAP_USER = "sabermaisapps@gmail.com"  # Conta que recebe os bounces
IMAP_PASSWORD = "llix scxy vreq rcyr"       # Senha de App do Gmail

# ============================================================
# CONFIGURAÇÕES DA CAMPANHA
# ============================================================
PASTA_RAIZ = Path(__file__).parent
PASTA_LOGS = PASTA_RAIZ / "logs"

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def decode_mime_header(header):
    """Decodifica cabeçalhos MIME corretamente"""
    if not header:
        return ""
    decoded_parts = decode_header(header)
    decoded_string = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            try:
                if encoding:
                    decoded_string += part.decode(encoding)
                else:
                    decoded_string += part.decode('utf-8', errors='replace')
            except:
                decoded_string += part.decode('latin-1', errors='replace')
        else:
            decoded_string += str(part)
    return decoded_string

def extrair_email_from_string(texto):
    """Extrai e-mail de uma string usando regex"""
    if not texto:
        return None
    # Padrão para encontrar e-mails
    padrao = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails_encontrados = re.findall(padrao, texto)
    return emails_encontrados[0] if emails_encontrados else None

def identificar_email_bounce(corpo_email, destinatarios_originais=None):
    """
    Tenta identificar qual e-mail original falhou a partir do bounce.
    Retorna o e-mail que falhou ou None.
    """
    corpo_texto = corpo_email.lower()
    
    # Padrões comuns em mensagens de bounce
    padroes_bounce = [
        r'final-recipient:\s*rfc822;\s*([^\s]+)',  # Final-Recipient: rfc822; email@dominio.com
        r'original-recipient:\s*rfc822;\s*([^\s]+)',  # Original-Recipient
        r'failed address:\s*([^\s]+@[^\s]+)',  # Failed address: email@dominio.com
        r'<([^\s]+@[^\s]+)>',  # <email@dominio.com>
        r'to:\s*([^\s]+@[^\s]+)',  # To: email@dominio.com
    ]
    
    for padrao in padroes_bounce:
        matches = re.findall(padrao, corpo_texto, re.IGNORECASE)
        if matches:
            email_encontrado = matches[0].strip('<>').lower()
            return email_encontrado
    
    # Se não encontrou pelos padrões, tenta qualquer e-mail no corpo
    todos_emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', corpo_texto)
    if todos_emails:
        # Exclui e-mails do remetente (bounce@...)
        for email_candidato in todos_emails:
            if IMAP_USER.lower() not in email_candidato:
                return email_candidato.lower()
    
    return None

def classificar_bounce(corpo_email):
    """
    Classifica o tipo de bounce baseado no código de erro.
    Retorna: 'hard' (permanente) ou 'soft' (temporário)
    """
    corpo_lower = corpo_email.lower()
    
    # Padrões de soft bounce (temporários - pode tentar novamente)
    soft_patterns = [
        'mailbox full', 'quota exceeded', 'over quota',
        'temporarily unavailable', 'try again later',
        'too many connections', 'rate limit', 'grey listed',
        '451', '421',  # Códigos SMTP temporários
        'delayed', 'deferred'
    ]
    
    # Padrões de hard bounce (permanentes - remover da lista)
    hard_patterns = [
        'user unknown', 'no such user', 'invalid recipient',
        'account disabled', 'mailbox not found', 'does not exist',
        'address rejected', 'domain not found', 'dns error',
        '550', '553', '554', '501', '510',  # Códigos SMTP permanentes
        'rejected', 'blocked', 'spam'
    ]
    
    for pattern in soft_patterns:
        if pattern in corpo_lower:
            return 'soft'
    
    for pattern in hard_patterns:
        if pattern in corpo_lower:
            return 'hard'
    
    return 'unknown'

def conectar_imap():
    """Conecta ao servidor IMAP e retorna a conexão"""
    print(f"🔌 Conectando ao servidor IMAP: {IMAP_SERVER}:{IMAP_PORT}")
    
    try:
        # Conecta com SSL/TLS
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(IMAP_USER, IMAP_PASSWORD)
        print("✅ Conexão IMAP estabelecida!")
        return mail
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

def processar_bounces(campanha_log_path=None):
    """
    Processa os bounces da caixa de e-mail.
    
    Args:
        campanha_log_path: Caminho para o log da campanha (opcional)
                          Se fornecido, atualiza os status no log.
    
    Returns:
        Dicionário com os e-mails que falharam e suas classificações
    """
    
    print("=" * 60)
    print("📬 PROCESSAMENTO DE BOUNCE (NÃO ENTREGUES)")
    print("=" * 60)
    
    # Carrega os e-mails enviados se o log da campanha foi fornecido
    emails_enviados = set()
    if campanha_log_path and Path(campanha_log_path).exists():
        try:
            with open(campanha_log_path, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
                for envio in log_data.get('envios', []):
                    if envio.get('status') == 'sucesso':
                        emails_enviados.add(envio.get('email', ''))
            print(f"📋 Carregados {len(emails_enviados)} e-mails da campanha")
        except Exception as e:
            print(f"⚠️  Não foi possível carregar log da campanha: {e}")
    
    # Conecta ao servidor
    mail = conectar_imap()
    if not mail:
        return {}
    
    try:
        # Seleciona a caixa de entrada (INBOX)
        mail.select('INBOX')
        
        # Busca todos os e-mails não lidos
        status, mensagens_ids = mail.search(None, 'UNSEEN')
        if status != 'OK' or not mensagens_ids[0]:
            print("📭 Nenhum e-mail não lido encontrado.")
            return {}
        
        ids_lista = mensagens_ids[0].split()
        print(f"📧 Encontrados {len(ids_lista)} e-mails não lidos para processar.")
        
        bounces_encontrados = {}
        
        for email_id in ids_lista:
            # Busca o e-mail completo
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            if status != 'OK':
                continue
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # Parse do e-mail
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Extrai assunto e remetente
                    assunto = decode_mime_header(msg.get('Subject', ''))
                    remetente = decode_mime_header(msg.get('From', ''))
                    
                    print(f"\n📨 Processando: {assunto[:60]}...")
                    
                    # Extrai o corpo do e-mail
                    corpo = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() in ['text/plain', 'text/html']:
                                try:
                                    payload = part.get_payload(decode=True)
                                    corpo += payload.decode('utf-8', errors='replace')
                                except:
                                    pass
                    else:
                        try:
                            payload = msg.get_payload(decode=True)
                            corpo += payload.decode('utf-8', errors='replace')
                        except:
                            corpo = str(msg.get_payload())
                    
                    # Identifica qual e-mail falhou
                    email_falhou = identificar_email_bounce(corpo)
                    
                    if email_falhou:
                        # Classifica o tipo de bounce
                        tipo_bounce = classificar_bounce(corpo)
                        
                        bounces_encontrados[email_falhou] = {
                            'tipo': tipo_bounce,
                            'assunto': assunto,
                            'remetente': remetente,
                            'data': datetime.now().isoformat()
                        }
                        
                        print(f"   ❌ E-mail falhou: {email_falhou}")
                        print(f"   📊 Tipo: {'HARD (permanente)' if tipo_bounce == 'hard' else 'SOFT (temporário)' if tipo_bounce == 'soft' else 'desconhecido'}")
                    else:
                        print(f"   ⚠️  Não foi possível identificar o e-mail que falhou")
        
        # Fecha conexão
        mail.close()
        
    except Exception as e:
        print(f"❌ Erro durante processamento: {e}")
    
    finally:
        mail.logout()
        print("\n🔌 Conexão IMAP encerrada.")
    
    # Relatório
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO DE BOUNCE")
    print("=" * 60)
    print(f"🔴 Total de e-mails com falha detectados: {len(bounces_encontrados)}")
    
    hards = sum(1 for b in bounces_encontrados.values() if b['tipo'] == 'hard')
    softs = sum(1 for b in bounces_encontrados.values() if b['tipo'] == 'soft')
    
    print(f"   Hard bounces (permanentes - remover da lista): {hards}")
    print(f"   Soft bounces (temporários - tentar novamente): {softs}")
    
    if emails_enviados:
        print(f"\n📊 Análise com base na campanha ({len(emails_enviados)} e-mails enviados):")
        print(f"   Taxa de falha detectada: {len(bounces_encontrados)} / {len(emails_enviados)} ({len(bounces_encontrados)/len(emails_enviados)*100:.1f}%)")
    
    # Salva relatório
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    relatorio_path = PASTA_LOGS / f"bounce_report_{timestamp}.json"
    with open(relatorio_path, 'w', encoding='utf-8') as f:
        json.dump(bounces_encontrados, f, indent=2, ensure_ascii=False)
    print(f"\n📁 Relatório salvo em: {relatorio_path}")
    
    return bounces_encontrados

def atualizar_log_campanha_com_bounces(campanha_log_path, bounces):
    """
    Atualiza o log da campanha marcando os e-mails que falharam.
    """
    if not Path(campanha_log_path).exists():
        print(f"❌ Log da campanha não encontrado: {campanha_log_path}")
        return
    
    with open(campanha_log_path, 'r', encoding='utf-8') as f:
        log_data = json.load(f)
    
    # Atualiza os registros
    for envio in log_data.get('envios', []):
        email = envio.get('email', '')
        if email in bounces:
            envio['bounce_detectado'] = True
            envio['bounce_tipo'] = bounces[email]['tipo']
            envio['bounce_data'] = bounces[email]['data']
            envio['status'] = 'bounce'
    
    # Salva log atualizado
    with open(campanha_log_path, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Log da campanha atualizado com informações de bounce")

def listar_bounces_por_campanha():
    """Lista todas as campanhas e seus bounces"""
    if not PASTA_LOGS.exists():
        print("📁 Nenhum log encontrado.")
        return
    
    logs_campanha = list(PASTA_LOGS.glob("campanha_*.json"))
    if not logs_campanha:
        print("📁 Nenhuma campanha encontrada.")
        return
    
    print("\n" + "=" * 60)
    print("📋 CAMPANHAS E SEUS BOUNCES")
    print("=" * 60)
    
    for log_path in sorted(logs_campanha, reverse=True)[:10]:
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            bounces = [e for e in log_data.get('envios', []) if e.get('bounce_detectado')]
            hards = [b for b in bounces if b.get('bounce_tipo') == 'hard']
            softs = [b for b in bounces if b.get('bounce_tipo') == 'soft']
            
            data_inicio = log_data.get('data_inicio', '')[:16]
            print(f"\n📊 {log_path.name}")
            print(f"   Data: {data_inicio}")
            print(f"   Total de e-mails: {log_data.get('total_emails', 0)}")
            print(f"   Bounces detectados: {len(bounces)}")
            print(f"     - Hard bounces: {len(hards)}")
            print(f"     - Soft bounces: {len(softs)}")
            
            if bounces:
                print(f"   🚫 E-mails que falharam:")
                for bounce in bounces[:5]:
                    print(f"     • {bounce.get('email', 'N/A')} ({bounce.get('bounce_tipo', 'unknown')})")
                if len(bounces) > 5:
                    print(f"     ... e mais {len(bounces)-5}")
                    
        except Exception as e:
            print(f"⚠️  Erro ao ler {log_path.name}: {e}")

def gerar_lista_limpa(arquivo_saida="listas/emails_validos_apos_bounce.csv"):
    """
    Gera uma lista limpa (sem hard bounces) para reenvio.
    """
    if not PASTA_LOGS.exists():
        print("📁 Nenhum log encontrado.")
        return
    
    # Encontra o log mais recente
    logs = list(PASTA_LOGS.glob("campanha_*.json"))
    if not logs:
        print("📁 Nenhuma campanha encontrada.")
        return
    
    logs.sort(reverse=True)
    log_recente = logs[0]
    
    with open(log_recente, 'r', encoding='utf-8') as f:
        log_data = json.load(f)
    
    # Identifica hard bounces
    hard_bounces = set()
    for envio in log_data.get('envios', []):
        if envio.get('bounce_detectado') and envio.get('bounce_tipo') == 'hard':
            hard_bounces.add(envio.get('email', ''))
    
    # E-mails que falharam permanentemente
    print(f"\n🔴 Hard bounces detectados: {len(hard_bounces)}")
    for email in hard_bounces:
        print(f"   - {email}")
    
    print(f"\n💡 Sugestão: Remova estes {len(hard_bounces)} e-mails da sua lista antes de reenviar.")

# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def main():
    print("📬 SISTEMA DE RASTREAMENTO DE BOUNCE")
    print("=" * 60)
    print("\nOpções disponíveis:")
    print("1. Processar bounces agora (verificar falhas de entrega)")
    print("2. Ver relatório de bounces das campanhas")
    print("3. Gerar lista limpa (remover hard bounces)")
    print("4. Sair")
    
    opcao = input("\nEscolha uma opção (1-4): ").strip()
    
    if opcao == "1":
        processar_bounces()
    elif opcao == "2":
        listar_bounces_por_campanha()
    elif opcao == "3":
        gerar_lista_limpa()
    else:
        print("Saindo...")

if __name__ == "__main__":
    main()