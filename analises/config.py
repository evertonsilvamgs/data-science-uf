"""Configuração compartilhada dos scripts de análise (caminhos, sementes, códigos)."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DIR_MICRODADOS = RAIZ / "MICRODADOS_SAEB_2023" / "DADOS"
ARQ_ALUNO_9EF = DIR_MICRODADOS / "TS_ALUNO_9EF.csv"
ARQ_ESCOLA = DIR_MICRODADOS / "TS_ESCOLA.csv"

DIR_DADOS = RAIZ / "dados"            # bases derivadas (fora do git)
DIR_RESULTADOS = RAIZ / "resultados"  # tabelas e figuras (versionadas)
ARQ_BASE_ANALITICA = DIR_DADOS / "saeb2023_9ef_publicas.parquet"

SEMENTE = 20231

# Leitura dos CSV do INEP
CSV_SEP = ";"
CSV_ENCODING = "latin-1"

# Códigos de não resposta no questionário: '*' = nulo (marcação inválida), '.' = branco
CODIGOS_AUSENTES = ["*", "."]

# Variáveis de identificação, desenho, proficiência e contexto lidas do TS_ALUNO_9EF
COLS_ID = ["ID_UF", "ID_REGIAO", "ID_AREA", "ID_ESCOLA", "ID_TURMA", "ID_ALUNO",
           "IN_PUBLICA", "ID_LOCALIZACAO"]
COLS_FILTRO = ["IN_SITUACAO_CENSO", "IN_PRESENCA_MT", "IN_PROFICIENCIA_MT",
               "IN_PROFICIENCIA_LP", "IN_PREENCHIMENTO_QUESTIONARIO", "IN_INSE"]
COLS_NUM = ["PESO_ALUNO_MT", "PESO_ALUNO_LP", "PROFICIENCIA_MT_SAEB", "ERRO_PADRAO_MT_SAEB",
            "PROFICIENCIA_LP_SAEB", "ERRO_PADRAO_LP_SAEB", "INSE_ALUNO", "NU_TIPO_NIVEL_INSE"]
COLS_ESTRATO = ["ESTRATO"]
