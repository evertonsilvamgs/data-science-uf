<!--
Versão de PROTOCOLO (tempo futuro), redigida antes da estimação dos modelos.
Após a execução, converter para o pretérito e preencher os campos marcados com [__].
Números de amostra vêm de resultados/tab_fluxo_amostra.csv (analises/01_preparacao.py).
Alvo de extensão (template refs/Template Artigo.docx, artigo de 12–20 p.): ~4 páginas.
O template exige o tempo passado na versão final; o texto sobre o CEP será preenchido no fechamento (fora da contagem de páginas).
-->

# METODOLOGIA

## Delineamento da pesquisa

Trata-se de um estudo quantitativo, observacional e transversal, de caráter explicativo-correlacional, baseado em dados secundários de uma avaliação educacional em larga escala. O termo "explicativo" designa a modelagem de associações condicionais orientadas por hipóteses teóricas, e não a identificação de efeitos causais (SHMUELI, 2010). Como o desenho não envolve manipulação de variáveis nem acompanhamento longitudinal dos estudantes, os resultados serão interpretados exclusivamente como associações estatísticas. O estudo tem ainda um componente comparativo: os padrões encontrados serão confrontados com os indicadores do Programa Internacional de Avaliação de Estudantes (PISA) 2025 para o Brasil.

## Fonte de dados e população

Os dados vêm dos microdados do Sistema de Avaliação da Educação Básica (Saeb) 2023, publicados pelo Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira (INEP, 2024). Será utilizada a base de estudantes do 9º ano do ensino fundamental (TS_ALUNO_9EF). Ela reúne as proficiências em Língua Portuguesa e Matemática e as respostas ao questionário contextual do estudante, que trata de perfil, condições socioeconômicas, trajetória escolar e uso do tempo. Na rede pública, o Saeb 2023 é censitário para essa etapa; na rede privada, é amostral. A população-alvo deste estudo é formada pelos estudantes do 9º ano de escolas públicas brasileiras em 2023. A escolha do 9º ano se justifica pela maior qualidade das respostas ao questionário em relação ao 5º ano e pela maior taxa de comparecimento em relação ao ensino médio. Além disso, essa etapa é a mais próxima da população de 15 anos avaliada pelo PISA.

As proficiências são estimadas pela Teoria de Resposta ao Item e expressas na escala única do Saeb, com média 250 e desvio-padrão 50 na população de referência de 1997. Para cada estudante, a base informa uma estimativa pontual e seu erro-padrão, que é em média de 25,3 pontos em Matemática. Por exigência da Lei Geral de Proteção de Dados (LGPD), os códigos de escola e de município são substituídos por máscaras. Elas permitem agrupar os estudantes por escola, mas impedem o cruzamento com o Censo Escolar ou com indicadores municipais (INEP, 2024). Por isso, as variáveis de escola utilizadas serão as do próprio Saeb: as disponíveis na base TS_ESCOLA e as agregadas a partir dos estudantes. A Unidade da Federação (UF) é a única variável geográfica com código real.

## Amostra analítica

A amostra analítica seguirá os critérios usados pelo INEP no cálculo dos resultados oficiais, acrescidos do preenchimento do questionário. A Tabela 1 apresenta o efeito de cada filtro. Das 2.502.907 observações da base, 2.447.143 pertencem a escolas públicas. Serão excluídos os registros inconsistentes com o Censo Escolar (13.523), os de estudantes ausentes na prova de Matemática (380.231), os sem proficiência calculável (5.229), os sem peso amostral (142) e os sem questionário preenchido (14.737). Restam 2.033.281 estudantes de 36.181 escolas. O modelo principal usará os casos completos nas variáveis analisadas: 1.764.251 estudantes (86,8%) de 36.176 escolas.

**Tabela 1 – Fluxo de construção da amostra analítica**
*(gerar a partir de resultados/tab_fluxo_amostra.csv; tamanho 10, centralizado)*
Fonte: elaborada pelos autores a partir dos microdados do Saeb 2023 (INEP, 2024).

## Variáveis

O Quadro 1 sintetiza a operacionalização das variáveis.

- **Variável dependente:** a proficiência em Matemática. A proficiência em Língua Portuguesa será usada como desfecho alternativo na análise de robustez.
- **Exposições:** três grupos de variáveis, correspondentes às hipóteses do estudo:
  - **trajetória escolar:** reprovação e abandono, usados como aproximação da continuidade e da frequência escolar, já que o Saeb não registra faltas;
  - **uso do tempo:** tempo diário de estudo fora da escola;
  - **envolvimento familiar:** práticas parentais relatadas pelo estudante.
- **Variável de controle principal:** o Indicador de Nível Socioeconômico do estudante (INSE). O INSE é construído pelo INEP com base em bens do domicílio, serviços e escolaridade dos responsáveis (ALVES; SOARES; XAVIER, 2014). Por já incorporar a escolaridade dos pais, essa informação não será incluída separadamente, para evitar redundância.
- **Fora do modelo principal:** variáveis de engajamento e de percepção sobre os professores, por poderem atuar como mediadoras das associações investigadas.

**Quadro 1 – Variáveis do estudo**

| Papel | Variável (item do questionário) | Operacionalização |
|---|---|---|
| Dependente | Proficiência em Matemática | Escala Saeb (contínua); também expressa em desvios-padrão |
| Dependente (robustez) | Proficiência em Língua Portuguesa | Escala Saeb (contínua) |
| Trajetória | Reprovação (Q19) | Nunca (ref.); uma vez; duas vezes ou mais |
| Trajetória | Abandono (Q20) | Nunca (ref.); uma vez ou mais |
| Trajetória (alternativa) | Distorção idade-série (Q02) | 16 anos ou mais no 9º ano (dois ou mais anos acima da idade esperada) |
| Uso do tempo | Estudo fora da escola em dias de aula (Q21a) | Não estuda (ref.); menos de 1 h; de 1 a 2 h; mais de 2 h |
| Família | Socialização acadêmica (Q10a, Q10b) | Índice: pais leem em casa; conversam sobre a escola |
| Família | Monitoramento (Q10c, Q10d) | Índice: pais incentivam a estudar; incentivam a fazer a tarefa |
| Família | Participação na escola (Q10f) | Ordinal: frequência de ida às reuniões |
| Controle | INSE do estudante | Contínua, padronizada |
| Controle | Sexo (Q01); cor/raça (Q04); deficiência (Q05a) | Categóricas |
| Controle | Idade de entrada na escola (Q17) | Categórica |
| Controle | Trabalho fora de casa (Q21d) | Categórica |
| Controle | Localização (rural/urbana); capital/interior; UF | Categóricas (UF como efeito fixo) |
| Escola (nível 2) | INSE médio; proporção de reprovados; tempo médio de estudo | Médias ponderadas dos estudantes da escola |

Fonte: elaborado pelos autores com base no dicionário de dados do Saeb 2023 (INEP, 2024).

Os índices de envolvimento familiar distinguem práticas de socialização acadêmica e práticas de monitoramento. Essa separação segue a evidência de que as duas formas de envolvimento se relacionam de modo distinto com o desempenho (HILL; TYSON, 2009). A estrutura será testada por análise fatorial exploratória sobre correlações policóricas, em metade aleatória da amostra, e confirmatória, na outra metade. A confiabilidade será avaliada pelo ômega de McDonald. Se a estrutura de dois fatores não se sustentar (cargas inferiores a 0,40 ou ajuste inadequado), os itens serão usados isoladamente.

## Preparação dos dados

Os códigos de não resposta do questionário ("*" para marcação inválida e "." para item em branco) serão convertidos em valores ausentes. A unicidade dos identificadores de estudante já foi verificada. A análise de ausências mostrou que os estudantes com informação incompleta têm proficiência média ponderada inferior à dos demais (229,8 contra 253,2 pontos). Os dados, portanto, não são ausentes de forma completamente aleatória. Por isso, a análise principal usará os casos completos, e uma análise de sensibilidade manterá todos os estudantes, codificando a ausência como categoria própria de cada variável.

Todas as estimativas usarão o peso amostral do estudante em Matemática. Na rede pública, esse peso funciona essencialmente como ajuste de não resposta: tem mediana de 1,07 e 99% dos valores são inferiores a 1,72. Como 355 estudantes têm pesos superiores a 5, será feita uma análise de sensibilidade com pesos aparados no percentil 99 e outra sem ponderação. As variáveis contínuas usadas como controle serão padronizadas (média 0 e desvio-padrão 1, ponderados). As categóricas serão codificadas em variáveis indicadoras com categoria de referência definida pela teoria.

## Estratégia analítica

A análise terá quatro etapas.

**Primeira etapa: descrição.** Serão calculadas a distribuição das variáveis e médias ponderadas de proficiência por categoria das exposições, com intervalos de confiança de 95%. Também será estimado o modelo multinível nulo, que fornece a correlação intraclasse: a parcela da variância da proficiência situada entre escolas.

**Segunda etapa: regressão linear ponderada em blocos.** Os blocos serão incluídos cumulativamente, para verificar quanto cada grupo de fatores acrescenta à explicação:
- B1: controles demográficos e territoriais;
- B2: B1 + INSE;
- B3: B2 + trajetória escolar;
- B4: B3 + estudo fora da escola;
- B5: B4 + envolvimento familiar.

A contribuição de cada bloco será avaliada pela variação do R² e pela estabilidade dos coeficientes. Os erros-padrão serão agrupados por escola, porque estudantes da mesma escola não são observações independentes. Esse modelo corresponde às hipóteses H1, H2 e H3.

**Terceira etapa: comparações dentro das escolas.** O modelo B5 será reestimado com efeitos fixos de escola. Essa especificação compara apenas estudantes da mesma escola e remove todo fator constante no nível escolar, como a rede, a localização, a infraestrutura e a composição social. A diferença entre os coeficientes com e sem efeitos fixos indica quanto de cada associação se deve a diferenças entre escolas (hipótese H4), como sugerem estudos em que a associação entre dever de casa e desempenho muda de sinal entre os níveis individual e escolar (FERNÁNDEZ-ALONSO et al., 2017).

Complementarmente, será estimado um modelo multinível de intercepto aleatório (RAUDENBUSH; BRYK, 2002). Nele, o INSE do estudante será centrado na média da escola, e as médias escolares de INSE, de reprovação e de tempo de estudo entrarão como preditores de nível 2. O objetivo é separar os efeitos individuais dos efeitos de composição. Por limitação computacional, esse modelo será estimado em uma amostra aleatória de 3.000 escolas, estratificada por UF.

**Quarta etapa: heterogeneidade.** Para testar se as associações variam com o nível socioeconômico (H5), serão incluídos termos de interação entre o INSE e as variáveis de reprovação e de tempo de estudo no modelo com efeitos fixos.

Dado o tamanho da amostra, praticamente qualquer coeficiente será estatisticamente significativo. A interpretação, portanto, se apoiará na magnitude dos efeitos, expressos em pontos da escala Saeb e em desvios-padrão, e nos intervalos de confiança, e não apenas nos valores-p.

A robustez será verificada pela repetição do modelo principal:
- com Língua Portuguesa como desfecho;
- sem ponderação e com pesos aparados;
- com a categoria de ausentes;
- substituindo a reprovação pela distorção idade-série.

## Análise complementar com aprendizado de máquina

O objetivo do estudo é explicativo, e não preditivo, de modo que o aprendizado de máquina terá papel apenas diagnóstico (SHMUELI, 2010). Será ajustado um modelo de *gradient boosting* (LightGBM) com as mesmas variáveis do modelo B5, em uma amostra aleatória de 300 mil estudantes. O desempenho será avaliado por validação cruzada em cinco partições agrupadas por escola, o que impede que estudantes da mesma escola estejam simultaneamente nos dados de treino e de teste. O erro quadrático médio e o R² fora da amostra serão comparados aos da regressão linear com as mesmas variáveis. Ganho expressivo do modelo não linear indicará relações ou interações não captadas pela especificação linear. Essas relações serão examinadas por valores SHAP (LUNDBERG; LEE, 2017), com atenção ao formato da associação do tempo de estudo e do INSE. Os valores SHAP descrevem a contribuição das variáveis para as previsões do modelo e não serão interpretados como efeitos causais.

## Relação com o PISA 2025

Os resultados do PISA 2025 foram divulgados em setembro de 2026 (OECD, 2026a). A comparação será feita no nível dos padrões de associação, e não das médias de desempenho. As duas avaliações diferem quanto:
- à população: o Saeb avalia uma série escolar, e o PISA, estudantes de 15 anos em qualquer série;
- ao construto: o Saeb usa uma matriz curricular, e o PISA mede letramento;
- à escala;
- ao período de aplicação;
- ao tratamento da proficiência: estimativa pontual no Saeb e valores plausíveis no PISA (RUTKOWSKI et al., 2010).

Assim, as escalas não serão convertidas uma na outra. Três comparações serão feitas (H6):
1. a proporção da variância da proficiência associada ao nível socioeconômico no Saeb (R² do INSE) com a reportada pela OCDE para o índice socioeconômico do PISA (ESCS) no Brasil;
2. a direção das associações de reprovação e de envolvimento familiar com as relações análogas descritas pela OCDE;
3. a ausência de registro de faltas no Saeb com os indicadores de frequência do PISA 2025 (OECD, 2026b), discutindo o que essa lacuna implica para a interpretação da trajetória escolar como aproximação da frequência.

## Reprodutibilidade e aspectos éticos

As análises serão feitas em Python (versão 3.13), com as bibliotecas pandas, statsmodels, pyfixest, factor_analyzer, lightgbm e shap. O código será organizado em scripts numerados, com semente aleatória fixa e versões registradas, e ficará disponível em repositório. O estudo usa apenas dados públicos e anonimizados, sem acesso a informações que permitam identificar os participantes, e por isso não foi submetido a Comitê de Ética em Pesquisa [texto final sobre o CEP a ser preenchido no fechamento]. Não haverá tentativa de reidentificar escolas ou municípios. Os resultados serão apresentados de forma agregada, sem classificação de escolas ou de redes e sem interpretações que atribuam responsabilidade individual a estudantes, famílias ou docentes.
