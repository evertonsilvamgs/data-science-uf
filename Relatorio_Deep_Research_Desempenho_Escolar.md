# Desempenho escolar no Brasil: trajetória, hábitos de estudo e contexto familiar (SAEB 2023 × PISA 2025)

**Relatório de pesquisa exploratória (Deep Research), base metodológica para o artigo de Ciências de Dados II**
Data: 07/10/2026

**Convenção de leitura.** Cada afirmação traz uma destas marcas:
- **[FONTE]**: fato encontrado em fonte verificável, citada na seção 15.
- **[DADO]**: número que eu calculei nos microdados da pasta `MICRODADOS_SAEB_2023`. É exploração preliminar e descritiva (médias ponderadas pelo `PESO_ALUNO_MT`), não resultado do artigo. O script está em [analises/00_perfil_preliminar_saeb2023.py](analises/00_perfil_preliminar_saeb2023.py).
- **[INTERPRETAÇÃO]**: leitura minha a partir de fontes ou dados.
- **[PROPOSTA]**: decisão metodológica sugerida.

---

## TL;DR

1. **A pergunta original não é investigável do jeito que está.** O questionário do aluno do SAEB 2023 **não mede frequência (faltas)** **[DADO: dicionário]**. Mede trajetória: reprovação (Q19), abandono (Q20) e idade, da qual se deriva a distorção idade-série (Q02). Mede também tempo de estudo (Q21a), envolvimento familiar (Q10a–f) e nível socioeconômico (INSE_ALUNO e escolaridade dos pais). Proponho trocar "frequência" por **trajetória escolar** e buscar a frequência propriamente dita no PISA 2025, que mede *truancy* (cabular aulas ou dias) diretamente.
2. **Os códigos de escola e de município do SAEB público são máscaras** **[FONTE: Leia-Me SAEB 2023, seção 6]**. Não dá para juntar os alunos do SAEB com o Censo Escolar, o IDEB ou o IBGE por escola ou município. Dá para juntar, **dentro do SAEB**, aluno, escola, professor e diretor (a máscara é a mesma em todas as bases), e usar a UF, que é real.
3. **Pergunta recomendada (9º ano EF, Matemática):** *"Depois de controlar o nível socioeconômico, em que medida a trajetória escolar (reprovação, abandono e distorção idade-série), o tempo de estudo fora da escola e o envolvimento familiar se associam à proficiência dos estudantes do 9º ano no SAEB 2023? Essas associações se mantêm dentro das escolas e variam com o nível socioeconômico?"* O método central é regressão multinível (aluno dentro de escola) com pesos amostrais, comparada a um modelo de efeitos fixos de escola. Gradient boosting com SHAP entra só como análise complementar de não linearidades.
4. **Sobre o "PISA 2026":** a edição que o professor quer é o **PISA 2025**, com resultados divulgados em **08/09/2026** e microdados públicos já disponíveis **[FONTE: OCDE]**. O Brasil teve 30.140 alunos em 1.053 escolas. O ESCS explica 16% da variância em ciências. A taxa de alunos que faltaram ao menos um dia nas duas semanas anteriores ao teste foi de 55% (22% em 2022). O apoio familiar relatado caiu (62% → 51%). **[FONTE: country note Brasil]** Como relacionar: (a) comparar **direção e magnitude padronizada** das associações, sem equiparar escalas; (b) replicar, de forma opcional, um modelo análogo nos microdados do PISA 2025 do Brasil.
5. **Achados descritivos que já sinalizam boas discussões** **[DADO, preliminar]**:
   - Quem relata ter sido reprovado tem média em Matemática cerca de 35 a 41 pontos menor no 9º ano.
   - O "incentivo dos pais a fazer a tarefa" tem gradiente **invertido** no 9º ano e no EM. Isso é consistente com envolvimento parental reativo e com Hill & Tyson (2009).
   - No 5º ano, mais de 2 horas de estudo diário se associa a nota **menor** que 1 a 2 horas.
   - A correlação intraclasse (ICC) por escola fica entre 0,18 e 0,23, o que justifica o modelo multinível.

---

## 1. Diagnóstico inicial

**O tema é bom, mas a pergunta original tem três problemas.**

| Problema | Por que importa | Encaminhamento [PROPOSTA] |
|---|---|---|
| "Frequência" não existe no SAEB 2023 | Não há item sobre faltas no questionário do aluno; há apenas Q10e, "pais incentivam a comparecer às aulas", com efeito teto: 86% marcam "sempre" **[DADO]** | Usar a **trajetória** (reprovação, abandono, distorção) como construto no SAEB e a **frequência** via PISA 2025 (truancy) |
| "Explicar as notas" sugere causalidade | O SAEB é transversal e observacional; reprovação e estudo são endógenos (alunos com dificuldade estudam mais ou menos, reprovam, recebem mais cobrança) | Falar em **associação condicional**, com linguagem não causal. Usar efeitos fixos de escola só para reduzir confundimento entre escolas |
| "Contexto familiar" mistura coisas diferentes | NSE (recursos) e envolvimento parental (práticas) têm teorias e efeitos distintos. O INSE **já inclui** a escolaridade dos pais | Separar **INSE** (controle) de **práticas familiares** (exposição) e não colocar Q08/Q09 junto com o INSE no mesmo modelo |

**Avaliação geral [INTERPRETAÇÃO].** A pergunta "X ajuda a explicar Y?" é respondida quase trivialmente: com cerca de 2 milhões de alunos, tudo é estatisticamente significativo. Um artigo bom precisa de uma pergunta sobre **magnitude, robustez (dentro vs. entre escolas) e heterogeneidade (por NSE)**. É isso que a pergunta recomendada faz.

---

## 2. Estado da arte (síntese)

### 2.1 Origem social e efeito-escola
- Desde o Relatório Coleman, o debate central é quanto do desempenho se deve à família e quanto à escola **[FONTE: Coleman et al., 1966]**.
- A meta-análise de Sirin (2005), com 74 amostras e 101.157 alunos, encontra associação de média a forte entre NSE e desempenho, moderada pela forma de medir o NSE e pela unidade de análise (aluno vs. escola) **[FONTE]**. **Implicação:** o INSE deve ser o principal controle, e os efeitos no nível do aluno e no nível da escola devem ser separados.
- No Brasil, com SAEB 1999 (8ª série) e HLM, cerca de 80% da variância entre escolas se deve à composição socioeconômica **[FONTE: Albernaz, Ferreira & Franco, 2002]**.
- O INSE do INEP vem da metodologia TRI de Alves, Soares & Xavier (2014) **[FONTE]**.
- Escolas com alunos de menor NSE têm IDEB pior mesmo com controles **[FONTE: Alves & Soares, 2013]**.
- O efeito-escola existe e é mensurável com modelos hierárquicos no SAEB **[FONTE: Andrade & Soares, 2008]**.
- Fatores que elevam a média da escola podem ampliar a desigualdade interna **[FONTE: Franco et al., 2007]**.
- Os fatores de eficácia favorecem mais os alunos brancos **[FONTE: Soares & Alves, 2003]**. **Atenção:** o título correto desse artigo é "Desigualdades raciais no sistema brasileiro de educação básica", sem "e de gênero".

### 2.2 Trajetória: reprovação e distorção idade-série
- No SAEB 2001 (3ª série EM), cada ano de atraso escolar custa cerca de 9,7 pontos. O percentual de repetentes da escola tem efeito negativo próprio **[FONTE: Laros, Marciano & Andrade, 2012]**.
- Andrade & Laros (2007) encontram ICC de 0,17, com o atraso escolar entre as variáveis mais fortes **[FONTE]**. Isso **converge** com o ICC de 0,185 que calculei no 9º ano de 2023 **[DADO]**.
- A perda associada à defasagem é não linear (quadrática). A promoção automática em SP e MG não pareceu reduzir a aprendizagem **[FONTE: Ferrão, Beltrão & Santos, 2002]**.
- Em dados longitudinais de MG, entre alunos com a mesma proficiência, quem não repetiu tende a ter proficiência maior no ano seguinte **[FONTE: Riani, Silva & Soares, 2012]**.
- **Contraponto metodológico essencial:** desenhos de pesquisa melhores encontram efeitos da retenção **menos negativos** **[FONTE: Allen et al., 2009]**. Isso indica viés de seleção em estudos transversais como o nosso.
- Evidência causal latino-americana: no Uruguai, a reprovação aumenta a evasão **[FONTE: Manacorda, 2012]**.
- Com dados do PISA 2022 do Brasil, a reprovação tem o maior coeficiente negativo do modelo, e o SAEB 2021 por UF se correlaciona com o PISA **[FONTE: Cito & Marôco, 2026]**. Esse é o elo mais direto entre SAEB e PISA na literatura recente.

### 2.3 Dever de casa e tempo de estudo
- Há associação positiva consistente, mais forte nos anos finais e no ensino médio **[FONTE: Cooper, Robinson & Patall, 2006]**.
- O esforço prediz melhor que o tempo **[FONTE secundária: Trautwein, 2007]**.
- **Achado crucial para nós:** a relação entre tempo de dever e desempenho é **negativa no nível individual e positiva no nível da escola** **[FONTE: Fernández-Alonso et al., 2017]**. É uma razão direta para separar os efeitos dentro e entre escolas.
- **Lacuna:** não encontrei artigo revisado por pares e verificável sobre dever de casa e proficiência com SAEB ou Prova Brasil. O que apareceu foram dissertações e TCCs. **Isso é uma oportunidade de contribuição.**

### 2.4 Envolvimento parental
- O envolvimento parental se associa positivamente ao desempenho, **exceto a ajuda direta no dever de casa**. A "socialização acadêmica" (expectativas, conversar sobre a escola) tem a associação mais forte **[FONTE: Hill & Tyson, 2009; Wilder, 2014]**.
- Jeynes (2005, 2007) encontra efeitos de cerca de 0,5 a 0,75 desvio-padrão **[FONTE]**.
- No Brasil, no modelo conjunto prevalecem o NSE e o capital cultural sobre outros fatores familiares **[FONTE: Alves et al., 2013, *Dados*]**.

### 2.5 Frequência e absenteísmo
- Há evidência quase-causal de que faltas reduzem o desempenho, com dano maior para alunos de baixa renda **[FONTE: Gottfried, 2010, 2014; Gershenson, Jacknowitz & Brannegan, 2017]**.
- **Lacuna brasileira:** não encontrei estudo revisado por pares e verificável sobre faltas do aluno e proficiência no Brasil. O mais próximo trata de absenteísmo docente. Isso reforça usar o PISA 2025 para o construto frequência.

### 2.6 Machine learning em dados educacionais
- Há uma distinção entre explicar e predizer **[FONTE: Shmueli, 2010; Breiman, 2001]**.
- O SHAP é uma ferramenta de interpretação de modelos **[FONTE: Lundberg & Lee, 2017]**.
- Aplicações brasileiras:
  - Random Forest com SAEB e SHAP aponta o NSE médio da escola como preditor dominante **[FONTE: Tertulino & Alencar, 2026; verificado só o resumo]**;
  - Random Forest seguido de regressão logística multinível no PISA 2018 do Brasil, com a reprovação associada negativamente **[FONTE: San Martin Soares, 2024]**;
  - GBM no IDEB, com correlação apenas moderada entre previsto e observado **[FONTE: Maia, Bueno & Sato, 2021]**.
- **[INTERPRETAÇÃO]** A literatura de ML repete que "o NSE é o mais importante". Um artigo que só faça Random Forest + SHAP **não traz novidade**. ML deve ser auxiliar.

### 2.7 Cautelas com avaliações em larga escala
- É preciso tratar corretamente pesos, desenho amostral e valores plausíveis **[FONTE: Rutkowski et al., 2010; Wu, 2005]**.
- Pós-pandemia: Lichand et al. (2022) e Betthäuser et al. (2023) documentam perdas de aprendizagem maiores entre os mais pobres **[FONTE]**. O SAEB 2023 é uma medida pós-pandemia, o que importa para interpretar as médias.

---

## 3. Avaliação do SAEB 2023 (arquivos locais)

### 3.1 Bases disponíveis [DADO: pasta e dicionário]

| Arquivo | Conteúdo | Tamanho | Útil para |
|---|---|---|---|
| TS_ALUNO_2EF | prova LP e MT, **sem questionário** | 9 MB | não serve para a pergunta |
| TS_ALUNO_5EF | prova, questionário, INSE | 1,07 GB | alternativa (mas veja os problemas abaixo) |
| **TS_ALUNO_9EF** | prova (LP, MT, CH e CN amostral), questionário, INSE | 1,11 GB | **base principal recomendada** |
| TS_ALUNO_34EM | prova, questionário (+Q25 EJA), INSE | 0,83 GB | robustez ou extensão |
| TS_ESCOLA | INSE da escola, adequação da formação docente, taxa de participação, distribuição em níveis, médias | 22 MB | variáveis de nível 2 |
| TS_PROFESSOR / TS_DIRETOR | questionários (224 itens no diretor) | 139 / 55 MB | nível 2 opcional (clima, gestão) |
| TS_SECRETARIO_MUNICIPAL | questionário municipal | 2 MB | fora do escopo |
| TS_ITEM | parâmetros dos itens | — | fora do escopo |

Os arquivos são CSV separados por `;`, com encoding latin-1, e acompanham inputs em R, SAS e SPSS.

### 3.2 Variáveis relevantes no TS_ALUNO_9EF [DADO: dicionário]

- **Desfecho:**
  - `PROFICIENCIA_MT_SAEB` e `PROFICIENCIA_LP_SAEB`, na escala SAEB (média 250, DP 50, referência SAEB/97);
  - `ERRO_PADRAO_*_SAEB`;
  - versões padronizadas `PROFICIENCIA_MT` (média 0, DP 1).
- **Pesos e desenho:**
  - `PESO_ALUNO_MT` (idêntico ao de LP para 5º, 9º e EM) e `PESO_ALUNO_INSE`;
  - `ESTRATO`, `IN_AMOSTRA`, `IN_SITUACAO_CENSO`, `IN_PROFICIENCIA_MT`.
- **Trajetória:**
  - Q19 "já foi reprovado?" (não / uma vez / duas ou mais);
  - Q20 "abandonou a escola?";
  - Q02 idade (13 ou menos até 18 ou mais), de onde vem a **distorção idade-série**;
  - Q17 idade de entrada na escola;
  - Q18 trajetória pública ou privada.
- **Hábitos de estudo e uso do tempo:**
  - Q21a estudar fora da escola (não / menos de 1h / 1–2h / mais de 2h);
  - Q21b cursos extracurriculares;
  - Q21c trabalho doméstico;
  - Q21d trabalho fora de casa;
  - Q21e lazer.
- **Envolvimento familiar:** Q10a–f, sobre a frequência com que os pais leem, conversam sobre a escola, incentivam a estudar, a fazer a tarefa e a comparecer, e vão às reuniões.
- **NSE:** `INSE_ALUNO`, `NU_TIPO_NIVEL_INSE` (níveis I–VIII), Q08 e Q09 (escolaridade da mãe e do pai), Q11–Q13 (bens e serviços).
- **Demografia:** Q01 sexo, Q04 cor/raça, Q05 deficiência/TEA, Q06–Q07 composição do domicílio.
- **Engajamento e escola:** Q22 práticas docentes, Q23 interesse, segurança e expectativa dos professores, Q24 expectativa futura.
- **Contexto (nível 2):** `IN_PUBLICA`, `ID_LOCALIZACAO`, `ID_AREA`, `ID_UF` (real), `ID_ESCOLA` (máscara).

### 3.3 Qualidade e cobertura [DADO, preliminar]

| Indicador | 5º EF | **9º EF** | 3ª/4ª EM |
|---|---|---|---|
| Registros | 2.442.143 | 2.502.907 | 2.091.337 |
| Presentes em MT | 86,0% | **83,6%** | **73,1%** |
| Com proficiência e peso | 2.086.070 | **2.083.218** | 1.519.701 |
| Escolas (máscara) | 46.213 | 38.115 | 20.730 |
| Com INSE válido (entre os analisáveis) | 93,8% | 95,1% | 94,2% |
| Q08 "não sei a escolaridade da mãe" | **47,1%** | 27,6% | 12,9% |
| Itens em branco (".") por questão | ~3–6% | ~2–6% | ~2–7% |
| ICC escola (MT, ANOVA não ponderada) | 0,231 | **0,185** | 0,202 |
| Média ponderada MT (conferir com o oficial) | 224,8 | 257,1 | 274,1 |

**Leitura [INTERPRETAÇÃO]:**
- **O 9º ano é a melhor base.** No 5º ano, quase metade não sabe a escolaridade da mãe, o que indica limites de compreensão do questionário aos 10–11 anos. O EM tem 27% de ausência no dia da prova, o que gera viés de seleção forte, porque quem falta tende a ter trajetória mais frágil. O 9º ano também é o mais próximo da população do PISA: 45,6% dos alunos do 9º ano declaram 15 anos **[DADO]**.
- **Desenho:** nas três séries, o número de registros com `IN_AMOSTRA = 1` é exatamente igual ao de `IN_PUBLICA = 0` (por exemplo, 55.764 no 9º ano) **[DADO]**. Isso indica que **as escolas públicas são censitárias e as privadas são amostrais**. Por isso os pesos são indispensáveis: sem eles, a rede privada fica sub-representada em termos relativos.
- **Proficiência:** o SAEB público traz **uma estimativa pontual por aluno, com erro-padrão**, e não valores plausíveis como o PISA **[DADO: dicionário]**. Isso não viesa coeficientes de regressão de forma relevante (o erro está no desfecho), mas subestima a incerteza e distorce estimativas de variância e de percentis. Isso deve ir para as limitações.
- **Ponto de atenção:** em Q21d ("trabalhar fora de casa"), 17,3% dos alunos do 9º ano e **39,8% do EM** marcam "mais de 2 horas por dia" **[DADO]**. No EM é plausível; no 9º ano parece alto e pode ser erro de compreensão do item. Recomendo tratar essa variável só como controle, com cautela.
- **Os itens Q10c e Q10e têm efeito teto** (76% e 86% em "sempre"), com pouca variabilidade.
- **14.000 alunos (0,5%) têm `IN_SITUACAO_CENSO = 0`.** O INEP os exclui do cálculo oficial **[FONTE: Leia-Me]**. Devemos fazer o mesmo.

### 3.4 Gradientes descritivos (9º ano, média ponderada em MT) [DADO, só descritivo e sem controles]

| Variável | Categorias → média MT |
|---|---|
| Q19 reprovação | nunca **264,5** · uma vez **229,5** · duas ou mais **223,7** |
| Q20 abandono | nunca **259,0** · uma vez **237,5** · duas ou mais **232,4** |
| Q21a estudo fora da escola | não estuda **240,9** · menos de 1h **254,8** · 1–2h **267,1** · mais de 2h **266,2** (platô) |
| Q10d pais incentivam a tarefa | nunca **262,6** · às vezes **259,3** · sempre **257,5** (**gradiente invertido**) |
| Q08 escolaridade da mãe | não completou o 5º ano **231,3** … superior **283,5** · "não sei" **244,2** |
| Rede | privada **295,0** · pública **249,9** |

Os mesmos padrões nas outras séries [DADO]:
- **Q10d** é invertido no EM (282,6 → 272,6) e **positivo no 5º ano** (216,2 → 229,7). **[INTERPRETAÇÃO]** Isso é compatível com envolvimento **reativo**: pais cobram mais de quem vai mal, e esse padrão se fortalece com a idade. É coerente com Hill & Tyson (2009) e uma hipótese ótima para o artigo.
- **Q21a no 5º ano é não monotônico:** mais de 2h dá 211,2, contra 238,2 em 1–2h. No EM é monotônico até 303,2. Isso é compatível com Fernández-Alonso et al. (2017).
- Os alunos que deixam itens em branco têm médias bem menores (por exemplo, 245 contra 264 na Q19). **A ausência não é aleatória**, e isso precisa de tratamento explícito.

### 3.5 O SAEB 2023 é suficiente?
**Sim** para trajetória, estudo, envolvimento familiar e NSE no nível do aluno, com estrutura multinível por escola mascarada. **Não** para:
1. frequência ou faltas;
2. variáveis de escola externas, como infraestrutura do Censo, IDEB e taxas de rendimento, porque as máscaras impedem o cruzamento;
3. variáveis municipais.

O PISA 2025 resolve (1). O item (2) só se resolve com análise no nível da escola (desenho alternativo, seção 5, P4) ou pelo Sedap/INEP.

---

## 4. Bases complementares

Situação de verificação em 07/10/2026; os detalhes e as URLs estão na seção 15.

| Base | Granularidade | Variáveis úteis | Liga com o SAEB público? | Veredito [PROPOSTA] |
|---|---|---|---|---|
| **PISA 2025 (OCDE), PUFs** | aluno e escola (amostra de 15 anos) | proficiência (10 PVs), ESCS, repetência, **truancy**, apoio familiar, pesos BRR | **Não** (outra amostra) | **Usar em análise paralela comparativa.** É a forma correta de cumprir a exigência |
| PISA 2022 (OCDE) | aluno e escola | idem | Não | Para tendência 2022 → 2025 (opcional) |
| INSE 2023 (INEP) | escola, município, UF | INSE médio, % por nível | Escola: não (máscara). **UF: sim** | No nível do aluno, usar `INSE_ALUNO`, que já está no SAEB |
| Censo Escolar 2023 (INEP) | escola (público); aluno só via Sedap | infraestrutura, contagens | Não (máscara) | Só para o desenho P4 (nível escola) |
| IDEB e Indicadores Educacionais 2023 (TDI, taxas de rendimento, AFD, ICG, IED, ATU, HAD, IRD) | escola, município, UF | distorção, reprovação, abandono, docência | Escola e município: não. **UF: sim** | Contexto por UF (n = 27, só descritivo) ou desenho P4 |
| Taxas de Transição (INEP) | município e UF (até 2021–2022) | promoção, repetência, evasão | UF | Contexto descritivo |
| PNAD Contínua Educação (IBGE) | pessoa (amostra) | frequência escolar, atraso, renda | Só agregado por UF | Contexto |
| Censo 2022, PIB municipal, IDHM | município | contexto territorial | Não (máscara de município) | Fora do desenho principal |
| Enem | participante | questionário e notas | Não. Desde 2024 o arquivo foi separado e não há chave entre questionário e nota | Não usar |
| Frequência do Bolsa Família (MEC/Sistema Presença) | UF (público); município sob pedido | frequência | UF | Contexto opcional |
| Base dos Dados (BigQuery) | idem às fontes | SAEB até 2023, Censo e IDEB | Mesmas restrições | Alternativa de acesso |
| ERCE 2019 (UNESCO) e TALIS 2024 (OCDE) | aluno/família; professor | dever de casa, família; prática docente | Não | Horizonte (seção 13+) |
| Sedap (INEP) | microdados com códigos reais | tudo cruzável | Sim | Inviável no prazo da disciplina; citar como trabalho futuro |

**Conclusão [INTERPRETAÇÃO].** A única integração **defensável** no nível do aluno é **SAEB × SAEB**: aluno com TS_ESCOLA, TS_PROFESSOR e TS_DIRETOR pela máscara. Juntar dados por UF (n = 27) cai na **falácia ecológica** quando usado para explicar variação individual; serve só para descrição.

**Não tente reidentificar escolas** cruzando atributos. Isso contraria a finalidade do mascaramento declarada pelo INEP e a LGPD **[FONTE: Leia-Me, seção 6]**.

---

## 5. Possíveis perguntas de pesquisa

### P1. Trajetória, estudo e família no 9º ano (multinível) [recomendada]
- **Pergunta:** depois de controlar o INSE, a trajetória (reprovação, abandono, distorção), o tempo de estudo e as práticas familiares se associam à proficiência em MT no 9º ano? Essas associações se mantêm dentro das escolas e variam por NSE?
- **Variável dependente:** `PROFICIENCIA_MT_SAEB`; LP como robustez.
- **Variáveis independentes:** Q19, Q20, distorção (Q02), Q21a, índices de envolvimento familiar (Q10).
- **Unidade e população:** aluno dentro de escola; 9º ano EF de escolas públicas e privadas; 2023.
- **Hipótese principal:** a trajetória irregular é a associação negativa mais forte depois do NSE e persiste dentro das escolas.
- **Bases:** SAEB 2023 (9EF + TS_ESCOLA); PISA 2025 para a ponte.
- **Método:** MQO ponderado → efeitos fixos de escola → multinível de intercepto aleatório; GBM + SHAP como complemento.
- **Limitações:** transversal, autorrelato, endogeneidade da reprovação, sem frequência.

### P2. "Custo" da reprovação (pseudo-causal)
- **Pergunta:** alunos reprovados têm proficiência menor que alunos comparáveis não reprovados?
- **Variável dependente:** proficiência MT. **Exposição:** Q19.
- **Método:** pareamento por escore de propensão ou ponderação (IPW) com INSE, sexo, raça, idade de entrada e escola.
- **Problema:** a proficiência antes da reprovação não é observada, então o pareamento não resolve a seleção por habilidade prévia. Allen et al. (2009) mostram que exatamente esse viés domina a literatura. **Risco alto de conclusão causal indevida.**

### P3. Decomposição de desigualdades (raça e NSE)
- **Pergunta:** quanto da diferença de proficiência entre brancos e pretos/pardos, ou entre os níveis de INSE, se associa a diferenças de trajetória e de práticas familiares?
- **Método:** decomposição de Oaxaca-Blinder (ou Gelbach), ponderada.
- **Vantagens:** relevância social alta e método de economia aplicada interessante.
- **Riscos:** a interpretação de "parcela explicada" pode soar causal e culpabilizar famílias. Exige muito cuidado na redação.

### P4. Nível escola: fluxo e infraestrutura (arquivos públicos com códigos reais)
- **Pergunta:** a nota SAEB média da escola se associa à taxa de distorção, à reprovação e ao abandono, ao INSE escolar e à infraestrutura?
- **Bases:** IDEB por escola (nota SAEB 2023), INSE 2023 escolas, TDI, taxas de rendimento, AFD e Censo Escolar 2023, todos ligados pelo código INEP real.
- **Vantagens:** é a única forma de usar o Censo Escolar.
- **Riscos:** **falácia ecológica**; os hábitos de estudo e a família ficam de fora. Responde a outra pergunta (eficácia escolar).

### P5. Frequência e apoio familiar no PISA 2025 (Brasil)
- **Pergunta:** faltar à escola (truancy), repetir de ano e o apoio familiar se associam ao desempenho dos alunos brasileiros de 15 anos?
- **Bases:** PISA 2025 Brasil (30.140 alunos).
- **Método:** regressão com 10 valores plausíveis (regras de Rubin) e 80 pesos replicados BRR-Fay.
- **Vantagens:** mede a frequência diretamente e se conecta ao PISA de forma nativa.
- **Riscos:** metodologia mais pesada (PVs, BRR); a amostra é menor; não usa o SAEB, que o grupo já tem.

### Comparação crítica (1 = fraco, 5 = forte) [INTERPRETAÇÃO]

| Critério | P1 | P2 | P3 | P4 | P5 |
|---|---|---|---|---|---|
| Relevância científica | 4 | 4 | 5 | 3 | 4 |
| Dados disponíveis | 5 | 5 | 5 | 4 | 5 |
| Viabilidade técnica (graduação) | 4 | 3 | 3 | 4 | 2 |
| Clareza das variáveis | 4 | 4 | 4 | 4 | 4 |
| Testabilidade das hipóteses | 5 | 3 | 4 | 4 | 4 |
| Uso de métodos de ciência de dados | 5 | 4 | 3 | 3 | 3 |
| Potencial de resultado interessante | 4 | 3 | 5 | 3 | 4 |
| Ligação com o PISA 2025 | 4 (paralela) | 2 | 3 | 2 | 5 |
| Risco de conclusão causal indevida (5 = baixo risco) | 4 | 1 | 3 | 3 | 4 |
| **Total** | **38** | 29 | 35 | 30 | 35 |

**Proposta:** seguir com **P1 como núcleo** e usar **P5 em versão enxuta** como ponte com o PISA. A hipótese de interação com NSE em P1 já incorpora a preocupação de equidade de P3.

---

## 6. Pergunta recomendada

> **Em estudantes do 9º ano do ensino fundamental avaliados pelo SAEB 2023, em que medida a trajetória escolar (reprovação, abandono e distorção idade-série), o tempo de estudo fora da escola e as práticas de envolvimento familiar se associam à proficiência em Matemática, depois de controlar o nível socioeconômico e características demográficas? Essas associações persistem quando se comparam alunos da mesma escola e variam conforme o nível socioeconômico? Como os padrões encontrados se relacionam com os do PISA 2025 para o Brasil?**

**Por que essa pergunta [INTERPRETAÇÃO]:**
1. **Preserva o tema do professor** (trajetória e frequência, estudo, família) e corrige a impossibilidade de medir faltas no SAEB.
2. **Tem uma contribuição não trivial:** a comparação **entre escolas × dentro da escola** mostra quanto das associações é composição social da escola. A literatura (Fernández-Alonso et al., 2017; Albernaz et al., 2002) prevê mudanças de sinal ou de magnitude, e os dados preliminares já sugerem isso.
3. **É viável:** usa uma única base local já baixada, com variáveis prontas.
4. **Usa ciência de dados de forma justificada:** pipeline de dados de 1 GB, modelagem estatística, ML para checar não linearidades e reprodutibilidade.
5. **Liga-se ao PISA 2025 com honestidade:** compara a direção das associações e os gradientes socioeconômicos, sem equiparar escalas.

---

## 7. Hipóteses

Todas são associações condicionais, testadas com MQO ponderado, efeitos fixos de escola (EF) e modelo multinível (ML). Os controles padrão (**C**) são: `INSE_ALUNO`, sexo, cor/raça, deficiência, `IN_PUBLICA`, localização, área, UF, Q17 (idade de entrada) e Q21d (trabalho fora de casa).

| ID | Hipótese | Teste | Base na literatura |
|---|---|---|---|
| **H1** | Ter sido reprovado (Q19) se associa a proficiência MT menor que "nunca reprovado", com gradiente (2 ou mais < 1 < 0), condicional a C | coeficientes das dummies < 0; teste de Wald de igualdade entre as dummies | Laros et al. 2012; Andrade & Laros 2007; Cito & Marôco 2026 |
| **H1b** | A associação de H1 diminui, mas não desaparece, no modelo de EF de escola | comparar β no MQO e no EF (Δβ e IC) | Albernaz et al. 2002 |
| **H2** | O abandono prévio (Q20) se associa negativamente à proficiência **além** da reprovação | β(Q20) < 0 com Q19 no modelo | Leon & Menezes-Filho 2002 |
| **H3** | A distorção idade-série (16 anos ou mais no 9º ano) se associa negativamente; colinear com H1 (ver nota) | β < 0; VIF; modelos separados | Ferrão et al. 2002 |
| **H4** | O tempo de estudo (Q21a) tem associação positiva **com retornos decrescentes** (platô entre 1–2h e mais de 2h) | dummies: β(menos de 1h) < β(1–2h) ≈ β(mais de 2h) | Cooper et al. 2006; Trautwein 2007 |
| **H4b** | A associação do tempo de estudo é menor **dentro** da escola que **entre** escolas | β(EF) < β(MQO); média escolar de Q21a no modelo multinível (efeito contextual) | Fernández-Alonso et al. 2017 |
| **H5** | Práticas de **socialização acadêmica** (Q10a ler, Q10b conversar sobre a escola) se associam positivamente | índice SOC padronizado: β > 0 | Hill & Tyson 2009; Wilder 2014 |
| **H6** | Práticas de **monitoramento/cobrança** (Q10c, Q10d) têm associação nula ou **negativa** depois de C (envolvimento reativo) | índice MON: β ≤ 0 | Hill & Tyson 2009 (dever de casa); [DADO] gradiente invertido |
| **H7** | As associações de H1 e H4 variam com o INSE (penalidade da reprovação maior para alunos de NSE baixo) | interações Q19×INSE e Q21a×INSE; inclinação aleatória | Gershenson et al. 2017 (por analogia); Franco et al. 2007 |
| **H8** | A maior parte da variância entre escolas é explicada pela composição socioeconômica (INSE médio da escola) | redução da variância do intercepto (τ₀₀) do modelo nulo para o modelo com INSE escolar | Albernaz et al. 2002 |
| **H9 (ponte PISA)** | No PISA 2025 Brasil, repetência, truancy e apoio familiar têm **o mesmo sinal** das associações análogas no SAEB | concordância de sinais e comparação de efeitos padronizados (em DP) | Cito & Marôco 2026; Carnoy et al. 2015 |

**Nota sobre H1 e H3.** A reprovação e a distorção são fortemente correlacionadas, porque a distorção decorre em grande parte da reprovação. **[PROPOSTA]** O modelo principal usa a Q19. A distorção entra em um modelo alternativo, ou se cria uma variável de trajetória combinada (regular / reprovado / reprovado e distorcido).

**Resultados que contrariariam as expectativas, e o que significariam:**
- **H4 invertida** (mais estudo associado a nota menor): estudo **compensatório**, em que quem tem dificuldade estuda mais. Seria um caso de causalidade reversa, não evidência de que estudar prejudica.
- **H5 nula:** o item Q10b pode ter pouca variância ou viés de desejabilidade.
- **H1 desaparecendo no EF:** a "penalidade" da reprovação seria sobretudo composição das escolas, ou seja, escolas que reprovam muito concentram alunos vulneráveis.
- **H9 com sinais divergentes:** diferenças de população (idade × série), de construto ou de época (2023 × 2025). Seria um achado em si, não um fracasso.

---

## 8. Quadro de variáveis

| Papel | Variável | Origem | Tipo | Tratamento [PROPOSTA] |
|---|---|---|---|---|
| **Dependente** | `PROFICIENCIA_MT_SAEB` | TS_ALUNO_9EF | contínua | escala SAEB; também em DP (÷50) para comparar com o PISA |
| Dependente (robustez) | `PROFICIENCIA_LP_SAEB` | idem | contínua | idem |
| Dependente (alternativa) | Nível adequado em MT (≥ 275, ponto de corte usado pelo movimento Todos pela Educação; **conferir a fonte antes de usar**) | derivada | binária | regressão logística como robustez |
| Independente: trajetória | `REPROV` (Q19: 0 / 1 / 2 ou mais) | Q19 | categórica ordinal | dummies; referência "nunca" |
| Independente: trajetória | `ABAND` (Q20) | Q20 | categórica | dummy "abandonou alguma vez" |
| Independente: trajetória | `DISTORCAO` (Q02 ≥ 16 anos) | Q02 | binária | derivada; modelo alternativo |
| Independente: estudo | `ESTUDO` (Q21a: 0 / menos de 1h / 1–2h / mais de 2h) | Q21a | categórica ordinal | dummies (permite não linearidade) |
| Independente: família | `FAM_SOC` = média padronizada de Q10a e Q10b | Q10a, Q10b | contínua (índice) | validar com AFE/AFC e α ou ω |
| Independente: família | `FAM_MON` = Q10c e Q10d | Q10c, Q10d | contínua (índice) | idem |
| Independente: família | `FAM_ESCOLA` = Q10f (reuniões) | Q10f | ordinal | item isolado |
| Controle: NSE | `INSE_ALUNO` | SAEB | contínua | padronizar; **não** incluir Q08 e Q09 junto (o INSE já os contém) |
| Controle | sexo (Q01), cor/raça (Q04), deficiência/TEA (Q05a–b) | SAEB | categóricas | dummies; "não quero declarar" como categoria |
| Controle | idade de entrada (Q17) | SAEB | ordinal | dummies |
| Controle | trabalho fora (Q21d), trabalho doméstico (Q21c) | SAEB | ordinal | dummies; cautela de medição |
| Controle: escola | `IN_PUBLICA`, `ID_LOCALIZACAO`, `ID_AREA`, `ID_UF` | SAEB | categóricas | efeitos fixos de UF |
| Nível 2 (escola) | `INSE_ESC` = média do INSE_ALUNO na escola | derivada | contínua | efeito contextual (composição) |
| Nível 2 | `REPROV_ESC` = % de reprovados na escola | derivada | contínua | efeito contextual |
| Nível 2 | `PC_FORMACAO_DOCENTE_FINAL` | TS_ESCOLA | contínua | opcional |
| Desenho | `PESO_ALUNO_MT`, `ESTRATO`, `ID_ESCOLA` | SAEB | — | pesos; erros-padrão por cluster de escola |
| Filtros | `IN_SITUACAO_CENSO = 1`, `IN_PROFICIENCIA_MT = 1`, peso não nulo | SAEB | — | igual ao cálculo oficial do INEP |
| Mediador / heterogeneidade (opcional) | engajamento (Q23a–b), expectativa docente (Q23h) | SAEB | ordinal | **não** controlar no modelo principal (são possíveis mediadores) |

---

## 9. Metodologia recomendada

### 9.1 Desenho
**Estudo quantitativo, observacional, transversal, explicativo-correlacional, com análise de dados secundários** de uma avaliação em larga escala. É também **comparativo**, por causa da análise paralela com o PISA 2025.
- Não é experimental nem longitudinal; logo, **não identifica efeitos causais**.
- "Explicativo" se refere a modelar associações condicionais teoricamente motivadas (no sentido de Shmueli, 2010), não a afirmar causalidade.
- Há um componente descritivo, a caracterização da população.

### 9.2 Unidade de análise
**Aluno (nível 1) aninhado em escola (nível 2).** A UF entra como efeito fixo. A escola mascarada serve como identificador de cluster, o que é legítimo dentro do SAEB.

### 9.3 Tratamento dos dados [PROPOSTA]
1. **Leitura eficiente:** ler só as colunas necessárias (`usecols`), com tipos definidos, e converter para **Parquet** (pandas + pyarrow) ou consultar com **DuckDB**. O CSV de 1,1 GB cabe em memória se for filtrado por colunas.
2. **Filtros (fluxo documentado com contagens):**
   - `IN_SITUACAO_CENSO = 1`;
   - `IN_PROFICIENCIA_MT = 1`;
   - `PESO_ALUNO_MT` não nulo.
   - Isso dá cerca de 2,08 milhões de alunos no 9º ano **[DADO]**.
3. **Valores inválidos:** os códigos `*` (nulo, marcação inválida) e `.` (branco) viram NaN.
4. **"Não sei"** na escolaridade dos pais: é uma **categoria informativa** (média de 244 pontos) **[DADO]**. Só importa se Q08 for usada no modelo alternativo.
5. **Ausentes:**
   - descrever o percentual por variável e testar se a ausência se associa ao INSE e à proficiência (já há evidência de que a ausência **não é aleatória**);
   - estratégia principal: casos completos nas variáveis do modelo, com contagem e comparação entre incluídos e excluídos;
   - **robustez:** categoria "ausente" como dummy, ou imputação múltipla por equações encadeadas (MICE, com `IterativeImputer` ou `statsmodels.imputation.mice`) em uma subamostra.
6. **Duplicidades:** verificar a unicidade de `ID_ALUNO` (não testado).
7. **Inconsistências:** idade incompatível com a série (13 anos ou menos no 9º ano) é rara (0,8%) **[DADO]**; manter e sinalizar.
8. **Outliers:** a proficiência TRI é limitada pela escala; não remover. Checar só valores impossíveis.
9. **Categóricas:** one-hot com categoria de referência teoricamente escolhida (por exemplo, "nunca reprovado" e "não estuda").
10. **Padronização:** INSE e índices em escore z, para comparar coeficientes. A proficiência fica na escala SAEB e também em DP, para a ponte com o PISA.
11. **Pesos:** usar `PESO_ALUNO_MT` em todas as estimativas descritivas e nos modelos. Em modelos multinível, pesos amostrais exigem cuidado (pesos por nível); por isso a **estimativa principal usa MQO ponderado e EF com erros por cluster**, e o modelo multinível serve para decompor variâncias. Sensibilidade com e sem pesos.
12. **Índices de família:** fazer uma análise fatorial exploratória (AFE) em metade da amostra e uma confirmatória (AFC) na outra metade, ou ao menos AFE com correlação policórica, e relatar α ou ω. Se SOC e MON não se separarem empiricamente, usar os itens isolados.

### 9.4 Análise exploratória
- Fluxograma da amostra.
- Tabela 1: descritivas ponderadas (proporções, médias e IC) por categoria.
- Distribuição da proficiência (histograma ou densidade) por rede e por INSE.
- Médias ponderadas de MT por categoria de cada exposição, com IC95% (gráfico de pontos).
- Matriz de associações (Spearman, V de Cramér ou policórica) entre exposições e controles, para checar colinearidade.
- Mapa de ausências.
- Modelo nulo e ICC.
- Mapa por UF (choropleth) da proficiência média e da taxa de reprovação declarada (a UF é real).

### 9.5 Modelos estatísticos (sequência)

| Modelo | Especificação | Pergunta que responde |
|---|---|---|
| M0 | Multinível nulo: proficiência ~ 1 + (1 \| escola) | Quanto da variância está entre escolas (ICC)? |
| M1 | MQO ponderado: proficiência ~ exposições + UF | Associação bruta (só exposições) |
| M2 | M1 + INSE + demografia + controles | Associação condicional ao NSE (H1–H6) |
| M3 | **M2 com efeitos fixos de escola** (absorvidos) | As associações persistem **dentro** da escola? (H1b, H4b) |
| M4 | Multinível: M2 + (1 \| escola) + INSE_ESC + REPROV_ESC | Efeitos de composição; quanto de τ₀₀ o INSE escolar explica (H8) |
| M5 | M4 + interações exposição×INSE, inclinação aleatória do INSE | Heterogeneidade (H7) |
| M6 | M2 e M3 com LP como desfecho; somente públicas; logística para "nível adequado"; casos completos × imputação | Robustez |

**Justificativas:**
- **MQO ponderado com erros por cluster de escola:** estima associações médias populacionais respeitando os pesos e a dependência intraescolar. É o modelo mais transparente.
- **Efeitos fixos de escola:** eliminam todo confundidor constante na escola (qualidade, rede, composição, região). Não eliminam confundidores individuais.
- **Multinível:** o ICC de 0,18 a 0,23 **[DADO]** mostra que ignorar a estrutura subestima os erros-padrão. Ele também permite separar efeitos individuais de efeitos de composição e modelar heterogeneidade, o que é tradição forte na literatura do SAEB (Andrade & Soares, 2008; Laros et al., 2012).
- **Significância:** com cerca de 2 milhões de observações, os p-valores são quase sempre menores que 0,001 e **pouco informativos**. Reportar **tamanho do efeito (pontos SAEB e DP) com IC95%** e mudança no R² e nos componentes de variância.
- **Viabilidade:** o multinível com 2 milhões de linhas e 38 mil escolas é pesado no `statsmodels`. Proposta: rodar M4–M5 em uma **amostra aleatória de escolas estratificada por UF e rede** (por exemplo, 3.000 escolas, cerca de 150 mil alunos). M1–M3 rodam na base completa com `pyfixest`. Alternativa: `lme4` em R.

### 9.6 Machine learning: necessário? [INTERPRETAÇÃO e PROPOSTA]
- **Inferência ou explicação** pergunta "qual a associação de X com Y, mantidos os demais fatores, e com que incerteza?". Exige especificação teórica, coeficientes interpretáveis e erros-padrão. **Predição** pergunta "quão bem consigo prever Y para novos casos?". Otimiza o erro fora da amostra, mesmo com modelos opacos (Breiman, 2001; Shmueli, 2010).
- A nossa pergunta é **explicativa**. Logo, ML **não é necessário** para respondê-la. Ele é útil para dois papéis auxiliares:
  1. **Diagnóstico de especificação:** um gradient boosting (LightGBM) com SHAP e gráficos de dependência parcial ou ALE revela não linearidades (por exemplo, o platô da Q21a) e interações (por exemplo, reprovação × INSE) que o modelo linear pode ter omitido. Se o GBM tiver R² fora da amostra muito superior ao do MQO, há estrutura não modelada.
  2. **Benchmark de poder preditivo:** quanto da variância individual essas variáveis conseguem prever? Isso dá uma resposta direta a "ajudam a explicar as notas?".
- **Cuidados:**
  - validação cruzada **agrupada por escola** (`GroupKFold`), para evitar vazamento entre alunos da mesma escola;
  - SHAP **não é efeito causal**;
  - descartar Random Forest e XGBoost **ao mesmo tempo** (redundância). Um único GBM bem ajustado mais a árvore de decisão rasa como baseline interpretável basta.
- **Não usar ML para "prever quem vai mal"** com fins de classificação de alunos. Isso cria risco ético de rotulação.

---

## 10. Métodos e algoritmos a implementar (Python)

| # | Algoritmo | Objetivo | Entradas | Pré-processamento | Saída | Métricas | Hipóteses | Bibliotecas |
|---|---|---|---|---|---|---|---|---|
| A1 | Pipeline de ingestão | Ler, filtrar e salvar a base analítica | TS_ALUNO_9EF, TS_ESCOLA | `usecols`, latin-1, `;`, filtros, recodificação `*`/`.` → NaN | `saeb9_analitico.parquet` e log com contagens | nº de registros por etapa | todas | pandas, pyarrow ou duckdb |
| A2 | Engenharia de variáveis | Criar dummies, distorção, médias escolares | base A1 | codificação de referência | variáveis derivadas | — | H1–H8 | pandas |
| A3 | Validação de índices | Verificar se Q10 forma SOC e MON | Q10a–f | ordinal → policórica | cargas, α ou ω, ajuste da AFC (CFI, RMSEA) | α ≥ 0,6–0,7; CFI ≥ 0,90 | H5, H6 | factor_analyzer, semopy |
| A4 | Descritivas ponderadas | Tabela 1 e gradientes | base A2 | pesos | médias e proporções com IC95% | — | contexto | statsmodels (DescrStatsW) |
| A5 | Modelo nulo e ICC | Decompor a variância | proficiência, escola | amostra de escolas | ICC, τ₀₀, σ² | ICC (IC por bootstrap) | H8 | statsmodels MixedLM |
| A6 | MQO ponderado (M1, M2) | Associações condicionais | todas | z-scores, dummies | β, IC95%, R² | erro por cluster de escola | H1–H6 | statsmodels WLS ou pyfixest |
| A7 | Efeitos fixos de escola (M3) | Associação dentro da escola | idem | absorver `ID_ESCOLA` | β_within e Δβ em relação ao M2 | erro por cluster | H1b, H4b | **pyfixest** (`feols`) |
| A8 | Multinível (M4, M5) | Composição e heterogeneidade | idem + médias escolares | centrar na média do grupo (CWC) | efeitos fixos e aleatórios, Δτ₀₀ | AIC/BIC, R² de Nakagawa | H7, H8 | statsmodels MixedLM (ou lme4 via R) |
| A9 | Robustez (M6) | Testar se os achados resistem | variações | idem | tabela de coeficientes comparados | estabilidade de sinal e magnitude | todas | idem |
| A10 | GBM + SHAP | Não linearidade, interação, poder preditivo | mesmas features do M2 (sem ID de escola) | sem one-hot (categorias nativas do LightGBM) | R² e RMSE fora da amostra; SHAP; dependência parcial | RMSE, R², MAE (GroupKFold, 5 folds) vs. MQO | H4, H7 (diagnóstico) | lightgbm, shap, scikit-learn |
| A11 | Replicação no PISA 2025 Brasil | Ponte com o PISA (H9) | PUF do aluno do Brasil | 10 PVs; peso final + 80 réplicas BRR-Fay (k = 0,5); **conferir os nomes das variáveis no codebook de 2025** | β por PV combinados pelas regras de Rubin; erro BRR | β em DP com IC95% | H9 | pyreadstat, numpy (implementação manual) ou R `intsvy`/`EdSurvey` |
| A12 | Comparação SAEB × PISA | Tabela e gráfico de efeitos padronizados | saídas A6/A7 e A11 | converter para DP | forest plot lado a lado | concordância de sinais | H9 | matplotlib |

**Reprodutibilidade [PROPOSTA]:**
- repositório com `requirements.txt`, sementes fixas e scripts numerados (`01_ingestao.py` … `12_comparacao_pisa.py`);
- os dados brutos não são versionados (são grandes e públicos); o caminho fica em um arquivo de configuração;
- Jupyter só para visualização.

**Escopo mínimo viável para a disciplina:** A1–A7 + A10 + uma versão simplificada do A12 que usa os números publicados pela OCDE em vez do A11. O A8 completo e o A11 são "nível ouro".

---

## 11. Artefatos para o artigo

| Artefato | Pergunta que responde |
|---|---|
| Fig. 1: fluxograma da amostra | Quem entrou na análise e quem foi perdido (viés de seleção)? |
| Tab. 1: descritivas ponderadas | Como é a população de alunos do 9º ano (trajetória, estudo, família, NSE)? |
| Tab. 2: percentual de ausentes por variável × INSE | A ausência é aleatória? |
| Fig. 2: distribuição da proficiência MT por rede e quartil de INSE | Quão desigual é o desempenho? |
| Fig. 3: médias ponderadas com IC por categoria de Q19, Q20, Q21a e Q10 | Qual o gradiente bruto de cada fator? |
| Fig. 4: mapa por UF (proficiência e % de reprovados declarados) | Há padrão territorial? |
| Tab. 3: cargas da AFE/AFC dos itens Q10 e confiabilidade | Os índices de família medem construtos distintos? |
| Tab. 4: modelos M1 → M2 → M3 lado a lado (β, IC95%, R², N) | Como as associações mudam com controles e dentro da escola? (**tabela central**) |
| Fig. 5: coefficient plot MQO × EF | Visualização de H1b e H4b |
| Tab. 5: modelo multinível (fixos, τ₀₀, σ², ICC, % de variância explicada) | Composição escolar e H8 |
| Fig. 6: efeitos marginais das interações exposição × INSE | Heterogeneidade (H7) |
| Tab. 6: robustez (LP, só públicas, logística, imputação) | Os achados são robustos? |
| Tab. 7: desempenho preditivo MQO × árvore × GBM (GroupKFold) | Quanto as variáveis predizem? Há não linearidade? |
| Fig. 7: SHAP beeswarm e dependência parcial (Q21a, INSE) | Formato das relações; confirmar o platô do estudo |
| Tab. 8: quadro comparativo SAEB 2023 × PISA 2025 (desenho) | Por que as avaliações não são equivalentes? |
| Fig. 8: forest plot de efeitos padronizados SAEB × PISA 2025 (Brasil) | As associações têm a mesma direção? (H9) |
| Tab. 9: gradiente socioeconômico, R² do INSE no SAEB × % de variância explicada pelo ESCS no PISA (16% em ciências) | Equidade comparada |

---

## 12. PISA 2025 (a exigência "PISA 2026")

### 12.1 Situação verificada [FONTE]
- **Não existe "PISA 2026".** A edição mais recente é o **PISA 2025**. Os resultados do Volume I foram divulgados em **8 de setembro de 2026**. Os volumes seguintes saem em 2027; as análises de aprendizagem autodirigida também ficam para 2027.
- **91 países e economias** e mais de 760 mil alunos. O foco é ciências; matemática e leitura são domínios secundários; há um domínio novo, a resolução computacional de problemas.
- **Microdados:** os Public Use Files (SAS e SPSS) estão disponíveis para todos os países, com codebook, questionários e um rascunho do relatório técnico. O relatório técnico final sai em 2027.
- **O próximo ciclo é o PISA 2029**, com foco em leitura e no domínio inovador Media & AI Literacy. A partir dele, o ciclo passa a ser de 4 anos.

### 12.2 Brasil no PISA 2025 [FONTE: country note da OCDE, salvo indicação]
- **Amostra:** 30.140 alunos em 1.053 escolas, representando cerca de 2.185.000 jovens de 15 anos, aproximadamente **76%** da população dessa idade. Todos os dados atenderam aos padrões de qualidade.
- **Médias:** **Leitura 408, Matemática 377, Ciências 409** **[FONTE: Agência Gov/EBC e imprensa; confirmar nas tabelas I.B1.2a da OCDE]**. São estáveis em relação a 2022 e a 2015, segundo a OCDE.
- **Proficiência mínima (Nível 2 ou mais):** 28% em matemática (OCDE 65%), 49% em leitura e 48% em ciências.
- **NSE:**
  - o ESCS explica **16%** da variância em ciências (OCDE 12%);
  - a diferença entre o quartil mais rico e o mais pobre é de **96 pontos** (OCDE 85);
  - essa diferença **aumentou** entre 2015 e 2025;
  - 10% dos alunos desfavorecidos são "resilientes".
- **Frequência:** **55%** faltaram ao menos um dia nas duas semanas anteriores ao teste (OCDE 22%); 53% cabularam ao menos uma aula; 44% chegaram atrasados. Em 2022 os valores foram 22%, 19% e 51%; em 2018, 50%, 51% e 44%.
- **Família:** 51% relatam que os pais perguntam semanalmente o que fizeram na escola (62% em 2022); 41% discutem semanalmente problemas da escola (55% em 2022).
- **Atitudes:** 52% têm mentalidade de crescimento; mais curiosidade e valorização da escola se associam a notas maiores depois de controlar o NSE.

**[INTERPRETAÇÃO] Atenção ao vaivém da truancy (50% → 22% → 55%).** A própria OCDE adverte que indicadores de questionário podem refletir comportamento de resposta. Antes de interpretar como mudança real, investigar se houve mudança na aplicação, na tradução ou no calendário.

### 12.3 Comparabilidade SAEB 2023 × PISA 2025

| Dimensão | SAEB 2023 (9º ano EF) | PISA 2025 | Consequência |
|---|---|---|---|
| População | **Por série:** alunos do 9º ano | **Por idade:** 15 anos e 3 meses a 16 anos e 2 meses, com pelo menos 6 anos de escolaridade, em qualquer série a partir do 7º ano | Populações diferentes. No PISA, alunos atrasados estão em séries anteriores (a defasagem entra de outro jeito) |
| Cobertura | Censo das públicas e amostra das privadas; 83,6% de presença **[DADO]** | Amostra probabilística; cobre cerca de 76% dos jovens de 15 anos | Fora da escola não entra em nenhuma das duas; no PISA, a exclusão por idade fora da escola é explícita |
| Período | Out./nov. 2023 | 2025 | Dois anos e contextos pós-pandemia diferentes |
| Construto | Matriz de referência curricular (habilidades esperadas na série) | Letramento: aplicação em situações da vida real | Construtos relacionados, mas distintos |
| Escala | 0–500, média 250 e DP 50 (SAEB/97) | Média OCDE 500, DP 100 (escalas de referência) | **Não converter uma na outra.** Comparar só em DP intra-avaliação |
| Medida individual | Estimativa pontual + erro-padrão | 10 valores plausíveis | Métodos de inferência diferentes |
| Pesos e erros | `PESO_ALUNO_*`; cluster por escola | Peso final + 80 réplicas BRR-Fay | Implementações distintas |
| NSE | INSE (bens, serviços, escolaridade dos pais; TRI) | ESCS (ocupação, escolaridade dos pais, posses) | Índices análogos, não idênticos |
| Frequência | **Não medida** | Truancy (faltar dia ou aula, atraso) nas últimas 2 semanas | O PISA complementa o SAEB |
| Trajetória | Reprovação e abandono autodeclarados | Repetência autodeclarada | Comparáveis em direção |
| Família | Q10 (incentivo, conversa, reuniões) | Itens de apoio parental (perguntar sobre a escola, discutir problemas) | Parcialmente análogos |
| Modo de aplicação | Papel | Computador | Efeito de modo possível |

### 12.4 Como relacionar no artigo [PROPOSTA]
1. **Contextualização (mínimo):** na Introdução e na Discussão, situar os achados do SAEB nos indicadores oficiais do PISA 2025 do Brasil (gradiente socioeconômico, frequência, apoio familiar).
2. **Comparação de gradientes (intermediário):** calcular no SAEB o R² do INSE sozinho (o "percentual da variância explicada pelo NSE") e colocá-lo ao lado dos 16% do ESCS no PISA, ressalvando as diferenças de desfecho (MT × ciências) e de população.
3. **Replicação paralela (avançado, A11):** estimar no PISA 2025 Brasil um modelo análogo (desfecho MATH em PVs; REPEAT, truancy, apoio familiar, ESCS, sexo, rede) e comparar **sinais e efeitos em DP**. Esse é o teste de H9.
4. **Linguagem:** "convergência" ou "divergência" de padrões, **nunca** "o SAEB prevê o PISA" nem "a nota SAEB equivale a X pontos no PISA".

---

## 13. Vieses, limitações e responsabilidade

| Risco | Onde aparece | Mitigação [PROPOSTA] |
|---|---|---|
| **Seleção** | 16% de ausentes no dia da prova (9º ano), em geral mais vulneráveis; quem abandonou a escola não está na base; o PISA cobre 76% da coorte | Relatar; comparar a taxa de participação das escolas (TS_ESCOLA); dizer que os resultados valem para "alunos presentes" |
| **Dados ausentes não aleatórios** | quem deixa itens em branco tem proficiência menor **[DADO]** | Comparar incluídos × excluídos; imputação múltipla como robustez |
| **Medição e autorrelato** | 10–11 anos (5º) e 14–15 anos (9º) respondendo sobre os pais; "não sei" alto; possível desejabilidade social em Q10; Q21d suspeito | Escolher o 9º ano; validar índices; tratar Q21d com cautela |
| **Erro de medida na proficiência** | estimativa pontual, não PVs | Usar o erro-padrão em análise de sensibilidade; declarar a limitação |
| **Variáveis omitidas e confundimento** | habilidade prévia, saúde, motivação, qualidade do professor | EF de escola remove o confundimento entre escolas; o individual permanece |
| **Causalidade reversa** | estudo e cobrança dos pais respondem ao desempenho (gradiente invertido de Q10d) | Discutir explicitamente; linguagem associativa |
| **Colinearidade** | reprovação × distorção; INSE × escolaridade dos pais | Modelos separados; VIF |
| **Inflação de significância** | N de cerca de 2 milhões | Ênfase em tamanho de efeito e IC |
| **Falácia ecológica** | dados por UF; desenho P4 | Não inferir comportamento individual a partir de agregados |
| **Generalização** | 9º ano 2023 ≠ outras séries ou anos; pós-pandemia | Delimitar no título e no resumo |
| **Comparação SAEB × PISA** | ver 12.3 | Só direções e DP |
| **Ética e estigmatização** | "família que não incentiva", "aluno reprovado", rankings | Não ranquear escolas nem UFs como "culpadas"; enquadrar a reprovação como **política educacional** e o envolvimento como **condicionado por tempo e recursos** (trabalho, escolaridade). Não usar ML para rotular alunos |
| **Privacidade (LGPD)** | máscaras | Não tentar reidentificar; não publicar células com menos de 10 alunos |

**Advogado do diabo [INTERPRETAÇÃO].** A crítica mais forte ao desenho é esta: "trajetória" e "hábitos" podem ser apenas **sintomas** do desempenho anterior, e não fatores que o explicam. Nesse caso, os coeficientes mediriam o quanto o desempenho passado persiste. Sem dados longitudinais, essa hipótese não pode ser descartada.

Respostas possíveis:
1. Admitir isso e enquadrar os resultados como **marcadores de risco associados**, úteis para políticas de **acompanhamento**, e não como alavancas causais.
2. Mostrar que as associações sobrevivem dentro da escola.
3. Apoiar-se na literatura causal (Manacorda, 2012; Gottfried, 2010), que indica que parte da associação tende a ser real.

A conclusão recomendada **se mantém** porque a pergunta é descritivo-explicativa, não causal.

---

## 14. Plano do artigo

1. **Título (sugestão):** "Trajetória escolar, tempo de estudo e envolvimento familiar na proficiência em Matemática no 9º ano: evidências do SAEB 2023 e diálogo com o PISA 2025"
2. **Resumo:** problema, dados, método (MQO, EF, multinível, GBM), principais magnitudes, ressalva causal.
3. **Introdução:** desigualdade educacional no Brasil; PISA 2025 como contexto; lacuna (estudo e família com SAEB recente; dentro × entre escolas); pergunta e hipóteses.
4. **Referencial teórico:** origem social e efeito-escola; trajetória e reprovação; dever de casa; envolvimento parental; frequência (literatura internacional, com a lacuna brasileira).
5. **Metodologia** (a seção mais desenvolvida):
   - 5.1 Desenho do estudo (quantitativo, observacional, transversal, explicativo-correlacional, dados secundários).
   - 5.2 Fonte de dados (SAEB 2023: desenho censitário e amostral, máscaras e LGPD; PISA 2025).
   - 5.3 População, amostra analítica e fluxograma.
   - 5.4 Variáveis e operacionalização (quadro da seção 8; construção e validação dos índices).
   - 5.5 Tratamento dos dados (ausentes, códigos, pesos).
   - 5.6 Estratégia analítica (M0–M6; justificativa do multinível e do EF; tamanho de efeito).
   - 5.7 Análise complementar de ML (objetivo diagnóstico; GroupKFold; SHAP).
   - 5.8 Análise comparativa com o PISA 2025 (quadro de comparabilidade; PVs e BRR, se o A11 for feito).
   - 5.9 Reprodutibilidade (software, versões, repositório).
   - 5.10 Considerações éticas.
6. **Resultados:** descritivos → modelos → robustez → ML → comparação com o PISA.
7. **Discussão:** convergências com a literatura; o gradiente invertido de Q10d; dentro × entre escolas; implicações para políticas (acompanhamento da trajetória, não culpabilização).
8. **Limitações.**
9. **Conclusão.**
10. **Referências.**

---

## Oportunidades adjacentes (além do pedido)

- **Dados de professor e diretor do SAEB (mesma máscara):** dá para incluir no nível 2 clima escolar, práticas de dever de casa relatadas pelo professor e políticas de reforço. Relevância alta: responde "o que a escola faz" sem sair do SAEB. Busca: dicionário TS_PROFESSOR, itens sobre "tarefa de casa".
- **Itens Q22 e Q23 (práticas docentes, expectativa dos professores):** a variável "meus professores acreditam que sou capaz" (Q23h) permite um artigo sobre expectativas docentes (efeito Pigmalião) com 2 milhões de alunos. Relevância média.
- **Domínio de Ciências no 9º ano (CN e CH amostrais):** o PISA 2025 tem foco em **ciências**. Usar `PROFICIENCIA_CN_SAEB` (subamostra com `PESO_ALUNO_CN`) aproxima os construtos. Relevância alta para a ponte com o PISA. Busca: `ESTRATO_CIENCIAS`, `PESO_ALUNO_CN`.
- **Desenho P4 (nível escola com códigos reais):** é um segundo artigo possível, sobre eficácia escolar, juntando IDEB, INSE, Censo Escolar e indicadores. Relevância média.
- **Uso de IA no PISA 2025:** 48% dos alunos brasileiros usam chatbots semanalmente, e há associação negativa com uso para tarefas específicas. É um "hábito de estudo" do século XXI. Relevância alta como gancho na Discussão.

## Horizonte

- **Microdados do SAEB 2025:** a planilha de resultados de 2025 já foi publicada, mas os **microdados ainda não** (até a verificação de 07/10/2026). Quando saírem, permitem comparar 2023 × 2025 por estrato.
- **Sedap/INEP:** dá acesso aos códigos reais e permite cruzar com o Censo Escolar e seguir trajetórias no tempo. É o caminho para identificação causal em trabalhos futuros (TCC ou iniciação científica).
- **PISA 2025 Volumes II–III e relatório técnico final (2027):** trarão análises de engajamento e aprendizagem autodirigida.
- **PISA 2029 (Media & AI Literacy):** a próxima janela de comparação.
- **ERCE (UNESCO/LLECE):** tem questionário de família com dever de casa para a América Latina; serve para comparação regional.

---

## 15. Referências

Os metadados foram conferidos no Crossref, SciELO, nas páginas das editoras ou em documentos oficiais. A marca *[resumo]* indica que só o resumo foi lido: **leiam o texto completo antes de citar achados específicos**.

### Documentos oficiais e bases de dados
- BRASIL. INEP. *Microdados do Saeb 2023: Leia-me*. 1. ed. Brasília: Inep, out. 2024. (Arquivo local: `MICRODADOS_SAEB_2023/LEIA-ME E DOCUMENTOS TÉCNICOS/Leia-Me_Microdados_Saeb_2023.pdf`.) Páginas: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/saeb
- BRASIL. INEP. *Saeb 2023: detalhamento da população e resultados: nota técnica*. Brasília: Inep, 2024. (Arquivo local.)
- BRASIL. INEP. *Relatório de Amostragem do Saeb 2023*. (Arquivo local.)
- BRASIL. INEP. *Indicador de Nível Socioeconômico (Inse) 2023: nota técnica*. https://download.inep.gov.br/publicacoes/institucionais/estatisticas_e_indicadores/indicador_nivel_socioeconomico_saeb_2023_nota_tecnica.pdf ; página: https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais/nivel-socioeconomico
- BRASIL. INEP. *Indicadores Educacionais*. https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/indicadores-educacionais
- BRASIL. INEP. *Ideb: resultados*. https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados
- BRASIL. INEP. *Microdados do Censo Escolar*. https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar
- BRASIL. INEP. *Serviço de Acesso a Dados Protegidos (Sedap)*. https://www.gov.br/inep/pt-br/areas-de-atuacao/gestao-do-conhecimento-e-estudos-educacionais/cibec/servico-de-acesso-a-dados-protegidos-sedap
- BRASIL. INEP. *Saeb: resultados*. https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/saeb/resultados
- OECD. *PISA 2025 Results (Volume I): Future-Ready Students*. Paris: OECD Publishing, 8 set. 2026. https://www.oecd.org/en/publications/2026/09/pisa-2025-results-volume-i_5265bfb1.html
- OECD. *PISA 2025 Results (Volume I): Brazil* (country note; autor: F. Avvisati). 2026. https://www.oecd.org/en/publications/pisa-2025-results-volume-i-country-notes_2d4ff9ea-en/brazil_d65ba095-en.html
- OECD. *PISA 2025 Database*. https://www.oecd.org/en/data/datasets/pisa-2025-database.html
- OECD. *PISA 2025 Assessment and Analytical Framework*. 29 maio 2026. https://www.oecd.org/en/publications/2026/05/pisa-2025-assessment-and-analytical-framework_3abce6d6.html
- OECD. *OECD to launch PISA 2025 on 8 September 2026* (media advisory). https://www.oecd.org/en/about/news/media-advisories/2026/09/oecd-to-launch-pisa-2025-on-8-september-2026.html
- OECD. *PISA 2022 Results (Volume I): The State of Learning and Equity in Education*. Paris: OECD, 2023. DOI: 10.1787/53f23881-en
- OECD. *PISA 2022 Database*. https://www.oecd.org/en/data/datasets/pisa-2022-database.html
- ACER. *ACER to deliver PISA 2029 with novel focus on AI and media literacy*. https://www.acer.org/news/article/acer-to-deliver-pisa-2029-with-novel-focus-on-ai-and-media-literacy
- AGÊNCIA GOV (EBC). *Pisa: Brasil está entre os países que mais avançaram em educação nos últimos 20 anos*. set. 2026. https://agenciagov.ebc.com.br/noticias/202609/pisa-brasil-esta-entre-os-paises-que-mais-avancaram-em-educacao-nos-ultimos-20-anos (fonte das médias 408/377/409; conferir nas tabelas da OCDE)

### Clássicos e teoria
- COLEMAN, J. S. et al. *Equality of Educational Opportunity*. Washington, DC: U.S. Office of Education, 1966. ERIC ED012275. https://files.eric.ed.gov/fulltext/ED012275.pdf
- BOURDIEU, P. Os três estados do capital cultural. In: NOGUEIRA, M. A.; CATANI, A. (orgs.). *Escritos de educação*. Petrópolis: Vozes, 1998.
- SIRIN, S. R. Socioeconomic status and academic achievement: a meta-analytic review of research. *Review of Educational Research*, v. 75, n. 3, p. 417-453, 2005. DOI: 10.3102/00346543075003417 *[resumo]*
- HANUSHEK, E. A. Conceptual and empirical issues in the estimation of educational production functions. *Journal of Human Resources*, v. 14, n. 3, p. 351-388, 1979. DOI: 10.2307/145575 *[resumo]*
- HANUSHEK, E. A. The failure of input-based schooling policies. *The Economic Journal*, v. 113, n. 485, p. F64-F98, 2003. DOI: 10.1111/1468-0297.00099 *[resumo]*

### Brasil: fatores associados, NSE e eficácia escolar
- SOARES, J. F.; ALVES, M. T. G. Desigualdades raciais no sistema brasileiro de educação básica. *Educação e Pesquisa*, v. 29, n. 1, p. 147-165, 2003. DOI: 10.1590/S1517-97022003000100011 *[resumo]*
- ALVES, M. T. G.; SOARES, J. F.; XAVIER, F. P. Índice socioeconômico das escolas de educação básica brasileiras. *Ensaio*, v. 22, n. 84, p. 671-703, 2014. DOI: 10.1590/S0104-40362014000300005 *[resumo]*
- ALVES, M. T. G.; SOARES, J. F. Contexto escolar e indicadores educacionais. *Educação e Pesquisa*, v. 39, n. 1, p. 177-194, 2013. DOI: 10.1590/S1517-97022013000100012 *[resumo]*
- ANDRADE, R. J.; SOARES, J. F. O efeito da escola básica brasileira. *Estudos em Avaliação Educacional*, v. 19, n. 41, p. 379-406, 2008. DOI: 10.18222/eae194120082067 *[resumo]*
- ALBERNAZ, Â.; FERREIRA, F. H. G.; FRANCO, C. Qualidade e eqüidade no ensino fundamental brasileiro. *Pesquisa e Planejamento Econômico*, v. 32, n. 3, p. 453-476, 2002. https://ppe.ipea.gov.br/index.php/ppe/article/view/139/74
- FRANCO, C. et al. Qualidade e eqüidade em educação: reconsiderando o significado de "fatores intra-escolares". *Ensaio*, v. 15, n. 55, p. 277-298, 2007. DOI: 10.1590/S0104-40362007000200007 *[resumo]*
- ALVES, M. T. G.; NOGUEIRA, M. A.; NOGUEIRA, C. M. M.; RESENDE, T. F. Fatores familiares e desempenho escolar: uma abordagem multidimensional. *Dados*, v. 56, n. 3, p. 571-603, 2013. DOI: 10.1590/S0011-52582013000300004
- LAROS, J. A.; MARCIANO, J. L.; ANDRADE, J. M. Fatores associados ao desempenho escolar em Português: um estudo multinível por regiões. *Ensaio*, v. 20, n. 77, p. 623-646, 2012. DOI: 10.1590/S0104-40362012000400002
- ANDRADE, J. M.; LAROS, J. A. Fatores associados ao desempenho escolar: estudo multinível com dados do SAEB/2001. *Psicologia: Teoria e Pesquisa*, v. 23, n. 1, p. 33-41, 2007. DOI: 10.1590/S0102-37722007000100005 *[resumo]*
- SOARES, J. F.; DELGADO, V. M. S. Medida das desigualdades de aprendizado entre estudantes de ensino fundamental. *Estudos em Avaliação Educacional*, v. 27, n. 66, p. 754-780, 2016. DOI: 10.18222/eae.v27i66.4101 *[resumo]*
- KLEIN, R. Como está a educação no Brasil? O que fazer? *Ensaio*, v. 14, n. 51, p. 139-171, 2006. DOI: 10.1590/S0104-40362006000200002 *[resumo]*

### Trajetória e reprovação
- LEON, F. L. L.; MENEZES-FILHO, N. A. Reprovação, avanço e evasão escolar no Brasil. *Pesquisa e Planejamento Econômico*, v. 32, n. 3, p. 417-451, 2002. https://ppe.ipea.gov.br/index.php/ppe/article/view/138
- FERRÃO, M. E.; BELTRÃO, K. I.; SANTOS, D. P. O impacto de políticas de não-repetência sobre o aprendizado dos alunos da 4ª série. *Pesquisa e Planejamento Econômico*, v. 32, n. 3, p. 495-514, 2002. https://ppe.ipea.gov.br/index.php/ppe/article/view/141/76
- RIANI, J. L. R.; SILVA, V. C.; SOARES, T. M. Repetir ou progredir? Uma análise da repetência nas escolas públicas de Minas Gerais. *Educação e Pesquisa*, v. 38, n. 3, p. 623-636, 2012. DOI: 10.1590/S1517-97022012000300006 *[resumo]*
- JIMERSON, S. R. Meta-analysis of grade retention research. *School Psychology Review*, v. 30, n. 3, p. 420-437, 2001. DOI: 10.1080/02796015.2001.12086124 *[resumo]*
- ALLEN, C. S.; CHEN, Q.; WILLSON, V. L.; HUGHES, J. N. Quality of research design moderates effects of grade retention on achievement. *Educational Evaluation and Policy Analysis*, v. 31, n. 4, p. 480-499, 2009. DOI: 10.3102/0162373709352239 *[resumo]*
- MANACORDA, M. The cost of grade retention. *Review of Economics and Statistics*, v. 94, n. 2, p. 596-606, 2012. DOI: 10.1162/REST_a_00165 *[resumo]*

### Dever de casa e estudo
- COOPER, H.; ROBINSON, J. C.; PATALL, E. A. Does homework improve academic achievement? A synthesis of research, 1987-2003. *Review of Educational Research*, v. 76, n. 1, p. 1-62, 2006. DOI: 10.3102/00346543076001001 *[resumo]*
- TRAUTWEIN, U. The homework-achievement relation reconsidered. *Learning and Instruction*, v. 17, n. 3, p. 372-388, 2007. DOI: 10.1016/j.learninstruc.2007.02.009 *[achado via fonte secundária]*
- FERNÁNDEZ-ALONSO, R.; SUÁREZ-ÁLVAREZ, J.; MUÑIZ, J. Adolescents' homework performance in mathematics and science. *Journal of Educational Psychology*, v. 107, n. 4, p. 1075-1085, 2015. DOI: 10.1037/edu0000032 *[resumo]*
- FERNÁNDEZ-ALONSO, R.; ÁLVAREZ-DÍAZ, M.; SUÁREZ-ÁLVAREZ, J.; MUÑIZ, J. Students' achievement and homework assignment strategies. *Frontiers in Psychology*, v. 8, art. 286, 2017. DOI: 10.3389/fpsyg.2017.00286 *[resumo]*
- CARVALHO, M. E. P. Escola como extensão da família ou família como extensão da escola? *Revista Brasileira de Educação*, n. 25, p. 94-104, 2004. DOI: 10.1590/S1413-24782004000100009 *[resumo]*

### Envolvimento parental
- HILL, N. E.; TYSON, D. F. Parental involvement in middle school: a meta-analytic assessment. *Developmental Psychology*, v. 45, n. 3, p. 740-763, 2009. DOI: 10.1037/a0015362 *[resumo]*
- WILDER, S. Effects of parental involvement on academic achievement: a meta-synthesis. *Educational Review*, v. 66, n. 3, p. 377-397, 2014. DOI: 10.1080/00131911.2013.780009 *[resumo]*
- JEYNES, W. H. A meta-analysis of the relation of parental involvement to urban elementary school student academic achievement. *Urban Education*, v. 40, n. 3, p. 237-269, 2005. DOI: 10.1177/0042085905274540 *[resumo]*
- JEYNES, W. H. The relationship between parental involvement and urban secondary school student academic achievement: a meta-analysis. *Urban Education*, v. 42, n. 1, p. 82-110, 2007. DOI: 10.1177/0042085906293818 *[resumo]*
- CIA, F.; PAMPLIN, R. C. O.; WILLIAMS, L. C. A. O impacto do envolvimento parental no desempenho acadêmico de crianças escolares. *Psicologia em Estudo*, v. 13, n. 2, p. 351-360, 2008. DOI: 10.1590/S1413-73722008000200018 *[resumo]*
- OLIVEIRA, F. R.; RAPOSO, I. P. A.; SILVA, J. L. B. A. O comportamento familiar pode afetar o desempenho escolar e aspirações futuras dos estudantes de raças distintas? *Economia e Sociedade*, v. 32, n. 3, p. 669-689, 2023. DOI: 10.1590/1982-3533.2023v32n3art07 *[resumo]*

### Frequência e absenteísmo
- GOTTFRIED, M. A. Evaluating the relationship between student attendance and achievement in urban elementary and middle schools. *American Educational Research Journal*, v. 47, n. 2, p. 434-465, 2010. DOI: 10.3102/0002831209350494 *[resumo]*
- GOTTFRIED, M. A. Chronic absenteeism and its effects on students' academic and socioemotional outcomes. *Journal of Education for Students Placed at Risk*, v. 19, n. 2, p. 53-75, 2014. DOI: 10.1080/10824669.2014.962696 *[resumo]*
- GERSHENSON, S.; JACKNOWITZ, A.; BRANNEGAN, A. Are student absences worth the worry in U.S. primary schools? *Education Finance and Policy*, v. 12, n. 2, p. 137-165, 2017. DOI: 10.1162/EDFP_a_00207 *[resumo]*

### Métodos (multinível, ML, avaliações em larga escala)
- RAUDENBUSH, S. W.; BRYK, A. S. *Hierarchical Linear Models: Applications and Data Analysis Methods*. 2. ed. Thousand Oaks: Sage, 2002. https://www.sagepub.com/en-us/nam/hierarchical-linear-models/book9230
- BREIMAN, L. Statistical modeling: the two cultures. *Statistical Science*, v. 16, n. 3, p. 199-231, 2001. DOI: 10.1214/ss/1009213726 (conferir páginas)
- SHMUELI, G. To explain or to predict? *Statistical Science*, v. 25, n. 3, p. 289-310, 2010. DOI: 10.1214/10-STS330 (conferir páginas)
- LUNDBERG, S. M.; LEE, S.-I. A unified approach to interpreting model predictions. In: *Advances in Neural Information Processing Systems 30 (NIPS 2017)*. https://papers.nips.cc/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html
- RUTKOWSKI, L.; GONZALEZ, E.; JONCAS, M.; VON DAVIER, M. International large-scale assessment data: issues in secondary analysis and reporting. *Educational Researcher*, v. 39, n. 2, p. 142-151, 2010. DOI: 10.3102/0013189X10363170 *[resumo]*
- WU, M. The role of plausible values in large-scale surveys. *Studies in Educational Evaluation*, v. 31, n. 2-3, p. 114-128, 2005. DOI: 10.1016/j.stueduc.2005.05.005 *[resumo]*
- TERTULINO, R.; ALENCAR, L. A multi-level analysis of factors associated with student performance: a machine learning approach to the SAEB microdata. *Discover Education*, v. 5, art. 653, 2026. DOI: 10.1007/s44217-026-01699-0 *[resumo; periódico novo, avaliar]*
- SAN MARTIN SOARES, P. Combining statistical and machine learning methods to identify predictors of Brazilian students' proficiency in PISA 2018. *Journal of Psychoeducational Assessment*, v. 42, n. 8, p. 927-954, 2024. DOI: 10.1177/07342829241262861 *[resumo]*
- MAIA, J. S. Z.; BUENO, A. P. A.; SATO, J. R. Assessing the educational performance of different Brazilian school cycles using data science methods. *PLOS ONE*, v. 16, n. 3, e0248525, 2021. DOI: 10.1371/journal.pone.0248525 *[resumo]*

### PISA, Brasil e comparabilidade
- CARNOY, M.; KHAVENSON, T.; FONSECA, I.; COSTA, L.; MAROTTA, L. A educação brasileira está melhorando? Evidências do Pisa e do Saeb. *Cadernos de Pesquisa*, v. 45, n. 157, p. 450-485, 2015. https://publicacoes.fcc.org.br/cp/article/view/3331 *[resumo]*
- CITO, L.; MARÔCO, J. Beyond the average: mapping educational inequality in Brazil with PISA 2022. *Large-scale Assessments in Education*, v. 14, art. 30, 2026. DOI: 10.1186/s40536-026-00302-0 *[resumo]*

### Pandemia
- LICHAND, G.; DORIA, C. A.; LEAL-NETO, O.; FERNANDES, J. P. C. The impacts of remote learning in secondary education during the pandemic in Brazil. *Nature Human Behaviour*, v. 6, n. 8, p. 1079-1086, 2022. DOI: 10.1038/s41562-022-01350-6
- BETTHÄUSER, B. A.; BACH-MORTENSEN, A. M.; ENGZELL, P. A systematic review and meta-analysis of the evidence on learning during the COVID-19 pandemic. *Nature Human Behaviour*, v. 7, n. 3, p. 375-385, 2023. DOI: 10.1038/s41562-022-01506-4 *[achado via fonte secundária]*

### Não usar (não verificadas ou com problemas)
- "Soares & Alves (2003), *Desigualdades raciais e de gênero…*": esse título não existe. Use o artigo listado acima.
- Menezes-Filho (2007), "Os determinantes do desempenho escolar do Brasil": não localizei a fonte primária.
- Hattie (2009), *Visible Learning*, e Hanushek (1986), JEL: não verificados nesta rodada.

---

## Fontes e grau de confiança

| Bloco | Confiança | Motivo |
|---|---|---|
| Estrutura do SAEB 2023, máscaras, variáveis | **Alta** | Lido diretamente no dicionário e no Leia-Me locais |
| Números [DADO] | **Média-alta** | Calculados por mim; descritivos; o ICC não é ponderado; a média de 257,1 deve ser conferida com o resultado oficial |
| Situação do PISA 2025 e country note do Brasil | **Alta** | Páginas oficiais da OCDE lidas em 07/10/2026 |
| Médias do Brasil no PISA 2025 (408/377/409) | **Média** | Agência Gov e imprensa; conferir nas tabelas da OCDE |
| Referências | **Alta** para metadados; **média** para achados | A maior parte dos achados foi lida só no resumo |
| Lacunas (frequência e dever de casa no Brasil) | **Média** | Ausência de evidência na busca não prova que não existam estudos |

**Confiança geral: ALTA** para o diagnóstico e o desenho recomendado; **MÉDIA** para as magnitudes esperadas.

---

## Recomendação final

Seguir a **P1**: 9º ano do SAEB 2023, Matemática; trajetória, estudo e família, controlando o INSE.
- **Núcleo do método:** MQO ponderado → efeitos fixos de escola → multinível.
- **Papel do ML:** auditoria de não linearidades.
- **PISA 2025:** contexto e comparação de padrões em DP, com replicação opcional nos microdados.

Essa cadeia (**problema → pergunta → hipóteses → dados → variáveis → método → algoritmos → artefatos → PISA**) é viável no prazo de uma disciplina, usa dados já baixados, evita as duas armadilhas principais (cruzar bases mascaradas e afirmar causalidade) e tem um achado potencialmente original: a diferença dentro × entre escolas e o envolvimento parental reativo.
