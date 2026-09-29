#!/usr/bin/env python3
"""Static report previews of existing FlameGraph SVG frame rectangles/text.

Does not regenerate or change sampled data or original SVGs. The SVG title and
interactive UI are omitted; labels and sampling caveats are in the report.
Requires Pillow. All plot coordinates/colours come from the saved SVG frames.
"""
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/reports/assets'
NS = '{http://www.w3.org/2000/svg}'

def render(source, dest):
    svg = ET.parse(source).getroot()
    frames = next(e for e in svg.iter() if e.get('id') == 'frames')
    rects = list(frames.iter(NS + 'rect'))
    top = min(float(r.get('y')) for r in rects) - 6
    bottom = max(float(r.get('y')) + float(r.get('height')) for r in rects) + 6
    img = Image.new('RGB', (int(float(svg.get('width'))), int(bottom-top+1)), '#fffef5')
    draw = ImageDraw.Draw(img)
    fonts = ['/System/Library/Fonts/Supplemental/Arial.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
    font = next((ImageFont.truetype(p,12) for p in fonts if Path(p).exists()), ImageFont.load_default())
    for g in frames:
        for e in g:
            if e.tag == NS+'rect':
                x,y,w,h=[float(e.get(k)) for k in ('x','y','width','height')]
                draw.rectangle((x,y-top,x+w,y+h-top),fill=e.get('fill','#f5bd53'),outline='#fffef5',width=1)
            elif e.tag == NS+'text' and e.text:
                x,y=float(e.get('x')),float(e.get('y'))
                draw.text((x,y-top),e.text,font=font,fill='#171717',anchor='ls')
    img.save(dest)
    print(dest.relative_to(ROOT),img.size)

if __name__=='__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for bench in ('raytrace','nbody'):
        for variant in ('baseline','optimized'):
            source=ROOT/f'results/latest_{bench}_{variant}/flame/{variant}.svg'
            render(source,OUT/f'{bench}_{variant}_flame.png')
