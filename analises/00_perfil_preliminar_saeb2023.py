import sys, pandas as pd, numpy as np
base = r"C:/Users/evert/OneDrive/Documentos/Faculdade/Ciencia de Dados II/MICRODADOS_SAEB_2023/DADOS/"
grade = sys.argv[1]
q = ['TX_RESP_Q01','TX_RESP_Q02','TX_RESP_Q04','TX_RESP_Q08','TX_RESP_Q09','TX_RESP_Q10a','TX_RESP_Q10b','TX_RESP_Q10c',
     'TX_RESP_Q10d','TX_RESP_Q10e','TX_RESP_Q10f','TX_RESP_Q17','TX_RESP_Q19','TX_RESP_Q20','TX_RESP_Q21a','TX_RESP_Q21d','TX_RESP_Q23a']
cols = ['ID_UF','ID_ESCOLA','ID_TURMA','IN_PUBLICA','ID_LOCALIZACAO','IN_SITUACAO_CENSO','IN_PRESENCA_MT','IN_PROFICIENCIA_MT',
        'IN_AMOSTRA','ESTRATO','PESO_ALUNO_MT','PROFICIENCIA_MT_SAEB','PROFICIENCIA_LP_SAEB','IN_PREENCHIMENTO_QUESTIONARIO',
        'IN_INSE','INSE_ALUNO','NU_TIPO_NIVEL_INSE'] + q
df = pd.read_csv(base + f"TS_ALUNO_{grade}.csv", sep=';', usecols=lambda c: c in cols, dtype=str, encoding='latin-1')
print("GRADE", grade, "rows", len(df), "cols", df.shape[1])
num = ['IN_PUBLICA','IN_PRESENCA_MT','IN_PROFICIENCIA_MT','IN_AMOSTRA','PESO_ALUNO_MT','PROFICIENCIA_MT_SAEB','PROFICIENCIA_LP_SAEB',
       'IN_PREENCHIMENTO_QUESTIONARIO','IN_INSE','INSE_ALUNO','IN_SITUACAO_CENSO','ID_LOCALIZACAO']
for c in num:
    if c in df: df[c] = pd.to_numeric(df[c].str.replace(',', '.'), errors='coerce')
print("schools", df.ID_ESCOLA.nunique(), "turmas", df.ID_TURMA.nunique())
for c in ['IN_PRESENCA_MT','IN_PROFICIENCIA_MT','IN_AMOSTRA','IN_PREENCHIMENTO_QUESTIONARIO','IN_INSE','IN_PUBLICA','IN_SITUACAO_CENSO']:
    if c in df: print(c, df[c].value_counts(dropna=False).to_dict())
print("PESO_MT nonnull", df.PESO_ALUNO_MT.notna().sum(), "PROF_MT nonnull", df.PROFICIENCIA_MT_SAEB.notna().sum())
an = df[df.PROFICIENCIA_MT_SAEB.notna() & df.PESO_ALUNO_MT.notna()].copy()
print("analytic (prof+peso)", len(an))
w = an.PESO_ALUNO_MT
print("weighted mean MT", round(np.average(an.PROFICIENCIA_MT_SAEB, weights=w), 1), "sd", round(an.PROFICIENCIA_MT_SAEB.std(), 1),
      "sum weights", round(w.sum()))
print("INSE nonnull among analytic", an.INSE_ALUNO.notna().mean().round(3))
for c in q:
    if c not in an: continue
    vc = an[c].fillna('NaN').value_counts(normalize=True).round(3).to_dict()
    print(c, vc)
# descriptive weighted means by key items
for c in ['TX_RESP_Q19','TX_RESP_Q20','TX_RESP_Q21a','TX_RESP_Q10d','TX_RESP_Q08']:
    if c not in an: continue
    g = an.groupby(an[c].fillna('NaN')).apply(lambda d: pd.Series({'n': len(d), 'mean_MT': np.average(d.PROFICIENCIA_MT_SAEB, weights=d.PESO_ALUNO_MT)}))
    print("by", c); print(g.round(1).to_string())
# crude ICC (unweighted one-way ANOVA estimator) on MT
s = an.groupby('ID_ESCOLA').PROFICIENCIA_MT_SAEB
k = s.size(); n0 = (len(an) - (k**2).sum()/len(an)) / (len(k)-1)
msb = (k*(s.mean()-an.PROFICIENCIA_MT_SAEB.mean())**2).sum()/(len(k)-1)
msw = ((an.PROFICIENCIA_MT_SAEB - s.transform('mean'))**2).sum()/(len(an)-len(k))
sb2 = (msb-msw)/n0
print("ICC_school_MT (unweighted ANOVA)", round(sb2/(sb2+msw), 3), "mean students/school", round(k.mean(), 1))
# questionnaire missingness among those with proficiency
an['q_any'] = an[[c for c in q if c in an]].apply(lambda r: r.isin(['A','B','C','D','E','F']).any(), axis=1)
print("prof students with any valid questionnaire item", round(an.q_any.mean(), 3))
pub = an.groupby('IN_PUBLICA').apply(lambda d: pd.Series({'n': len(d), 'mean_MT': np.average(d.PROFICIENCIA_MT_SAEB, weights=d.PESO_ALUNO_MT)}))
print(pub.round(1).to_string())
