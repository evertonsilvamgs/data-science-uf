"""Gera o artigo em .docx a partir dos rascunhos em Markdown, usando o template da UNIFIMES.

Uso:  python artigo/gerar_docx.py
Saída: artigo/saida/Artigo-Ciencia-de-Dados-II.docx

Convenções do Markdown aceitas:
  # TÍTULO DE SEÇÃO            -> seção primária (negrito, caixa alta)
  ## Subseção                  -> seção secundária (negrito)
  parágrafo comum              -> corpo (Times New Roman 12, 1,5, justificado, recuo 1,25 cm)
  - item / 1. item / a) item   -> lista
  | a | b |                    -> tabela (Times New Roman 10, espaçamento simples)
  **Tabela 1 – título**        -> legenda (linha inteira em negrito começando com Tabela/Quadro/Figura)
  Fonte: ...                   -> fonte da tabela/figura (Times New Roman 10, centralizada)
  ![legenda](caminho.png "13")  -> figura centralizada (largura opcional em cm)
  *(texto)*                    -> marcador de pendência (destacado em amarelo)
  **negrito**, *itálico*, [__] -> formatação inline; colchetes [..] ficam destacados em amarelo
  <!-- ... -->                 -> comentário (ignorado)
"""
import json
import re
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_COLOR_INDEX
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

DIR_ARTIGO = Path(__file__).resolve().parent
RAIZ = DIR_ARTIGO.parent
TEMPLATE = RAIZ / "refs" / "Template Artigo.docx"
SAIDA = DIR_ARTIGO / "saida" / "Artigo-Ciencia-de-Dados-II.docx"

FONTE = "Times New Roman"  # pedido da equipe (24/11/2026), no lugar da Arial do template
RECUO = Cm(1.25)
PALAVRAS_POR_PAGINA = 330  # calibrado em 07/10/2026 com a contagem do Word (15 p. para ~4.270 palavras + quadros)

TITULOS_PADRAO = {
    "01_introducao.md": "INTRODUÇÃO",
    "02_metodologia.md": "METODOLOGIA",
    "03_resultados.md": "RESULTADOS",
    "04_discussao.md": "DISCUSSÃO",
    "05_conclusao.md": "CONCLUSÃO",
    "referencias.md": "REFERÊNCIAS",
}

RE_INLINE = re.compile(r"(\*\*.+?\*\*|\*[^*\s][^*]*?\*|\[[^\]]*\])")
RE_LEGENDA = re.compile(r"^\*\*(Tabela|Quadro|Figura)\s.+\*\*$")
RE_IMAGEM = re.compile(r'^!\[(.*?)\]\((\S+?)(?:\s+"([\d.]+)")?\)$')
RE_NUMERADA = re.compile(r"^(\d+\.|[a-z]\))\s+(.*)$")


# --------------------------------------------------------------------------------------
# Utilidades de formatação
# --------------------------------------------------------------------------------------
def _fonte(run, tamanho=12, negrito=None, italico=None):
    run.font.name = FONTE
    run.font.size = Pt(tamanho)
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = rpr.makeelement(qn("w:rFonts"), {})
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(attr), FONTE)
    if negrito is not None:
        run.bold = negrito
    if italico is not None:
        run.italic = italico


def _formato(par, alinhamento=WD_ALIGN_PARAGRAPH.JUSTIFY, entrelinha=1.5, recuo=None,
             antes=0, depois=0, recuo_esq=None):
    pf = par.paragraph_format
    par.alignment = alinhamento
    pf.line_spacing = entrelinha
    pf.space_before = Pt(antes)
    pf.space_after = Pt(depois)
    pf.first_line_indent = recuo
    if recuo_esq is not None:
        pf.left_indent = recuo_esq


MARCADORES = ("__", "preencher", "redigir", "confirmar", "verificar", "pendente", "ajustar")


def _eh_marcador(trecho: str) -> bool:
    """Colchetes que sinalizam pendência (destacados em amarelo no .docx)."""
    return any(m in trecho.lower() for m in MARCADORES)


def _inline(par, texto, tamanho=12, negrito_base=False, italico_base=False):
    """Escreve texto com **negrito**, *itálico* e [marcadores] destacados."""
    for parte in RE_INLINE.split(texto):
        if not parte:
            continue
        negrito, italico, destaque = negrito_base, italico_base, False
        if parte.startswith("**") and parte.endswith("**"):
            parte, negrito = parte[2:-2], True
        elif parte.startswith("*") and parte.endswith("*") and len(parte) > 2:
            parte, italico = parte[1:-1], True
        elif parte.startswith("[") and parte.endswith("]"):
            if not _eh_marcador(parte):  # ex.: [S. l.] nas referências -> texto normal
                _fonte(par.add_run("["), tamanho, negrito_base, italico_base)
                _inline(par, parte[1:-1], tamanho, negrito_base, italico_base)
                _fonte(par.add_run("]"), tamanho, negrito_base, italico_base)
                continue
            destaque = True
        run = par.add_run(parte)
        _fonte(run, tamanho, negrito, italico)
        if destaque:
            run.font.highlight_color = WD_COLOR_INDEX.YELLOW


def _limpar_corpo(doc):
    corpo = doc.element.body
    for el in list(corpo):
        if el.tag != qn("w:sectPr"):
            corpo.remove(el)


def _cabecalho(doc, unidade):
    for par in doc.sections[0].header.paragraphs:
        if "Unidade" in par.text:
            for run in par.runs[1:]:
                run.text = ""
            par.runs[0].text = unidade


def _fonte_global(doc):
    """Troca a fonte de todos os estilos, do padrão do documento, do cabeçalho e do rodapé."""
    for estilo in doc.styles:
        if getattr(estilo, "font", None) is not None:
            estilo.font.name = FONTE
            rpr = estilo.element.get_or_add_rPr()
            rf = rpr.find(qn("w:rFonts"))
            if rf is None:
                rf = rpr.makeelement(qn("w:rFonts"), {})
                rpr.append(rf)
            for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
                rf.set(qn(attr), FONTE)
            for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
                rf.attrib.pop(qn(attr), None)
    padrao = doc.styles.element.find(qn("w:docDefaults"))
    if padrao is not None:
        for rf in padrao.iter(qn("w:rFonts")):
            for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
                rf.set(qn(attr), FONTE)
            for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
                rf.attrib.pop(qn(attr), None)
    for sec in doc.sections:
        for parte in (sec.header, sec.footer, sec.first_page_header, sec.first_page_footer):
            # inclui caixas de texto e marcas de parágrafo, que parte.paragraphs não alcança
            for rf in parte._element.iter(qn("w:rFonts")):
                for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
                    rf.set(qn(attr), FONTE)


# --------------------------------------------------------------------------------------
# Blocos
# --------------------------------------------------------------------------------------
def paragrafo(doc, texto, **kw):
    par = doc.add_paragraph()
    _formato(par, recuo=kw.pop("recuo", RECUO), **kw)
    _inline(par, texto)
    return par


def secao(doc, texto, nivel=1):
    par = doc.add_paragraph()
    _formato(par, alinhamento=WD_ALIGN_PARAGRAPH.LEFT, antes=12, depois=6)
    run = par.add_run(texto.upper() if nivel == 1 else texto)
    _fonte(run, 12, negrito=True)
    _manter_com_seguinte(par)


def item_lista(doc, texto, marcador):
    par = doc.add_paragraph()
    _formato(par, recuo=Cm(-0.5), recuo_esq=Cm(1.75))
    _fonte(par.add_run(f"{marcador} "), 12)
    _inline(par, texto)


def legenda_ou_fonte(doc, texto, italico=False, destaque=False):
    par = doc.add_paragraph()
    _formato(par, alinhamento=WD_ALIGN_PARAGRAPH.CENTER, entrelinha=1.0, antes=3, depois=3)
    if destaque:
        run = par.add_run(texto)
        _fonte(run, 10, italico=True)
        run.font.highlight_color = WD_COLOR_INDEX.YELLOW
    else:
        _inline(par, texto, tamanho=10, italico_base=italico)


def _bordas(tab):
    """Bordas simples em todas as células (o template não traz o estilo 'Table Grid')."""
    tbl_pr = tab._tbl.tblPr
    bordas = tbl_pr.makeelement(qn("w:tblBorders"), {})
    for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = bordas.makeelement(qn(f"w:{lado}"), {qn("w:val"): "single", qn("w:sz"): "4",
                                                  qn("w:space"): "0", qn("w:color"): "000000"})
        bordas.append(el)
    tbl_pr.append(bordas)


LARGURA_TEXTO = 16.0  # cm: 21 cm - margens de 3 e 2 cm


def _manter_com_seguinte(par, valor=True):
    par.paragraph_format.keep_with_next = valor


def tabela(doc, linhas):
    """Tabela na largura do texto, colunas proporcionais ao conteúdo, sem quebra entre páginas."""
    celulas = [[c.strip() for c in l.strip().strip("|").split("|")] for l in linhas]
    celulas = [r for r in celulas if not all(re.fullmatch(r":?-{2,}:?", c) for c in r)]
    ncol = max(len(r) for r in celulas)
    tab = doc.add_table(rows=len(celulas), cols=ncol)
    _bordas(tab)
    tab.alignment = WD_TABLE_ALIGNMENT.CENTER
    tab.autofit = False
    # peso de cada coluna: comprimento típico do texto (limitado), com mínimo
    pesos = []
    for j in range(ncol):
        tam = [len(r[j]) if j < len(r) else 0 for r in celulas]
        pesos.append(max(6, min(60, sorted(tam)[len(tam) // 2] * 0.5 + max(tam) * 0.5)))
    # mínimo: a palavra mais longa da coluna cabe sem ser partida (~0,19 cm por caractere em 10 pt)
    minimos = [0.45 + 0.19 * max(len(p) for r in celulas if j < len(r) for p in (r[j].split() or [""]))
               for j in range(ncol)]
    cm = [LARGURA_TEXTO * w / sum(pesos) for w in pesos]
    fixas = {j for j in range(ncol) if cm[j] < minimos[j]}
    resto = LARGURA_TEXTO - sum(minimos[j] for j in fixas)
    soma_livres = sum(pesos[j] for j in range(ncol) if j not in fixas)
    cm = [minimos[j] if j in fixas else resto * pesos[j] / soma_livres for j in range(ncol)]
    larguras = [Cm(c) for c in cm]
    for i, linha in enumerate(celulas):
        tr_pr = tab.rows[i]._tr.get_or_add_trPr()
        tr_pr.append(tr_pr.makeelement(qn("w:cantSplit"), {}))
        if i == 0:
            tr_pr.append(tr_pr.makeelement(qn("w:tblHeader"), {}))
        for j in range(ncol):
            cel = tab.cell(i, j)
            cel.width = larguras[j]
            par = cel.paragraphs[0]
            _formato(par, alinhamento=WD_ALIGN_PARAGRAPH.LEFT, entrelinha=1.0)
            _manter_com_seguinte(par)  # a tabela e a linha de Fonte ficam na mesma página
            _inline(par, linha[j] if j < len(linha) else "", tamanho=10, negrito_base=(i == 0))


def figura(doc, caminho, base, largura=15.0):
    arq = (base / caminho).resolve()
    if not arq.exists():
        legenda_ou_fonte(doc, f"[figura não encontrada: {caminho}]", destaque=True)
        return
    doc.add_picture(str(arq), width=Cm(largura))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    _manter_com_seguinte(doc.paragraphs[-1])


# --------------------------------------------------------------------------------------
# Conversão de um arquivo Markdown
# --------------------------------------------------------------------------------------
def converter_markdown(doc, texto, base):
    texto = re.sub(r"<!--.*?-->", "", texto, flags=re.S)
    linhas = texto.splitlines()
    buffer_par, buffer_tab = [], []
    palavras = 0

    def descarregar():
        nonlocal palavras
        if buffer_par:
            t = " ".join(s.strip() for s in buffer_par)
            palavras += len(t.split())
            paragrafo(doc, t)
            buffer_par.clear()
        if buffer_tab:
            palavras += sum(len(l.replace("|", " ").split()) for l in buffer_tab)
            tabela(doc, buffer_tab)
            buffer_tab.clear()

    for linha in linhas:
        s = linha.strip()
        if s.startswith("|"):
            if buffer_par:
                descarregar()
            buffer_tab.append(s)
            continue
        if buffer_tab:
            descarregar()
        if not s:
            descarregar()
        elif s.startswith("## "):
            descarregar(); secao(doc, s[3:], nivel=2)
        elif s.startswith("# "):
            descarregar(); secao(doc, s[2:], nivel=1)
        elif s.startswith("- "):
            descarregar(); item_lista(doc, s[2:], "•"); palavras += len(s.split())
        elif RE_NUMERADA.match(s):
            descarregar(); n, t = RE_NUMERADA.match(s).groups(); item_lista(doc, t, n.rstrip(".)") + ")")
            palavras += len(t.split())
        elif RE_LEGENDA.match(s):
            descarregar(); legenda_ou_fonte(doc, s[2:-2]); _manter_com_seguinte(doc.paragraphs[-1])
        elif s.startswith("Fonte:"):
            descarregar(); legenda_ou_fonte(doc, s)
        elif RE_IMAGEM.match(s):
            descarregar(); m = RE_IMAGEM.match(s); figura(doc, m.group(2), base, float(m.group(3) or 15))
        elif s.startswith("*(") and s.endswith(")*"):
            descarregar(); legenda_ou_fonte(doc, s[1:-1], destaque=True)
        else:
            buffer_par.append(s)
    descarregar()
    return palavras


def referencias(doc, texto):
    """Referências: alinhadas à esquerda, espaçamento simples, uma linha em branco entre elas."""
    texto = re.sub(r"<!--.*?-->", "", texto, flags=re.S)
    palavras = 0
    for bloco in texto.split("\n\n"):
        b = " ".join(bloco.split())
        if not b:
            continue
        if b.startswith("# "):
            secao(doc, b[2:])
            continue
        par = doc.add_paragraph()
        _formato(par, alinhamento=WD_ALIGN_PARAGRAPH.LEFT, entrelinha=1.0, depois=12)
        _inline(par, b)
        palavras += len(b.split())
    return palavras


# --------------------------------------------------------------------------------------
# Elementos pré-textuais
# --------------------------------------------------------------------------------------
def preambulo(doc, meta):
    for chave, antes in (("titulo", 12), ("titulo_en", 6)):
        par = doc.add_paragraph()
        _formato(par, alinhamento=WD_ALIGN_PARAGRAPH.CENTER, antes=antes, depois=6)
        _fonte(par.add_run(meta[chave]), 12, negrito=True)

    par = doc.add_paragraph()
    _formato(par, antes=12)
    _fonte(par.add_run("Autores:"), 12, negrito=True)
    par = doc.add_paragraph()
    _formato(par)
    for i, a in enumerate(meta["autores"]):
        if i:
            _fonte(par.add_run(", "), 12)
        _fonte(par.add_run(a["nome"]), 12)
        sup = par.add_run(str(a["afiliacao"]))
        _fonte(sup, 12)
        sup.font.superscript = True
        if a.get("papel"):
            _fonte(par.add_run(f" ({a['papel']})"), 12)

    par = doc.add_paragraph()
    _formato(par, antes=12)
    _fonte(par.add_run("Afiliação:"), 12, negrito=True)
    for num, texto in meta["afiliacoes"].items():
        par = doc.add_paragraph()
        _formato(par)
        sup = par.add_run(num)
        _fonte(sup, 12)
        sup.font.superscript = True
        _fonte(par.add_run(texto), 12)

    for rotulo, chave_txt, rotulo_kw, chave_kw in (("Resumo:", "resumo", "Palavras-chave:", "palavras_chave"),
                                                   ("Abstract:", "abstract", "Keywords:", "keywords")):
        par = doc.add_paragraph()
        _formato(par, entrelinha=1.0, antes=12)
        _fonte(par.add_run(rotulo), 12, negrito=True)
        par = doc.add_paragraph()
        _formato(par, entrelinha=1.0, depois=6)
        _inline(par, meta[chave_txt])
        par = doc.add_paragraph()
        _formato(par, entrelinha=1.0, depois=6)
        _fonte(par.add_run(rotulo_kw + " "), 12, negrito=True)
        _fonte(par.add_run("; ".join(meta[chave_kw])), 12)


def declaracao_ia(doc):
    """Declaração de uso de IA (fora da contagem de páginas), em nova página.
    No arquivo: '# título' centralizado; linhas iniciadas por '>' centralizadas (data e assinaturas)."""
    par = doc.add_paragraph()
    par.add_run().add_break(WD_BREAK.PAGE)
    arq = DIR_ARTIGO / "declaracao_ia.md"
    texto = re.sub(r"<!--.*?-->", "", arq.read_text(encoding="utf-8"), flags=re.S)
    for bloco in texto.split("\n\n"):
        b = " ".join(bloco.split())
        if not b:
            continue
        par = doc.add_paragraph()
        if b.startswith("# "):
            _formato(par, alinhamento=WD_ALIGN_PARAGRAPH.CENTER, depois=6)
            _fonte(par.add_run(b[2:]), 12, negrito=True)
        elif b.startswith(">"):
            _formato(par, alinhamento=WD_ALIGN_PARAGRAPH.CENTER, antes=12)
            _inline(par, b[1:].strip())
        else:
            _formato(par, recuo=RECUO)
            _inline(par, b)


def main():
    meta = json.loads((DIR_ARTIGO / "metadados.json").read_text(encoding="utf-8"))
    doc = Document(str(TEMPLATE))
    _limpar_corpo(doc)
    _fonte_global(doc)
    _cabecalho(doc, meta["cabecalho_unidade"])
    preambulo(doc, meta)

    contagem = {}
    for nome in meta["secoes"]:
        arq = DIR_ARTIGO / nome
        if not arq.exists():
            secao(doc, TITULOS_PADRAO.get(nome, nome))
            legenda_ou_fonte(doc, "(Seção a redigir.)", destaque=True)
            contagem[nome] = 0
            continue
        texto = arq.read_text(encoding="utf-8")
        contagem[nome] = referencias(doc, texto) if nome == "referencias.md" \
            else converter_markdown(doc, texto, DIR_ARTIGO)
    declaracao_ia(doc)

    SAIDA.parent.mkdir(exist_ok=True)
    doc.save(str(SAIDA))
    total = sum(contagem.values())
    print(f"Gerado: {SAIDA}")
    for nome, n in contagem.items():
        print(f"  {nome:<28} {n:>6} palavras  (~{n / PALAVRAS_POR_PAGINA:.1f} p.)")
    print(f"  {'TOTAL (sem pré-textuais)':<28} {total:>6} palavras  (~{total / PALAVRAS_POR_PAGINA:.1f} p. "
          f"+ ~1,5 p. de título/resumo + figuras)")


if __name__ == "__main__":
    main()
