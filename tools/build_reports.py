#!/usr/bin/env python3
"""Build required TXT and supplementary PDFs from reviewed JSON.

python3 tools/build_reports.py
Dependency: reportlab (see requirements-docs.txt). Does not run benchmarks or Git.
"""
import json
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Table, TableStyle,
                               Spacer, PageBreak, Image, Flowable, Preformatted)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'docs/reports'
PAGE_W, PAGE_H = A4
WIDTH = PAGE_W - 84
BLUE = colors.HexColor('#183A60')
TEAL = colors.HexColor('#087F8C')
INK = colors.HexColor('#253044')
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='BodyR', fontName='Helvetica', fontSize=10,
    leading=14, spaceAfter=9, textColor=INK))
styles.add(ParagraphStyle(name='SmallR', parent=styles['BodyR'], fontSize=8.5,
    leading=11.5, spaceAfter=7))
styles.add(ParagraphStyle(name='CellR', parent=styles['BodyR'], fontSize=8.5,
    leading=11.4, spaceAfter=0))
styles.add(ParagraphStyle(name='TitleR', fontName='Helvetica-Bold', fontSize=24,
    leading=28, spaceAfter=14, textColor=BLUE))
styles.add(ParagraphStyle(name='HeadR', fontName='Helvetica-Bold', fontSize=17,
    leading=21, spaceAfter=12, textColor=BLUE))
styles.add(ParagraphStyle(name='LabelR', fontName='Helvetica-Bold', fontSize=8.5,
    leading=11, spaceAfter=8, textColor=TEAL))
styles.add(ParagraphStyle(name='CodeR', fontName='Courier', fontSize=8,
    leading=11, spaceAfter=10, backColor=colors.HexColor('#F3F6F9'),
    borderPadding=8))

def para(text, style='BodyR'):
    return Paragraph(escape(str(text)).replace('\n', '<br/>'), styles[style])

class Bars(Flowable):
    def __init__(self, block):
        super().__init__()
        self.block = block
        self.width = WIDTH
        self.height = block.get('height', 175)
    def draw(self):
        c = self.canv
        rows = self.block['rows']
        left, right = 158, self.width - 70
        top, bottom = self.height - 21, 27
        maxv = max(float(row[1]) for row in rows) * 1.06
        c.setFont('Helvetica', 8)
        c.setFillColor(colors.HexColor('#657184'))
        c.drawString(left, 6, self.block.get('unit', 'milliseconds (lower is better)'))
        for i, (name, value, kind) in enumerate(rows):
            y = top - i * (top-bottom) / max(1, len(rows)-1)
            c.setFillColor(TEAL if kind == 'selected' else (BLUE if kind == 'historical' else colors.HexColor('#98AABD')))
            c.roundRect(left, y-9, (right-left)*float(value)/maxv, 17, 3, stroke=0, fill=1)
            c.setFillColor(INK); c.setFont('Helvetica', 8.7)
            c.drawRightString(left-9, y-3, name)
            c.setFont('Helvetica-Bold', 8.7)
            c.drawString(left+(right-left)*float(value)/maxv+6, y-3, f'{float(value):.3f}')

class Architecture(Flowable):
    def __init__(self):
        super().__init__(); self.width=WIDTH; self.height=204
    def draw(self):
        c=self.canv
        boxes=[(0,139,153,49,['Python benchmark','native microkernel API']),
               (180,139,331,49,['CPU loop / proposed hardware bridge','many GEOM commands within a native call']),
               (0,51,153,62,['Operand bank: 8 x 64 bits','opcode + ready/valid','stable result + status']),
               (180,51,151,62,['GEOM sequencer','operand snapshots','micro-step + temporaries']),
               (357,51,154,62,['HardFloat datapath','FP64 add/sub, multiply','iterative div/sqrt'])]
        for x,y,w,h,lines in boxes:
            c.setFillColor(colors.HexColor('#EFF5F8'));c.setStrokeColor(colors.HexColor('#89A8BE'))
            c.roundRect(x,y,w,h,5,fill=1,stroke=1)
            c.setFillColor(INK);c.setFont('Helvetica',8.5)
            for i,line in enumerate(lines):c.drawCentredString(x+w/2,y+h-15-i*12,line)
        c.setStrokeColor(TEAL)
        for x1,y1,x2,y2 in [(154,163,178,163),(256,138,77,115),(154,81,178,81),(332,81,355,81)]:
            c.line(x1,y1,x2,y2)
            if y1==y2:c.line(x2,y2,x2-4,y2+3);c.line(x2,y2,x2-4,y2-3)
        c.setFont('Helvetica',8);c.setFillColor(INK)
        c.drawString(0,28,'Solid datapath boxes describe included RTL; CPU-to-device binding is proposed integration.')
        c.drawString(0,15,'Ordered operations round separately. One outstanding command; no FMA or DMA engine.')

def block_flows(block, plain):
    typ=block['type']
    if typ in ('p','small'):
        plain.extend([block['text'],''])
        return [para(block['text'], 'SmallR' if typ=='small' else 'BodyR')]
    if typ=='code':
        plain.extend([block['text'],''])
        return [Preformatted(block['text'],styles['CodeR'])]
    if typ=='table':
        rows=[[para(cell,'CellR') for cell in row] for row in block['rows']]
        widths=[WIDTH*x for x in block.get('widths',[1/len(rows[0])]*len(rows[0]))]
        table=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E4EDF4')),
            ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),
            ('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),
            ('BOTTOMPADDING',(0,0),(-1,-1),6),
            ('LINEBELOW',(0,0),(-1,0),.65,colors.HexColor('#89A8BE')),
            ('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#DDE4E9'))]))
        plain.extend([' | '.join(map(str,row)) for row in block['rows']]);plain.append('')
        return [table,Spacer(1,10)]
    if typ=='bars':
        plain.extend([block['caption']]+[f'{r[0]}: {r[1]:.6f}' for r in block['rows']]+[''])
        return [Bars(block),para(block['caption'],'SmallR')]
    if typ=='flames':
        images=[]
        for item in block['items']:
            image=Image(str(SOURCE/item['path']))
            factor=min((WIDTH-16)/2/image.imageWidth,block.get('max_height',225)/image.imageHeight)
            image.drawWidth=image.imageWidth*factor;image.drawHeight=image.imageHeight*factor
            images.append([para(item['label'],'SmallR'),image])
            plain.append(f"Flame graph: {item['original']}")
        table=Table([[images[0],images[1]]],colWidths=[WIDTH/2,WIDTH/2])
        table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),0)]))
        plain.extend([block['caption'],''])
        return [table,Spacer(1,6),para(block['caption'],'SmallR')]
    if typ=='links':
        flows=[]
        for label,path in block['items']:
            plain.append(f'{label}: {path}')
            flows.append(Paragraph(f'<link href="../../{escape(path)}" color="#087F8C">{escape(label)}</link>',styles['BodyR']))
        plain.append('')
        return flows
    if typ=='architecture':
        plain.extend(['Block diagram: Python -> native CPU loop -> proposed device bridge -> operand bank -> GEOM sequencer -> shared HardFloat add/sub, multiply and iterative div/sqrt -> result/status -> CPU.',
                      'Native calls and hardware commands are separate boundaries. See hardware/docs/HARDWARE_DESIGN.md and hardware/diagrams/.',''])
        return [Architecture()]
    raise ValueError(f'unknown report block: {typ}')

def build(bench):
    src=json.loads((SOURCE/f'{bench}_source.json').read_text())
    pdf=SOURCE/f'report_{bench}.pdf'
    plain=[src['title'],'HW/SW Co-design | Latest evidence reviewed 29 September 2026',
           f"Selected implementation: {src['kernel']}",'']
    story=[]
    for i,page in enumerate(src['pages']):
        if i:story.append(PageBreak())
        flows=[para(f"{bench.upper()} / {page['section']}",'LabelR'),
               para(page['title'],'TitleR' if i==0 else 'HeadR')]
        plain.extend([page['section'].upper(),page['title'],''])
        for block in page['blocks']:flows.extend(block_flows(block,plain))
        height=sum(f.wrap(WIDTH,PAGE_H)[1]+f.getSpaceBefore()+f.getSpaceAfter() for f in flows)
        if height>PAGE_H-108:raise ValueError(f'{bench} authored page {i+1} too tall ({height:.1f} pt)')
        story.extend(flows)
    def footer(c,doc):
        c.setStrokeColor(colors.HexColor('#DDE4E9'));c.line(42,39,PAGE_W-42,39)
        c.setFillColor(colors.HexColor('#657184'));c.setFont('Helvetica',8)
        c.drawString(42,26,f"HW/SW Co-design | {bench} | {src['kernel']} | 29 September 2026")
        c.drawRightString(PAGE_W-42,26,str(doc.page))
    doc=SimpleDocTemplate(str(pdf),pagesize=A4,leftMargin=42,rightMargin=42,
        topMargin=40,bottomMargin=53,title=src['title'],author='HW/SW Co-design project')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    (ROOT/f'report_{bench}.txt').write_text('\n'.join(plain)+'\n',encoding='utf-8')
    print(f'{bench}: {len(src["pages"])} authored pages -> {pdf}')

if __name__=='__main__':
    for benchmark in ('raytrace','nbody'):build(benchmark)
