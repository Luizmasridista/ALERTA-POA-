# 🚨 Alerta POA - Sistema Avançado de Análise de Segurança Pública

## 📋 Sobre o Projeto

O **Alerta POA** é um sistema completo de análise de dados de segurança pública desenvolvido especificamente para Porto Alegre/RS. Este projeto representa um case de sucesso para analistas de dados, demonstrando como transformar dados brutos de criminalidade em insights acionáveis através de visualizações interativas, análise preditiva e sistema de alertas em tempo real.

## 🎯 Objetivos

- **Análise Descritiva**: Compreender padrões históricos de criminalidade
- **Análise Preditiva**: Prever tendências futuras de assaltos
- **Visualização Interativa**: Mapas e gráficos dinâmicos para exploração dos dados
- **Sistema de Alertas**: Notificações baseadas em risco atual
- **Relatórios Automatizados**: Geração de relatórios executivos

## 🏗️ Arquitetura do Sistema

### Componentes Principais

1. **Coleta de Dados**
   - Dados oficiais da SSP-RS (Secretaria de Segurança Pública)
   - Dados geográficos da Prefeitura de Porto Alegre
   - Processamento e limpeza automatizada

2. **Análise de Dados**
   - Análise temporal (horário, dia da semana, mês)
   - Análise geográfica (distribuição por bairros)
   - Análise de padrões criminais

3. **Modelos Preditivos**
   - Regressão linear para previsão de tendências
   - Cálculo de score de risco em tempo real
   - Análise de sazonalidade

4. **Interface Web**
   - Dashboard interativo com Streamlit
   - Mapas dinâmicos com Folium
   - Visualizações com Plotly

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.11**: Linguagem principal
- **Pandas**: Manipulação e análise de dados
- **GeoPandas**: Análise de dados geoespaciais
- **Scikit-learn**: Modelos de machine learning
- **NumPy**: Computação numérica

### Frontend
- **Streamlit**: Framework para aplicações web
- **Plotly**: Visualizações interativas
- **Folium**: Mapas interativos
- **HTML/CSS**: Customização da interface

### Dados
- **CSV**: Armazenamento de dados estruturados
- **GeoJSON**: Dados geográficos dos bairros
- **Shapefile**: Dados vetoriais geográficos

## 📊 Funcionalidades

### 🗺️ Mapa Interativo
- Visualização geográfica dos assaltos por bairro
- Marcadores dinâmicos com cores baseadas no nível de risco
- Tooltips informativos com estatísticas detalhadas
- Camadas de calor para identificação de hotspots

### 📈 Análises Estatísticas
- **Distribuição Temporal**: Análise por hora, dia da semana e mês
- **Ranking de Bairros**: Identificação das áreas mais perigosas
- **Tipos de Crime**: Categorização e análise dos diferentes tipos de assalto
- **Correlações**: Identificação de padrões entre variáveis

### 🔮 Análise Preditiva
- **Previsão de Tendências**: Modelo de regressão para próximos 7 dias
- **Score de Risco**: Cálculo em tempo real baseado em múltiplos fatores
- **Sazonalidade**: Identificação de padrões sazonais

### 🚨 Sistema de Alertas
- **Alertas de Risco**: Notificações baseadas no nível de perigo atual
- **Recomendações**: Sugestões de segurança personalizadas
- **Bairros de Risco**: Identificação das áreas a evitar

### 📄 Relatórios
- **Relatório Executivo**: Resumo completo das análises
- **Exportação**: Download em formato texto
- **Métricas KPI**: Indicadores principais de performance

## 🚀 Como Executar

### Pré-requisitos
```bash
Python 3.11+
pip (gerenciador de pacotes Python)
```

### Instalação
```bash
# Clone o repositório
git clone <repository-url>
cd alerta-poa

# Instale as dependências
pip install -r requirements.txt

# Execute o aplicativo
streamlit run alerta_poa_final.py --server.port 8501 --server.address 0.0.0.0
```

### Acesso
Abra seu navegador e acesse: `http://localhost:8501`

## 📁 Estrutura do Projeto

```
alerta-poa/
├── alerta_poa_final.py          # Aplicativo principal
├── process_data.py              # Script de processamento de dados
├── geo_processor.py             # Processamento de dados geográficos
├── assaltos_porto_alegre.csv    # Dados de assaltos processados
├── bairros_poa.geojson         # Dados geográficos dos bairros
├── bairros_stats.json          # Estatísticas por bairro
├── requirements.txt            # Dependências do projeto
├── README.md                   # Documentação principal
└── docs/                       # Documentação adicional
    ├── case_study.md           # Estudo de caso
    └── technical_guide.md      # Guia técnico
```

## 📈 Resultados e Insights

### Principais Descobertas

1. **Padrões Temporais**
   - Maior incidência de assaltos entre 18h-23h
   - Picos nos finais de semana
   - Sazonalidade relacionada a eventos e feriados

2. **Distribuição Geográfica**
   - Centro e Cidade Baixa concentram 40% dos casos
   - Bairros periféricos apresentam menor incidência
   - Correlação com densidade populacional e fluxo comercial

3. **Tipos de Crime**
   - Roubo de celular representa 35% dos casos
   - Roubo a pedestres é mais comum em áreas centrais
   - Roubo a estabelecimentos concentra-se em zonas comerciais

### Impacto do Projeto

- **Redução de Risco**: Identificação proativa de áreas perigosas
- **Otimização de Recursos**: Direcionamento inteligente do policiamento
- **Conscientização Pública**: Informação acessível para cidadãos
- **Tomada de Decisão**: Dados para políticas públicas

## 🎯 Case de Sucesso para Analistas de Dados

Este projeto demonstra competências essenciais para analistas de dados:

### Habilidades Técnicas
- **Coleta e Limpeza de Dados**: ETL de fontes governamentais
- **Análise Exploratória**: Identificação de padrões e insights
- **Visualização de Dados**: Criação de dashboards interativos
- **Machine Learning**: Implementação de modelos preditivos
- **Desenvolvimento Web**: Criação de aplicações para usuários finais

### Habilidades de Negócio
- **Compreensão do Domínio**: Conhecimento sobre segurança pública
- **Storytelling com Dados**: Comunicação eficaz de insights
- **Impacto Social**: Aplicação de dados para benefício público
- **Pensamento Crítico**: Análise contextualizada dos resultados

## 🔧 Melhorias Futuras

### Curto Prazo
- [ ] Integração com APIs em tempo real
- [ ] Notificações push para usuários
- [ ] Versão mobile responsiva
- [ ] Mais tipos de visualizações

### Médio Prazo
- [ ] Modelos de ML mais sofisticados
- [ ] Análise de sentimento em redes sociais
- [ ] Integração com câmeras de segurança
- [ ] Sistema de denúncias integrado

### Longo Prazo
- [ ] Expansão para outras cidades
- [ ] Análise preditiva por IA
- [ ] Integração com IoT urbano
- [ ] Plataforma de segurança integrada

## 👥 Contribuições

Contribuições são bem-vindas! Por favor, leia o guia de contribuição antes de submeter pull requests.

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo LICENSE para detalhes.

## 📞 Contato

**Desenvolvedor**: Analista de Dados - Case de Sucesso  
**Email**: contato@alertapoa.com  
**LinkedIn**: [linkedin.com/in/analista-dados-poa](https://linkedin.com/in/analista-dados-poa)

## 🙏 Agradecimentos

- **SSP-RS**: Pela disponibilização dos dados de segurança pública
- **Prefeitura de Porto Alegre**: Pelos dados geográficos dos bairros
- **Comunidade Open Source**: Pelas bibliotecas e ferramentas utilizadas

---

**⚠️ Aviso Legal**: Este sistema é desenvolvido para fins educacionais e de conscientização. Os dados apresentados são baseados em registros oficiais, mas podem não refletir a situação em tempo real. Sempre consulte fontes oficiais para informações atualizadas sobre segurança pública.

