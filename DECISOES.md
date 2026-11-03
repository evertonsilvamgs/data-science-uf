# Registro de decisões do projeto

Artigo de Ciência de Dados II (Prof. Ivan Martins, 2026/02)
Autores: Everton Silva, Enrique Almeida, Raymora Araujo
Base metodológica: [Relatorio_Deep_Research_Desempenho_Escolar.md](Relatorio_Deep_Research_Desempenho_Escolar.md)
Última atualização: 03/11/2026

## Escopo e logística

| # | Decisão | Valor |
|---|---|---|
| 1 | Prazo | **20/11/2026** (confirmado em 03/11/2026) |
| 2 | Formato | Template `refs/Template Artigo.docx` (ABNT), **12 a 20 páginas** (regra confirmada com colegas em 07/10/2026). Ver "Estrutura e formatação", abaixo |
| 3 | Autoria | Everton Silva, Enrique Almeida, Raymora Araujo (sem divisão de funções no texto) |
| 4 | Produtos extras | Nenhum por enquanto |
| 5 | Linguagem | Python |

## Desenho

| # | Decisão | Valor |
|---|---|---|
| 6 | Pergunta | P1: trajetória, tempo de estudo e envolvimento familiar × proficiência, controlando o INSE; comparação dentro × entre escolas; heterogeneidade por NSE; ponte com o PISA 2025 |
| 7 | Série | 9º ano do EF (`TS_ALUNO_9EF`) |
| 8 | Desfecho | Matemática (`PROFICIENCIA_MT_SAEB`) como principal; Língua Portuguesa como robustez; Ciências da Natureza como extensão opcional |
| 9 | Rede | **Somente escolas públicas** (`IN_PUBLICA = 1`) |
| 10 | Modelos | MQO ponderado → efeitos fixos de escola → multinível (em amostra de escolas, se necessário) |
| 11 | ML | LightGBM + SHAP apenas como diagnóstico de não linearidade, em subseção curta |
| 12 | PISA 2025 | (a) Comparação com indicadores publicados pela OCDE (compromisso); (b) replicação nos microdados (extensão, se houver tempo) |
| 13 | Hipóteses | Enxutas: H1, H1b, H4, H4b, H5, H6, H7, H9. H2, H3 e H8 viram análises secundárias |

## Padrões técnicos (grupo 3, sem objeção)

- **Ausentes:** casos completos na análise principal; dummy de "ausente" como robustez.
- **Trajetória:** Q19 (reprovação) no modelo principal; distorção idade-série em modelo alternativo.
- **Família (decidido em 03/11/2026, após a análise fatorial da etapa 2):** índice de **incentivo** = média de Q10c, Q10d e Q10e (ômega 0,85; estrutura idêntica nas duas metades da amostra, congruência de Tucker ≥ 0,999), padronizado. Q10a (pais leem), Q10b (conversam sobre a escola) e Q10f (reuniões) entram como itens separados, porque o par Q10a–Q10b tem confiabilidade baixa (ômega 0,48). A inclusão de Q10e no índice difere do protocolo e será relatada na Metodologia.
- **Mediadores:** Q23 e expectativa docente ficam fora do modelo principal.
- **Bases:** professor e diretor ficam fora; desfecho logístico (nível adequado) fica fora.
- **Repositório:** scripts numerados, dados brutos fora do git, sementes fixas.

## Fatos dos dados que sustentam as decisões

Valores calculados em 07/10/2026 na amostra analítica de escolas públicas do 9º ano (`IN_SITUACAO_CENSO = 1`, `IN_PROFICIENCIA_MT = 1`, peso não nulo):

- 2.048.018 alunos em 36.201 escolas.
- 99,3% preencheram o questionário.
- `PESO_ALUNO_MT`:
  - média 1,113; mediana 1,071; coeficiente de variação 0,21; máximo 109,2;
  - desvio-padrão médio dentro da escola de 0,052.
  - As públicas são censitárias e o peso funciona basicamente como ajuste de não resposta. Usar o peso na análise principal, fazer sensibilidade sem peso e investigar os pesos extremos.

## Estrutura e formatação (template `refs/Template Artigo.docx`)

O template anterior (`template-previa-artigo.docx`, com limite de 7–14 páginas) foi substituído em 07/10/2026. Vale a regra de **12 a 20 páginas**. **Alvo: 16–17 páginas**, deixando folga para os ajustes finais.

### Estrutura prevista e orçamento de páginas

| Seção | Conteúdo | Páginas (alvo) |
|---|---|---|
| Título / Title | Centralizado, caixa alta, tamanho 12, mais a versão em inglês | — |
| Autores e afiliação | Everton Silva¹, Enrique Almeida¹, Raymora Araujo¹, Ivan Martins¹ (orientador); ¹ Centro Universitário de Mineiros – UNIFIMES, Mineiros, GO, Brasil | — |
| Resumo / Abstract | Introdução, objetivos, metodologia, resultados e conclusão; espaçamento simples; 3 palavras-chave e keywords | 1 |
| **INTRODUÇÃO** | Contexto (Saeb, PISA 2025, desigualdade), **referencial teórico** (NSE e efeito-escola, trajetória, dever de casa, envolvimento parental, frequência), justificativa, objetivos e hipóteses | 3,5 |
| **METODOLOGIA** | Desenho, fonte de dados, amostra, variáveis, preparação, estratégia analítica, aprendizado de máquina, PISA 2025, reprodutibilidade e ética. **Escrita no passado na versão final** | 4 |
| **RESULTADOS** | Descritivas, modelos em blocos, efeitos fixos e multinível, heterogeneidade, robustez, aprendizado de máquina | 4 |
| **DISCUSSÃO** | Comparação com a literatura e com o PISA 2025, interpretação não causal, implicações e limitações | 2,5 |
| **CONSIDERAÇÕES FINAIS** | Resposta aos objetivos, de forma objetiva | 0,5 |
| **REFERÊNCIAS** | ABNT, apenas obras citadas | 1,5 |
| **Total** | | **≈ 17** |

A declaração de uso de IA e a informação sobre o Comitê de Ética **não entram na contagem de páginas**. As duas serão preenchidas no fechamento.

As figuras e tabelas já estão incluídas no orçamento de cada seção. A previsão é de 6 a 8 figuras e tabelas no corpo do artigo.

### Formatação
- **Arial** 12, espaçamento entre linhas 1,5, texto justificado.
- Margens: superior e esquerda 3 cm; inferior e direita 2 cm.
- Resumo e Abstract em Arial 12, com espaçamento simples.
- Legendas e fontes de tabelas e figuras em Arial 10, centralizadas, espaçamento simples.
- Figuras em GIF ou JPEG. A fonte das figuras será "Elaborada pelos autores a partir dos microdados do Saeb 2023 (INEP, 2024)", porque elas são geradas pelo nosso código, e não por IA.
- Citações e referências conforme as normas ABNT em vigor.

## Pendências

| # | Pendência | Responsável | Observação |
|---|---|---|---|
| P1 | **Comitê de Ética (CEP).** O template pede o número de aprovação | Equipe | **Adiado para o fechamento** (decisão de 07/10/2026). Fora da contagem de páginas |
| P3 | **Declaração de uso de IA** | Equipe | **Adiado para o fechamento** (decisão de 07/10/2026). Fora da contagem de páginas |

Resolvidas em 07/10/2026:
- **P2:** Ivan Martins entra como orientador.
- **Cabeçalho:** Unidade Básica das Ciências Exatas – Curso de Sistemas de Informação (03/11/2026).
- **P4:** confirmados 3.000 escolas para o multinível e 300 mil alunos para o aprendizado de máquina.
