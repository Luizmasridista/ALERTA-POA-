"""Módulo para análises de segurança e cálculos de risco do sistema Alerta POA.

Este módulo contém:
- Cálculos de score de risco
- Análises sinérgicas de segurança
- Modelos preditivos
- Geração de alertas
"""

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')


def calculate_risk_score(df, bairro):
    """Calcula score de risco para um bairro específico.
    
    Args:
        df (pd.DataFrame): DataFrame com dados de criminalidade
        bairro (str): Nome do bairro
        
    Returns:
        dict: Dicionário com informações de risco do bairro
    """
    if df.empty:
        return {
            'bairro': bairro,
            'total_crimes': 0,
            'score_risco': 0,
            'nivel_risco': 'Baixo',
            'crimes_por_tipo': {},
            'tendencia': 'Estável'
        }
    
    # Filtrar dados do bairro - normalizar para comparação consistente
    df_bairro = df[df['bairro'].str.upper().str.strip() == bairro.upper().strip()]
    
    if df_bairro.empty:
        return {
            'bairro': bairro,
            'total_crimes': 0,
            'score_risco': 0,
            'nivel_risco': 'Baixo',
            'crimes_por_tipo': {},
            'tendencia': 'Estável'
        }
    
    # Calcular métricas básicas
    total_crimes = len(df_bairro)
    crimes_por_tipo = df_bairro['tipo_crime'].value_counts().to_dict()
    
    # Calcular score de risco baseado em diferentes fatores
    score_base = total_crimes
    
    # Fator de gravidade por tipo de crime
    pesos_crimes = {
        'ROUBO': 3.0,
        'FURTO': 2.0,
        'LESÃO CORPORAL': 2.5,
        'HOMICÍDIO': 5.0,
        'TRÁFICO DE DROGAS': 3.5,
        'AMEAÇA': 1.5,
        'VIOLÊNCIA DOMÉSTICA': 2.8
    }
    
    score_ponderado = 0
    for tipo_crime, quantidade in crimes_por_tipo.items():
        peso = pesos_crimes.get(tipo_crime.upper(), 1.0)
        score_ponderado += quantidade * peso
    
    # Fator temporal (crimes recentes têm maior peso)
    if 'Data Registro' in df_bairro.columns:
        df_bairro_temp = df_bairro.copy()
        df_bairro_temp['Data Registro'] = pd.to_datetime(df_bairro_temp['Data Registro'])
        data_mais_recente = df_bairro_temp['Data Registro'].max()
        
        # Crimes dos últimos 30 dias têm peso maior
        crimes_recentes = df_bairro_temp[
            df_bairro_temp['Data Registro'] >= (data_mais_recente - pd.Timedelta(days=30))
        ]
        fator_temporal = len(crimes_recentes) * 1.5
        score_ponderado += fator_temporal
    
    # Normalizar score (0-100)
    score_risco = min(100, (score_ponderado / max(1, total_crimes)) * 20)
    
    # Determinar nível de risco
    if score_risco >= 80:
        nivel_risco = 'Crítico'
    elif score_risco >= 60:
        nivel_risco = 'Alto'
    elif score_risco >= 40:
        nivel_risco = 'Médio'
    elif score_risco >= 20:
        nivel_risco = 'Baixo'
    else:
        nivel_risco = 'Muito Baixo'
    
    # Calcular tendência
    tendencia = 'Estável'
    if 'Data Registro' in df_bairro.columns and len(df_bairro) > 10:
        df_bairro_temp = df_bairro.copy()
        df_bairro_temp['Data Registro'] = pd.to_datetime(df_bairro_temp['Data Registro'])
        df_bairro_temp = df_bairro_temp.sort_values('Data Registro')
        
        # Comparar últimos 30 dias com 30 dias anteriores
        data_mais_recente = df_bairro_temp['Data Registro'].max()
        crimes_ultimos_30 = len(df_bairro_temp[
            df_bairro_temp['Data Registro'] >= (data_mais_recente - pd.Timedelta(days=30))
        ])
        crimes_30_anteriores = len(df_bairro_temp[
            (df_bairro_temp['Data Registro'] >= (data_mais_recente - pd.Timedelta(days=60))) &
            (df_bairro_temp['Data Registro'] < (data_mais_recente - pd.Timedelta(days=30)))
        ])
        
        if crimes_30_anteriores > 0:
            variacao = (crimes_ultimos_30 - crimes_30_anteriores) / crimes_30_anteriores
            if variacao > 0.2:
                tendencia = 'Crescente'
            elif variacao < -0.2:
                tendencia = 'Decrescente'
    
    return {
        'bairro': bairro,
        'total_crimes': total_crimes,
        'score_risco': round(score_risco, 2),
        'nivel_risco': nivel_risco,
        'crimes_por_tipo': crimes_por_tipo,
        'tendencia': tendencia
    }


def calculate_enhanced_risk_score_with_police_ops(df_crimes, df_operacoes, bairro):
    """Calcula score de risco aprimorado considerando operações policiais.
    
    Args:
        df_crimes (pd.DataFrame): DataFrame com dados de crimes
        df_operacoes (pd.DataFrame): DataFrame com dados de operações policiais
        bairro (str): Nome do bairro
        
    Returns:
        dict: Dicionário com análise de risco aprimorada
    """
    # Calcular score básico de crimes
    risk_data = calculate_risk_score(df_crimes, bairro)
    
    # Adicionar dados de operações policiais se disponíveis
    if not df_operacoes.empty:
        ops_bairro = df_operacoes[df_operacoes['bairro'].str.upper() == bairro.upper()]
        total_operacoes = len(ops_bairro)
        
        # Fator de redução baseado em operações policiais
        fator_reducao = min(0.5, total_operacoes * 0.05)  # Máximo 50% de redução
        score_ajustado = risk_data['score_risco'] * (1 - fator_reducao)
        
        # Atualizar dados
        risk_data['total_operacoes'] = total_operacoes
        risk_data['score_risco_ajustado'] = round(score_ajustado, 2)
        risk_data['fator_reducao'] = round(fator_reducao * 100, 1)
        
        # Recalcular nível de risco com score ajustado
        if score_ajustado >= 80:
            risk_data['nivel_risco_ajustado'] = 'Crítico'
        elif score_ajustado >= 60:
            risk_data['nivel_risco_ajustado'] = 'Alto'
        elif score_ajustado >= 40:
            risk_data['nivel_risco_ajustado'] = 'Médio'
        elif score_ajustado >= 20:
            risk_data['nivel_risco_ajustado'] = 'Baixo'
        else:
            risk_data['nivel_risco_ajustado'] = 'Muito Baixo'
    
    return risk_data


def calculate_synergistic_security_analysis(df_crimes, df_operacoes, bairro):
    """Realiza análise sinérgica detalhada de segurança usando TODOS os dados integrados.
    
    Args:
        df_crimes (pd.DataFrame): DataFrame com dados de crimes (dados integrados)
        df_operacoes (pd.DataFrame): DataFrame com dados de operações policiais (não usado, dados já integrados)
        bairro (str): Nome do bairro
        
    Returns:
        dict: Análise sinérgica completa
    """
    # Usar dados integrados do df_crimes que já contém informações de operações
    crimes_bairro = df_crimes[df_crimes['bairro'].str.upper().str.strip() == bairro.upper().strip()] if not df_crimes.empty else pd.DataFrame()
    
    # Filtrar operações para o bairro específico
    operacoes_bairro = df_operacoes[df_operacoes['bairro'].str.upper().str.strip() == bairro.upper().strip()] if df_operacoes is not None and not df_operacoes.empty else pd.DataFrame()
    
    total_crimes = len(crimes_bairro)
    
    # Extrair TODOS os dados de operações dos dados integrados
    if not crimes_bairro.empty:
        total_operacoes = crimes_bairro['policiais_envolvidos'].sum() if 'policiais_envolvidos' in crimes_bairro.columns else 0
        mortes_confronto = crimes_bairro['mortes_intervencao_policial'].sum() if 'mortes_intervencao_policial' in crimes_bairro.columns else 0
        prisoes_realizadas = crimes_bairro['prisoes_realizadas'].sum() if 'prisoes_realizadas' in crimes_bairro.columns else 0
        apreensoes_armas = crimes_bairro['apreensoes_armas'].sum() if 'apreensoes_armas' in crimes_bairro.columns else 0
        apreensoes_drogas = crimes_bairro['apreensoes_drogas_kg'].sum() if 'apreensoes_drogas_kg' in crimes_bairro.columns else 0
        
        # Analisar tipos de operações
        operacoes_tipos = crimes_bairro['tipo_operacao'].value_counts().to_dict() if 'tipo_operacao' in crimes_bairro.columns else {}
        operacoes_ativas = len(crimes_bairro[crimes_bairro['tipo_operacao'] != 'Nenhuma']) if 'tipo_operacao' in crimes_bairro.columns else 0
    else:
        total_operacoes = 0
        mortes_confronto = 0
        prisoes_realizadas = 0
        apreensoes_armas = 0
        apreensoes_drogas = 0
        operacoes_tipos = {}
        operacoes_ativas = 0
    
    # Análise temporal
    analise_temporal = {
        'crimes_ultimo_mes': 0,
        'operacoes_ultimo_mes': 0,
        'tendencia_crimes': 'Estável',
        'efetividade_operacoes': 'Não avaliável'
    }
    
    if not crimes_bairro.empty and 'Data Registro' in crimes_bairro.columns:
        crimes_bairro_temp = crimes_bairro.copy()
        crimes_bairro_temp['Data Registro'] = pd.to_datetime(crimes_bairro_temp['Data Registro'])
        data_limite = crimes_bairro_temp['Data Registro'].max() - pd.Timedelta(days=30)
        analise_temporal['crimes_ultimo_mes'] = len(crimes_bairro_temp[crimes_bairro_temp['Data Registro'] >= data_limite])
    
    if not operacoes_bairro.empty and 'data_operacao' in operacoes_bairro.columns:
        operacoes_bairro_temp = operacoes_bairro.copy()
        operacoes_bairro_temp['data_operacao'] = pd.to_datetime(operacoes_bairro_temp['data_operacao'])
        data_limite = operacoes_bairro_temp['data_operacao'].max() - pd.Timedelta(days=30)
        analise_temporal['operacoes_ultimo_mes'] = len(operacoes_bairro_temp[operacoes_bairro_temp['data_operacao'] >= data_limite])
    
    # Cálculo de efetividade
    if total_operacoes > 0 and total_crimes > 0:
        ratio_operacao_crime = total_operacoes / total_crimes
        if ratio_operacao_crime >= 0.3:
            analise_temporal['efetividade_operacoes'] = 'Alta'
        elif ratio_operacao_crime >= 0.15:
            analise_temporal['efetividade_operacoes'] = 'Média'
        else:
            analise_temporal['efetividade_operacoes'] = 'Baixa'
    
    # Análise de padrões
    padroes_crimes = {}
    if not crimes_bairro.empty:
        if 'tipo_crime' in crimes_bairro.columns:
            padroes_crimes['tipos_predominantes'] = crimes_bairro['tipo_crime'].value_counts().head(3).to_dict()
        
        if 'periodo_dia' in crimes_bairro.columns:
            padroes_crimes['periodos_criticos'] = crimes_bairro['periodo_dia'].value_counts().to_dict()
    
    # Score sinérgico COMPLETO considerando TODOS os indicadores
    score_base = total_crimes
    
    # Penalidades por indicadores negativos (com pesos ajustados)
    penalidades = 0
    
    # Mortes em confronto - penálidade crítica
    if mortes_confronto > 0:
        penalidades += mortes_confronto * 75  # Peso aumentado para refletir gravidade
    
    # Fatores positivos (reduções no score de risco)
    beneficios = 0
    
    # Prisões realizadas - indicador de efetividade policial
    if prisoes_realizadas > 0:
        beneficios += prisoes_realizadas * 3  # Cada prisão reduz o risco
    
    # Apreensões de armas - redução significativa do risco
    if apreensoes_armas > 0:
        beneficios += apreensoes_armas * 8  # Armas apreendidas reduzem muito o risco
    
    # Apreensões de drogas - indicador de combate ao tráfico
    if apreensoes_drogas > 0:
        beneficios += apreensoes_drogas * 5  # Por kg apreendido
    
    # Operações ativas - fator positivo
    if operacoes_ativas > 0:
        beneficios += operacoes_ativas * 2  # Operações ativas reduzem risco
    
    # Score final considerando todos os fatores
    score_bruto = score_base + penalidades - beneficios
    
    # Fator de redução adicional baseado em operações policiais
    fator_operacoes = 1.0
    if total_operacoes > 0 and total_crimes > 0:
        efetividade = min(0.5, total_operacoes / total_crimes)  # Max 50% de redução
        fator_operacoes = 1 - efetividade
    
    score_ajustado = max(0, score_bruto * fator_operacoes)  # Não permitir score negativo
    
    # Normalizar para escala apropriada
    score_final = score_ajustado
    
    # Calcular efetividade global das operações
    efetividade_global = 0
    if total_crimes > 0:
        taxa_prisao = prisoes_realizadas / total_crimes
        taxa_apreensao = (apreensoes_armas + apreensoes_drogas) / total_crimes
        taxa_operacao = operacoes_ativas / total_crimes
        efetividade_global = (taxa_prisao * 0.4 + taxa_apreensao * 0.3 + taxa_operacao * 0.3) * 100
    
    # Determinar nível de risco usando escala mais refinada
    if score_final >= 120:
        nivel_risco = '⚫ Crítico'
        cor_risco = '#2B0000'
    elif score_final >= 80:
        nivel_risco = '🔴 Muito Alto'
        cor_risco = '#8B0000'
    elif score_final >= 50:
        nivel_risco = '🟠 Alto'
        cor_risco = '#FF0000'
    elif score_final >= 30:
        nivel_risco = '🟡 Médio-Alto'
        cor_risco = '#FF4500'
    elif score_final >= 15:
        nivel_risco = '🟡 Médio'
        cor_risco = '#FFA500'
    elif score_final >= 8:
        nivel_risco = '🟢 Baixo-Médio'
        cor_risco = '#FFD700'
    elif score_final >= 3:
        nivel_risco = '🟢 Baixo'
        cor_risco = '#FFFF00'
    else:
        nivel_risco = '🟢 Muito Baixo'
        cor_risco = '#90EE90'
    
    # Recomendações baseadas em análise completa
    recomendacoes = []
    
    # Recomendações por nível de risco
    if '⚫' in nivel_risco or '🔴' in nivel_risco:  # Crítico/Muito Alto
        recomendacoes.extend([
            "URGENT: Aumentar patrulhamento imediatamente",
            "Implementar operações preventivas intensivas",
            "Reforçar segurança pública e iluminação"
        ])
        if mortes_confronto > 0:
            recomendacoes.append("Revisar protocolos de uso da força")
    elif '🟠' in nivel_risco:  # Alto
        recomendacoes.extend([
            "Intensificar patrulhamento preventivo",
            "Implementar operações especiais focadas",
            "Monitorar pontos críticos identificados"
        ])
    elif '🟡' in nivel_risco:  # Médio-Alto/Médio
        recomendacoes.extend([
            "Manter vigilância regular",
            "Implementar ações comunitárias de segurança",
            "Focar em prevenção situacional"
        ])
    else:  # Baixo
        recomendacoes.append("Manter ações preventivas atuais")
    
    # Recomendações específicas baseadas nos indicadores
    if total_operacoes == 0 and total_crimes > 5:
        recomendacoes.append("👮 Implementar operações policiais no bairro")
    
    if prisoes_realizadas == 0 and total_crimes > 10:
        recomendacoes.append("🔒 Focar em operações com prisões efetivas")
    
    if apreensoes_armas == 0 and 'roubo' in str(padroes_crimes.get('tipos_predominantes', {})).lower():
        recomendacoes.append("🔫 Intensificar busca e apreensão de armas")
    
    if apreensoes_drogas == 0 and total_crimes > 15:
        recomendacoes.append("💊 Investigar possível atividade de tráfico")
    
    if efetividade_global < 10 and total_crimes > 20:
        recomendacoes.append("📈 Melhorar efetividade das operações atuais")
    
    # Criar popup content COMPLETO com todos os indicadores
    popup_content = f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; width: 380px; padding: 8px;">
        <h4 style="color: #1f4e79; margin: 0 0 12px 0; padding-bottom: 8px; border-bottom: 2px solid #e1e5e9; font-size: 16px;">
            📍 {bairro}
        </h4>
        
        <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; margin-bottom: 12px;">
            <h5 style="color: #495057; margin: 0 0 8px 0; font-size: 14px;">📊 Estatísticas de Crimes</h5>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px;">
                <div><strong>📊 Total:</strong> {total_crimes}</div>
                <div><strong>👮 Policiais:</strong> {int(total_operacoes)}</div>
                <div><strong>🔒 Prisões:</strong> {int(prisoes_realizadas)}</div>
                <div><strong>💀 Mortes:</strong> {int(mortes_confronto)}</div>
            </div>
        </div>
        
        <div style="background: #e8f4fd; padding: 12px; border-radius: 8px; margin-bottom: 12px;">
            <h5 style="color: #0066cc; margin: 0 0 8px 0; font-size: 14px;">🔫 Apreensões & Operações</h5>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px;">
                <div><strong>🔫 Armas:</strong> {int(apreensoes_armas)}</div>
                <div><strong>💊 Drogas:</strong> {apreensoes_drogas:.1f}kg</div>
                <div><strong>🚨 Op. Ativas:</strong> {int(operacoes_ativas)}</div>
                <div><strong>📈 Efetividade:</strong> {efetividade_global:.1f}%</div>
            </div>
        </div>
        
        <div style="background: #f0f0f0; padding: 10px; border-radius: 6px; margin-bottom: 10px;">
            <div style="font-size: 14px;"><strong>⚠️ Risco:</strong> <span style="font-weight: bold;">{nivel_risco}</span></div>
            <div style="font-size: 13px; color: #666;"><strong>📈 Score:</strong> {score_final:.1f}</div>
        </div>
    </div>
    """
    
    return {
        'bairro': bairro,
        'total_crimes': total_crimes,
        'total_operacoes': int(total_operacoes),
        'mortes_confronto': int(mortes_confronto),
        'prisoes_realizadas': int(prisoes_realizadas),
        'apreensoes_armas': int(apreensoes_armas),
        'apreensoes_drogas': round(apreensoes_drogas, 2),
        'operacoes_ativas': int(operacoes_ativas),
        'operacoes_tipos': operacoes_tipos,
        'efetividade_global': round(efetividade_global, 2),
        'score_sinergico': round(score_final, 2),
        'score_bruto': round(score_bruto, 2),
        'penalidades': round(penalidades, 2),
        'beneficios': round(beneficios, 2),
        'nivel_risco': nivel_risco,
        'cor': cor_risco,
        'analise_temporal': analise_temporal,
        'padroes_crimes': padroes_crimes,
        'recomendacoes': recomendacoes,
        'fator_operacoes': round(fator_operacoes, 3),
        'popup_content': popup_content
    }


def generate_alerts(df, threshold_crimes=10, threshold_increase=0.3):
    """Gera alertas baseados em dados de segurança.
    
    Args:
        df (pd.DataFrame): DataFrame com dados de criminalidade
        threshold_crimes (int): Limite de crimes para alerta
        threshold_increase (float): Limite de aumento percentual para alerta
        
    Returns:
        list: Lista de alertas gerados
    """
    alerts = []
    
    if df.empty:
        return alerts
    
    # Verificar se as colunas necessárias existem
    required_columns = ['bairro', 'Data Registro']
    if not all(col in df.columns for col in required_columns):
        return alerts
    
    try:
        # Converter data para datetime
        df_temp = df.copy()
        df_temp['Data Registro'] = pd.to_datetime(df_temp['Data Registro'])
        
        # Obter data mais recente
        data_mais_recente = df_temp['Data Registro'].max()
        data_30_dias = data_mais_recente - pd.Timedelta(days=30)
        data_60_dias = data_mais_recente - pd.Timedelta(days=60)
        
        # Analisar por bairro
        for bairro in df_temp['bairro'].unique():
            if pd.isna(bairro):
                continue
                
            df_bairro = df_temp[df_temp['bairro'] == bairro]
            
            # Crimes dos últimos 30 dias
            crimes_recentes = df_bairro[df_bairro['Data Registro'] >= data_30_dias]
            crimes_anteriores = df_bairro[
                (df_bairro['Data Registro'] >= data_60_dias) & 
                (df_bairro['Data Registro'] < data_30_dias)
            ]
            
            total_recentes = len(crimes_recentes)
            total_anteriores = len(crimes_anteriores)
            
            # Alerta por volume alto
            if total_recentes >= threshold_crimes:
                alerts.append({
                    'tipo': 'Volume Alto',
                    'bairro': bairro,
                    'descricao': f'Alto número de crimes: {total_recentes} nos últimos 30 dias',
                    'prioridade': 'Alta' if total_recentes >= threshold_crimes * 2 else 'Média',
                    'crimes_count': total_recentes
                })
            
            # Alerta por aumento significativo
            if total_anteriores > 0:
                aumento_percentual = (total_recentes - total_anteriores) / total_anteriores
                if aumento_percentual >= threshold_increase:
                    alerts.append({
                        'tipo': 'Aumento Significativo',
                        'bairro': bairro,
                        'descricao': f'Aumento de {aumento_percentual:.1%} nos crimes (de {total_anteriores} para {total_recentes})',
                        'prioridade': 'Alta' if aumento_percentual >= 0.5 else 'Média',
                        'aumento_percentual': aumento_percentual
                    })
            
            # Alerta por tipos específicos de crime
            if 'tipo_crime' in df_temp.columns:
                crimes_graves = crimes_recentes[crimes_recentes['tipo_crime'].isin([
                    'HOMICÍDIO', 'ROUBO', 'LATROCÍNIO', 'ESTUPRO'
                ])]
                
                if len(crimes_graves) >= 3:
                    alerts.append({
                        'tipo': 'Crimes Graves',
                        'bairro': bairro,
                        'descricao': f'{len(crimes_graves)} crimes graves nos últimos 30 dias',
                        'prioridade': 'Crítica',
                        'crimes_graves': len(crimes_graves)
                    })
    
    except Exception as e:
        st.warning(f"Erro ao gerar alertas: {str(e)}")
    
    # Ordenar alertas por prioridade
    prioridade_ordem = {'Crítica': 0, 'Alta': 1, 'Média': 2, 'Baixa': 3}
    alerts.sort(key=lambda x: prioridade_ordem.get(x['prioridade'], 3))
    
    return alerts


def create_prediction_model(df):
    """Cria modelo preditivo para assaltos.
    
    Args:
        df (pd.DataFrame): DataFrame com dados de criminalidade
        
    Returns:
        tuple: (modelo, encoder, score) ou (None, None, 0) se falhar
    """
    try:
        if df.empty or 'tipo_crime' not in df.columns:
            return None, None, 0
        
        # Filtrar apenas assaltos/roubos
        df_assaltos = df[df['tipo_crime'].str.contains('ROUBO|ASSALTO', case=False, na=False)]
        
        if len(df_assaltos) < 10:  # Dados insuficientes
            return None, None, 0
        
        # Preparar features
        features = []
        target = []
        
        # Usar bairro, hora e dia da semana como features
        required_cols = ['bairro', 'Data Registro']
        if not all(col in df_assaltos.columns for col in required_cols):
            return None, None, 0
        
        df_model = df_assaltos.copy()
        df_model['Data Registro'] = pd.to_datetime(df_model['Data Registro'])
        df_model['dia_semana'] = df_model['Data Registro'].dt.dayofweek
        df_model['mes'] = df_model['Data Registro'].dt.month
        
        # Encoder para bairros
        le_bairro = LabelEncoder()
        df_model['bairro_encoded'] = le_bairro.fit_transform(df_model['bairro'].astype(str))
        
        # Agrupar por bairro e período para criar features
        for bairro in df_model['bairro'].unique():
            df_bairro = df_model[df_model['bairro'] == bairro]
            
            if len(df_bairro) < 3:
                continue
            
            # Contar assaltos por mês
            assaltos_por_mes = df_bairro.groupby(['mes']).size()
            
            for mes, count in assaltos_por_mes.items():
                bairro_encoded = le_bairro.transform([bairro])[0]
                features.append([bairro_encoded, mes])
                target.append(count)
        
        if len(features) < 5:
            return None, None, 0
        
        # Treinar modelo
        X = np.array(features)
        y = np.array(target)
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Calcular score simples
        score = model.score(X, y)
        
        return model, le_bairro, score
        
    except Exception as e:
        st.warning(f"Erro ao criar modelo preditivo: {str(e)}")
        return None, None, 0


def predict_crimes_for_bairro(model, encoder, bairro, mes=None):
    """Prediz número de crimes para um bairro específico.
    
    Args:
        model: Modelo treinado
        encoder: Encoder de bairros
        bairro (str): Nome do bairro
        mes (int): Mês para predição (padrão: próximo mês)
        
    Returns:
        int: Número predito de crimes
    """
    try:
        if model is None or encoder is None:
            return 0
        
        if mes is None:
            mes = pd.Timestamp.now().month + 1
            if mes > 12:
                mes = 1
        
        # Verificar se o bairro existe no encoder
        try:
            bairro_encoded = encoder.transform([bairro])[0]
        except ValueError:
            # Bairro não visto durante treinamento
            return 0
        
        # Fazer predição
        prediction = model.predict([[bairro_encoded, mes]])
        return max(0, int(round(prediction[0])))
        
    except Exception:
        return 0