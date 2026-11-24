# Trajetória escolar, tempo de estudo e envolvimento familiar na proficiência em Matemática (Saeb 2023 e PISA 2025)

Pacote de replicação do artigo da disciplina Ciência de Dados II (Centro Universitário de Mineiros – UNIFIMES, Curso de Sistemas de Informação, 2026).

Autores: Everton Silva, Enrique Almeida e Raymora Araujo. Orientador: Ivan Martins.

O estudo analisa a associação entre reprovação, tempo de estudo fora da escola e práticas familiares e a proficiência em Matemática de 1.715.248 estudantes do 9º ano de escolas públicas avaliados pelo Saeb 2023, considerando o nível socioeconômico (INSE). Os padrões são comparados aos indicadores publicados pela OCDE para o Brasil no PISA 2025. Os resultados são associações, e não efeitos causais.

## Estrutura

| Pasta ou arquivo | Conteúdo |
|---|---|
| `analises/` | *Scripts* numerados, executados em ordem |
| `resultados/` | Tabelas (`.csv`) e figuras (`figuras/`) geradas pelos *scripts* |
| `artigo/` | Texto do artigo em Markdown e gerador do `.docx` (`gerar_docx.py`) |
| `DECISOES.md` | Registro das decisões de desenho e de formatação |
| `Relatorio_Deep_Research_Desempenho_Escolar.md` | Relatório de levantamento da literatura e de planejamento |

| *Script* | Etapa |
|---|---|
| `01_preparacao.py` | Filtros da amostra, recodificação do questionário e base analítica |
| `02_descritivas.py` | Médias ponderadas, correlação intraclasse e análise fatorial dos itens sobre a família |
| `03_modelos.py` | Regressões em blocos, efeitos fixos de escola, modelo multinível, interações e robustez (cerca de 18 min) |
| `04_ml_diagnostico.py` | LightGBM com validação cruzada agrupada por escola e valores SHAP |
| `05_pisa_comparacao.py` | Gradiente socioeconômico e quadro comparativo com o PISA 2025 |
| `06_figuras_artigo.py` | Figuras do artigo, a partir das tabelas de `resultados/` |

## Como reproduzir

1. Baixe os microdados do Saeb 2023 no portal do Inep (<https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/saeb>) e extraia-os em `MICRODADOS_SAEB_2023/`, na raiz do projeto, de modo que existam `MICRODADOS_SAEB_2023/DADOS/TS_ALUNO_9EF.csv` e `MICRODADOS_SAEB_2023/DADOS/TS_ESCOLA.csv`. Os microdados não estão no repositório por serem grandes (mais de 3 GB), mas são públicos.
2. Instale as dependências (Python 3.13):

   ```
   pip install -r requirements.txt
   ```

3. Execute os *scripts* em ordem, a partir da pasta `analises/`:

   ```
   cd analises
   python 01_preparacao.py
   python 02_descritivas.py
   python 03_modelos.py
   python 04_ml_diagnostico.py
   python 05_pisa_comparacao.py
   python 06_figuras_artigo.py
   ```

4. Para gerar o artigo em `.docx`, a partir da raiz: `python artigo/gerar_docx.py` (saída em `artigo/saida/`).

A semente aleatória é fixa (`config.py`). A base analítica derivada (`dados/`) é gerada pelo primeiro *script* e não é versionada.

## Ética e privacidade

Foram usados apenas microdados públicos e anonimizados. Os códigos de escola e de município são mascarados pelo Inep, e não houve tentativa de reidentificação. Os resultados são apresentados apenas de forma agregada.
