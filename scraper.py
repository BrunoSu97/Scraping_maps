"""
Módulo de scraping do Google Maps.

Contém todas as funções de interação com o navegador:
  - Inicialização do Chrome WebDriver
  - Navegação e busca no Google Maps
  - Scroll do painel de resultados
  - Extração dos dados de cada estabelecimento
  - Encerramento do navegador
"""

import re
import time
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
    StaleElementReferenceException,
)

import config

# Logger do módulo
logger = logging.getLogger("rpa_google_maps")


# ==========================================================================
# Inicialização do WebDriver
# ==========================================================================

def init_driver() -> webdriver.Chrome:
    """
    Inicializa e retorna uma instância do Chrome WebDriver.

    Configurações aplicadas:
      - Modo visível (config.HEADLESS = False) ou headless
      - Idioma português do Brasil
      - Desativa notificações e pop-ups do navegador
      - ChromeDriver baixado automaticamente via webdriver-manager

    Returns:
        webdriver.Chrome: Instância do navegador pronta para uso.

    Raises:
        WebDriverException: Se não for possível iniciar o navegador.
    """
    try:
        logger.info("Inicializando o Chrome WebDriver...")

        options = Options()

        # Modo headless (sem interface) ou visível
        if config.HEADLESS:
            options.add_argument("--headless=new")
            logger.debug("Modo headless ativado.")
        else:
            logger.debug("Modo visível ativado (com interface gráfica).")

        # Configurações de estabilidade e performance
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(
            f"--window-size={config.WINDOW_WIDTH},{config.WINDOW_HEIGHT}"
        )
        options.add_argument("--lang=pt-BR")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")

        # Força idioma português nas preferências do navegador
        options.add_experimental_option("prefs", {
            "intl.accept_languages": "pt-BR,pt",
        })

        # Selenium 4.6+ gerencia o ChromeDriver automaticamente (Selenium Manager)
        driver = webdriver.Chrome(options=options)

        # Timeout implícito para busca de elementos
        driver.implicitly_wait(5)

        logger.info("Chrome WebDriver inicializado com sucesso.")
        return driver

    except WebDriverException as e:
        logger.critical(f"Falha ao inicializar o Chrome WebDriver: {e}")
        raise


# ==========================================================================
# Navegação e busca
# ==========================================================================

def search_maps(driver: webdriver.Chrome, query: str) -> None:
    """
    Acessa o Google Maps e realiza a busca pelo termo informado.

    Fluxo:
      1. Navega até google.com/maps
      2. Localiza o campo de busca pelo XPath configurado
      3. Digita o termo de busca e pressiona Enter
      4. Aguarda o feed de resultados carregar

    Args:
        driver: Instância do WebDriver.
        query: Termo de busca (ex: "academias em São Paulo").

    Raises:
        TimeoutException: Se a página ou resultados não carregarem.
        WebDriverException: Se ocorrer erro na navegação.
    """
    try:
        logger.info(f"Acessando Google Maps para busca: '{query}'")
        driver.get(config.GOOGLE_MAPS_URL)

        # Aguarda o campo de busca estar disponível (XPath fornecido)
        search_box = WebDriverWait(driver, config.TIMEOUT).until(
            EC.presence_of_element_located((By.XPATH, config.SEARCH_INPUT_XPATH))
        )
        logger.debug("Campo de busca encontrado.")

        # Se já existe um feed de resultados antigo, aguarda ele sumir
        # para evitar ler dados da busca anterior
        try:
            old_feed = driver.find_elements(By.CSS_SELECTOR, config.FEED_SELECTOR)
            if old_feed:
                logger.debug("Feed antigo detectado. Aguardando renovação...")
        except Exception:
            pass

        # Limpa o campo e digita o termo de busca
        search_box.clear()
        time.sleep(0.5)
        search_box.send_keys(query)
        search_box.send_keys(Keys.ENTER)

        logger.info(f"Busca realizada: '{query}'")

        # Aguarda o feed de resultados aparecer na página
        WebDriverWait(driver, config.TIMEOUT).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, config.FEED_SELECTOR)
            )
        )
        logger.debug("Feed de resultados carregado.")

        # Aguarda os cards renderizarem completamente antes de extrair dados.
        # Sem essa espera, os dados podem ser lidos do feed da busca anterior.
        time.sleep(config.SEARCH_WAIT)

    except TimeoutException:
        logger.error(f"Timeout ao buscar '{query}' no Google Maps.")
        raise
    except WebDriverException as e:
        logger.error(f"Erro ao acessar Google Maps: {e}")
        raise


# ==========================================================================
# Scroll para carregar mais resultados
# ==========================================================================

def scroll_results(driver: webdriver.Chrome) -> int:
    """
    Rola o painel lateral de resultados para carregar mais estabelecimentos.

    O Google Maps carrega resultados sob demanda conforme o usuário
    rola o painel. Esta função simula esse comportamento, rolando
    até o final do container de resultados várias vezes.

    Args:
        driver: Instância do WebDriver.

    Returns:
        int: Número de scrolls efetivamente realizados.
    """
    try:
        feed = driver.find_element(By.CSS_SELECTOR, config.FEED_SELECTOR)
        logger.debug("Iniciando scroll no painel de resultados...")

        scrolls_done = 0
        previous_height = 0

        for i in range(config.MAX_SCROLLS):
            # Rola o painel de resultados até o final
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight", feed
            )
            time.sleep(config.SCROLL_PAUSE)
            scrolls_done += 1

            # Verifica se houve carregamento de novos resultados
            current_height = driver.execute_script(
                "return arguments[0].scrollHeight", feed
            )
            if current_height == previous_height:
                logger.debug(
                    f"Scroll {i + 1}: sem novos resultados. Encerrando scroll."
                )
                break
            previous_height = current_height
            logger.debug(f"Scroll {i + 1}/{config.MAX_SCROLLS} realizado.")

        logger.info(f"Scroll completo: {scrolls_done} iterações realizadas.")
        return scrolls_done

    except NoSuchElementException:
        logger.warning("Painel de resultados não encontrado para scroll.")
        return 0
    except WebDriverException as e:
        logger.warning(f"Erro durante scroll: {e}")
        return 0


# ==========================================================================
# Extração de dados
# ==========================================================================

def extract_results(driver: webdriver.Chrome, tipo: str) -> list:
    """
    Extrai dados dos estabelecimentos listados no feed de resultados.

    Para cada resultado encontrado no painel, tenta extrair:
      - Nome (via atributo aria-label do link)
      - Nota/rating (via parsing de texto com regex)
      - Quantidade de avaliações (via parsing de texto com regex)
      - Endereço completo (via heurística de padrões brasileiros)

    Args:
        driver: Instância do WebDriver.
        tipo: Tipo do estabelecimento ("academia", "restaurante", "sorveteria").

    Returns:
        list: Lista de dicionários com os dados de cada estabelecimento.
    """
    results = []

    try:
        feed = driver.find_element(By.CSS_SELECTOR, config.FEED_SELECTOR)

        # Localiza todos os links de estabelecimentos dentro do feed
        items = feed.find_elements(
            By.CSS_SELECTOR, config.PLACE_LINK_SELECTOR
        )
        logger.info(f"Encontrados {len(items)} resultados para '{tipo}'.")

        for idx, item in enumerate(items):
            # Respeita o limite máximo de resultados por tipo
            if len(results) >= config.MAX_RESULTADOS_POR_TIPO:
                logger.debug(
                    f"Limite de {config.MAX_RESULTADOS_POR_TIPO} resultados atingido."
                )
                break

            try:
                data = _extract_single_result(item, tipo)
                if data:
                    results.append(data)
                    logger.debug(
                        f"  [{idx + 1}] Extraído: {data['nome']}"
                    )
            except StaleElementReferenceException:
                # Elemento foi removido do DOM (ex: re-render da página)
                logger.warning(
                    f"  [{idx + 1}] Elemento obsoleto (stale). Pulando..."
                )
                continue
            except Exception as e:
                logger.warning(
                    f"  [{idx + 1}] Falha ao extrair resultado: {e}"
                )
                continue

    except NoSuchElementException:
        logger.error("Feed de resultados não encontrado para extração.")
    except WebDriverException as e:
        logger.error(f"Erro ao extrair resultados: {e}")

    logger.info(f"Total extraído para '{tipo}': {len(results)} estabelecimentos.")
    return results


def _extract_single_result(item, tipo: str) -> dict:
    """
    Extrai os dados de um único card de resultado do Google Maps.

    Estratégia de extração:
      1. Nome: atributo aria-label do elemento <a>
      2. Texto completo: obtido do container pai do card
      3. Nota, avaliações e endereço: parseados via regex do texto

    Args:
        item: Elemento Selenium (link <a>) do estabelecimento.
        tipo: Tipo do estabelecimento.

    Returns:
        dict: Dados do estabelecimento ou None se nome não encontrado.
    """
    # --- Nome ---
    nome = item.get_attribute("aria-label")
    if not nome or nome.strip() == "":
        return None
    nome = nome.strip()

    # --- Texto do container pai ---
    # O card do resultado contém nome, nota, avaliações, categoria e endereço
    text_content = _get_card_text(item)

    # --- Nota (rating) ---
    nota = _extract_rating(text_content)

    # --- Quantidade de avaliações ---
    avaliacoes = _extract_reviews(text_content)

    # --- Endereço ---
    endereco = _extract_address(text_content)

    return {
        "nome": nome,
        "tipo": tipo,
        "nota": nota,
        "avaliacoes": avaliacoes,
        "endereco": endereco,
    }


def _get_card_text(item) -> str:
    """
    Obtém o texto completo do card de resultado.

    Tenta múltiplas estratégias para encontrar o container correto:
      1. Ancestral com classe conhecida do Google Maps (ex: Nv2PK)
      2. Pai direto do elemento
      3. Texto do próprio elemento como fallback

    Args:
        item: Elemento Selenium do link do estabelecimento.

    Returns:
        str: Texto completo do card.
    """
    # Estratégia 1: Busca o container mais próximo que contém todo o card
    # O Google Maps geralmente usa divs com classes específicas
    try:
        container = item.find_element(
            By.XPATH, "./ancestor::div[contains(@jsaction,'mouseover')]"
        )
        return container.text
    except NoSuchElementException:
        pass

    # Estratégia 2: Sobe 3 níveis no DOM para capturar o card completo
    try:
        parent = item.find_element(By.XPATH, "./../../..")
        text = parent.text
        if len(text) > 10:
            return text
    except NoSuchElementException:
        pass

    # Estratégia 3: Pai direto
    try:
        parent = item.find_element(By.XPATH, "./..")
        return parent.text
    except NoSuchElementException:
        pass

    # Fallback: texto do próprio elemento
    return item.text


def _extract_rating(text: str) -> str:
    """
    Extrai a nota (rating) do texto do card.

    Busca padrões numéricos como "4,5" ou "4.5" que precedem
    a quantidade de avaliações entre parênteses.

    Args:
        text: Texto completo do card do resultado.

    Returns:
        str: Nota formatada (ex: "4,5") ou "N/A" se não encontrada.
    """
    # Padrão principal: número decimal seguido de parênteses com avaliações
    # Ex: "4,5(1.234)" ou "4,5 (1.234)"
    match = re.search(r'(\d[,\.]\d)\s*\(', text)
    if match:
        return match.group(1).replace('.', ',')

    # Fallback: número decimal isolado no início de uma linha
    match = re.search(r'(?:^|\n)(\d[,\.]\d)', text)
    if match:
        return match.group(1).replace('.', ',')

    return "N/A"


def _extract_reviews(text: str) -> str:
    """
    Extrai a quantidade de avaliações do texto do card.

    Busca números entre parênteses. No formato brasileiro, milhares
    são separados por ponto (ex: "1.234").

    Args:
        text: Texto completo do card do resultado.

    Returns:
        str: Quantidade de avaliações (ex: "1.234") ou "N/A".
    """
    # Padrão: números (com pontos de milhar opcionais) entre parênteses
    # Ex: "(1.234)", "(567)", "(12.345)"
    match = re.search(r'\(([0-9][0-9.]*)\)', text)
    if match:
        return match.group(1)

    return "N/A"


def _extract_address(text: str) -> str:
    """
    Extrai o endereço completo do texto do card.

    Utiliza heurísticas baseadas em padrões de endereço brasileiro:
      - Prefixos: R., Av., Al., Rod., Rua, Avenida, etc.
      - Padrões de CEP: 01234-567
      - Números de logradouro

    Se nenhum padrão for encontrado, tenta identificar o endereço
    pela posição no texto (geralmente nas últimas linhas do card).

    Args:
        text: Texto completo do card do resultado.

    Returns:
        str: Endereço encontrado ou "N/A".
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # Padrões comuns em endereços brasileiros
    address_patterns = [
        r'R\.\s',           # R. (Rua)
        r'Av\.\s',          # Av. (Avenida)
        r'Al\.\s',          # Al. (Alameda)
        r'Tv\.\s',          # Tv. (Travessa)
        r'Pç\.\s',          # Pç. (Praça)
        r'Rod\.\s',         # Rod. (Rodovia)
        r'Estr\.\s',        # Estr. (Estrada)
        r'\d{5}-?\d{3}',    # CEP (01234-567)
        r'Rua\s',
        r'Avenida\s',
        r'Alameda\s',
        r'Praça\s',
        r'Travessa\s',
        r'Rodovia\s',
        r'Estrada\s',
    ]

    # Primeira tentativa: busca por padrões explícitos de endereço
    for line in lines:
        for pattern in address_patterns:
            if re.search(pattern, line):
                return line

    # Segunda tentativa: busca nas últimas linhas do card
    # O endereço costuma estar após a nota/avaliações e categoria
    if len(lines) >= 3:
        # Percorre as últimas linhas de trás para frente
        for line in reversed(lines[-4:]):
            # Ignora linhas com horário de funcionamento ou status
            if re.search(
                r'(Aberto|Fechado|Fecha|Abre|24 horas|Delivery|Retirada)',
                line,
                re.IGNORECASE
            ):
                continue
            # Ignora linhas que são apenas nota/rating
            if re.match(r'^\d[,\.]\d$', line):
                continue
            # Ignora linhas muito curtas (provavelmente categoria)
            if len(line) > 10:
                return line

    return "N/A"


# ==========================================================================
# Encerramento
# ==========================================================================

def close_driver(driver: webdriver.Chrome) -> None:
    """
    Fecha o navegador de forma segura.

    Args:
        driver: Instância do WebDriver a ser encerrada.
    """
    try:
        if driver:
            driver.quit()
            logger.info("Navegador fechado com sucesso.")
    except WebDriverException as e:
        logger.warning(f"Erro ao fechar o navegador: {e}")
