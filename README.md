# Automação RPA - Google Maps

Automação em Python que acessa o Google Maps e coleta informações de estabelecimentos (academias, restaurantes e sorveterias), gerando relatórios em JSON e Excel.

## Estrutura do Projeto

```
rpa-google-maps/
├── config.py           # Configurações e constantes da automação
├── utils.py            # Funções auxiliares (logging, JSON, Excel)
├── scraper.py          # Lógica de scraping do Google Maps (Selenium)
├── main.py             # Script principal - executa a automação
├── requirements.txt    # Dependências Python
├── README.md           # Este arquivo
├── automation.log      # Log da execução (gerado automaticamente)
├── resultados.json     # Dados coletados em JSON (gerado automaticamente)
└── resultados.xlsx     # Planilha Excel formatada (gerado automaticamente)
```

## Dependências

- **Python 3.10+**
- **Google Chrome** instalado na máquina
- Bibliotecas Python (instaladas via pip):
  - `selenium` — Automação do navegador
  - `openpyxl` — Geração de planilhas Excel

## Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/BrunoSu97/rpa-google-maps.git
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

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Verificar o Google Chrome

Certifique-se de que o Google Chrome está instalado. O ChromeDriver é gerenciado automaticamente pelo Selenium Manager (integrado ao Selenium 4.6+), sem necessidade de download manual.

## Execução

```bash
python main.py
```

A automação irá:
1. Abrir o Google Chrome (modo visível por padrão).
2. Buscar academias, restaurantes e sorveterias em São Paulo.
3. Coletar nome, nota, avaliações e endereço de cada estabelecimento.
4. Salvar os dados em `resultados.json` e `resultados.xlsx`.
5. Registrar toda a execução em `automation.log`.

## Configurações (config.py)

Para executar em outro computador ou com outras preferências, edite o arquivo `config.py`:

| Variável | Descrição | Padrão |
|---|---|---|
| `CIDADE` | Cidade alvo para as buscas | `"São Paulo"` |
| `HEADLESS` | Navegador sem interface gráfica | `False` (visível) |
| `MAX_RESULTADOS_POR_TIPO` | Limite de resultados por categoria | `20` |
| `MAX_SCROLLS` | Quantidade de scrolls para carregar resultados | `5` |
| `TIMEOUT` | Tempo máximo de espera por elementos (segundos) | `15` |
| `SEARCH_INPUT_XPATH` | XPath do campo de busca do Google Maps | `//*[@id="UGojuc"]` |

### O que ajustar em outro computador

- **`CIDADE`**: Altere para a cidade desejada.
- **`HEADLESS`**: Mude para `True` se quiser execução sem interface gráfica (servidores, CI/CD).
- **`SEARCH_INPUT_XPATH`**: Se o Google Maps alterar o ID do campo de busca, atualize este XPath.
- **Google Chrome**: Deve estar instalado. O ChromeDriver é gerenciado automaticamente pelo Selenium.

## Logs

O arquivo `automation.log` registra toda a execução com 5 níveis:

| Nível | Uso |
|---|---|
| `DEBUG` | Detalhes de depuração (seletores, scrolls, dados brutos) |
| `INFO` | Eventos normais (início, buscas, resultados, finalização) |
| `WARNING` | Avisos (dados incompletos, elementos não encontrados) |
| `ERROR` | Erros recuperáveis (falha em uma busca específica) |
| `CRITICAL` | Falhas graves que interrompem a automação |

Formato: `2026-01-28 14:30:00 [INFO] Mensagem aqui`

## Dados Coletados

Para cada estabelecimento:

```json
{
    "nome": "BW Academia | Santana - Zona Norte - São Paulo",
    "tipo": "academia",
    "nota": "4,9",
    "avaliacoes": "1.293",
    "endereco": "R. Mateus Leme, 114"
}
```

## Tratamento de Erros

A automação possui tratativas para:
- **Falha de conexão**: erro ao acessar o Google Maps.
- **Timeout de carregamento**: página ou resultados não carregam no tempo limite.
- **Falha na extração**: dados ausentes em um card (pula e continua).
- **Erro ao gerar arquivos**: falha ao salvar JSON ou Excel.
- **Interrupção do usuário**: Ctrl+C encerra a automação de forma limpa.
