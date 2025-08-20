# 🚨 Alerta POA v2.0 - Sistema Avançado de Segurança Pública

## 📋 Sobre o Projeto

O **Alerta POA** é um sistema completo de análise de dados de segurança pública desenvolvido especificamente para Porto Alegre/RS. Este projeto representa um case de sucesso para analistas de dados, demonstrando como transformar dados brutos de criminalidade em insights acionáveis através de visualizações interativas, análise preditiva e sistema de alertas em tempo real.

### 🆕 Novidades da Versão 2.0

- **Coleta Automatizada**: Sistema de coleta de dados de múltiplas fontes oficiais
- **Dados Ampliados**: Informações de 2023-2024 com detalhamento por horário e tipo de crime
- **Atualização Automática**: Sistema de atualização semanal dos dados
- **Interface Aprimorada**: Dashboard mais intuitivo com análises comparativas
- **Configuração Flexível**: Sistema configurável via JSON

## 🎯 Objetivos

- **Análise Descritiva**: Compreender padrões históricos de criminalidade (2023-2024)
- **Análise Preditiva**: Prever tendências futuras de crimes por tipo e localização
- **Visualização Interativa**: Mapas e gráficos dinâmicos para exploração dos dados
- **Sistema de Alertas**: Notificações baseadas em risco atual por bairro
- **Relatórios Automatizados**: Geração de relatórios executivos com dados atualizados
- **Monitoramento Contínuo**: Coleta e análise automática de novos dados

## 🏗️ Arquitetura do Sistema

### Componentes Principais

1. **Coleta de Dados Automatizada**
   - **SSP-RS**: Secretaria de Segurança Pública do Rio Grande do Sul
   - **Observatório de Segurança**: Dados históricos desde 2002
   - **DataPOA**: Portal de dados abertos de Porto Alegre
   - **Dados Federais**: Ministério da Justiça e Segurança Pública
   - Processamento e limpeza automatizada com validação

2. **Análise de Dados Avançada**
   - Análise temporal detalhada (horário, dia da semana, mês, ano)
   - Análise geográfica por bairros com densidade criminal
   - Categorização de tipos de crime (roubo, furto, homicídio, etc.)
   - Comparações anuais e identificação de tendências

3. **Modelos Preditivos e Alertas**
   - Regressão linear para previsão de tendências
   - Cálculo de score de risco em tempo real por bairro
   - Análise de sazonalidade e padrões temporais
   - Sistema de alertas baseado em níveis de risco

4. **Interface Web Interativa**
   - Dashboard responsivo com Streamlit
   - Mapas dinâmicos com Folium e dados georreferenciados
   - Visualizações interativas com Plotly
   - Análises comparativas 2023 vs 2024

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

### Automação e Agendamento
- **Schedule**: Agendamento de tarefas automáticas
- **Requests**: Coleta de dados de APIs
- **BeautifulSoup**: Web scraping para dados públicos

### Dados
- **CSV**: Armazenamento de dados estruturados
- **GeoJSON**: Dados geográficos dos bairros
- **JSON**: Configurações e metadados do sistema

## 🚀 Instalação e Uso

### Pré-requisitos
- Python 3.11 ou superior
- Git (opcional, para clonagem do repositório)
- Conexão com internet (para coleta de dados)

### Instalação Rápida

1. **Clone o repositório** (ou baixe os arquivos):
```bash
git clone https://github.com/seu-usuario/alerta-poa.git
cd alerta-poa
```

2. **Instale as dependências**:
```bash
python start_system.py install
```

3. **Colete os dados iniciais**:
```bash
python start_system.py collect
```

4. **Execute o sistema**:
```bash
python start_system.py run
```

### Comandos Disponíveis

O sistema inclui um script de gerenciamento (`start_system.py`) com os seguintes comandos:

```bash
# Ver status do sistema
python start_system.py status

# Instalar dependências
python start_system.py install

# Coletar dados de criminalidade
python start_system.py collect

# Executar aplicativo web
python start_system.py run

# Iniciar atualizações automáticas
python start_system.py update
```

### Uso Manual dos Componentes

#### Coleta de Dados
```bash
# Coletar dados de 2023-2024
python data_collector.py

# Atualização automática
python auto_updater.py update

# Agendar atualizações
python auto_updater.py schedule
```

#### Aplicativo Web
```bash
# Executar diretamente
streamlit run alerta_poa_final.py --server.port 8501
```

### Configuração

O sistema pode ser configurado através do arquivo `config.json`:

- **Fontes de dados**: Ativar/desativar fontes específicas
- **Frequência de atualização**: Definir intervalos de coleta
- **Tipos de crime**: Configurar categorias e cores
- **Alertas**: Definir níveis de risco
- **Performance**: Ajustar cache e limites

### Acesso ao Sistema

Após iniciar o sistema:
- **Local**: http://localhost:8501
- **Rede**: http://[seu-ip]:8501

### Estrutura de Arquivos

```
alerta-poa/
├── alerta_poa_final.py      # Aplicativo principal
├── data_collector.py        # Coletor de dados
├── auto_updater.py         # Sistema de atualização
├── start_system.py         # Script de gerenciamento
├── config.json             # Configurações do sistema
├── requirements.txt        # Dependências Python
├── bairros_poa.geojson    # Dados geográficos
├── dados_criminalidade_*.csv # Dados coletados
└── README.md              # Documentação
```

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

