# Automacao RPA - Google Maps

Automacao em Python que acessa o Google Maps e coleta informacoes de estabelecimentos (academias, restaurantes e sorveterias), gerando relatorios em JSON e Excel.

## Estrutura do Projeto

```
rpa-google-maps/
├── config.py           # Configuracoes e constantes da automacao
├── utils.py            # Funcoes auxiliares (logging, JSON, Excel)
├── scraper.py          # Logica de scraping do Google Maps (Selenium)
├── main.py             # Script principal - executa a automacao
├── requirements.txt    # Dependencias Python
├── README.md           # Este arquivo
├── automation.log      # Log da execucao (gerado automaticamente)
├── resultados.json     # Dados coletados em JSON (gerado automaticamente)
└── resultados.xlsx     # Planilha Excel formatada (gerado automaticamente)
```

## Dependencias

- **Python 3.10+**
- **Google Chrome** instalado na maquina
- Bibliotecas Python (instaladas via pip):
  - `selenium` — Automacao do navegador
  - `webdriver-manager` — Download automatico do ChromeDriver
  - `openpyxl` — Geracao de planilhas Excel

## Instalacao

### 1. Clonar o repositorio

```bash
git clone https://github.com/SEU_USUARIO/rpa-google-maps.git
cd rpa-google-maps
```

### 2. Criar ambiente virtual (recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Verificar o Google Chrome

Certifique-se de que o Google Chrome esta instalado. O ChromeDriver sera baixado automaticamente pelo `webdriver-manager` na primeira execucao.

## Execucao

```bash
python main.py
```

A automacao ira:
1. Abrir o Google Chrome (modo visivel por padrao).
2. Buscar academias, restaurantes e sorveterias em Sao Paulo.
3. Coletar nome, nota, avaliacoes e endereco de cada estabelecimento.
4. Salvar os dados em `resultados.json` e `resultados.xlsx`.
5. Registrar toda a execucao em `automation.log`.

## Configuracoes (config.py)

Para executar em outro computador ou com outras preferencias, edite o arquivo `config.py`:

| Variavel | Descricao | Padrao |
|---|---|---|
| `CIDADE` | Cidade alvo para as buscas | `"São Paulo"` |
| `HEADLESS` | Navegador sem interface grafica | `False` (visivel) |
| `MAX_RESULTADOS_POR_TIPO` | Limite de resultados por categoria | `20` |
| `MAX_SCROLLS` | Quantidade de scrolls para carregar resultados | `5` |
| `TIMEOUT` | Tempo maximo de espera por elementos (segundos) | `15` |
| `SEARCH_INPUT_XPATH` | XPath do campo de busca do Google Maps | `//*[@id="UGojuc"]` |

### O que ajustar em outro computador

- **`CIDADE`**: Altere para a cidade desejada.
- **`HEADLESS`**: Mude para `True` se quiser execucao sem interface grafica (servidores, CI/CD).
- **`SEARCH_INPUT_XPATH`**: Se o Google Maps alterar o ID do campo de busca, atualize este XPath.
- **Google Chrome**: Deve estar instalado. O ChromeDriver e gerenciado automaticamente.

## Logs

O arquivo `automation.log` registra toda a execucao com 5 niveis:

| Nivel | Uso |
|---|---|
| `DEBUG` | Detalhes de depuracao (seletores, scrolls, dados brutos) |
| `INFO` | Eventos normais (inicio, buscas, resultados, finalizacao) |
| `WARNING` | Avisos (dados incompletos, elementos nao encontrados) |
| `ERROR` | Erros recuperaveis (falha em uma busca especifica) |
| `CRITICAL` | Falhas graves que interrompem a automacao |

Formato: `2025-01-28 14:30:00 [INFO] Mensagem aqui`

## Dados Coletados

Para cada estabelecimento:

```json
{
    "nome": "Nome do Estabelecimento",
    "tipo": "academia",
    "nota": "4,5",
    "avaliacoes": "1.234",
    "endereco": "R. Augusta, 1234 - Consolacao, Sao Paulo - SP"
}
```

## Tratamento de Erros

A automacao possui tratativas para:
- **Falha de conexao**: erro ao acessar o Google Maps.
- **Timeout de carregamento**: pagina ou resultados nao carregam no tempo limite.
- **Falha na extracao**: dados ausentes em um card (pula e continua).
- **Erro ao gerar arquivos**: falha ao salvar JSON ou Excel.
- **Interrupcao do usuario**: Ctrl+C encerra a automacao de forma limpa.
