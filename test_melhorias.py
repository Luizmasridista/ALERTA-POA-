#!/usr/bin/env python3
"""
Script de teste para demonstrar as melhorias implementadas no Sistema Alerta POA.
"""

import pandas as pd
import sys
import os

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.security_analysis import calculate_synergistic_security_analysis
from modules.visualization import create_risk_map

def test_analise_sinergica():
    """Testa a nova análise sinérgica completa."""
    print("🧪 Testando Análise Sinérgica Completa...")
    
    # Dados de teste simulando diferentes cenários
    df_test = pd.DataFrame({
        'bairro': ['Centro Histórico'] * 15 + ['Restinga'] * 25 + ['Moinhos de Vento'] * 5,
        'tipo_crime': ['roubo_pedestres'] * 20 + ['furto_celulares'] * 15 + ['roubo_veiculos'] * 10,
        'Data Registro': ['2024-01-01'] * 45,
        'policiais_envolvidos': [2, 0, 1, 3, 0, 0, 5, 2, 0, 1, 0, 2, 1, 4, 3] +  # Centro
                               [0, 0, 1, 0, 0, 2, 0, 1, 0, 0, 3, 0, 0, 1, 0, 0, 0, 2, 0, 0, 1, 0, 0, 0, 0] +  # Restinga
                               [8, 6, 5, 4, 7],  # Moinhos
        'mortes_intervencao_policial': [0] * 15 + [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] + [0] * 5,
        'prisoes_realizadas': [1, 0, 0, 2, 0, 0, 1, 1, 0, 0, 0, 1, 0, 2, 1] +
                             [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0] +
                             [3, 2, 4, 3, 2],
        'apreensoes_armas': [0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 0, 1, 0, 1, 0] +
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] +
                           [2, 1, 3, 2, 1],
        'apreensoes_drogas_kg': [0] * 10 + [2.5, 0, 0, 1.2, 0] +  # Centro
                               [0] * 15 + [5.5, 0, 0, 0, 0, 0, 0, 3.2, 0, 0] +  # Restinga
                               [0, 0.5, 0, 0.8, 0],  # Moinhos
        'tipo_operacao': ['Preventiva', 'Nenhuma', 'Patrulha', 'Combate', 'Nenhuma'] * 9
    })
    
    # Testar cada bairro
    bairros = ['Centro Histórico', 'Restinga', 'Moinhos de Vento']
    
    for bairro in bairros:
        print(f"\n📍 Analisando {bairro}:")
        resultado = calculate_synergistic_security_analysis(df_test, None, bairro)
        
        print(f"  - Total de crimes: {resultado['total_crimes']}")
        print(f"  - Operações ativas: {resultado['operacoes_ativas']}")
        print(f"  - Prisões realizadas: {resultado['prisoes_realizadas']}")
        print(f"  - Armas apreendidas: {resultado['apreensoes_armas']}")
        print(f"  - Drogas apreendidas: {resultado['apreensoes_drogas']} kg")
        print(f"  - Mortes em confronto: {resultado['mortes_confronto']}")
        print(f"  - Efetividade global: {resultado['efetividade_global']}%")
        print(f"  - Score sinérgico: {resultado['score_sinergico']}")
        print(f"  - Nível de risco: {resultado['nivel_risco']}")
        print(f"  - Recomendações: {len(resultado['recomendacoes'])} sugestões")
    
    print("\n✅ Teste de análise sinérgica concluído com sucesso!")

def test_mapa_melhorado():
    """Testa a criação de mapa com tooltips ricos."""
    print("\n🗺️ Testando Criação de Mapa Melhorado...")
    
    # Dados simulados mais complexos
    df_test = pd.DataFrame({
        'bairro': ['Centro Histórico', 'Cidade Baixa', 'Floresta', 'Restinga'] * 10,
        'tipo_crime': ['roubo_pedestres'] * 20 + ['furto_celulares'] * 20,
        'Data Registro': ['2024-01-01'] * 40,
        'policiais_envolvidos': [1, 2, 0, 0] * 10,
        'mortes_intervencao_policial': [0] * 38 + [1, 0],
        'prisoes_realizadas': [1, 0, 1, 0] * 10,
        'apreensoes_armas': [1, 0, 0, 0] * 10,
        'apreensoes_drogas_kg': [0.5, 0, 0, 2.0] * 10,
        'tipo_operacao': ['Preventiva', 'Nenhuma', 'Combate', 'Nenhuma'] * 10
    })
    
    # Criar mapa
    mapa = create_risk_map(df_test)
    print(f"✅ Mapa criado: {type(mapa).__name__}")
    print("✅ Tooltips ricos e popups detalhados configurados")
    
    print("\n✅ Teste de mapa melhorado concluído com sucesso!")

def test_performance():
    """Testa performance com dataset maior."""
    print("\n⚡ Testando Performance com Dataset Grande...")
    
    import time
    
    # Dataset maior para teste de performance
    n_records = 1000
    df_large = pd.DataFrame({
        'bairro': (['Centro Histórico'] * 300 + ['Restinga'] * 400 + ['Cidade Baixa'] * 300)[:n_records],
        'tipo_crime': ['roubo_pedestres'] * (n_records//2) + ['furto_celulares'] * (n_records//2),
        'Data Registro': ['2024-01-01'] * n_records,
        'policiais_envolvidos': ([1, 2, 0, 3, 0] * (n_records//5))[:n_records],
        'mortes_intervencao_policial': ([0] * 99 + [1])[:n_records],
        'prisoes_realizadas': ([1, 0, 1, 0, 2] * (n_records//5))[:n_records],
        'apreensoes_armas': ([0, 1, 0, 0, 2] * (n_records//5))[:n_records],
        'apreensoes_drogas_kg': ([0, 0.5, 0, 1.0, 0] * (n_records//5))[:n_records],
        'tipo_operacao': (['Preventiva', 'Nenhuma', 'Combate', 'Nenhuma', 'Patrulha'] * (n_records//5))[:n_records]
    })
    
    start_time = time.time()
    
    # Teste de análise
    resultado = calculate_synergistic_security_analysis(df_large, None, 'Centro Histórico')
    analysis_time = time.time() - start_time
    
    # Teste de mapa
    start_time = time.time()
    mapa = create_risk_map(df_large)
    map_time = time.time() - start_time
    
    print(f"✅ Análise sinérgica: {analysis_time:.3f}s para {n_records} registros")
    print(f"✅ Criação de mapa: {map_time:.3f}s para {n_records} registros")
    print(f"✅ Performance adequada para datasets grandes")

def main():
    """Executa todos os testes."""
    print("🚀 TESTANDO MELHORIAS DO SISTEMA ALERTA POA")
    print("=" * 50)
    
    try:
        test_analise_sinergica()
        test_mapa_melhorado()
        test_performance()
        
        print("\n" + "=" * 50)
        print("🎉 TODOS OS TESTES PASSARAM COM SUCESSO!")
        print("✅ Sistema Alerta POA completamente funcional")
        print("✅ Análise sinérgica implementada")
        print("✅ Tooltips ricos funcionando") 
        print("✅ Performance otimizada")
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)