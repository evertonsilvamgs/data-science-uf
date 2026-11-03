"""Etapa 3 - Modelos explicativos da proficiência em Matemática (H1-H5).

Entrada : dados/saeb2023_9ef_publicas.parquet
Saídas  : resultados/tab_modelos_coef.csv     coeficientes de todos os modelos (pontos e DP, IC95%)
          resultados/tab_modelos_ajuste.csv   N, R² e R² intra de cada modelo
          resultados/tab_multinivel.csv       modelo multinível (efeitos fixos e componentes de variância)
          resultados/figuras/fig_coef_mqo_ef.jpg
          resultados/figuras/fig_interacao_inse.jpg

Modelos (pesos PESO_ALUNO_MT; erros-padrão agrupados por escola):
  B0  só INSE (comparação com o ESCS do PISA)
  B1  controles + EF de UF  |  B2 +INSE  |  B3 +trajetória  |  B4 +estudo  |  B5 +família
  EF  B5 com efeitos fixos de escola (comparação dentro da escola, H4)
  INT EF + interações com o INSE (H5)
  Robustez: LP; sem peso; peso aparado (p99); distorção no lugar da reprovação; ausentes como categoria
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pyfixest as pf
import statsmodels.formula.api as smf

import config as cfg

DIR_FIG = cfg.DIR_RESULTADOS / "figuras"
AZUL, LARANJA = "#2a78d6", "#eb6834"          # slots 1 e 2 da paleta categórica (dataviz)
TINTA, TINTA_2, MUDO, GRADE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9"

# --------------------------------------------------------------------------------------
# Variáveis indicadoras (categoria de referência omitida)
# --------------------------------------------------------------------------------------
CONTROLES = ["sexo_fem", "sexo_nd", "raca_preta", "raca_parda", "raca_amarela", "raca_indigena", "raca_nd",
             "deficiencia", "ent_ate3", "ent_6a7", "ent_8mais", "tf_menos1h", "tf_1a2h", "tf_mais2h",
             "rural", "capital"]
INSE = ["inse_z"]
TRAJETORIA = ["rep_1", "rep_2mais", "aband_sim"]
ESTUDO = ["est_menos1h", "est_1a2h", "est_mais2h"]
FAMILIA = ["incentivo_z", "conv_vezes", "conv_sempre", "le_vezes", "le_sempre", "reun_vezes", "reun_sempre"]

ROTULOS = {
    "inse_z": "INSE (+1 DP)",
    "rep_1": "Reprovado uma vez", "rep_2mais": "Reprovado duas ou mais vezes", "aband_sim": "Já abandonou a escola",
    "dist_sim": "Distorção idade-série",
    "est_menos1h": "Estuda menos de 1h", "est_1a2h": "Estuda de 1 a 2h", "est_mais2h": "Estuda mais de 2h",
    "incentivo_z": "Incentivo dos pais (+1 DP)",
    "conv_vezes": "Conversam sobre a escola: às vezes", "conv_sempre": "Conversam sobre a escola: sempre",
    "le_vezes": "Pais leem: às vezes", "le_sempre": "Pais leem: sempre",
    "reun_vezes": "Vão às reuniões: às vezes", "reun_sempre": "Vão às reuniões: sempre",
}


def _z(x: pd.Series, w: pd.Series) -> pd.Series:
    ok = x.notna()
    m = np.average(x[ok], weights=w[ok])
    dp = np.sqrt(np.average((x[ok] - m) ** 2, weights=w[ok]))
    return (x - m) / dp


def montar(df: pd.DataFrame) -> pd.DataFrame:
    """Cria as indicadoras e os escores padronizados. Ausentes ficam NaN (tratados por quem chama)."""
    out = df[["id_escola", "uf", "peso_mt", "prof_mt", "prof_lp", "peso_lp", "rural", "capital",
              "inse", "esc_inse_medio", "esc_pct_reprov", "esc_estudo_medio"]].copy()

    def ind(serie, valor):
        return (serie == valor).astype("float").where(serie.notna())

    out["sexo_fem"], out["sexo_nd"] = ind(df["sexo"], "Feminino"), ind(df["sexo"], "Não declarou")
    for rot, nome in [("Preta", "preta"), ("Parda", "parda"), ("Amarela", "amarela"),
                      ("Indígena", "indigena"), ("Não declarou", "nd")]:
        out[f"raca_{nome}"] = ind(df["raca"], rot)
    out["deficiencia"] = df["deficiencia"].astype("float")
    for rot, nome in [("3 anos ou menos", "ate3"), ("6 ou 7 anos", "6a7"), ("8 anos ou mais", "8mais")]:
        out[f"ent_{nome}"] = ind(df["idade_entrada"], rot)
    for v, nome in [(1, "menos1h"), (2, "1a2h"), (3, "mais2h")]:
        out[f"tf_{nome}"] = ind(df["trab_fora"], v)
        out[f"est_{nome}"] = ind(df["estudo"], v)
    out["rep_1"], out["rep_2mais"] = ind(df["reprov"], 1), ind(df["reprov"], 2)
    out["aband_sim"] = (df["aband"] > 0).astype("float").where(df["aband"].notna())
    out["dist_sim"] = df["distorcao"].astype("float")
    for item, nome in [("fam_conversa", "conv"), ("fam_le", "le"), ("fam_reunioes", "reun")]:
        out[f"{nome}_vezes"], out[f"{nome}_sempre"] = ind(df[item], 1), ind(df[item], 2)
    # Índice de incentivo (AFE, etapa 2): média de Q10c, Q10d e Q10e, padronizada
    out["incentivo"] = df[["fam_inc_estudar", "fam_inc_tarefa", "fam_inc_comparecer"]].astype("float").mean(axis=1, skipna=False)
    out["inse_z"] = _z(out["inse"], out["peso_mt"])
    out["incentivo_z"] = _z(out["incentivo"], out["peso_mt"])
    return out


# --------------------------------------------------------------------------------------
# Estimação
# --------------------------------------------------------------------------------------
def ajustar(df, nome, x, y="prof_mt", fe="uf", peso="peso_mt", dp_y=None):
    formula = f"{y} ~ {' + '.join(x)}" + (f" | {fe}" if fe else "")
    fit = pf.feols(formula, data=df, weights=peso, vcov={"CRV1": "id_escola"})
    tab = fit.tidy().reset_index().rename(columns={"Coefficient": "termo", "Estimate": "coef",
                                                   "Std. Error": "ep", "2.5%": "ic_inf", "97.5%": "ic_sup",
                                                   "Pr(>|t|)": "p"})
    tab = tab[["termo", "coef", "ep", "ic_inf", "ic_sup", "p"]]
    tab.insert(0, "modelo", nome)
    if dp_y:
        for c in ("coef", "ic_inf", "ic_sup"):
            tab[f"{c}_dp"] = tab[c] / dp_y
    ajuste = {"modelo": nome, "desfecho": y, "efeitos_fixos": fe or "-", "peso": peso or "-",
              "n": fit._N, "r2": fit._r2, "r2_intra": fit._r2_within if fe else np.nan}
    print(f"  {nome:<28} N={fit._N:>9,}  R²={fit._r2:.3f}")
    return tab, ajuste


def multinivel(df, rng):
    """Intercepto aleatório em amostra de 3.000 escolas estratificada por UF (não ponderado)."""
    escolas = df[["id_escola", "uf"]].drop_duplicates()
    amostra = escolas.groupby("uf", group_keys=False).apply(
        lambda d: d.sample(frac=3000 / len(escolas), random_state=int(rng.integers(1e9))))
    sub = df[df["id_escola"].isin(amostra["id_escola"])].copy()
    # centragem na média da escola (CWC) e preditores de nível 2 padronizados
    sub["inse_cwc"] = sub["inse_z"] - sub.groupby("id_escola")["inse_z"].transform("mean")
    for c in ("esc_inse_medio", "esc_pct_reprov", "esc_estudo_medio"):
        sub[f"{c}_z"] = (sub[c] - sub[c].mean()) / sub[c].std()
    nivel1 = CONTROLES + ["inse_cwc"] + TRAJETORIA + ESTUDO + FAMILIA
    nivel2 = ["esc_inse_medio_z", "esc_pct_reprov_z", "esc_estudo_medio_z"]
    nulo = smf.mixedlm("prof_mt ~ 1", sub, groups=sub["id_escola"]).fit(reml=True)
    cheio = smf.mixedlm("prof_mt ~ " + " + ".join(nivel1 + nivel2 + ["C(uf)"]), sub,
                        groups=sub["id_escola"]).fit(reml=True)
    t0, s0 = float(nulo.cov_re.iloc[0, 0]), float(nulo.scale)
    t1, s1 = float(cheio.cov_re.iloc[0, 0]), float(cheio.scale)
    ci = cheio.conf_int()
    tab = pd.DataFrame({"termo": cheio.params.index, "coef": cheio.params.values, "ep": cheio.bse.values,
                        "ic_inf": ci[0].values, "ic_sup": ci[1].values, "p": cheio.pvalues.values})
    tab = tab[~tab["termo"].str.startswith(("C(uf)", "Group"))]
    comp = pd.DataFrame([
        {"termo": "escolas", "coef": sub["id_escola"].nunique()}, {"termo": "alunos", "coef": len(sub)},
        {"termo": "tau2_nulo", "coef": t0}, {"termo": "sigma2_nulo", "coef": s0},
        {"termo": "icc_nulo", "coef": t0 / (t0 + s0)},
        {"termo": "tau2_completo", "coef": t1}, {"termo": "sigma2_completo", "coef": s1},
        {"termo": "pct_variancia_entre_escolas_explicada", "coef": 100 * (1 - t1 / t0)},
        {"termo": "pct_variancia_intra_escolas_explicada", "coef": 100 * (1 - s1 / s0)},
    ])
    return pd.concat([tab, comp], ignore_index=True)


# --------------------------------------------------------------------------------------
# Figuras
# --------------------------------------------------------------------------------------
def _br(v, casas=0):
    return f"{v:.{casas}f}".replace(".", ",").replace("-", "−")


def figura_coef(coef, destino):
    termos = TRAJETORIA + ESTUDO + FAMILIA
    a = coef[coef["modelo"] == "B5"].set_index("termo").loc[termos]
    b = coef[coef["modelo"] == "EF escola"].set_index("termo").loc[termos]
    y = np.arange(len(termos))[::-1]
    fig, ax = plt.subplots(figsize=(8.5, 6.2), constrained_layout=True)
    ax.axvline(0, color=MUDO, linewidth=1)
    for d, cor, desloc, rot in ((a, AZUL, 0.17, "Entre todos os alunos (MQO, B5)"),
                                (b, LARANJA, -0.17, "Dentro da mesma escola (efeitos fixos)")):
        ax.hlines(y + desloc, d["ic_inf"], d["ic_sup"], color=cor, linewidth=2)
        ax.plot(d["coef"], y + desloc, "o", color=cor, markersize=6, markeredgecolor="white",
                markeredgewidth=1.5, label=rot)
    ax.set_yticks(y, [ROTULOS[t] for t in termos])
    ax.set_xlabel("Diferença na proficiência em Matemática (pontos Saeb) e IC 95%", fontsize=9, color=TINTA_2)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: _br(v)))
    ax.grid(axis="x", color=GRADE, linewidth=0.6); ax.set_axisbelow(True)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(colors=TINTA_2, labelsize=8.5, length=0)
    ax.legend(frameon=False, fontsize=8.5, loc="upper right")
    fig.savefig(destino, dpi=300, pil_kwargs={"quality": 95})
    plt.close(fig)


def figura_interacao(coef, destino):
    """Diferença associada à reprovação e ao estudo de 1-2h, conforme o INSE (-2 a +2 DP)."""
    d = coef[coef["modelo"] == "Interações INSE"].set_index("termo")["coef"]
    z = np.linspace(-2, 2, 41)
    series = [("rep_1", "Reprovado uma vez", AZUL), ("est_1a2h", "Estuda de 1 a 2h", LARANJA)]
    fig, ax = plt.subplots(figsize=(7.5, 4), constrained_layout=True)
    ax.axhline(0, color=MUDO, linewidth=1)
    for termo, rot, cor in series:
        efeito = d[termo] + d[f"{termo}:inse_z"] * z
        ax.plot(z, efeito, color=cor, linewidth=2)
        ax.text(2.05, efeito[-1], rot, color=TINTA_2, fontsize=8.5, va="center")
    ax.set_xlabel("INSE do estudante (desvios-padrão em relação à média)", fontsize=9, color=TINTA_2)
    ax.set_ylabel("Diferença em pontos Saeb", fontsize=9, color=TINTA_2)
    ax.set_xlim(-2, 2.9)
    for eixo in (ax.xaxis, ax.yaxis):
        eixo.set_major_formatter(plt.FuncFormatter(lambda v, _: _br(v)))
    ax.grid(axis="y", color=GRADE, linewidth=0.6)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(colors=TINTA_2, labelsize=8.5)
    fig.savefig(destino, dpi=300, pil_kwargs={"quality": 95})
    plt.close(fig)


# --------------------------------------------------------------------------------------
def main() -> None:
    rng = np.random.default_rng(cfg.SEMENTE)
    base = pd.read_parquet(cfg.ARQ_BASE_ANALITICA)
    df = montar(base[base["caso_completo"] == 1])
    dp_y = np.sqrt(np.average((df["prof_mt"] - np.average(df["prof_mt"], weights=df["peso_mt"])) ** 2,
                              weights=df["peso_mt"]))
    print(f"Casos completos: {len(df):,}; DP ponderado de MT = {dp_y:.2f}")

    tabs, ajustes = [], []

    def rodar(*args, **kw):
        t, a = ajustar(*args, dp_y=dp_y, **kw)
        tabs.append(t); ajustes.append(a)

    # Blocos (H1-H3) e comparação com o PISA (B0)
    rodar(df, "B0 (só INSE)", INSE, fe=None)
    blocos = [CONTROLES, INSE, TRAJETORIA, ESTUDO, FAMILIA]
    for i in range(1, 6):
        rodar(df, f"B{i}", sum(blocos[:i], []))
    completo = sum(blocos, [])
    # Dentro da escola (H4) e heterogeneidade por NSE (H5)
    sem_escola = [v for v in completo if v not in ("rural", "capital")]
    rodar(df, "EF escola", sem_escola, fe="id_escola")
    interacoes = [f"{t}:inse_z" for t in TRAJETORIA + ESTUDO]
    rodar(df, "Interações INSE", sem_escola + interacoes, fe="id_escola")

    # Robustez
    rodar(df.dropna(subset=["prof_lp", "peso_lp"]), "Rob. LP (B5)", completo, y="prof_lp", peso="peso_lp")
    rodar(df.dropna(subset=["prof_lp", "peso_lp"]), "Rob. LP (EF)", sem_escola, y="prof_lp",
          fe="id_escola", peso="peso_lp")
    rodar(df, "Rob. sem peso (B5)", completo, peso=None)
    df["peso_aparado"] = df["peso_mt"].clip(upper=df["peso_mt"].quantile(0.99))
    rodar(df, "Rob. peso aparado p99 (B5)", completo, peso="peso_aparado")
    rodar(df.dropna(subset=["dist_sim"]), "Rob. distorção (B5)", [v for v in completo if not v.startswith("rep_")] + ["dist_sim"])

    # Ausentes como categoria (toda a base com questionário)
    todos = montar(base)
    todos = todos[todos["prof_mt"].notna()].copy()
    for v in completo:
        aus = todos[v].isna()
        if aus.any():
            todos[f"{v}_aus"] = aus.astype("float")
            todos[v] = todos[v].fillna(0.0)
    extra = [c for c in todos.columns if c.endswith("_aus")]
    # indicadoras de ausência duplicadas (mesmo item) são colineares: mantém uma por padrão distinto
    extra = list(pd.Series(extra, index=extra)[~todos[extra].T.duplicated()].index)
    rodar(todos, "Rob. ausentes como categoria (B5)", completo + extra)

    coef = pd.concat(tabs, ignore_index=True)
    coef.round(4).to_csv(cfg.DIR_RESULTADOS / "tab_modelos_coef.csv", index=False)
    pd.DataFrame(ajustes).round(4).to_csv(cfg.DIR_RESULTADOS / "tab_modelos_ajuste.csv", index=False)

    # Multinível (composição escolar)
    print("  Multinível (3.000 escolas)...")
    multinivel(df, rng).round(4).to_csv(cfg.DIR_RESULTADOS / "tab_multinivel.csv", index=False)

    figura_coef(coef, DIR_FIG / "fig_coef_mqo_ef.jpg")
    figura_interacao(coef, DIR_FIG / "fig_interacao_inse.jpg")
    print("Etapa 3 concluída.")


if __name__ == "__main__":
    main()
