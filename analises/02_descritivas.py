"""Etapa 2 - Análise descritiva, correlação intraclasse e validação dos índices de família.

Entrada : dados/saeb2023_9ef_publicas.parquet (gerado por 01_preparacao.py)
Saídas  : resultados/tab_descritivas.csv        % ponderado e média de MT (IC95% por cluster de escola)
          resultados/tab_desfecho.csv           resumo ponderado da proficiência e do INSE
          resultados/tab_icc.csv                correlação intraclasse (ANOVA e modelo nulo multinível)
          resultados/tab_afe_cargas.csv         cargas fatoriais dos itens Q10 (metades A e B)
          resultados/tab_afe_resumo.csv         autovalores, congruência de Tucker e ômega
          resultados/figuras/fig_gradientes.jpg
          resultados/figuras/fig_familia.jpg
          resultados/figuras/fig_distribuicao_inse.jpg
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import factor_analyzer.factor_analyzer as _fa_mod
from factor_analyzer import FactorAnalyzer
from scipy.optimize import minimize_scalar
from scipy.stats import multivariate_normal, norm

import config as cfg

DIR_FIG = cfg.DIR_RESULTADOS / "figuras"

# factor_analyzer 0.5 chama check_array(force_all_finite=...), renomeado para ensure_all_finite
# no scikit-learn >= 1.8. Adaptador local, para não fixar uma versão antiga do scikit-learn.
_check_array_original = _fa_mod.check_array


def _check_array_compat(*args, force_all_finite=None, **kwargs):
    if force_all_finite is not None:
        kwargs["ensure_all_finite"] = force_all_finite
    return _check_array_original(*args, **kwargs)


_fa_mod.check_array = _check_array_compat

# Paleta (skill dataviz, instância de referência; modo claro para impressão)
AZUL = "#2a78d6"
RAMPA_AZUL = ["#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#104281"]
TINTA, TINTA_2, MUDO, GRADE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
XLIM_COMUM = (220, 278)  # mesma escala nas figuras de gradiente, para não exagerar diferenças pequenas


def _br(valor, casas=1):
    """Número no padrão brasileiro (vírgula decimal)."""
    return f"{valor:.{casas}f}".replace(".", ",")


def _formatar_eixo_br(eixo):
    from matplotlib.ticker import FuncFormatter
    eixo.set_major_formatter(FuncFormatter(lambda v, _: _br(v, 0) if float(v).is_integer() else _br(v, 3)))

ITENS_FAMILIA = {
    "fam_le": "Pais leem em casa",
    "fam_conversa": "Conversam sobre a escola",
    "fam_inc_estudar": "Incentivam a estudar",
    "fam_inc_tarefa": "Incentivam a fazer a tarefa",
    "fam_inc_comparecer": "Incentivam a comparecer às aulas",
    "fam_reunioes": "Vão às reuniões da escola",
}
ROTULO_FREQ3 = {0: "Nunca ou quase nunca", 1: "De vez em quando", 2: "Sempre ou quase sempre"}
ROTULO_ABAND = {0: "Nunca", 1: "Uma vez", 2: "Duas ou mais"}
ROTULO_TEMPO = {0: "Não usa", 1: "Menos de 1h", 2: "Entre 1 e 2h", 3: "Mais de 2h"}


# --------------------------------------------------------------------------------------
# Estatística ponderada com erro-padrão por conglomerado (linearização)
# --------------------------------------------------------------------------------------
def media_ic(y: pd.Series, w: pd.Series, cluster: pd.Series) -> tuple[float, float, float]:
    ok = y.notna() & w.notna()
    y, w, cluster = y[ok].astype(float), w[ok], cluster[ok]
    m = np.average(y, weights=w)
    escore = (w * (y - m)) / w.sum()
    s = escore.groupby(cluster.values).sum()
    g = len(s)
    ep = np.sqrt(g / (g - 1) * (s ** 2).sum())
    return m, m - 1.96 * ep, m + 1.96 * ep


def tabela_categorias(df: pd.DataFrame, var: str, rotulos: dict | None, nome: str) -> pd.DataFrame:
    linhas = []
    total_w = df.loc[df[var].notna(), "peso_mt"].sum()
    for valor, sub in df.groupby(var, observed=True):
        m, li, ls = media_ic(sub["prof_mt"], sub["peso_mt"], sub["id_escola"])
        linhas.append({"variavel": nome, "categoria": rotulos.get(valor, valor) if rotulos else valor,
                       "ordem": valor if not isinstance(valor, str) else len(linhas),
                       "n": len(sub), "pct_ponderado": 100 * sub["peso_mt"].sum() / total_w,
                       "media_mt": m, "ic95_inf": li, "ic95_sup": ls})
    return pd.DataFrame(linhas)


# --------------------------------------------------------------------------------------
# Correlação policórica (itens ordinais de 3 categorias) por máxima verossimilhança
# --------------------------------------------------------------------------------------
def _limiares(x: np.ndarray, k: int) -> np.ndarray:
    prop = np.bincount(x, minlength=k) / len(x)
    return np.concatenate([[-8.0], norm.ppf(np.cumsum(prop)[:-1]), [8.0]])


def policorica(x: np.ndarray, y: np.ndarray, k: int = 3) -> float:
    tx, ty = _limiares(x, k), _limiares(y, k)
    obs = np.zeros((k, k))
    np.add.at(obs, (x, y), 1)

    def menos_logv(rho):
        mvn = multivariate_normal(mean=[0, 0], cov=[[1, rho], [rho, 1]])
        F = np.array([[mvn.cdf([a, b]) for b in ty] for a in tx])  # ±8 aproxima ±infinito
        p = F[1:, 1:] - F[:-1, 1:] - F[1:, :-1] + F[:-1, :-1]
        return -(obs * np.log(np.clip(p, 1e-12, None))).sum()

    return minimize_scalar(menos_logv, bounds=(-0.99, 0.99), method="bounded").x


def matriz_policorica(df: pd.DataFrame, itens: list[str]) -> pd.DataFrame:
    R = pd.DataFrame(np.eye(len(itens)), index=itens, columns=itens)
    for i, a in enumerate(itens):
        for b in itens[i + 1:]:
            R.loc[a, b] = R.loc[b, a] = policorica(df[a].to_numpy(int), df[b].to_numpy(int))
    return R


def afe(R: pd.DataFrame, n_fatores: int) -> pd.DataFrame:
    fa = FactorAnalyzer(n_factors=n_fatores, rotation="oblimin" if n_fatores > 1 else None,
                        method="minres", is_corr_matrix=True)
    fa.fit(R.to_numpy())
    return pd.DataFrame(fa.loadings_, index=R.index, columns=[f"F{i + 1}" for i in range(n_fatores)])


def omega(R: pd.DataFrame, itens: list[str]) -> float:
    if len(itens) == 2:  # dois itens: fator não identificado; assume cargas iguais (= raiz de r)
        lam = pd.Series([np.sqrt(abs(R.loc[itens[0], itens[1]]))] * 2)
    else:
        lam = afe(R.loc[itens, itens], 1)["F1"].abs()
    return lam.sum() ** 2 / (lam.sum() ** 2 + (1 - lam ** 2).sum())


def congruencia(a: pd.Series, b: pd.Series) -> float:
    return float((a * b).sum() / np.sqrt((a ** 2).sum() * (b ** 2).sum()))


# --------------------------------------------------------------------------------------
# Figuras
# --------------------------------------------------------------------------------------
def _eixo(ax, titulo):
    ax.set_title(titulo, fontsize=10, color=TINTA, loc="left")
    ax.grid(axis="x", color=GRADE, linewidth=0.6)
    ax.set_axisbelow(True)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(MUDO)
    ax.tick_params(colors=TINTA_2, labelsize=8.5, length=0)


def _pontos(ax, tab: pd.DataFrame, titulo: str, xlim):
    tab = tab.sort_values("ordem").reset_index(drop=True)
    ypos = np.arange(len(tab))[::-1]
    ax.hlines(ypos, tab["ic95_inf"], tab["ic95_sup"], color=AZUL, linewidth=2)
    ax.plot(tab["media_mt"], ypos, "o", color=AZUL, markersize=6, markeredgecolor="white", markeredgewidth=1.5)
    for yy, (_, r) in zip(ypos, tab.iterrows()):
        ax.text(r["ic95_sup"] + 1.2, yy, _br(r['media_mt']), va="center", fontsize=8, color=TINTA_2)
    ax.set_yticks(ypos, [f"{c} ({p:.0f}%)" for c, p in zip(tab["categoria"], tab["pct_ponderado"])])
    ax.set_xlim(*xlim)
    _formatar_eixo_br(ax.xaxis)
    _eixo(ax, titulo)


def figura_gradientes(desc: pd.DataFrame, destino):
    paineis = [("Reprovação", "Já foi reprovado(a)"), ("Abandono", "Já abandonou a escola"),
               ("Tempo de estudo", "Tempo de estudo fora da escola"), ("Distorção idade-série", "Distorção idade-série (16+ anos)")]
    fig, eixos = plt.subplots(2, 2, figsize=(9, 5.2), constrained_layout=True)
    for ax, (var, titulo) in zip(eixos.flat, paineis):
        _pontos(ax, desc[desc["variavel"] == var], titulo, XLIM_COMUM)
    fig.supxlabel("Proficiência média em Matemática (escala Saeb) e IC 95%", fontsize=9, color=TINTA_2)
    fig.savefig(destino, dpi=300, pil_kwargs={"quality": 95})
    plt.close(fig)


def figura_familia(desc: pd.DataFrame, destino):
    fig, eixos = plt.subplots(3, 2, figsize=(9, 6.4), constrained_layout=True)
    for ax, titulo in zip(eixos.flat, ITENS_FAMILIA.values()):
        _pontos(ax, desc[desc["variavel"] == titulo], titulo, XLIM_COMUM)
    fig.supxlabel("Proficiência média em Matemática (escala Saeb) e IC 95%", fontsize=9, color=TINTA_2)
    fig.savefig(destino, dpi=300, pil_kwargs={"quality": 95})
    plt.close(fig)


def figura_distribuicao(df: pd.DataFrame, destino):
    q = pd.qcut(df["inse"], 5, labels=[f"{i}º quintil" for i in range(1, 6)])
    bordas = np.linspace(100, 420, 161)
    centros = (bordas[:-1] + bordas[1:]) / 2
    fig, ax = plt.subplots(figsize=(8, 4), constrained_layout=True)
    for cor, (rot, sub) in zip(RAMPA_AZUL, df.groupby(q, observed=True)):
        dens, _ = np.histogram(sub["prof_mt"], bins=bordas, weights=sub["peso_mt"], density=True)
        dens = np.convolve(dens, np.ones(9) / 9, mode="same")  # suavização (média móvel de 9 classes de 2 pontos)
        ax.plot(centros, dens, color=cor, linewidth=2, label=f"{rot} de INSE")
        m = np.average(sub["prof_mt"], weights=sub["peso_mt"])
        ax.axvline(m, color=cor, linewidth=1, linestyle=(0, (3, 3)))
    ax.set_xlabel("Proficiência em Matemática (escala Saeb)", fontsize=9, color=TINTA_2)
    ax.set_ylabel("Densidade", fontsize=9, color=TINTA_2)
    _formatar_eixo_br(ax.xaxis)
    _formatar_eixo_br(ax.yaxis)
    ax.legend(frameon=False, fontsize=8.5, title="Linhas tracejadas: médias", title_fontsize=8)
    ax.grid(axis="y", color=GRADE, linewidth=0.6)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(colors=TINTA_2, labelsize=8.5)
    fig.savefig(destino, dpi=300, pil_kwargs={"quality": 95})
    plt.close(fig)


# --------------------------------------------------------------------------------------
def main() -> None:
    DIR_FIG.mkdir(parents=True, exist_ok=True)
    base = pd.read_parquet(cfg.ARQ_BASE_ANALITICA)
    cc = base[base["caso_completo"] == 1].copy()
    print(f"Base analítica: {len(base):,}; casos completos: {len(cc):,}")

    # 1. Desfecho e INSE ----------------------------------------------------------------
    resumo = []
    for nome, d in (("Todos (questionário preenchido)", base), ("Casos completos", cc)):
        m, li, ls = media_ic(d["prof_mt"], d["peso_mt"], d["id_escola"])
        mi, _, _ = media_ic(d["inse"], d["peso_mt"], d["id_escola"])
        resumo.append({"amostra": nome, "n": len(d), "escolas": d["id_escola"].nunique(),
                       "media_mt": m, "ic95_inf": li, "ic95_sup": ls,
                       "dp_mt": np.sqrt(np.cov(d["prof_mt"], aweights=d["peso_mt"])),
                       "ep_individual_medio": d["ep_mt"].mean(), "media_inse": mi,
                       "dp_inse": np.sqrt(np.cov(d["inse"].dropna(), aweights=d.loc[d["inse"].notna(), "peso_mt"]))})
    pd.DataFrame(resumo).round(3).to_csv(cfg.DIR_RESULTADOS / "tab_desfecho.csv", index=False)

    # 2. Distribuições e gradientes (casos completos) ------------------------------------
    cc["aband_cat"] = cc["aband"].astype("Int8")
    especificacao = [
        ("reprov", ROTULO_ABAND, "Reprovação"), ("aband_cat", ROTULO_ABAND, "Abandono"),
        ("estudo", ROTULO_TEMPO, "Tempo de estudo"), ("distorcao", {0: "Não", 1: "Sim"}, "Distorção idade-série"),
        ("trab_fora", ROTULO_TEMPO, "Trabalho fora de casa"), ("trab_domestico", ROTULO_TEMPO, "Trabalho doméstico"),
        ("sexo", None, "Sexo"), ("raca", None, "Cor/raça"), ("idade_entrada", None, "Idade de entrada"),
        ("rural", {0: "Urbana", 1: "Rural"}, "Localização"),
    ] + [(v, ROTULO_FREQ3, rot) for v, rot in ITENS_FAMILIA.items()]
    desc = pd.concat([tabela_categorias(cc, v, r, n) for v, r, n in especificacao], ignore_index=True)
    desc.round(2).to_csv(cfg.DIR_RESULTADOS / "tab_descritivas.csv", index=False)

    # 3. Correlação intraclasse ------------------------------------------------------------
    s = cc.groupby("id_escola")["prof_mt"]
    k = s.size(); N = len(cc); G = len(k)
    n0 = (N - (k ** 2).sum() / N) / (G - 1)
    msb = (k * (s.mean() - cc["prof_mt"].mean()) ** 2).sum() / (G - 1)
    msw = ((cc["prof_mt"] - s.transform("mean")) ** 2).sum() / (N - G)
    icc_anova = ((msb - msw) / n0) / ((msb - msw) / n0 + msw)

    rng = np.random.default_rng(cfg.SEMENTE)
    escolas = cc[["id_escola", "uf"]].drop_duplicates()
    amostra_esc = escolas.groupby("uf", group_keys=False).apply(
        lambda d: d.sample(frac=3000 / len(escolas), random_state=rng.integers(1e9)))
    sub = cc[cc["id_escola"].isin(amostra_esc["id_escola"])]
    nulo = smf.mixedlm("prof_mt ~ 1", sub, groups=sub["id_escola"]).fit(reml=True)
    tau2, sigma2 = float(nulo.cov_re.iloc[0, 0]), float(nulo.scale)
    pd.DataFrame([
        {"metodo": "ANOVA (todas as escolas, não ponderado)", "escolas": G, "alunos": N, "icc": icc_anova},
        {"metodo": "Multinível nulo, REML (amostra de escolas estratificada por UF)",
         "escolas": sub["id_escola"].nunique(), "alunos": len(sub), "icc": tau2 / (tau2 + sigma2),
         "tau2": tau2, "sigma2": sigma2},
    ]).round(4).to_csv(cfg.DIR_RESULTADOS / "tab_icc.csv", index=False)

    # 4. Análise fatorial dos itens de envolvimento familiar ---------------------------------
    itens = list(ITENS_FAMILIA)
    fam = base[itens].dropna().astype(int)
    metade = rng.random(len(fam)) < 0.5
    RA, RB = matriz_policorica(fam[metade], itens), matriz_policorica(fam[~metade], itens)
    RA.round(3).to_csv(cfg.DIR_RESULTADOS / "tab_policorica_familia_A.csv")
    autoval = np.linalg.eigvalsh(RA.to_numpy())[::-1]
    cargas = []
    for nf in (1, 2):
        LA, LB = afe(RA, nf), afe(RB, nf)
        if nf == 2 and congruencia(LA["F1"], LB["F1"]) < congruencia(LA["F1"], LB["F2"]):
            LB = LB[["F2", "F1"]].set_axis(["F1", "F2"], axis=1)  # alinha fatores entre metades
        for f in LA.columns:
            for it in itens:
                cargas.append({"solucao": f"{nf} fator(es)", "fator": f, "item": ITENS_FAMILIA[it],
                               "carga_A": LA.loc[it, f], "carga_B": LB.loc[it, f]})
        if nf == 2:
            congr = {f: congruencia(LA[f], LB[f]) for f in LA.columns}
    pd.DataFrame(cargas).round(3).to_csv(cfg.DIR_RESULTADOS / "tab_afe_cargas.csv", index=False)
    pd.DataFrame([
        {"medida": "n alunos (metade A / B)", "valor": f"{metade.sum()} / {(~metade).sum()}"},
        {"medida": "autovalores (metade A)", "valor": "; ".join(f"{v:.3f}" for v in autoval)},
        {"medida": "congruência de Tucker F1 (2 fatores)", "valor": f"{congr['F1']:.3f}"},
        {"medida": "congruência de Tucker F2 (2 fatores)", "valor": f"{congr['F2']:.3f}"},
        {"medida": "ômega - socialização (le, conversa)", "valor": f"{omega(RA, ['fam_le', 'fam_conversa']):.3f}"},
        {"medida": "ômega - monitoramento (inc_estudar, inc_tarefa)",
         "valor": f"{omega(RA, ['fam_inc_estudar', 'fam_inc_tarefa']):.3f}"},
        {"medida": "ômega - incentivo (inc_estudar, inc_tarefa, inc_comparecer)",
         "valor": f"{omega(RA, ['fam_inc_estudar', 'fam_inc_tarefa', 'fam_inc_comparecer']):.3f}"},
        {"medida": "ômega - 6 itens (1 fator)", "valor": f"{omega(RA, itens):.3f}"},
    ]).to_csv(cfg.DIR_RESULTADOS / "tab_afe_resumo.csv", index=False)

    # 5. Figuras ----------------------------------------------------------------------------
    figura_gradientes(desc, DIR_FIG / "fig_gradientes.jpg")
    figura_familia(desc, DIR_FIG / "fig_familia.jpg")
    figura_distribuicao(cc, DIR_FIG / "fig_distribuicao_inse.jpg")
    print("Etapa 2 concluída.")


if __name__ == "__main__":
    main()
