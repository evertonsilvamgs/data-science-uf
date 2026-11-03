"""Etapa 1 - Preparação da base analítica (SAEB 2023, 9º ano EF, escolas públicas).

Entrada : MICRODADOS_SAEB_2023/DADOS/TS_ALUNO_9EF.csv e TS_ESCOLA.csv (INEP)
Saídas  : dados/saeb2023_9ef_publicas.parquet       base analítica (antes dos casos completos)
          resultados/tab_fluxo_amostra.csv          contagens de cada filtro
          resultados/tab_ausentes.csv               % de ausentes e proficiência média por condição
          resultados/tab_pesos.csv                  distribuição dos pesos amostrais
"""
import numpy as np
import pandas as pd

import config as cfg

# --------------------------------------------------------------------------------------
# Recodificações do questionário (dicionário Saeb 2023, aba TS_ALUNO_9EF)
# --------------------------------------------------------------------------------------
MAP_SEXO = {"A": "Masculino", "B": "Feminino", "C": "Não declarou"}
MAP_IDADE = {"A": 13, "B": 14, "C": 15, "D": 16, "E": 17, "F": 18}  # A = 13 ou menos; F = 18 ou mais
MAP_RACA = {"A": "Branca", "B": "Preta", "C": "Parda", "D": "Amarela", "E": "Indígena", "F": "Não declarou"}
MAP_SIM_NAO = {"A": 0, "B": 1}
MAP_ESCOL_PAIS = {"A": "Até 4º ano EF", "B": "EF até 5º ano", "C": "EF completo",
                  "D": "EM completo", "E": "Superior completo", "F": "Não sabe"}
MAP_FREQ3 = {"A": 0, "B": 1, "C": 2}            # nunca/quase nunca, de vez em quando, sempre/quase sempre
MAP_IDADE_ENTRADA = {"A": "3 anos ou menos", "B": "4 ou 5 anos", "C": "6 ou 7 anos", "D": "8 anos ou mais"}
MAP_VEZES = {"A": 0, "B": 1, "C": 2}            # nunca, uma vez, duas vezes ou mais
MAP_TEMPO = {"A": 0, "B": 1, "C": 2, "D": 3}    # não usa, <1h, 1-2h, >2h
MAP_CONCORDA = {"A": 3, "B": 2, "C": 1, "D": 0}  # invertido: maior = mais concordância

ROTULO_REPROV = {0: "Nunca", 1: "Uma vez", 2: "Duas ou mais"}
ROTULO_TEMPO = {0: "Não estuda", 1: "Menos de 1h", 2: "Entre 1 e 2h", 3: "Mais de 2h"}

QUESTOES = ["Q01", "Q02", "Q04", "Q05a", "Q05b", "Q08", "Q09",
            "Q10a", "Q10b", "Q10c", "Q10d", "Q10e", "Q10f",
            "Q17", "Q19", "Q20", "Q21a", "Q21b", "Q21c", "Q21d", "Q21e",
            "Q23a", "Q23b", "Q23h"]
COLS_Q = [f"TX_RESP_{q}" for q in QUESTOES]


def ler_alunos() -> pd.DataFrame:
    cols = cfg.COLS_ID + cfg.COLS_FILTRO + cfg.COLS_NUM + cfg.COLS_ESTRATO + COLS_Q
    dtypes = {c: "category" for c in COLS_Q + cfg.COLS_ESTRATO}
    dtypes.update({c: "float64" for c in cfg.COLS_NUM})
    df = pd.read_csv(cfg.ARQ_ALUNO_9EF, sep=cfg.CSV_SEP, encoding=cfg.CSV_ENCODING,
                     usecols=cols, dtype=dtypes)
    return df


def ler_escolas() -> pd.DataFrame:
    cols = ["ID_ESCOLA", "PC_FORMACAO_DOCENTE_FINAL", "NIVEL_SOCIO_ECONOMICO",
            "NU_MATRICULADOS_CENSO_9EF", "NU_PRESENTES_9EF", "TAXA_PARTICIPACAO_9EF"]
    esc = pd.read_csv(cfg.ARQ_ESCOLA, sep=cfg.CSV_SEP, encoding=cfg.CSV_ENCODING,
                      usecols=cols, dtype=str)
    for c in cols[1:]:
        if c != "NIVEL_SOCIO_ECONOMICO":
            esc[c] = pd.to_numeric(esc[c].str.replace(",", "."), errors="coerce")
    esc["ID_ESCOLA"] = esc["ID_ESCOLA"].astype("int64")
    return esc.rename(columns={
        "PC_FORMACAO_DOCENTE_FINAL": "esc_afd_anos_finais",
        "NIVEL_SOCIO_ECONOMICO": "esc_inse_nivel",
        "NU_MATRICULADOS_CENSO_9EF": "esc_matriculados_9ef",
        "NU_PRESENTES_9EF": "esc_presentes_9ef",
        "TAXA_PARTICIPACAO_9EF": "esc_taxa_participacao_9ef"})


def aplicar_filtros(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Aplica os filtros em sequência e registra quantos alunos e escolas restam."""
    etapas = [
        ("Registros no TS_ALUNO_9EF", None),
        ("Escolas públicas (IN_PUBLICA = 1)", df["IN_PUBLICA"] == 1),
        ("Consistente com o Censo Escolar (IN_SITUACAO_CENSO = 1)", df["IN_SITUACAO_CENSO"] == 1),
        ("Presente na prova de MT (IN_PRESENCA_MT = 1)", df["IN_PRESENCA_MT"] == 1),
        ("Proficiência MT calculada (IN_PROFICIENCIA_MT = 1)", df["IN_PROFICIENCIA_MT"] == 1),
        ("Peso amostral de MT não nulo", df["PESO_ALUNO_MT"].notna()),
        ("Questionário preenchido (IN_PREENCHIMENTO_QUESTIONARIO = 1)", df["IN_PREENCHIMENTO_QUESTIONARIO"] == 1),
    ]
    mascara = pd.Series(True, index=df.index)
    linhas = []
    for nome, cond in etapas:
        if cond is not None:
            mascara &= cond
        sub = df.loc[mascara]
        linhas.append({"etapa": nome, "alunos": len(sub), "escolas": sub["ID_ESCOLA"].nunique()})
    fluxo = pd.DataFrame(linhas)
    fluxo["perda_alunos"] = -fluxo["alunos"].diff().fillna(0).astype(int)
    return df.loc[mascara].copy(), fluxo


def recodificar(df: pd.DataFrame) -> pd.DataFrame:
    q = lambda nome: df[f"TX_RESP_{nome}"].astype("string").replace(cfg.CODIGOS_AUSENTES, pd.NA)
    out = pd.DataFrame(index=df.index)

    # Identificação, desenho e desfechos
    out["id_aluno"] = df["ID_ALUNO"].astype("int64")
    out["id_escola"] = df["ID_ESCOLA"].astype("int64")
    out["id_turma"] = df["ID_TURMA"].astype("int64")
    out["uf"] = df["ID_UF"].astype("int64")
    out["regiao"] = df["ID_REGIAO"].astype("int64")
    out["rural"] = (df["ID_LOCALIZACAO"] == 2).astype("int8")
    out["capital"] = (df["ID_AREA"] == 1).astype("int8")
    out["estrato"] = df["ESTRATO"].astype("string")
    out["peso_mt"] = df["PESO_ALUNO_MT"]
    out["peso_lp"] = df["PESO_ALUNO_LP"]
    out["prof_mt"] = df["PROFICIENCIA_MT_SAEB"]
    out["ep_mt"] = df["ERRO_PADRAO_MT_SAEB"]
    out["prof_lp"] = df["PROFICIENCIA_LP_SAEB"].where(df["IN_PROFICIENCIA_LP"] == 1)
    out["ep_lp"] = df["ERRO_PADRAO_LP_SAEB"].where(df["IN_PROFICIENCIA_LP"] == 1)
    out["inse"] = df["INSE_ALUNO"].where(df["IN_INSE"] == 1)
    out["inse_nivel"] = df["NU_TIPO_NIVEL_INSE"].where(df["IN_INSE"] == 1)

    # Demografia
    out["sexo"] = q("Q01").map(MAP_SEXO).astype("category")
    out["idade"] = q("Q02").map(MAP_IDADE).astype("Int8")
    out["raca"] = q("Q04").map(MAP_RACA).astype("category")
    out["deficiencia"] = q("Q05a").map(MAP_SIM_NAO).astype("Int8")
    out["tea"] = q("Q05b").map(MAP_SIM_NAO).astype("Int8")
    out["escol_mae"] = q("Q08").map(MAP_ESCOL_PAIS).astype("category")
    out["escol_pai"] = q("Q09").map(MAP_ESCOL_PAIS).astype("category")
    out["idade_entrada"] = q("Q17").map(MAP_IDADE_ENTRADA).astype("category")

    # Trajetória escolar (proxy de continuidade/frequência)
    out["reprov"] = q("Q19").map(MAP_VEZES).astype("Int8")
    out["aband"] = q("Q20").map(MAP_VEZES).astype("Int8")
    # 9º ano em 2023: idade esperada 14 anos; distorção = 2+ anos acima (convenção do Inep)
    out["distorcao"] = (out["idade"] >= 16).astype("Int8").where(out["idade"].notna())
    out["traj_irregular"] = ((out["reprov"] > 0) | (out["aband"] > 0)).astype("Int8")
    out.loc[out["reprov"].isna() & out["aband"].isna(), "traj_irregular"] = pd.NA

    # Uso do tempo fora da escola em dias de aula
    out["estudo"] = q("Q21a").map(MAP_TEMPO).astype("Int8")
    out["extracurricular"] = q("Q21b").map(MAP_TEMPO).astype("Int8")
    out["trab_domestico"] = q("Q21c").map(MAP_TEMPO).astype("Int8")
    out["trab_fora"] = q("Q21d").map(MAP_TEMPO).astype("Int8")
    out["lazer"] = q("Q21e").map(MAP_TEMPO).astype("Int8")

    # Envolvimento familiar (0 = nunca/quase nunca ... 2 = sempre/quase sempre)
    for nome, item in [("fam_le", "Q10a"), ("fam_conversa", "Q10b"), ("fam_inc_estudar", "Q10c"),
                       ("fam_inc_tarefa", "Q10d"), ("fam_inc_comparecer", "Q10e"), ("fam_reunioes", "Q10f")]:
        out[nome] = q(item).map(MAP_FREQ3).astype("Int8")

    # Engajamento e expectativa docente (reservados; fora do modelo principal)
    out["interesse"] = q("Q23a").map(MAP_CONCORDA).astype("Int8")
    out["motivacao"] = q("Q23b").map(MAP_CONCORDA).astype("Int8")
    out["prof_acreditam"] = q("Q23h").map(MAP_CONCORDA).astype("Int8")

    # Rótulos categóricos com categoria de referência na primeira posição
    out["reprov_cat"] = pd.Categorical(out["reprov"].map(ROTULO_REPROV),
                                       categories=list(ROTULO_REPROV.values()))
    out["estudo_cat"] = pd.Categorical(out["estudo"].map(ROTULO_TEMPO),
                                       categories=list(ROTULO_TEMPO.values()))
    return out


def media_ponderada(valores: pd.Series, pesos: pd.Series) -> float:
    ok = valores.notna() & pesos.notna()
    return np.average(valores[ok].astype(float), weights=pesos[ok]) if ok.any() else np.nan


def contexto_escolar(df: pd.DataFrame) -> pd.DataFrame:
    """Médias ponderadas por escola (efeitos de composição), calculadas na base de públicas."""
    fontes = {
        "esc_inse_medio": df["inse"].astype("float64"),
        "esc_pct_reprov": (df["reprov"] > 0).astype("float64").where(df["reprov"].notna()),
        "esc_estudo_medio": df["estudo"].astype("float64"),
    }
    aux = pd.DataFrame({"id_escola": df["id_escola"]})
    for nome, v in fontes.items():
        w = df["peso_mt"].where(v.notna())
        aux[f"{nome}_wx"] = v * w
        aux[f"{nome}_w"] = w
    g = aux.groupby("id_escola")
    soma = g.sum(min_count=1)
    ctx = pd.DataFrame({"esc_n_alunos": g.size()})
    for nome in fontes:
        ctx[nome] = soma[f"{nome}_wx"] / soma[f"{nome}_w"]
    return ctx.reset_index()


def tabela_ausentes(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    linhas = []
    for c in cols:
        aus = df[c].isna()
        linhas.append({
            "variavel": c,
            "pct_ausente": round(100 * aus.mean(), 2),
            "prof_mt_presentes": round(media_ponderada(df.loc[~aus, "prof_mt"], df.loc[~aus, "peso_mt"]), 1),
            "prof_mt_ausentes": round(media_ponderada(df.loc[aus, "prof_mt"], df.loc[aus, "peso_mt"]), 1),
        })
    return pd.DataFrame(linhas)


def main() -> None:
    cfg.DIR_DADOS.mkdir(exist_ok=True)
    cfg.DIR_RESULTADOS.mkdir(exist_ok=True)

    brutos = ler_alunos()
    assert brutos["ID_ALUNO"].is_unique, "ID_ALUNO duplicado no TS_ALUNO_9EF"
    filtrados, fluxo = aplicar_filtros(brutos)
    del brutos

    base = recodificar(filtrados)
    del filtrados
    base = base.merge(contexto_escolar(base), on="id_escola", how="left", validate="m:1")
    base = base.merge(ler_escolas(), left_on="id_escola", right_on="ID_ESCOLA", how="left",
                      validate="m:1").drop(columns="ID_ESCOLA")

    # Casos completos para o modelo principal (registrado no fluxo; a base salva mantém todos)
    vars_modelo = ["prof_mt", "inse", "sexo", "raca", "deficiencia", "reprov", "aband", "estudo",
                   "fam_le", "fam_conversa", "fam_inc_estudar", "fam_inc_tarefa", "fam_inc_comparecer",
                   "fam_reunioes", "idade_entrada", "trab_fora"]
    completos = base[vars_modelo].notna().all(axis=1)
    base["caso_completo"] = completos.astype("int8")
    fluxo.loc[len(fluxo)] = {"etapa": "Casos completos nas variáveis do modelo principal",
                             "alunos": int(completos.sum()),
                             "escolas": base.loc[completos, "id_escola"].nunique(),
                             "perda_alunos": int((~completos).sum())}

    base.to_parquet(cfg.ARQ_BASE_ANALITICA, index=False)
    fluxo.to_csv(cfg.DIR_RESULTADOS / "tab_fluxo_amostra.csv", index=False)
    tabela_ausentes(base, vars_modelo[1:] + ["distorcao", "escol_mae"]) \
        .to_csv(cfg.DIR_RESULTADOS / "tab_ausentes.csv", index=False)
    q = base["peso_mt"].quantile([0, .01, .05, .25, .5, .75, .95, .99, 1]).round(3)
    pd.DataFrame({"quantil": q.index, "peso_mt": q.values}).to_csv(
        cfg.DIR_RESULTADOS / "tab_pesos.csv", index=False)

    print(fluxo.to_string(index=False))
    print(f"\nBase salva em {cfg.ARQ_BASE_ANALITICA} ({len(base):,} linhas, {base.shape[1]} colunas)")
    print(f"Pesos > 5: {(base['peso_mt'] > 5).sum()} alunos")


if __name__ == "__main__":
    main()
