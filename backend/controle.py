#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Sistema de Controle para Campanha de Email
Permite pausar, continuar, cancelar e verificar status da campanha
"""

import os
import json
from pathlib import Path
from datetime import datetime
import sys

# ============================================================
# CONFIGURAÇÕES
# ============================================================
PASTA_RAIZ = Path(__file__).parent
PASTA_CHECKPOINTS = PASTA_RAIZ / "checkpoints"
PASTA_LOGS = PASTA_RAIZ / "logs"

# Arquivos de controle
ARQUIVO_PAUSA = PASTA_CHECKPOINTS / "pausar.txt"
ARQUIVO_CANCELAMENTO = PASTA_CHECKPOINTS / "cancelar.txt"
ARQUIVO_CHECKPOINT = PASTA_CHECKPOINTS / "campanha_atual.json"

# ============================================================
# FUNÇÕES DE VERIFICAÇÃO
# ============================================================

def verificar_pasta_checkpoints():
    """Verifica se a pasta checkpoints existe"""
    if not PASTA_CHECKPOINTS.exists():
        print(f"⚠️  Pasta checkpoints não encontrada: {PASTA_CHECKPOINTS}")
        resposta = input("Deseja criar a pasta? (s/N): ").lower()
        if resposta == 's':
            PASTA_CHECKPOINTS.mkdir(parents=True)
            print(f"✅ Pasta criada: {PASTA_CHECKPOINTS}")
            return True
        else:
            print("❌ Não é possível continuar sem a pasta checkpoints.")
            return False
    return True

def carregar_checkpoint():
    """Carrega o checkpoint atual se existir"""
    if ARQUIVO_CHECKPOINT.exists():
        with open(ARQUIVO_CHECKPOINT, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# ============================================================
# FUNÇÕES DE CONTROLE
# ============================================================

def pausar_campanha():
    """Pausa a campanha atual"""
    if not verificar_pasta_checkpoints():
        return
    
    with open(ARQUIVO_PAUSA, "w", encoding="utf-8") as f:
        f.write("sim")
    
    print("\n" + "=" * 50)
    print("✅ CAMPANHA PAUSADA!")
    print("=" * 50)
    print(f"📁 Arquivo criado: {ARQUIVO_PAUSA}")
    print("\n📌 Para CONTINUAR a campanha:")
    print("   - Execute este script novamente e escolha 'Continuar'")
    print("   - OU delete manualmente o arquivo:")
    print(f"     del {ARQUIVO_PAUSA}")
    print("=" * 50)

def continuar_campanha():
    """Continua a campanha pausada"""
    if not verificar_pasta_checkpoints():
        return
    
    if ARQUIVO_PAUSA.exists():
        ARQUIVO_PAUSA.unlink()
        print("\n" + "=" * 50)
        print("✅ CAMPANHA CONTINUADA!")
        print("=" * 50)
        print("O script principal irá retomar os envios automaticamente.")
        print("=" * 50)
    else:
        print("\n⚠️  Nenhuma campanha pausada encontrada.")
        print("   O arquivo de pausa não existe.")

def cancelar_campanha():
    """Cancela a campanha atual"""
    if not verificar_pasta_checkpoints():
        return
    
    print("\n⚠️  ATENÇÃO: Isso irá cancelar a campanha atual!")
    print("   O checkpoint será salvo, mas a campanha não continuará.")
    resposta = input("\nTem certeza que deseja CANCELAR? (s/N): ").lower()
    
    if resposta == 's':
        with open(ARQUIVO_CANCELAMENTO, "w", encoding="utf-8") as f:
            f.write("sim")
        
        print("\n" + "=" * 50)
        print("🛑 CAMPANHA CANCELADA!")
        print("=" * 50)
        print(f"📁 Arquivo criado: {ARQUIVO_CANCELAMENTO}")
        print("\n📌 O script principal irá parar no próximo ciclo.")
        print("   Para iniciar uma nova campanha, delete o arquivo:")
        print(f"     del {ARQUIVO_CANCELAMENTO}")
        print("=" * 50)
    else:
        print("❌ Cancelamento abortado.")

def verificar_status():
    """Verifica o status atual da campanha"""
    print("\n" + "=" * 60)
    print("📊 STATUS DA CAMPANHA")
    print("=" * 60)
    
    # Verifica arquivos de controle
    print("\n🔘 ARQUIVOS DE CONTROLE:")
    print(f"   Pausa ativa: {'✅ SIM' if ARQUIVO_PAUSA.exists() else '❌ NÃO'}")
    print(f"   Cancelamento ativo: {'✅ SIM' if ARQUIVO_CANCELAMENTO.exists() else '❌ NÃO'}")
    
    # Verifica checkpoint
    checkpoint = carregar_checkpoint()
    if checkpoint:
        print("\n📋 CHECKPOINT DA CAMPANHA:")
        print(f"   Data do último checkpoint: {checkpoint.get('data_campanha', 'N/A')}")
        print(f"   Status: {checkpoint.get('status', 'N/A')}")
        print(f"   Progresso: {checkpoint.get('ultimo_indice', 0)} / {checkpoint.get('total_contatos', 0)}")
        print(f"   Enviados com sucesso: {checkpoint.get('enviados_com_sucesso', 0)}")
        
        falhas = checkpoint.get('falhas', [])
        print(f"   Falhas: {len(falhas) if isinstance(falhas, list) else falhas}")
        print(f"   Remetente: {checkpoint.get('remetente', 'N/A')}")
        print(f"   Assunto: {checkpoint.get('assunto', 'N/A')[:60]}...")
        
        # Calcula percentual
        total = checkpoint.get('total_contatos', 0)
        atual = checkpoint.get('ultimo_indice', 0)
        if total > 0:
            percentual = (atual / total) * 100
            print(f"   Percentual completo: {percentual:.1f}%")
    else:
        print("\n⚠️  Nenhum checkpoint encontrado.")
        print("   Nenhuma campanha em andamento ou concluída.")
    
    # Verifica logs recentes
    print("\n📁 LOGS RECENTES:")
    if PASTA_LOGS.exists():
        logs = list(PASTA_LOGS.glob("campanha_*.json"))
        logs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if logs:
            for log in logs[:5]:  # Mostra os 5 mais recentes
                data_mod = datetime.fromtimestamp(log.stat().st_mtime)
                tamanho = log.stat().st_size
                print(f"   📄 {log.name} - {data_mod.strftime('%d/%m/%Y %H:%M')} - {tamanho} bytes")
        else:
            print("   Nenhum log encontrado.")
    else:
        print("   Pasta logs não existe.")
    
    print("=" * 60)

def resetar_campanha():
    """Reseta a campanha atual (limpa checkpoint)"""
    print("\n⚠️  ATENÇÃO: Isso irá resetar completamente a campanha atual!")
    print("   Você perderá o progresso salvo.")
    resposta = input("\nTem certeza? (s/N): ").lower()
    
    if resposta == 's':
        # Remove arquivos de controle
        if ARQUIVO_PAUSA.exists():
            ARQUIVO_PAUSA.unlink()
            print("✅ Arquivo de pausa removido")
        
        if ARQUIVO_CANCELAMENTO.exists():
            ARQUIVO_CANCELAMENTO.unlink()
            print("✅ Arquivo de cancelamento removido")
        
        if ARQUIVO_CHECKPOINT.exists():
            ARQUIVO_CHECKPOINT.unlink()
            print("✅ Checkpoint removido")
        
        print("\n" + "=" * 50)
        print("✅ CAMPANHA RESETADA COM SUCESSO!")
        print("=" * 50)
        print("Você pode iniciar uma nova campanha normalmente.")
        print("=" * 50)
    else:
        print("❌ Reset cancelado.")

def mostrar_ajuda():
    """Mostra ajuda sobre os comandos"""
    print("\n" + "=" * 60)
    print("📖 AJUDA - SISTEMA DE CONTROLE")
    print("=" * 60)
    print("""
🔘 ARQUIVOS DE CONTROLE MANUAL:

Você também pode controlar a campanha manualmente criando arquivos:

1. PAUSAR a campanha:
   echo sim > checkpoints\\pausar.txt

2. CONTINUAR a campanha:
   del checkpoints\\pausar.txt

3. CANCELAR a campanha:
   echo sim > checkpoints\\cancelar.txt

📁 LOCALIZAÇÃO DOS ARQUIVOS:
   checkpoints/pausar.txt      - Arquivo de pausa
   checkpoints/cancelar.txt    - Arquivo de cancelamento  
   checkpoints/campanha_atual.json - Checkpoint automático

💡 DICAS:
   - O script principal verifica esses arquivos a cada envio
   - Não edite o arquivo campanha_atual.json manualmente
   - Para uma nova campanha, use a opção "Resetar" deste menu
   
🔗 COMANDOS RÁPIDOS (PowerShell):
   # Verificar status
   if (Test-Path checkpoints\\pausar.txt) { "PAUSADO" } else { "ATIVO" }
   
   # Pausar
   "sim" > checkpoints\\pausar.txt
   
   # Continuar
   del checkpoints\\pausar.txt
    """)
    print("=" * 60)

# ============================================================
# MENU PRINCIPAL
# ============================================================

def mostrar_menu():
    """Mostra o menu principal"""
    print("\n" + "=" * 50)
    print("🎮 NEWLEADS - CONTROLE DA CAMPANHA")
    print("=" * 50)
    print("""
  1. ⏸️  Pausar campanha
  2. ▶️  Continuar campanha
  3. 🛑 Cancelar campanha
  4. 📊 Verificar status
  5. 🔄 Resetar campanha
  6. 📖 Ajuda
  7. 🚪 Sair
""")
    print("=" * 50)

def main():
    """Função principal"""
    os.system('cls' if os.name == 'nt' else 'clear')  # Limpa a tela
    
    print("=" * 60)
    print("🎮 NEWLEADS - SISTEMA DE CONTROLE")
    print("=" * 60)
    print(f"📁 Pasta do projeto: {PASTA_RAIZ}")
    
    # Garante que a pasta checkpoints existe
    if not PASTA_CHECKPOINTS.exists():
        print("\n⚠️  Pasta checkpoints não encontrada. Criando...")
        PASTA_CHECKPOINTS.mkdir(parents=True)
        print(f"✅ Pasta criada: {PASTA_CHECKPOINTS}")
    
    while True:
        mostrar_menu()
        opcao = input("👉 Escolha uma opção (1-7): ").strip()
        
        if opcao == "1":
            pausar_campanha()
        elif opcao == "2":
            continuar_campanha()
        elif opcao == "3":
            cancelar_campanha()
        elif opcao == "4":
            verificar_status()
        elif opcao == "5":
            resetar_campanha()
        elif opcao == "6":
            mostrar_ajuda()
        elif opcao == "7":
            print("\n👋 Saindo do sistema de controle...")
            break
        else:
            print("\n❌ Opção inválida! Escolha de 1 a 7.")
        
        if opcao != "7":
            input("\n🔄 Pressione Enter para continuar...")
            os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrompido pelo usuário. Saindo...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)