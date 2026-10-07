# Registro de decisões do projeto

Artigo de Ciência de Dados II (Prof. Ivan Martins, 2026/02)
Autores: Everton Silva, Enrique Almeida, Raymora Araujo
Base metodológica: [Relatorio_Deep_Research_Desempenho_Escolar.md](Relatorio_Deep_Research_Desempenho_Escolar.md)
Última atualização: 07/10/2026

## Escopo e logística

| # | Decisão | Valor |
|---|---|---|
| 1 | Prazo | Segunda quinzena de novembro de 2026 |
| 2 | Formato | Template `template-previa-artigo.docx` (ABNT). Ver "Conflito de tamanho", abaixo |
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
- **Família:** testar os índices "socialização" (Q10a, Q10b) e "monitoramento" (Q10c, Q10d) com análise fatorial; se não se sustentarem, usar os itens isolados.
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

## Conflito de tamanho (pendente)

- O template diz: **7 a 14 páginas**, de 3.000 a 9.000 palavras, incluindo as referências.
- A orientação recebida diz: **12 a 20 páginas**.
- A interseção das duas regras é **12 a 14 páginas**.
- **Mirar em 13–14 páginas até o professor confirmar.**

## Estrutura imposta pelo template

Título (máx. 15 palavras) / Title → Autores → Resumo (máx. 250 palavras) / Abstract → Palavras-chave / Keywords → INTRODUÇÃO → METODOLOGIA → RESULTADOS E DISCUSSÃO → CONSIDERAÇÕES FINAIS → REFERÊNCIAS.

**Não há seção de referencial teórico.** A revisão de literatura entra na Introdução, que segundo o template deve trazer contextualização atualizada, justificativa e hipóteses.

Formatação:
- Times New Roman 12, espaçamento 1,5, texto justificado;
- margens: superior e esquerda 3 cm, inferior e direita 2 cm;
- recuo da primeira linha: 1,5 cm;
- legendas e fontes de tabelas e figuras: tamanho 10, centralizadas;
- figuras em GIF ou JPEG.
