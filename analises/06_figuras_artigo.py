"""Etapa 5 - Figuras finais do artigo, em Times New Roman (mesma fonte do texto).

Não reestima nada: lê as tabelas já gravadas em resultados/ pelas etapas 2 a 4.
Saídas (resultados/figuras/, JPEG 300 dpi, exigência do template):
  art_fig1_desenho.jpg     desenho do estudo (Metodologia)
  art_fig2_gradientes.jpg  médias de proficiência por categoria (Resultados)
  art_fig3_coeficientes.jpg  coeficientes do modelo B5 e do modelo com efeitos fixos de escola
  art_fig4_shap.jpg        diagnóstico com LightGBM/SHAP
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch

import config as cfg

AZUL, LARANJA = "#2a78d6", "#eb6834"
TINTA, TINTA_2, MUDO, GRADE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9"
AZUL_CLARO = "#dbe8f8"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "font.size": 11,
    "axes.edgecolor": TINTA_2,
    "axes.labelcolor": TINTA_2,
    "xtick.color": TINTA_2,
    "ytick.color": TINTA_2,
    "axes.unicode_minus": True,
})

DIR_FIG = cfg.DIR_RESULTADOS / "figuras"


def _br(v, casas=1):
    return f"{v:.{casas}f}".replace(".", ",").replace("-", "−")


def _salvar(fig, nome):
    fig.savefig(DIR_FIG / nome, dpi=300, bbox_inches="tight", pil_kwargs={"quality": 92})
    plt.close(fig)
    print("gravada:", nome)


def _limpar(ax, grade_x=True):
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(length=0)
    if grade_x:
        ax.grid(axis="x", color=GRADE, lw=0.8)
        ax.set_axisbelow(True)


# --------------------------------------------------------------------------------------
# Figura 1 - desenho do estudo
# --------------------------------------------------------------------------------------
def _caixa(ax, x, y, w, h, titulo, corpo, cor=AZUL_CLARO, borda=AZUL):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.015",
                                fc=cor, ec=borda, lw=1.1))
    ax.text(x + w / 2, y + h - 0.025, titulo, ha="center", va="top", fontsize=11.5,
            fontweight="bold", color=TINTA)
    ax.text(x + w / 2, y + h - 0.075, corpo, ha="center", va="top", fontsize=10,
            color=TINTA, linespacing=1.35)


def _seta(ax, x0, y0, x1, y1):
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color=TINTA_2, lw=1.1, shrinkA=0, shrinkB=0))


def fig_desenho():
    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.set_xlim(-0.01, 1.02)
    ax.set_ylim(0, 1.04)
    ax.axis("off")

    etapas = [
        ("1  Descrição e correlação intraclasse", "—"),
        ("2  Regressão ponderada em blocos", "H1 a H3"),
        ("3  Efeitos fixos de escola e multinível", "H4"),
        ("4  Interações com o INSE", "H5"),
        ("5  Análises de robustez", "todas"),
        ("6  LightGBM e SHAP (diagnóstico)", "H2, H5"),
        ("7  Comparação com o PISA 2025", "H6"),
    ]
    x0, w, topo, alt, gap = 0.62, 0.385, 0.96, 0.105, 0.028
    centros = []
    for i, (txt, hip) in enumerate(etapas):
        y = topo - (i + 1) * alt - i * gap
        centros.append(y + alt / 2)
        laranja = i == 6
        ax.add_patch(FancyBboxPatch((x0, y), w, alt, boxstyle="round,pad=0.006,rounding_size=0.012",
                                    fc="#fbe3d8" if laranja else AZUL_CLARO,
                                    ec=LARANJA if laranja else AZUL, lw=1.0))
        ax.text(x0 + 0.012, y + alt / 2, txt, va="center", fontsize=10, color=TINTA)
        ax.text(x0 + w - 0.010, y + alt / 2, hip, va="center", ha="right", fontsize=10,
                color=TINTA_2, style="italic")
    ax.text(x0 + w / 2, topo + 0.012, "Análises (hipóteses)", ha="center", va="bottom", fontsize=11.5,
            fontweight="bold", color=TINTA)

    _caixa(ax, 0.00, 0.50, 0.24, 0.46, "Dados",
           "Microdados do Saeb 2023\n9º ano do ensino\nfundamental\nescolas públicas\n\n"
           "1.715.248 estudantes\n36.176 escolas")
    _caixa(ax, 0.29, 0.50, 0.28, 0.46, "Variáveis",
           "Desfecho: proficiência\nem Matemática\n\nTrajetória: reprovação, abandono\n"
           "Estudo: tempo fora da escola\nFamília: incentivo, conversa,\nleitura e reuniões\n"
           "Controles: INSE, perfil e UF")
    ypisa = centros[-1]
    ax.add_patch(FancyBboxPatch((0.0, ypisa - 0.085), 0.57, 0.17,
                                boxstyle="round,pad=0.008,rounding_size=0.015", fc="#fbe3d8", ec=LARANJA, lw=1.1))
    ax.text(0.285, ypisa + 0.05, "Referência externa", ha="center", va="center", fontsize=11.5,
            fontweight="bold", color=TINTA)
    ax.text(0.285, ypisa - 0.035, "PISA 2025 – Brasil: indicadores publicados pela OCDE\n(comparação de padrões, sem conversão de escalas)",
            ha="center", va="center", fontsize=10, color=TINTA)

    _seta(ax, 0.24, 0.73, 0.29, 0.73)
    _seta(ax, 0.57, 0.73, x0, 0.73)
    _seta(ax, 0.57, ypisa, x0, ypisa)
    _salvar(fig, "art_fig1_desenho.jpg")


# --------------------------------------------------------------------------------------
# Figura 2 - médias por categoria
# --------------------------------------------------------------------------------------
PAINEIS = [
    ("Reprovação", "(a) Já foi reprovado(a)"),
    ("Tempo de estudo", "(b) Tempo de estudo fora da escola"),
    ("Conversam sobre a escola", "(c) Pais conversam sobre a escola"),
    ("Incentivam a fazer a tarefa", "(d) Pais incentivam a fazer a tarefa"),
]
ROTULOS_CAT = {"Não usa": "Não estuda", "Nunca ou quase nunca": "Nunca", "Sempre ou quase sempre": "Sempre",
               "Entre 1 e 2h": "De 1 a 2h"}


def fig_gradientes():
    d = pd.read_csv(cfg.DIR_RESULTADOS / "tab_descritivas.csv")
    fig, eixos = plt.subplots(2, 2, figsize=(10, 5.6), sharex=True)
    for ax, (var, titulo) in zip(eixos.flat, PAINEIS):
        s = d[d["variavel"] == var].sort_values("ordem")
        ys = list(range(len(s)))[::-1]
        for yy, (_, r) in zip(ys, s.iterrows()):
            ax.plot([r["ic95_inf"], r["ic95_sup"]], [yy, yy], color=AZUL, lw=2)
            ax.plot(r["media_mt"], yy, "o", color=AZUL, ms=6)
            ax.text(r["ic95_sup"] + 1.0, yy, _br(r["media_mt"]), va="center", fontsize=10, color=TINTA)
        ax.set_yticks(ys)
        ax.set_yticklabels([f"{ROTULOS_CAT.get(c, c)} ({int(r + 0.5)}%)"
                            for c, r in zip(s["categoria"], s["pct_ponderado"])], fontsize=10)
        ax.set_ylim(min(ys) - 0.6, max(ys) + 0.6)
        ax.set_xlim(220, 270)
        ax.set_title(titulo, fontsize=11.5, loc="left", color=TINTA)
        _limpar(ax)
    fig.supxlabel("Proficiência média em Matemática (escala Saeb) e intervalo de confiança de 95%",
                  fontsize=10.5, color=TINTA_2)
    fig.tight_layout()
    _salvar(fig, "art_fig2_gradientes.jpg")


# --------------------------------------------------------------------------------------
# Figura 3 - coeficientes B5 x efeitos fixos de escola
# --------------------------------------------------------------------------------------
TERMOS = [
    ("rep_1", "Reprovado uma vez"), ("rep_2mais", "Reprovado duas ou mais vezes"),
    ("aband_sim", "Já abandonou a escola"),
    ("est_menos1h", "Estuda menos de 1h"), ("est_1a2h", "Estuda de 1 a 2h"), ("est_mais2h", "Estuda mais de 2h"),
    ("incentivo_z", "Incentivo dos pais (+1 DP)"),
    ("conv_vezes", "Conversam sobre a escola: às vezes"), ("conv_sempre", "Conversam sobre a escola: sempre"),
    ("le_vezes", "Pais leem: às vezes"), ("le_sempre", "Pais leem: sempre"),
    ("reun_vezes", "Vão às reuniões: às vezes"), ("reun_sempre", "Vão às reuniões: sempre"),
    ("inse_z", "INSE (+1 DP)"),
]


def fig_coeficientes():
    c = pd.read_csv(cfg.DIR_RESULTADOS / "tab_modelos_coef.csv")
    fig, ax = plt.subplots(figsize=(10, 6.2))
    n = len(TERMOS)
    for modelo, cor, desl, rotulo in (("B5", AZUL, 0.17, "Todos os estudantes (modelo B5)"),
                                      ("EF escola", LARANJA, -0.17, "Estudantes da mesma escola (efeitos fixos)")):
        m = c[c["modelo"] == modelo].set_index("termo")
        for i, (t, _) in enumerate(TERMOS):
            y = n - 1 - i + desl
            ax.plot([m.loc[t, "ic_inf"], m.loc[t, "ic_sup"]], [y, y], color=cor, lw=2)
            ax.plot(m.loc[t, "coef"], y, "o", color=cor, ms=5.5, label=rotulo if i == 0 else None)
    ax.axvline(0, color=TINTA_2, lw=1)
    for sep in (n - 3.5, n - 6.5, n - 7.5, n - 13.5):
        ax.axhline(sep, color=GRADE, lw=0.8, ls=(0, (4, 3)))
    ax.set_yticks(range(n))
    ax.set_yticklabels([r for _, r in TERMOS][::-1], fontsize=10.5)
    ax.set_xlabel("Diferença na proficiência em Matemática (pontos Saeb) e intervalo de confiança de 95%",
                  fontsize=10.5)
    _limpar(ax)
    ax.set_xticks(range(-25, 25, 5))
    ax.set_xticklabels([_br(v, 0) for v in range(-25, 25, 5)])
    ax.legend(frameon=False, loc="upper right", fontsize=10.5)
    _salvar(fig, "art_fig3_coeficientes.jpg")


# --------------------------------------------------------------------------------------
# Figura 4 - LightGBM/SHAP
# --------------------------------------------------------------------------------------
def fig_shap():
    imp = pd.read_csv(cfg.DIR_RESULTADOS / "tab_ml_shap.csv").sort_values("shap_medio_abs")
    perf = pd.read_csv(cfg.DIR_RESULTADOS / "tab_ml_shap_perfis.csv")
    fig = plt.figure(figsize=(10, 6.2))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.15, 1], hspace=0.55, wspace=0.35)

    ax = fig.add_subplot(gs[:, 0])
    ax.barh(imp["rotulo"], imp["shap_medio_abs"], color=AZUL, height=0.65)
    for yy, v in enumerate(imp["shap_medio_abs"]):
        ax.text(v + 0.12, yy, _br(v), va="center", fontsize=9.5, color=TINTA)
    ax.set_title("(a) Importância média (|SHAP|, pontos Saeb)", fontsize=11.5, loc="left", color=TINTA)
    ax.tick_params(axis="y", labelsize=10)
    _limpar(ax)

    def painel(pos, chave, xt, titulo, cor, xlabel=None):
        a = fig.add_subplot(pos)
        p = perf[perf["perfil"] == chave].sort_values("x")
        xs = range(len(p))
        a.vlines(xs, p["q25"], p["q75"], color=cor, lw=2.2)
        a.plot(xs, p["media"], "-o", color=cor, ms=5.5, lw=1.8)
        a.axhline(0, color=MUDO, lw=0.8) if p["q75"].max() > 0 > p["q25"].min() else None
        a.set_xticks(list(xs))
        a.set_xticklabels(xt, fontsize=10)
        a.set_ylabel("SHAP (pontos Saeb)", fontsize=10)
        if xlabel:
            a.set_xlabel(xlabel, fontsize=10)
        a.set_title(titulo, fontsize=11.5, loc="left", color=TINTA)
        for lado in ("top", "right"):
            a.spines[lado].set_visible(False)
        a.grid(axis="y", color=GRADE, lw=0.8)
        a.set_axisbelow(True)
        a.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: _br(v, 0)))

    painel(gs[0, 1], "estudo", ["Não estuda", "< 1h", "1 a 2h", "> 2h"], "(b) Tempo de estudo", AZUL)
    painel(gs[1, 1], "reprov_por_inse", ["1º", "2º", "3º", "4º", "5º"],
           "(c) Reprovação, por quinto de INSE", LARANJA, "Quinto de INSE (1º = mais baixo); só reprovados")
    _salvar(fig, "art_fig4_shap.jpg")


def main():
    DIR_FIG.mkdir(parents=True, exist_ok=True)
    fig_desenho()
    fig_gradientes()
    fig_coeficientes()
    fig_shap()


if __name__ == "__main__":
    main()
