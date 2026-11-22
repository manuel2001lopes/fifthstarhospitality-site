#!/usr/bin/env python3
"""Gera os posts e stories da Fifth Star Hospitality no estilo B ("Livro de reservas").

Uso:  python3 fsh_ig.py post.json --out pasta/
O JSON descreve os slides (ver README.md nesta pasta). Gera <id>-1.jpg, <id>-2.jpg ...
e, se houver stories, <id>-story-1.jpg ...
Precisa de google-chrome e de Pillow. As fontes vêm do npm (@fontsource) e são
instaladas sozinhas em ~/.fsh-fonts na primeira vez.
"""
import argparse, html, json, os, subprocess, sys, tempfile, base64, mimetypes
from pathlib import Path

AQUI = Path(__file__).resolve().parent
FONT_DIR = Path.home() / '.fsh-fonts'

INK = '#1B1B1B'; PAPER = '#FAF7F0'; PAPER2 = '#F2ECE0'; CARD = '#FFFDF8'
GREY = '#5A554C'; BRICK = '#A8361F'; BRICK_L = '#E8A08A'; DOT = '#B3AC9E'; LINE = '#D6CDBB'
STAR = f'<svg width="34" height="34" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2l2.9 6.6 7.1.6-5.4 4.7 1.6 7-6.2-3.8-6.2 3.8 1.6-7L2 9.2l7.1-.6z" fill="{BRICK}"/></svg>'


def garantir_fontes():
    base = FONT_DIR / 'node_modules' / '@fontsource'
    if not (base / 'newsreader').exists() or not (base / 'ibm-plex-mono').exists():
        FONT_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.run(['npm', 'install', '--silent', '--prefix', str(FONT_DIR),
                        '@fontsource/newsreader', '@fontsource/ibm-plex-mono'], check=True)
    f = lambda p: f"url('file://{base}/{p}')"
    return f"""@font-face{{font-family:'Newsreader';font-weight:400;src:{f('newsreader/files/newsreader-latin-400-normal.woff2')}}}
@font-face{{font-family:'Newsreader';font-weight:500;src:{f('newsreader/files/newsreader-latin-500-normal.woff2')}}}
@font-face{{font-family:'Newsreader';font-weight:400;font-style:italic;src:{f('newsreader/files/newsreader-latin-400-italic.woff2')}}}
@font-face{{font-family:'Plex';font-weight:400;src:{f('ibm-plex-mono/files/ibm-plex-mono-latin-400-normal.woff2')}}}
@font-face{{font-family:'Plex';font-weight:500;src:{f('ibm-plex-mono/files/ibm-plex-mono-latin-500-normal.woff2')}}}"""


def e(s):
    return html.escape(str(s))


def tam(t, story=False):
    n = len(t)
    s = 112 if n <= 24 else 100 if n <= 40 else 88 if n <= 60 else 78 if n <= 85 else 68
    return s + (8 if story else 0)


def titulo(t, size=None, story=False):
    """A segunda frase do título fica em itálico tijolo."""
    size = size or tam(t, story)
    partes = t.split('. ', 1)
    if len(partes) == 2 and partes[1].strip():
        inner = f"{e(partes[0])}. <em style='color:{BRICK}'>{e(partes[1])}</em>"
    else:
        inner = e(t)
    return f"<h1 class='fit' style='margin:0;font-family:Newsreader;font-weight:400;font-size:{size}px;line-height:1.03;letter-spacing:-0.01em'>{inner}</h1>"


def para(t, size=36):
    return f"<p class='fit' style='margin:0;font-size:{size}px;line-height:1.45;color:{GREY};max-width:880px'>{e(t)}</p>"


def fonte(t):
    return f"<p style='margin:0;font-family:Plex;font-size:24px;line-height:1.4;color:{GREY}'>Fonte: {e(t)}</p>" if t else ''


def livro(linhas, total=None, size=28):
    r = ''.join(f"<div style='display:flex;justify-content:space-between;gap:24px;padding:20px 0;border-top:1px dashed {DOT}'><span>{e(a)}</span><span style='text-align:right'>{e(b)}</span></div>" for a, b in linhas)
    if total:
        r += f"<div style='display:flex;justify-content:space-between;gap:24px;padding:22px 0 0;border-top:3px solid {INK};font-weight:500'><span>{e(total[0])}</span><span style='color:{BRICK};text-align:right'>{e(total[1])}</span></div>"
    return f"<div style='border:1.5px solid {INK};background:{CARD};padding:16px 40px 36px;font-family:Plex;font-size:{size}px;line-height:1.4'>{r}</div>"


def passos(items):
    out = ''.join(f"<div style='display:flex;flex-direction:column;gap:12px;padding-top:28px;border-top:1px dashed {DOT}'><p style='margin:0;font-size:52px'><span style='font-family:Plex;font-size:40px;color:{BRICK};margin-right:18px'>{e(n)}</span>{e(h)}</p><p style='margin:0;font-size:33px;line-height:1.45;color:{GREY}'>{e(t)}</p></div>" for n, h, t in items)
    return f"<div style='display:flex;flex-direction:column;gap:36px'>{out}</div>"


def lista(items, marcar=False):
    out = ''
    for i, t in enumerate(items):
        m = (f"<span style='display:inline-block;width:34px;height:34px;border:2px solid {INK};margin-right:24px;position:relative;top:4px'></span>" if marcar
             else f"<span style='font-family:Plex;font-size:30px;color:{BRICK};margin-right:20px'>{i+1:02d}</span>")
        out += f"<div style='display:flex;align-items:baseline;padding:22px 0;border-top:1px dashed {DOT};font-size:40px;line-height:1.25'><span style='flex:none'>{m}</span><span>{e(t)}</span></div>"
    return f"<div>{out}</div>"


def grafico(barras, destaque=None, unidade=''):
    mx = max(float(v) for _, v, *_ in barras) or 1
    out = ''
    for i, b in enumerate(barras):
        lab, v = b[0], float(b[1]); disp = b[2] if len(b) > 2 else f"{b[1]}{unidade}"
        cor = BRICK if i == destaque else INK
        out += (f"<div style='display:grid;grid-template-columns:260px 1fr 150px;align-items:center;gap:20px;padding:14px 0;border-top:1px dashed {DOT}'>"
                f"<span style='font-family:Plex;font-size:26px'>{e(lab)}</span>"
                f"<span style='display:block;height:44px;width:{max(v/mx*100,1.5):.1f}%;background:{cor}'></span>"
                f"<span style='font-family:Plex;font-size:28px;text-align:right;color:{cor}'>{e(disp)}</span></div>")
    return f"<div style='border:1.5px solid {INK};background:{CARD};padding:20px 36px 28px'>{out}</div>"


def pesquisa(resultados, consulta):
    out = f"<div style='display:flex;align-items:center;gap:18px;border:1.5px solid {INK};padding:18px 26px;font-family:Plex;font-size:28px;background:#fff'><svg width='30' height='30' viewBox='0 0 24 24' fill='none' stroke='{GREY}' stroke-width='2'><circle cx='10' cy='10' r='7'/><path d='M15 15l6 6'/></svg>{e(consulta)}</div>"
    for r in resultados:
        tag = r.get('etiqueta', '')
        cor = BRICK if r.get('destaque') else INK
        out += (f"<div style='padding:22px 0;border-top:1px dashed {DOT}'>"
                f"<p style='margin:0 0 6px;font-family:Plex;font-size:22px;color:{GREY}'>{('<b style=\"color:'+INK+'\">'+e(tag)+'</b> · ') if tag else ''}{e(r.get('url',''))}</p>"
                f"<p style='margin:0;font-size:38px;color:{cor}'>{e(r['nome'])}</p>"
                f"{('<p style=\"margin:6px 0 0;font-family:Plex;font-size:26px;color:'+GREY+'\">'+e(r['detalhe'])+'</p>') if r.get('detalhe') else ''}</div>")
    return f"<div style='background:{CARD};border:1.5px solid {INK};padding:28px 36px 12px;display:flex;flex-direction:column;gap:14px'>{out}</div>"


def conversa(mensagens):
    out = ''
    for m in mensagens:
        hotel = m.get('de') == 'hotel'
        out += (f"<div style='display:flex;flex-direction:column;align-items:{'flex-end' if hotel else 'flex-start'};gap:6px'>"
                f"<div style='max-width:78%;padding:20px 26px;font-size:33px;line-height:1.35;background:{INK if hotel else '#fff'};color:{PAPER if hotel else INK};border:1.5px solid {INK}'>{e(m['texto'])}</div>"
                f"<span style='font-family:Plex;font-size:22px;color:{BRICK if m.get('alerta') else GREY}'>{e(m.get('hora',''))}</span></div>")
    return f"<div style='background:{PAPER2};border:1.5px solid {INK};padding:32px;display:flex;flex-direction:column;gap:22px'>{out}</div>"


def foto_src(nome):
    p = (AQUI / 'fotos' / nome) if not os.path.isabs(nome) else Path(nome)
    if not p.exists():
        sys.exit(f'Foto não encontrada: {p}')
    mt = mimetypes.guess_type(str(p))[0] or 'image/jpeg'
    return f"data:{mt};base64,{base64.b64encode(p.read_bytes()).decode()}"


def corpo(s, story):
    t = s.get('tipo', 'texto')
    tit = titulo(s['titulo'], s.get('tamanho'), story) if s.get('titulo') else ''
    txt = para(s['texto']) if s.get('texto') else ''
    if t in ('capa', 'texto', 'fecho'):
        return tit + txt
    if t == 'numero':
        big = f"<p style='margin:0;font-family:Newsreader;font-size:{300 if len(s['numero'])<=5 else 220}px;line-height:.9;color:{BRICK};letter-spacing:-0.03em'>{e(s['numero'])}</p>"
        return big + tit + txt + fonte(s.get('fonte'))
    if t == 'livro':
        return tit + livro(s['linhas'], s.get('total')) + txt + fonte(s.get('fonte'))
    if t == 'passos':
        return tit + passos(s['passos'])
    if t in ('lista', 'checklist'):
        return tit + lista(s['itens'], marcar=(t == 'checklist')) + txt
    if t == 'grafico':
        return tit + grafico(s['barras'], s.get('destaque'), s.get('unidade', '')) + txt + fonte(s.get('fonte'))
    if t == 'pesquisa':
        return tit + pesquisa(s['resultados'], s.get('consulta', '')) + txt
    if t == 'conversa':
        return tit + conversa(s['mensagens']) + txt
    if t == 'citacao':
        q = f"<p class='fit' style='margin:0;font-family:Newsreader;font-style:italic;font-size:{s.get('tamanho',76)}px;line-height:1.12'><span style='color:{BRICK}'>“</span>{e(s['citacao'])}<span style='color:{BRICK}'>”</span></p>"
        a = f"<p style='margin:0;font-family:Plex;font-size:26px;color:{GREY}'>{e(s['autor'])}</p>" if s.get('autor') else ''
        return q + a + txt
    if t == 'foto':
        h = 1000 if story else (640 if (s.get('titulo') and len(s['titulo']) > 40) else 720)
        img = f"<div style='border:1.5px solid {INK};background:{CARD};padding:16px'><div style='height:{h}px;background:url({foto_src(s['foto'])}) center/cover no-repeat'></div>{('<p style=\"margin:14px 0 0;font-family:Plex;font-size:22px;color:'+GREY+'\">'+e(s['legenda'])+'</p>') if s.get('legenda') else ''}</div>"
        return img + (titulo(s['titulo'], s.get('tamanho') or (64 if not story else 80), story) if s.get('titulo') else '') + txt
    sys.exit(f'Tipo de slide desconhecido: {t}')


FIT_JS = """<script>
(function(){const box=document.getElementById('meio');let k=0;
while(box.scrollHeight>box.clientHeight+2&&k<40){document.querySelectorAll('.fit').forEach(el=>{const fs=parseFloat(getComputedStyle(el).fontSize);el.style.fontSize=(fs*0.95)+'px'});k++}
document.body.setAttribute('data-fit',k);})();</script>"""


def pagina(fonts, w, h, bg, num, rotulo, body, rodape, pad):
    rot = f"<p style='margin:0;font-family:Plex;font-size:28px;color:{BRICK}'>{e(rotulo)}</p>" if rotulo else ''
    return f"""<!doctype html><html lang="pt-PT"><head><meta charset="utf-8"><style>{fonts}
html,body{{margin:0}}</style></head><body>
<div style="width:{w}px;height:{h}px;box-sizing:border-box;background:{bg};padding:{pad}px;display:flex;flex-direction:column;font-family:Newsreader;color:{INK}">
<div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:24px;border-bottom:2px solid {INK};flex:none">
<span style="display:flex;align-items:center;gap:14px;font-size:36px;font-weight:500">{STAR}Fifth Star Hospitality</span>
<span style="font-family:Plex;font-size:24px">{e(num)}</span></div>
<div id="meio" style="flex:1;min-height:0;overflow:hidden;display:flex;flex-direction:column;justify-content:center;gap:40px;padding:32px 0">{rot}{body}</div>
<div style="display:flex;justify-content:space-between;padding-top:24px;border-top:1px dashed {DOT};font-family:Plex;font-size:24px;color:{GREY};flex:none"><span>fifthstarhospitality.com</span><span>{e(rodape)}</span></div>
</div>{FIT_JS}</body></html>"""


def render(html_txt, w, h, destino):
    from PIL import Image
    with tempfile.TemporaryDirectory() as td:
        hp = Path(td) / 'p.html'; png = Path(td) / 'p.png'
        hp.write_text(html_txt, encoding='utf-8')
        subprocess.run(['google-chrome', '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
                        '--allow-file-access-from-files', '--force-device-scale-factor=1', f'--window-size={w},{h}',
                        '--virtual-time-budget=4000', f'--screenshot={png}', hp.as_uri()],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        Image.open(png).convert('RGB').crop((0, 0, w, h)).save(destino, 'JPEG', quality=92, optimize=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec'); ap.add_argument('--out', default='out')
    a = ap.parse_args()
    spec = json.loads(Path(a.spec).read_text(encoding='utf-8'))
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    fonts = garantir_fontes()
    pid = spec['id']; num = spec.get('numero', 'Fifth Star')
    feitos = []
    slides = spec.get('slides', [])
    for i, s in enumerate(slides):
        ult = i == len(slides) - 1
        bg = PAPER if (i == 0 or ult or s.get('tipo') == 'foto') else PAPER2
        rod = f"{i+1}/{len(slides)}" + ('' if ult else ' →') if len(slides) > 1 else ''
        dest = out / f'{pid}-{i+1}.jpg'
        render(pagina(fonts, 1080, 1350, bg, num, s.get('rotulo'), corpo(s, False), rod, 96), 1080, 1350, dest)
        feitos.append(str(dest))
    for i, s in enumerate(spec.get('stories', [])):
        dest = out / f'{pid}-story-{i+1}.jpg'
        html_s = pagina(fonts, 1080, 1920, PAPER, num, s.get('rotulo'), corpo(s, True), '', 110)
        html_s = html_s.replace('padding:110px', 'padding:240px 110px 280px', 1)
        render(html_s, 1080, 1920, dest)
        feitos.append(str(dest))
    print('\n'.join(feitos))


if __name__ == '__main__':
    main()
