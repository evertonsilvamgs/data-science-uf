"""Etapa 4a - Diagnóstico de especificação com aprendizado de máquina (LightGBM + SHAP).

Objetivo: verificar se um modelo não linear, com as MESMAS variáveis do modelo B5, prevê a
proficiência muito melhor que a regressão linear. Ganho grande indicaria não linearidades ou
interações que a especificação linear deixou de fora. Não é um modelo para classificar alunos.

Entrada : dados/saeb2023_9ef_publicas.parquet
Saídas  : resultados/tab_ml_metricas.csv        RMSE, MAE e R² fora da amostra (5 partições por escola)
          resultados/tab_ml_shap.csv            importância média |SHAP| por variável
          resultados/tab_ml_shap_perfis.csv     perfis SHAP (estudo, INSE, reprovação x INSE)
          resultados/figuras/fig_ml_shap.jpg
"""
import numpy as np
import pandas as pd
import lightgbm as lgb
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GroupKFold, GroupShuffleSplit

import config as cfg

DIR_FIG = cfg.DIR_RESULTADOS / "figuras"
N_AMOSTRA = 300_000
N_SHAP = 50_000
AZUL, LARANJA = "#2a78d6", "#eb6834"
TINTA, TINTA_2, MUDO, GRADE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9"

PARAMS = dict(objective="regression", learning_rate=0.05, num_leaves=63, min_child_samples=200,
              subsample=0.8, subsample_freq=1, colsample_bytree=0.8, reg_lambda=1.0,
              n_estimators=2000, random_state=cfg.SEMENTE, n_jobs=-1, verbose=-1)

ROTULOS = {
    "inse": "INSE", "reprov": "Reprovação", "aband": "Abandono", "estudo": "Tempo de estudo",
    "incentivo": "Incentivo dos pais", "fam_conversa": "Conversam sobre a escola",
    "fam_le": "Pais leem em casa", "fam_reunioes": "Vão às reuniões", "sexo": "Sexo", "raca": "Cor/raça",
    "deficiencia": "Deficiência", "idade_entrada": "Idade de entrada na escola",
    "trab_fora": "Trabalho fora de casa", "rural": "Escola rural", "capital": "Capital", "uf": "UF",
}
ORDEM_ENTRADA = ["3 anos ou menos", "4 ou 5 anos", "6 ou 7 anos", "8 anos ou mais"]


def matriz_arvore(df: pd.DataFrame) -> pd.DataFrame:
    """Mesma informação do B5, com ordinais em sua escala original e nominais como categoria."""
    X = pd.DataFrame(index=df.index)
    X["inse"] = df["inse"].astype(float)
    X["reprov"] = df["reprov"].astype(int)
    X["aband"] = (df["aband"] > 0).astype(int)
    X["estudo"] = df["estudo"].astype(int)
    X["incentivo"] = df[["fam_inc_estudar", "fam_inc_tarefa", "fam_inc_comparecer"]].astype(float).mean(axis=1)
    for c in ("fam_conversa", "fam_le", "fam_reunioes", "trab_fora", "deficiencia", "rural", "capital"):
        X[c] = df[c].astype(int)
    X["idade_entrada"] = pd.Categorical(df["idade_entrada"].astype(str), categories=ORDEM_ENTRADA, ordered=True).codes
    X["sexo"] = df["sexo"].astype(str).astype("category")
    X["raca"] = df["raca"].astype(str).astype("category")
    X["uf"] = df["uf"].astype(int).astype("category")
    return X


def matriz_linear(X: pd.DataFrame) -> pd.DataFrame:
    """Especificação do B5: indicadoras para todas as categorias; INSE e incentivo contínuos."""
    cat = [c for c in X.columns if c not in ("inse", "incentivo", "deficiencia", "rural", "capital", "aband")]
    return pd.get_dummies(X, columns=cat, drop_first=True, dtype=float)


def metricas(y, pred, w) -> dict:
    erro = y - pred
    m = np.average(y, weights=w)
    return {"rmse": np.sqrt(np.average(erro ** 2, weights=w)), "mae": np.average(np.abs(erro), weights=w),
            "r2": 1 - np.average(erro ** 2, weights=w) / np.average((y - m) ** 2, weights=w)}


def ajustar_lgbm(Xtr, ytr, wtr, grupos_tr, semente):
    """Número de árvores escolhido por parada antecipada em validação interna separada por escola."""
    interno = GroupShuffleSplit(n_splits=1, test_size=0.15, random_state=semente)
    i_tr, i_val = next(interno.split(Xtr, groups=grupos_tr))
    modelo = lgb.LGBMRegressor(**PARAMS)
    modelo.fit(Xtr.iloc[i_tr], ytr[i_tr], sample_weight=wtr[i_tr],
               eval_set=[(Xtr.iloc[i_val], ytr[i_val])], eval_sample_weight=[wtr[i_val]],
               callbacks=[lgb.early_stopping(50, verbose=False)])
    return modelo


def _br(v, casas=0):
    return f"{v:.{casas}f}".replace(".", ",").replace("-", "−")


def _limpar(ax, grade="y"):
    ax.grid(axis=grade, color=GRADE, linewidth=0.6); ax.set_axisbelow(True)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(colors=TINTA_2, labelsize=8.5)


def _eixo_numerico(eixo):
    eixo.set_major_formatter(plt.FuncFormatter(lambda v, _: _br(v, 0) if float(v).is_integer() else _br(v, 1)))


def figura(imp, perfis, destino):
    fig = plt.figure(figsize=(9.5, 6.6), constrained_layout=True)
    gs = fig.add_gridspec(2, 2, width_ratios=[1.1, 1])
    # (a) importância
    ax = fig.add_subplot(gs[:, 0])
    d = imp.sort_values("shap_medio_abs")
    ax.barh(d["rotulo"], d["shap_medio_abs"], color=AZUL, height=0.62)
    for yy, v in enumerate(d["shap_medio_abs"]):
        ax.text(v + 0.15, yy, _br(v, 1), va="center", fontsize=8, color=TINTA_2)
    ax.set_title("(a) Importância média (|SHAP|, pontos Saeb)", fontsize=10, loc="left", color=TINTA)
    ax.set_xlim(0, d["shap_medio_abs"].max() * 1.15)
    _limpar(ax, "x"); _eixo_numerico(ax.xaxis); ax.spines["left"].set_visible(False); ax.tick_params(length=0)
    # (b) tempo de estudo
    ax = fig.add_subplot(gs[0, 1])
    e = perfis[perfis["perfil"] == "estudo"]
    ax.axhline(0, color=MUDO, linewidth=1)
    ax.vlines(e["x"], e["q25"], e["q75"], color=AZUL, linewidth=2)
    ax.plot(e["x"], e["media"], "o-", color=AZUL, linewidth=2, markersize=6, markeredgecolor="white", markeredgewidth=1.5)
    ax.set_xticks(e["x"], ["Não estuda", "Menos de 1h", "1 a 2h", "Mais de 2h"])
    ax.set_title("(b) Tempo de estudo", fontsize=10, loc="left", color=TINTA)
    ax.set_ylabel("SHAP (pontos Saeb)", fontsize=9, color=TINTA_2)
    _limpar(ax); _eixo_numerico(ax.yaxis)
    # (c) reprovação conforme o INSE
    ax = fig.add_subplot(gs[1, 1])
    r = perfis[perfis["perfil"] == "reprov_por_inse"]
    ax.vlines(r["x"], r["q25"], r["q75"], color=LARANJA, linewidth=2)
    ax.plot(r["x"], r["media"], "o-", color=LARANJA, linewidth=2, markersize=6, markeredgecolor="white", markeredgewidth=1.5)
    ax.set_xticks(r["x"], [f"{int(v)}º" for v in r["x"]])
    ax.set_title("(c) Reprovação, por quinto de INSE", fontsize=10, loc="left", color=TINTA)
    ax.set_xlabel("Quinto de INSE (1º = mais baixo); só reprovados", fontsize=8.5, color=TINTA_2)
    ax.set_ylabel("SHAP (pontos Saeb)", fontsize=9, color=TINTA_2)
    _limpar(ax); _eixo_numerico(ax.yaxis)
    fig.savefig(destino, dpi=300, pil_kwargs={"quality": 95})
    plt.close(fig)


def main() -> None:
    base = pd.read_parquet(cfg.ARQ_BASE_ANALITICA)
    cc = base[base["caso_completo"] == 1]
    am = cc.sample(N_AMOSTRA, random_state=cfg.SEMENTE)
    X, y, w = matriz_arvore(am), am["prof_mt"].to_numpy(), am["peso_mt"].to_numpy()
    grupos = am["id_escola"].to_numpy()
    XL = matriz_linear(X)
    print(f"Amostra: {len(am):,} alunos, {am['id_escola'].nunique():,} escolas; {X.shape[1]} variáveis "
          f"({XL.shape[1]} colunas na regressão linear)")

    # 1. Validação cruzada agrupada por escola ---------------------------------------------
    linhas, iteracoes = [], []
    for k, (tr, te) in enumerate(GroupKFold(n_splits=5).split(X, y, grupos), start=1):
        lin = LinearRegression().fit(XL.iloc[tr], y[tr], sample_weight=w[tr])
        linhas.append({"modelo": "Regressão linear (B5)", "particao": k, **metricas(y[te], lin.predict(XL.iloc[te]), w[te])})
        gbm = ajustar_lgbm(X.iloc[tr], y[tr], w[tr], grupos[tr], cfg.SEMENTE + k)
        iteracoes.append(gbm.best_iteration_)
        linhas.append({"modelo": "LightGBM", "particao": k, **metricas(y[te], gbm.predict(X.iloc[te]), w[te])})
        print(f"  partição {k}: linear R²={linhas[-2]['r2']:.4f} | LightGBM R²={linhas[-1]['r2']:.4f} "
              f"({gbm.best_iteration_} árvores)")
    met = pd.DataFrame(linhas)
    resumo = met.groupby("modelo")[["rmse", "mae", "r2"]].agg(["mean", "std"])
    resumo.columns = [f"{a}_{'media' if b == 'mean' else 'dp'}" for a, b in resumo.columns]
    resumo = resumo.reset_index()
    resumo["n_alunos"], resumo["n_escolas"] = len(am), am["id_escola"].nunique()
    resumo["arvores_mediana"] = np.where(resumo["modelo"] == "LightGBM", int(np.median(iteracoes)), np.nan)
    resumo.round(4).to_csv(cfg.DIR_RESULTADOS / "tab_ml_metricas.csv", index=False)

    # 2. Modelo final e valores SHAP (TreeSHAP exato, implementado no LightGBM) ---------------
    final = lgb.LGBMRegressor(**{**PARAMS, "n_estimators": int(np.median(iteracoes))}).fit(X, y, sample_weight=w)
    rng = np.random.default_rng(cfg.SEMENTE)
    idx = rng.choice(len(X), N_SHAP, replace=False)
    Xs, ws = X.iloc[idx], w[idx]
    shap = pd.DataFrame(final.booster_.predict(Xs, pred_contrib=True)[:, :-1], columns=X.columns, index=Xs.index)
    imp = pd.DataFrame({"variavel": X.columns,
                        "shap_medio_abs": [np.average(shap[c].abs(), weights=ws) for c in X.columns]})
    imp["rotulo"] = imp["variavel"].map(ROTULOS)
    imp.sort_values("shap_medio_abs", ascending=False).round(3).to_csv(cfg.DIR_RESULTADOS / "tab_ml_shap.csv", index=False)

    def perfil(nome, chave, valores, mascara=None):
        d = pd.DataFrame({"x": chave, "s": valores})
        if mascara is not None:
            d = d[mascara]
        g = d.groupby("x")["s"]
        out = pd.DataFrame({"media": g.mean(), "q25": g.quantile(.25), "q75": g.quantile(.75), "n": g.size()}).reset_index()
        out.insert(0, "perfil", nome)
        return out

    quinto = pd.qcut(Xs["inse"], 5, labels=False) + 1
    decil = pd.qcut(Xs["inse"], 10, labels=False) + 1
    perfis = pd.concat([
        perfil("estudo", Xs["estudo"].to_numpy(), shap["estudo"].to_numpy()),
        perfil("inse_decil", decil.to_numpy(), shap["inse"].to_numpy()),
        perfil("reprov_por_inse", quinto.to_numpy(), shap["reprov"].to_numpy(), (Xs["reprov"] > 0).to_numpy()),
        perfil("reprov", Xs["reprov"].to_numpy(), shap["reprov"].to_numpy()),
        perfil("incentivo", Xs["incentivo"].round(2).to_numpy(), shap["incentivo"].to_numpy()),
    ], ignore_index=True)
    perfis.round(3).to_csv(cfg.DIR_RESULTADOS / "tab_ml_shap_perfis.csv", index=False)

    figura(imp, perfis, DIR_FIG / "fig_ml_shap.jpg")
    print(resumo.round(4).to_string(index=False))
    print("Etapa 4a concluída.")


if __name__ == "__main__":
    main()
