"""
Automação RPA - Google Maps
============================

Script principal que orquestra a coleta de dados de estabelecimentos
(academias, restaurantes e sorveterias) no Google Maps.

Fluxo de execução:
  1. Inicializa o sistema de logging.
  2. Abre o navegador Chrome via Selenium.
  3. Para cada tipo de estabelecimento configurado:
     a. Busca no Google Maps.
     b. Rola o painel de resultados para carregar mais itens.
     c. Extrai os dados de cada estabelecimento.
  4. Salva todos os dados coletados em arquivo JSON.
  5. Gera planilha Excel formatada a partir do JSON.
  6. Encerra o navegador e registra o tempo total de execução.

Uso:
    python main.py
"""

import sys
import time
import config
from utils import setup_logger, save_json, generate_excel
from scraper import (
    init_driver,
    search_maps,
    scroll_results,
    extract_results,
    close_driver,
)


def main():
    """Função principal — orquestra toda a automação."""

    # --- Etapa 1: Inicializar o logger ---
    logger = setup_logger()
    logger.info("=" * 60)
    logger.info("INÍCIO DA AUTOMAÇÃO RPA - GOOGLE MAPS")
    logger.info(f"Cidade alvo: {config.CIDADE}")
    logger.info(f"Tipos de estabelecimento: {list(config.TIPOS_ESTABELECIMENTO.keys())}")
    logger.info(f"Máximo por tipo: {config.MAX_RESULTADOS_POR_TIPO}")
    logger.info("=" * 60)

    start_time = time.time()
    all_results = []
    driver = None

    try:
        # --- Etapa 2: Inicializar o navegador ---
        driver = init_driver()

        # --- Etapa 3: Iterar sobre cada tipo de estabelecimento ---
        for tipo, query in config.TIPOS_ESTABELECIMENTO.items():
            logger.info("-" * 40)
            logger.info(f"BUSCANDO: {tipo.upper()}")
            logger.info(f"Termo de busca: '{query}'")
            logger.info("-" * 40)

            try:
                # 3a. Realiza a busca no Google Maps
                search_maps(driver, query)

                # 3b. Rola o painel para carregar mais resultados
                scroll_results(driver)

                # 3c. Extrai os dados dos resultados visíveis
                results = extract_results(driver, tipo)
                all_results.extend(results)

                logger.info(
                    f"Coleta de '{tipo}' concluída: "
                    f"{len(results)} estabelecimentos encontrados."
                )

            except Exception as e:
                # Se uma busca falhar, registra o erro e continua com o próximo tipo
                logger.error(f"Erro ao processar '{tipo}': {e}")
                logger.warning("Continuando para o próximo tipo de estabelecimento...")
                continue

        # --- Etapa 4: Verificar se houve resultados ---
        logger.info("=" * 60)
        if not all_results:
            logger.warning(
                "Nenhum resultado foi coletado. "
                "Verifique a conexão de internet e os seletores CSS/XPath."
            )
        else:
            logger.info(
                f"TOTAL de estabelecimentos coletados: {len(all_results)}"
            )

        # --- Etapa 5: Salvar resultados em JSON ---
        logger.info("Salvando resultados em JSON...")
        save_json(all_results)

        # --- Etapa 6: Gerar planilha Excel ---
        logger.info("Gerando planilha Excel...")
        generate_excel(all_results)

    except KeyboardInterrupt:
        # Usuário interrompeu a execução (Ctrl+C)
        logger.warning("Execução interrompida pelo usuário (Ctrl+C).")

    except Exception as e:
        # Falha crítica inesperada
        logger.critical(f"Falha crítica na automação: {e}")
        sys.exit(1)

    finally:
        # --- Etapa 7: Encerrar o navegador ---
        if driver:
            close_driver(driver)

        # Registra o tempo total de execução
        elapsed = time.time() - start_time
        logger.info("=" * 60)
        logger.info(f"AUTOMAÇÃO FINALIZADA — Tempo total: {elapsed:.1f}s")
        logger.info(f"Resultados: {len(all_results)} estabelecimentos")
        logger.info(f"Arquivos gerados: {config.OUTPUT_JSON}")
        logger.info(f"                  {config.OUTPUT_EXCEL}")
        logger.info(f"Log completo:     {config.LOG_FILE}")
        logger.info("=" * 60)


if __name__ == "__main__":
    main()
