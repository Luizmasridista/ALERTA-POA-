"""Módulos do sistema Alerta POA.

Este pacote contém todos os módulos refatorados do sistema:
- data_loader: Carregamento e processamento de dados
- mapping_utils: Utilitários de mapeamento e visualização
- security_analysis: Análises de segurança e cálculos de risco
- visualization: Criação de mapas e relatórios
"""

__version__ = "2.0.0"
__author__ = "Sistema Alerta POA"

# Importações principais para facilitar o uso
from .data_loader import (
    load_data,
    load_security_index_data,
    load_neighborhood_stats,
    load_bairros_sem_dados,
    load_geojson_data
)

from .mapping_utils import (
    map_bairro_name,
    get_color_for_map_integrated,
    get_color_for_map_original,
    get_risk_level_for_map_integrated,
    get_risk_level_for_map_original,
    get_color_based_on_synergistic_analysis
)

from .security_analysis import (
    calculate_risk_score,
    calculate_enhanced_risk_score_with_police_ops,
    calculate_synergistic_security_analysis,
    generate_alerts,
    create_prediction_model,
    predict_crimes_for_bairro
)

from .visualization import (
    create_advanced_map,
    export_report,
    create_heatmap_data
)

__all__ = [
    # Data loader functions
    'load_data',
    'load_security_index_data', 
    'load_neighborhood_stats',
    'load_bairros_sem_dados',
    'load_geojson_data',
    
    # Mapping utilities
    'map_bairro_name',
    'get_color_for_map_integrated',
    'get_color_for_map_original',
    'get_risk_level_for_map_integrated',
    'get_risk_level_for_map_original',
    'get_color_based_on_synergistic_analysis',
    
    # Security analysis
    'calculate_risk_score',
    'calculate_enhanced_risk_score_with_police_ops',
    'calculate_synergistic_security_analysis',
    'generate_alerts',
    'create_prediction_model',
    'predict_crimes_for_bairro',
    
    # Visualization
    'create_advanced_map',
    'export_report',
    'create_heatmap_data'
]