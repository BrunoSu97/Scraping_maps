"""
Arquivo de configuração da automação RPA - Google Maps.

Centraliza todas as constantes, caminhos e parâmetros utilizados
na automação. Para executar em outro computador, basta ajustar
as variáveis deste arquivo conforme necessário.
"""

import os

# ==========================================================================
# Diretório base do projeto
# ==========================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==========================================================================
# Configurações de busca no Google Maps
# ==========================================================================

# Cidade/região alvo para a busca dos estabelecimentos
CIDADE = "São Paulo"

# Mapeamento: tipo do estabelecimento -> termo de busca no Google Maps
TIPOS_ESTABELECIMENTO = {
    "academia": f"academias em {CIDADE}",
    "restaurante": f"restaurantes em {CIDADE}",
    "sorveteria": f"sorveterias em {CIDADE}",
}

# Número máximo de estabelecimentos a coletar por tipo
MAX_RESULTADOS_POR_TIPO = 20

# ==========================================================================
# URLs e seletores
# ==========================================================================

# URL base do Google Maps
GOOGLE_MAPS_URL = "https://www.google.com/maps"

# XPath do campo de busca do Google Maps
SEARCH_INPUT_XPATH = '//*[@id="UGojuc"]'

# CSS Selector do container de resultados (feed)
FEED_SELECTOR = 'div[role="feed"]'

# CSS Selector dos links individuais de cada estabelecimento
PLACE_LINK_SELECTOR = 'a[href*="/maps/place/"]'

# ==========================================================================
# Caminhos dos arquivos de saída
# ==========================================================================

OUTPUT_JSON = os.path.join(BASE_DIR, "resultados.json")
OUTPUT_EXCEL = os.path.join(BASE_DIR, "resultados.xlsx")
LOG_FILE = os.path.join(BASE_DIR, "automation.log")

# ==========================================================================
# Configurações do Selenium / WebDriver
# ==========================================================================

# Modo headless: False = navegador visível, True = sem interface gráfica
HEADLESS = False

# Tempo máximo de espera (segundos) por elementos na página
TIMEOUT = 15

# Tempo de espera (segundos) após cada busca para os resultados renderizarem
# Garante que os dados exibidos correspondem à busca atual e não à anterior
SEARCH_WAIT = 5

# Pausa entre scrolls para carregar mais resultados (segundos)
SCROLL_PAUSE = 2.0

# Número máximo de scrolls no painel de resultados
MAX_SCROLLS = 5

# Dimensões da janela do navegador
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
