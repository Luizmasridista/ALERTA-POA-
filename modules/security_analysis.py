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
    
    # Filtrar dados do bairro
    df_bairro = df[df['bairro'].str.upper() == bairro.upper()]
    
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
    """Realiza análise sinérgica detalhada de segurança.
    
    Args:
        df_crimes (pd.DataFrame): DataFrame com dados de crimes
        df_operacoes (pd.DataFrame): DataFrame com dados de operações policiais
        bairro (str): Nome do bairro
        
    Returns:
        dict: Análise sinérgica completa
    """
    # Análise básica de crimes
    crimes_bairro = df_crimes[df_crimes['bairro'].str.upper() == bairro.upper()] if not df_crimes.empty else pd.DataFrame()
    operacoes_bairro = df_operacoes[df_operacoes['bairro'].str.upper() == bairro.upper()] if not df_operacoes.empty else pd.DataFrame()
    
    total_crimes = len(crimes_bairro)
    total_operacoes = len(operacoes_bairro)
    
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
    
    # Score sinérgico
    score_base = total_crimes * 10  # Score base dos crimes
    
    # Fator de redução por operações
    fator_operacoes = max(0.3, 1 - (total_operacoes * 0.1))
    score_ajustado = score_base * fator_operacoes
    
    # Normalizar para 0-100
    score_final = min(100, score_ajustado)
    
    # Determinar nível de risco
    if score_final >= 80:
        nivel_risco = 'Crítico'
        cor_risco = '#8B0000'
    elif score_final >= 60:
        nivel_risco = 'Alto'
        cor_risco = '#FF0000'
    elif score_final >= 40:
        nivel_risco = 'Médio-Alto'
        cor_risco = '#FF4500'
    elif score_final >= 25:
        nivel_risco = 'Médio'
        cor_risco = '#FFA500'
    elif score_final >= 10:
        nivel_risco = 'Baixo-Médio'
        cor_risco = '#FFD700'
    elif score_final >= 1:
        nivel_risco = 'Baixo'
        cor_risco = '#FFFF00'
    else:
        nivel_risco = 'Muito Baixo'
        cor_risco = '#90EE90'
    
    # Recomendações
    recomendacoes = []
    if nivel_risco in ['Crítico', 'Alto']:
        recomendacoes.extend([
            "Aumentar patrulhamento na região",
            "Implementar operações preventivas",
            "Reforçar iluminação pública"
        ])
    elif nivel_risco in ['Médio-Alto', 'Médio']:
        recomendacoes.extend([
            "Manter vigilância regular",
            "Implementar ações comunitárias de segurança"
        ])
    else:
        recomendacoes.append("Manter ações preventivas atuais")
    
    if total_operacoes == 0 and total_crimes > 5:
        recomendacoes.append("Considerar implementar operações policiais")
    
    return {
        'bairro': bairro,
        'total_crimes': total_crimes,
        'total_operacoes': total_operacoes,
        'score_sinergico': round(score_final, 2),
        'nivel_risco': nivel_risco,
        'cor_risco': cor_risco,
        'analise_temporal': analise_temporal,
        'padroes_crimes': padroes_crimes,
        'recomendacoes': recomendacoes,
        'fator_operacoes': round(fator_operacoes, 3)
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