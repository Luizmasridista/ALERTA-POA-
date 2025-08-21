#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Inicialização do Sistema Alerta POA
Porto Alegre - Sistema Avançado de Segurança Pública

Este script facilita a inicialização e gerenciamento do sistema completo.
"""

import os
import sys
import json
import subprocess
import argparse
from datetime import datetime

def load_config():
    """
    Carrega configurações do sistema
    """
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Arquivo de configuração não encontrado!")
        return None

def check_dependencies():
    """
    Verifica se todas as dependências estão instaladas
    """
    print("🔍 Verificando dependências...")
    
    try:
        import streamlit
        import pandas
        import plotly
        import folium
        import schedule
        print("✅ Todas as dependências estão instaladas")
        return True
    except ImportError as e:
        print(f"❌ Dependência faltando: {e}")
        print("💡 Execute: pip install -r requirements.txt")
        return False

def check_data_files():
    """
    Verifica se os arquivos de dados existem
    """
    print("📁 Verificando arquivos de dados...")
    
    required_files = [
        'data/bairros_poa.geojson',
    ]
    
    optional_files = [
        'config.json',
        'relatorio_indicadores_criminais.json'
    ]
    
    # Verificar arquivos obrigatórios
    missing_required = []
    for file in required_files:
        if not os.path.exists(file):
            missing_required.append(file)
    
    if missing_required:
        print(f"❌ Arquivos obrigatórios faltando: {', '.join(missing_required)}")
        return False
    
    # Verificar arquivos opcionais
    missing_optional = []
    for file in optional_files:
        if not os.path.exists(file):
            missing_optional.append(file)
    
    if missing_optional:
        print(f"⚠️ Arquivos opcionais faltando: {', '.join(missing_optional)}")
        print("💡 O sistema funcionará com dados simulados")
    
    # Verificar se há dados coletados
    import glob
    
    # Verificar arquivos principais primeiro
    main_data_files = [
        'data/dados_criminalidade_poa.csv',
        'data/dados_criminalidade_operacoes_integrado.csv',
        'data/indice_seguranca_bairros.csv'
    ]
    
    found_files = []
    for file in main_data_files:
        if os.path.exists(file):
            found_files.append(file)
    
    if found_files:
        print(f"✅ Dados coletados encontrados: {', '.join(found_files)}")
    else:
        # Fallback para arquivos com timestamp
        data_files = glob.glob('data/dados_criminalidade_poa_*.csv')
        if data_files:
            latest_file = max(data_files, key=os.path.getctime)
            print(f"✅ Dados coletados encontrados: {latest_file}")
        else:
            print("⚠️ Nenhum dado coletado encontrado")
            print("💡 Execute: python scripts/data_collector_unified.py")
    
    return True

def start_streamlit(port=8501):
    """
    Inicia o aplicativo Streamlit em uma porta específica
    """
    print(f"🚀 Iniciando aplicativo Streamlit na porta {port}...")
    
    try:
        # Comando para iniciar o Streamlit
        cmd = [sys.executable, '-m', 'streamlit', 'run', 'alerta_poa_final.py', '--server.port', str(port)]
        
        print(f"📱 Aplicativo será aberto em: http://localhost:{port}")
        print(f"🌐 Acesso na rede: http://192.168.100.13:{port}")
        print("\n⏹️ Para parar o sistema, pressione Ctrl+C")
        
        # Executar comando
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Sistema interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar Streamlit: {e}")

def collect_data():
    """
    Executa coleta de dados
    """
    print("📊 Iniciando coleta de dados...")
    
    try:
        result = subprocess.run([sys.executable, 'data_collector.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Coleta de dados concluída com sucesso")
            print(result.stdout)
        else:
            print("❌ Erro na coleta de dados")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Erro ao executar coleta: {e}")

def start_auto_updater():
    """
    Inicia o sistema de atualização automática
    """
    print("🔄 Iniciando sistema de atualização automática...")
    
    try:
        cmd = [sys.executable, 'auto_updater.py', 'schedule']
        print("⏰ Sistema de atualização automática ativo")
        print("📅 Atualizações semanais programadas")
        print("\n⏹️ Para parar, pressione Ctrl+C")
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Sistema de atualização interrompido")
    except Exception as e:
        print(f"❌ Erro ao iniciar auto-updater: {e}")

def show_system_status():
    """
    Mostra status do sistema
    """
    config = load_config()
    if not config:
        return
    
    print("\n" + "="*50)
    print(f"🚨 {config['sistema']['nome']} v{config['sistema']['versao']}")
    print(f"📝 {config['sistema']['descricao']}")
    print("="*50)
    
    # Status das dependências
    deps_ok = check_dependencies()
    
    # Status dos arquivos
    files_ok = check_data_files()
    
    # Verificar dados coletados
    import glob
    data_files = glob.glob('dados_criminalidade_poa_*.csv')
    
    print("\n📊 RESUMO DO SISTEMA:")
    print(f"✅ Dependências: {'OK' if deps_ok else 'ERRO'}")
    print(f"✅ Arquivos: {'OK' if files_ok else 'ERRO'}")
    print(f"✅ Dados coletados: {len(data_files)} arquivo(s)")
    
    if data_files:
        latest_file = max(data_files, key=os.path.getctime)
        mod_time = datetime.fromtimestamp(os.path.getmtime(latest_file))
        print(f"📅 Última coleta: {mod_time.strftime('%d/%m/%Y %H:%M')}")
    
    print("\n🔗 COMANDOS DISPONÍVEIS:")
    print("  python start_system.py run        - Iniciar aplicativo")
    print("  python start_system.py collect    - Coletar dados")
    print("  python start_system.py update     - Atualização automática")
    print("  python start_system.py status     - Ver status do sistema")
    print("  python start_system.py install    - Instalar dependências")

def install_dependencies():
    """
    Instala dependências do sistema
    """
    print("📦 Instalando dependências...")
    
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependências instaladas com sucesso")
        else:
            print("❌ Erro na instalação das dependências")
            print(result.stderr)
            
    except Exception as e:
        print(f"❌ Erro ao instalar dependências: {e}")

def main():
    """
    Função principal
    """
    parser = argparse.ArgumentParser(
        description='Sistema Alerta POA - Gerenciador'
    )
    
    parser.add_argument(
        'command',
        choices=['run', 'collect', 'update', 'status', 'install'],
        nargs='?',
        default='status',
        help='Comando a executar'
    )
    
    args = parser.parse_args()
    
    if args.command == 'run':
        if check_dependencies() and check_data_files():
            start_streamlit(port=8501)  # Default port
        else:
            print("❌ Sistema não pode ser iniciado devido a problemas")
            
    elif args.command == 'collect':
        if check_dependencies():
            collect_data()
        else:
            print("❌ Instale as dependências primeiro")
            
    elif args.command == 'update':
        if check_dependencies():
            start_auto_updater()
        else:
            print("❌ Instale as dependências primeiro")
            
    elif args.command == 'status':
        show_system_status()
        
    elif args.command == 'install':
        install_dependencies()

if __name__ == "__main__":
    main()