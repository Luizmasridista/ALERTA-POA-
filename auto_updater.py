#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Atualização Automática de Dados de Criminalidade
Alerta POA - Porto Alegre

Este módulo implementa um sistema automatizado para coleta e atualização
periódica de dados de criminalidade de múltiplas fontes oficiais.
"""

import schedule
import time
import logging
import os
from datetime import datetime, timedelta
from data_collector import CrimeDataCollector
import pandas as pd
import json

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_updater.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoUpdater:
    """
    Sistema automatizado de atualização de dados de criminalidade
    """
    
    def __init__(self):
        self.collector = CrimeDataCollector()
        self.last_update_file = 'last_update.json'
        
    def load_last_update(self):
        """
        Carrega informações da última atualização
        """
        try:
            with open(self.last_update_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'last_update': None, 'total_records': 0}
    
    def save_last_update(self, update_info):
        """
        Salva informações da atualização atual
        """
        with open(self.last_update_file, 'w') as f:
            json.dump(update_info, f, indent=2)
    
    def check_for_updates(self):
        """
        Verifica se há necessidade de atualização
        """
        last_update_info = self.load_last_update()
        last_update = last_update_info.get('last_update')
        
        if last_update is None:
            logger.info("Primeira execução - coletando dados completos")
            return True
        
        last_update_date = datetime.fromisoformat(last_update)
        days_since_update = (datetime.now() - last_update_date).days
        
        # Atualizar se passou mais de 7 dias
        if days_since_update >= 7:
            logger.info(f"Última atualização há {days_since_update} dias - atualizando")
            return True
        
        logger.info(f"Dados atualizados há {days_since_update} dias - não é necessário atualizar")
        return False
    
    def collect_incremental_data(self):
        """
        Coleta dados incrementais desde a última atualização
        """
        logger.info("Iniciando coleta incremental de dados")
        
        try:
            # Coletar dados do ano atual
            current_year = datetime.now().year
            
            # Se estivermos no início do ano, coletar também o ano anterior
            years_to_collect = [current_year]
            if datetime.now().month <= 3:  # Primeiros 3 meses do ano
                years_to_collect.append(current_year - 1)
            
            all_data = []
            
            for year in years_to_collect:
                logger.info(f"Coletando dados para {year}")
                year_data = self.collector.collect_historical_data(year, year)
                all_data.append(year_data)
            
            # Combinar todos os dados
            if all_data:
                combined_data = pd.concat(all_data, ignore_index=True)
                
                # Remover duplicatas baseado em data, hora, tipo de crime e bairro
                combined_data = combined_data.drop_duplicates(
                    subset=['data_registro', 'hora', 'tipo_crime', 'bairro']
                )
                
                # Salvar dados atualizados
                filename = self.collector.save_data(combined_data)
                
                # Atualizar informações da última atualização
                update_info = {
                    'last_update': datetime.now().isoformat(),
                    'total_records': len(combined_data),
                    'filename': filename,
                    'years_collected': years_to_collect
                }
                
                self.save_last_update(update_info)
                
                logger.info(f"Atualização concluída: {len(combined_data)} registros salvos em {filename}")
                return True
            
        except Exception as e:
            logger.error(f"Erro durante coleta incremental: {str(e)}")
            return False
    
    def update_data(self):
        """
        Executa atualização completa dos dados
        """
        logger.info("=== INICIANDO ATUALIZAÇÃO AUTOMÁTICA ===")
        
        if not self.check_for_updates():
            return
        
        success = self.collect_incremental_data()
        
        if success:
            logger.info("=== ATUALIZAÇÃO CONCLUÍDA COM SUCESSO ===")
            self.generate_update_report()
        else:
            logger.error("=== FALHA NA ATUALIZAÇÃO ===")
    
    def generate_update_report(self):
        """
        Gera relatório da atualização
        """
        try:
            last_update_info = self.load_last_update()
            
            report = f"""
# RELATÓRIO DE ATUALIZAÇÃO AUTOMÁTICA
Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

## INFORMAÇÕES DA ATUALIZAÇÃO
- Última atualização: {last_update_info.get('last_update', 'N/A')}
- Total de registros: {last_update_info.get('total_records', 0):,}
- Arquivo gerado: {last_update_info.get('filename', 'N/A')}
- Anos coletados: {', '.join(map(str, last_update_info.get('years_collected', [])))}

## STATUS
✅ Atualização concluída com sucesso
✅ Dados disponíveis para o sistema Alerta POA
✅ Próxima atualização programada para 7 dias

## PRÓXIMOS PASSOS
1. Os novos dados serão automaticamente carregados pelo sistema
2. Análises e visualizações serão atualizadas
3. Alertas de segurança refletirão os dados mais recentes
"""
            
            # Salvar relatório
            report_filename = f"relatorio_atualizacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"Relatório de atualização salvo: {report_filename}")
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {str(e)}")
    
    def run_scheduler(self):
        """
        Executa o agendador de tarefas
        """
        logger.info("Iniciando sistema de atualização automática")
        
        # Agendar atualização semanal (toda segunda-feira às 02:00)
        schedule.every().monday.at("02:00").do(self.update_data)
        
        # Agendar verificação diária (todos os dias às 06:00)
        schedule.every().day.at("06:00").do(self.check_for_updates)
        
        logger.info("Agendamentos configurados:")
        logger.info("- Atualização semanal: Segunda-feira às 02:00")
        logger.info("- Verificação diária: Todos os dias às 06:00")
        
        # Executar uma atualização inicial se necessário
        self.update_data()
        
        # Loop principal do agendador
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar a cada minuto

def main():
    """
    Função principal para execução do auto-updater
    """
    updater = AutoUpdater()
    
    # Verificar argumentos da linha de comando
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'update':
            # Executar atualização manual
            updater.update_data()
        elif command == 'check':
            # Verificar se precisa atualizar
            needs_update = updater.check_for_updates()
            print(f"Necessita atualização: {'Sim' if needs_update else 'Não'}")
        elif command == 'schedule':
            # Executar agendador
            updater.run_scheduler()
        else:
            print("Comandos disponíveis:")
            print("  update   - Executar atualização manual")
            print("  check    - Verificar se precisa atualizar")
            print("  schedule - Executar agendador automático")
    else:
        # Executar atualização manual por padrão
        updater.update_data()

if __name__ == "__main__":
    main()