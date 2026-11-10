"""Etapa 4b - Comparação dos padrões do Saeb 2023 com os indicadores publicados do PISA 2025 (H6).

O lado do PISA usa SOMENTE números publicados pela OCDE (não há reanálise de microdados):
  [NP] OECD (2026b) - PISA 2025 Results (Volume I): Brazil, country note.
  [V1] OECD (2026a) - PISA 2025 Results (Volume I), capítulo 4 (padrões gerais, "quase todos os países").
O lado do Saeb é calculado aqui. As escalas NÃO são convertidas; compara-se direção e ordem de grandeza.

Entradas: dados/saeb2023_9ef_publicas.parquet; TS_ALUNO_9EF.csv (para incluir a rede privada no item 1);
          resultados/tab_modelos_coef.csv e tab_modelos_ajuste.csv (etapa 3)
Saídas  : resultados/tab_pisa_gradiente.csv   gradiente socioeconômico no Saeb (públicas x todas as redes)
          resultados/tab_pisa_comparacao.csv  quadro comparativo Saeb 2023 x PISA 2025
"""
import numpy as np
import pandas as pd

import config as cfg


def _stats_gradiente(d: pd.DataFrame, rotulo: str) -> dict:
    """R² do INSE sozinho, diferença entre quartos extremos de INSE e confiabilidade aproximada."""
    w, y, x = d["peso"].to_numpy(), d["prof"].to_numpy(), d["inse"].to_numpy()
    my, mx = np.average(y, weights=w), np.average(x, weights=w)
    vy, vx = np.average((y - my) ** 2, weights=w), np.average((x - mx) ** 2, weights=w)
    r = np.average((y - my) * (x - mx), weights=w) / np.sqrt(vy * vx)
    # quartos ponderados de INSE
    ordem = np.argsort(x)
    acum = np.cumsum(w[ordem]) / w.sum()
    q25, q75 = x[ordem][np.searchsorted(acum, 0.25)], x[ordem][np.searchsorted(acum, 0.75)]
    baixo, alto = x <= q25, x >= q75
    dif = np.average(y[alto], weights=w[alto]) - np.average(y[baixo], weights=w[baixo])
    # confiabilidade marginal aproximada da proficiência (duas convenções; ver nota no quadro)
    erro2 = np.average(d["ep"].to_numpy() ** 2, weights=w)
    return {"amostra": rotulo, "n": len(d), "r2_inse_pct": 100 * r ** 2, "dp_prof": np.sqrt(vy),
            "dif_quartos_extremos_pontos": dif, "dif_quartos_extremos_dp": dif / np.sqrt(vy),
            "confiab_aprox_min": 1 - erro2 / vy, "confiab_aprox_max": vy / (vy + erro2)}


def ler_todas_as_redes() -> pd.DataFrame:
    cols = ["IN_PUBLICA", "IN_SITUACAO_CENSO", "IN_PROFICIENCIA_MT", "IN_INSE", "PESO_ALUNO_MT",
            "PROFICIENCIA_MT_SAEB", "ERRO_PADRAO_MT_SAEB", "INSE_ALUNO"]
    d = pd.read_csv(cfg.ARQ_ALUNO_9EF, sep=cfg.CSV_SEP, encoding=cfg.CSV_ENCODING, usecols=cols)
    d = d[(d["IN_SITUACAO_CENSO"] == 1) & (d["IN_PROFICIENCIA_MT"] == 1) & (d["IN_INSE"] == 1)
          & d["PESO_ALUNO_MT"].notna() & d["INSE_ALUNO"].notna()]
    return d.rename(columns={"PESO_ALUNO_MT": "peso", "PROFICIENCIA_MT_SAEB": "prof",
                             "ERRO_PADRAO_MT_SAEB": "ep", "INSE_ALUNO": "inse", "IN_PUBLICA": "publica"})


def _br(v, casas=1):
    return f"{v:.{casas}f}".replace(".", ",").replace("-", "−")


def main() -> None:
    # 1. Gradiente socioeconômico no Saeb -------------------------------------------------
    todas = ler_todas_as_redes()
    base = pd.read_parquet(cfg.ARQ_BASE_ANALITICA)
    cc = base[base["caso_completo"] == 1].rename(columns={"peso_mt": "peso", "prof_mt": "prof", "ep_mt": "ep"})
    grad = pd.DataFrame([
        _stats_gradiente(cc[["peso", "prof", "ep", "inse"]], "Públicas, amostra do modelo (casos completos)"),
        _stats_gradiente(todas[todas["publica"] == 1], "Públicas, todos com INSE e proficiência"),
        _stats_gradiente(todas, "Públicas e privadas, todos com INSE e proficiência"),
    ])
    grad.round(4).to_csv(cfg.DIR_RESULTADOS / "tab_pisa_gradiente.csv", index=False)
    g_cc, g_pub, g_all = grad.iloc[0], grad.iloc[1], grad.iloc[2]

    # 2. Indicadores do Saeb (amostra do modelo) ---------------------------------------------
    w = cc["peso"]
    pct = lambda cond: 100 * np.average(cond.astype(float), weights=w)
    coef = pd.read_csv(cfg.DIR_RESULTADOS / "tab_modelos_coef.csv")
    b5 = coef[coef["modelo"] == "B5"].set_index("termo")
    ef = coef[coef["modelo"] == "EF escola"].set_index("termo")
    dp = g_cc["dp_prof"]

    def efeito(t):
        return f"{_br(b5.loc[t, 'coef'])} pontos ({_br(b5.loc[t, 'coef'] / dp, 2)} DP); na mesma escola: {_br(ef.loc[t, 'coef'])}"

    # 3. Quadro comparativo ---------------------------------------------------------------
    linhas = [
        ("Variância do desempenho associada ao nível socioeconômico",
         f"INSE explica {_br(g_cc['r2_inse_pct'])}% da variância em Matemática nas escolas públicas; "
         f"{_br(g_all['r2_inse_pct'])}% quando se incluem as privadas",
         "ESCS explica 16% da variância em Ciências (OCDE: 12%) [NP]",
         "Mesma direção; magnitude menor no Saeb",
         "Recorte de rede, erro de medida da proficiência individual (confiabilidade aproximada entre "
         f"{_br(g_cc['confiab_aprox_min'], 2)} e {_br(g_cc['confiab_aprox_max'], 2)}), índices e áreas diferentes"),
        ("Diferença entre o quarto mais alto e o mais baixo de nível socioeconômico",
         f"{_br(g_cc['dif_quartos_extremos_pontos'])} pontos Saeb ({_br(g_cc['dif_quartos_extremos_dp'], 2)} DP) nas públicas; "
         f"{_br(g_all['dif_quartos_extremos_pontos'])} pontos ({_br(g_all['dif_quartos_extremos_dp'], 2)} DP) com as privadas",
         "96 pontos PISA em Ciências (OCDE: 85); diferença aumentou entre 2015 e 2025 [NP]",
         "Mesma direção",
         "Escalas não comparáveis em pontos; o DP brasileiro no PISA 2025 não consta da nota do país"),
        ("Reprovação / repetência",
         f"{_br(pct(cc['reprov'] > 0))}% já reprovaram; uma reprovação: {efeito('rep_1')}",
         "Não analisada nos capítulos do Volume I (apenas tabelas do Anexo B1) [V1]. No PISA 2022, a repetência "
         "teve o maior coeficiente negativo para o Brasil (CITO; MARÔCO, 2026)",
         "Mesma direção (com base no PISA 2022)",
         "Comparação com o PISA 2025 depende das tabelas do anexo ou dos microdados"),
        ("Frequência às aulas",
         "Não medida (o questionário não registra faltas); aproximada pela trajetória",
         "55% faltaram ao menos um dia nas duas semanas anteriores (OCDE: 22%; Brasil 2022: 22%) [NP]; faltar se associa "
         "a menor desempenho em quase todos os países, mesmo controlando o nível socioeconômico [V1]",
         "Não comparável diretamente",
         "Lacuna do Saeb; a oscilação brasileira (50% em 2018, 22% em 2022, 55% em 2025) pede cautela"),
        ("Interesse dos pais pelo dia a dia escolar",
         f"{_br(pct(cc['fam_conversa'] == 2))}% dizem que os pais conversam sempre sobre a escola; "
         f"conversar (às vezes): {efeito('conv_vezes')}",
         "51% dizem que os pais perguntam ao menos semanalmente o que fizeram na escola (62% em 2022) [NP]; associação "
         "positiva com o desempenho, puxada pelo interesse no dia a dia escolar [V1]",
         "Mesma direção",
         "Itens e escalas de resposta diferentes"),
        ("Incentivo / cobrança dos pais",
         f"Índice de incentivo (+1 DP): {efeito('incentivo_z')}",
         "Conversas sobre o futuro educacional se associam negativamente ao desempenho na média da OCDE; a OCDE sugere que "
         "pais de estudantes com baixo desempenho tendem a motivá-los mais [V1]",
         "Mesma direção (construtos análogos, não idênticos)",
         "Leitura compatível com envolvimento reativo; não indica que incentivar prejudique"),
        ("Tempo de estudo fora da escola",
         f"1 a 2h por dia: {efeito('est_1a2h')}; mais de 2h: {_br(b5.loc['est_mais2h', 'coef'])} pontos",
         "Sem indicador equivalente na nota do país [NP]",
         "Sem comparação", "—"),
    ]
    quadro = pd.DataFrame(linhas, columns=["dimensao", "saeb_2023_9ano_publicas", "pisa_2025_brasil",
                                           "convergencia", "ressalvas"])
    quadro.to_csv(cfg.DIR_RESULTADOS / "tab_pisa_comparacao.csv", index=False)

    print(grad.round(3).to_string(index=False))
    for _, r in quadro.iterrows():
        print(f"\n- {r['dimensao']}\n    Saeb: {r['saeb_2023_9ano_publicas']}\n    PISA: {r['pisa_2025_brasil']}\n    => {r['convergencia']}")
    print("\nEtapa 4b concluída.")


if __name__ == "__main__":
    main()
