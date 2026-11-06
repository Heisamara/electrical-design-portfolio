"""Reproducible conceptual drawings. All model-space DXF units are feet."""
from pathlib import Path
import csv, json, math, zipfile
import ezdxf
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'downloads'; OUT.mkdir(exist_ok=True)
INK='#143d39'; GRAY='#687973'
loads=[(1,'Lighting: open office',240,'L01-L06'),(2,'Open office receptacles',900,'R01-R05'),(3,'Lighting: reception + conference',240,'L07-L12'),(4,'Open office receptacles',900,'R06-R10'),(5,'Lighting: kitchen + washroom',120,'L13-L15'),(6,'Reception / conference receptacles',900,'R11-R15'),(7,'Kitchen / washroom receptacles',900,'R16-R20'),(8,'Refrigerator - assumed',600,'EQ01'),(9,'Microwave - assumed',1500,'EQ02'),(10,'Dishwasher - assumed',1200,'EQ03'),(11,'HVAC terminal - assumed 120 V',2400,'EQ04'),(12,'Washroom exhaust - assumed',120,'EQ05')]
def phase(n): return 'ABC'[((n-1)//2)%3]
def totals(rows):
    if any(x[2]<0 for x in rows): raise ValueError('Negative load')
    p={x:sum(r[2] for r in rows if phase(r[0])==x) for x in 'ABC'}
    return sum(p.values()),p
TOTAL,PHASES=totals(loads)
lights=[(5,5),(15,5),(25,5),(5,13),(15,13),(25,13),(3,22),(8,22),(13,22),(20,22),(25,22),(29,22),(34,23),(38,23),(36,16)]
receps=[(2,1),(8,1),(14,1),(20,1),(26,1),(1,5),(1,10),(1,15),(29,5),(29,12),(1,25),(8,29),(13,29),(21,29),(28,29),(32,29),(36,29),(39,26),(39,21),(39,13)]
switches=[(9,19,'S1 / C1'),(9,20,'S2 / C3'),(22,20,'S3 / C3'),(32,20,'S4 / C5'),(32,13,'S5 / C5')]
equip=[(33,27,'EQ01',8),(36,27,'EQ02',9),(38,24,'EQ03',10),(23,9,'EQ04',11),(38,16,'EQ05',12)]
# Shared geometric primitives drive both PDF and DXF; diagrams are coordinated.
class Draw:
    def __init__(self,c,m): self.c=c;self.m=m
    def line(self,a,b,layer='A-WALLS',color=INK,dash=False):
        self.c.setStrokeColor(HexColor(color));self.c.setLineWidth(1 if layer=='A-WALLS' else .65);self.c.setDash([3,3] if dash else [])
        self.c.line(65+a[0]*17,160+a[1]*17,65+b[0]*17,160+b[1]*17); self.c.setDash([])
        self.m.add_line(a,b,dxfattribs={'layer':layer})
    def text(self,x,y,s,size=8,layer='E-TEXT'):
        self.c.setFillColor(HexColor(GRAY));self.c.setFont('Helvetica',size);self.c.drawString(65+x*17,160+y*17,s)
        self.m.add_text(s,dxfattribs={'height':size/17,'layer':layer,'insert':(x,y)})
    def rect(self,x,y,w,h,layer='E-LIGHTING'):
        for a,b in [((x,y),(x+w,y)),((x+w,y),(x+w,y+h)),((x+w,y+h),(x,y+h)),((x,y+h),(x,y))]:self.line(a,b,layer)
    def circle(self,x,y,r,layer='E-POWER'):
        self.c.setStrokeColor(HexColor(INK)); self.c.circle(65+x*17,160+y*17,r*17,stroke=1,fill=0)
        self.m.add_circle((x,y),r,dxfattribs={'layer':layer})
def base(d):
    for a,b in [((0,0),(16,0)),((20,0),(40,0)),((40,0),(40,30)),((40,30),(0,30)),((0,30),(0,0)),((0,18),(8,18)),((11,18),(18,18)),((18,18),(18,30)),((18,18),(21,18)),((24,18),(30,18)),((30,0),(30,10)),((30,13),(30,18)),((30,18),(30,30)),((30,12),(40,12))]:d.line(a,b)
    for x,y in [(16,0),(8,18),(21,18),(30,10)]:
        d.line((x,y),(x,y+3),'A-DOORS');d.line((x,y+3),(x+3,y),'A-DOORS',dash=True)
    d.line((32,18),(32,21),'A-DOORS');d.line((32,21),(35,18),'A-DOORS',dash=True)
    # Kitchen opening is in the horizontal wall.
    for a,b in [((30,18),(32,18)),((35,18),(40,18))]:d.line(a,b)
    for x,y,s in [(1,29.2,'RECEPTION | 18 x 12 ft'),(19,29.2,'CONFERENCE | 12 x 12 ft'),(31,29.2,'KITCHEN | 10 x 12 ft'),(31,17.5,'WASHROOM | 10 x 6 ft'),(3,16,'OPEN OFFICE | 30 x 18 ft'),(31,4,'CIRCULATION / PANEL')]:d.text(x,y,s,7)
    d.rect(38,3,1,2,'E-POWER');d.text(34,2,'LP-1',8)
    d.line((0,31),(40,31),'E-TEXT');d.text(17,31.2,'40 ft',9);d.text(-2,14,'30 ft',8)
    d.text(0,-3,'MODEL: 1 unit = 1 ft | Print scale 17 pt/ft at 17 x 11 in | Dimensioned geometry governs',8)
    d.line((0,-1.2),(10,-1.2),'E-TEXT');d.text(0,-1.9,'0',8);d.text(9,-1.9,'10 ft',8)
def light(d,x,y):
    d.rect(x-.8,y-.25,1.6,.5);d.line((x-.8,y-.25),(x+.8,y+.25),'E-LIGHTING');d.line((x-.8,y+.25),(x+.8,y-.25),'E-LIGHTING')
def rec(d,x,y):
    d.circle(x,y,.22);d.line((x-.08,y-.3),(x-.08,y+.3),'E-POWER');d.line((x+.08,y-.3),(x+.08,y+.3),'E-POWER')
W,H=1224,792;c=canvas.Canvas(str(OUT/'commercial-office-drawing-set.pdf'),pagesize=(W,H));c.setTitle('Commercial Office - Conceptual Electrical Design')
def page(code,title):
    c.setStrokeColor(HexColor(INK));c.rect(28,28,W-56,H-56)
    c.setFillColor(HexColor(INK));c.setFont('Helvetica-Bold',19);c.drawString(50,735,title)
    c.setFont('Helvetica',10);c.drawString(50,714,'AMARACHI | COMMERCIAL OFFICE STUDY | 1,200 SQ. FT. | REV 01 | 2026-11-06')
    c.line(28,85,W-28,85);c.setFont('Helvetica-Bold',12);c.drawString(50,61,'CONCEPTUAL DESIGN - NOT FOR CONSTRUCTION')
    c.setFont('Helvetica',8);c.drawString(50,43,'Python-generated portfolio study. Not reviewed in AutoCAD; no code compliance, professional seal, or permit suitability claimed.')
    c.setFont('Helvetica-Bold',22);c.drawRightString(W-48,53,code)
    doc=ezdxf.new('R2010');doc.units=2
    for name,col in [('A-WALLS',7),('A-DOORS',8),('E-LIGHTING',3),('E-POWER',4),('E-SWITCHES',2),('E-CIRCUITS',6),('E-TEXT',7)]:doc.layers.new(name,dxfattribs={'color':col})
    m=doc.modelspace();m.add_text('CONCEPTUAL DESIGN - NOT FOR CONSTRUCTION',dxfattribs={'insert':(0,37),'height':.6,'layer':'E-TEXT'})
    return doc,Draw(c,m)
def notes(lines,x=820,y=675):
    for line in lines:
        c.setFillColor(HexColor(INK));c.setFont('Helvetica',9);c.drawString(x,y,line);y-=18
for code,title in [('E-101','LIGHTING & SWITCHING PLAN'),('E-102','POWER & CIRCUIT IDENTIFICATION PLAN')]:
    doc,d=page(code,title);base(d)
    if code=='E-101':
        for i,(x,y) in enumerate(lights,1):
            light(d,x,y);n=1 if i<=6 else 3 if i<=12 else 5;d.text(x-.8,y+.65,f'L{i:02} / {n}',7)
        for x,y,s in switches:d.circle(x,y,.25,'E-SWITCHES');d.text(x+.4,y,s,7,'E-SWITCHES')
        for points in [[(9,19),(5,13),(15,13),(25,13),(25,5),(15,5),(5,5)],[(9,20),(3,22),(8,22),(13,22)],[(22,20),(20,22),(25,22),(29,22)],[(32,20),(34,23),(38,23)],[(32,13),(36,16)]]:
            for a,b in zip(points,points[1:]):d.line(a,b,'E-CIRCUITS',dash=True)
        notes(['DESIGN BASIS','15 illustrative LED fixtures at 40 VA each.','Lighting connected load: 600 VA.','C1: open office, 6 fixtures, 240 VA.','C3: reception + conference, 6, 240 VA.','C5: kitchen + washroom, 3, 120 VA.','','Dashed paths show control associations,','not cable routes or conduit quantities.','S1: open office; S2: reception;','S3: conference; S4: kitchen; S5: washroom.','','TO VERIFY','Fixture photometry, task illuminance, glare,','ceiling coordination and energy controls.','Emergency lighting, exit signs and egress','requirements are not designed in this set.','Switch locations / accessibility to be reviewed.'])
    else:
        for i,(x,y) in enumerate(receps,1):
            rec(d,x,y);n=2 if i<=5 else 4 if i<=10 else 6 if i<=15 else 7;d.text(x-.5,y-.9 if y==29 else y+.65,f'R{i:02}/{n}',7)
        for x,y,s,n in equip:d.rect(x-.4,y-.4,.8,.8,'E-POWER');d.text(x-1,y-1.1,f'{s}/{n}',7)
        notes(['DESIGN BASIS','20 duplex receptacle locations.','Illustrative allowance: 180 VA/location.','C2: R01-R05; C4: R06-R10.','C6: R11-R15; C7: R16-R20.','Device tags show ID / circuit number.','','Dedicated equipment is located conceptually.','EQ01 refrigerator: 600 VA.','EQ02 microwave: 1,500 VA.','EQ03 dishwasher: 1,200 VA.','EQ04 HVAC terminal: 2,400 VA, 120 V.','EQ05 exhaust fan: 120 VA.','','TO VERIFY','Actual nameplate ratings and supply voltage.','Wet-area protection, mounting, accessibility,','receptacle spacing and circuit requirements.','Panel access / working clearances and feeder','route require architectural coordination.'])
    doc.saveas(OUT/f'{code}.dxf');c.showPage()
doc,d=page('E-103','PRELIMINARY PANEL SCHEDULE & LOAD SUMMARY')
notes(['LP-1 | Assumed 120/208 V, 3-phase, 4-wire wye | All listed branches are assumed 120 V line-to-neutral.', '12 conceptual single-pole circuit positions. No breaker, conductor, bus rating or feeder size selected.'],50,680)
headers=['CIRCUIT','PHASE','DESCRIPTION','DEVICE IDS','CONNECTED VA','EST. A @ 120 V'];xs=[50,115,180,510,690,825];y=620
for x,s in zip(xs,headers):c.setFont('Helvetica-Bold',9);c.drawString(x,y,s)
y-=25
for n,desc,va,devices in loads:
    for x,s in zip(xs,[str(n),phase(n),desc,devices,str(va),f'{va/120:.2f}']):c.setFont('Helvetica',10);c.drawString(x,y,s)
    c.setStrokeColor(HexColor('#cdd4cb'));c.line(50,y-9,970,y-9);y-=27
notes([f'Total connected load: {TOTAL:,} VA = {TOTAL/1000:.2f} kVA. Illustrative demand factor: 100%; demand: {TOTAL:,} VA.',f'Phase A: {PHASES["A"]:,} VA / {PHASES["A"]/120:.1f} A | B: {PHASES["B"]:,} VA / {PHASES["B"]/120:.1f} A | C: {PHASES["C"]:,} VA / {PHASES["C"]/120:.1f} A','Phase allocation is preliminary and unbalanced. Maximum phase current = 32.0 A; rebalancing remains open.','Do not use S / (sqrt(3) x 208 V) as the design current for this unbalanced schedule.','Apparent power (VA) is used directly. Real power (kW) cannot be inferred without equipment power factors.','Excluded / unconfirmed: central HVAC, water heating, emergency systems, communications and future loads.','This is a partial tenant-load study, not a completed service calculation. No spare or growth allowance included.'],50,230)
for i,(n,desc,va,dev) in enumerate(loads):doc.modelspace().add_text(str((n,phase(n),desc,va)),dxfattribs={'insert':(0,30-i),'height':.45,'layer':'E-TEXT'})
doc.saveas(OUT/'E-103.dxf');c.showPage()
doc,d=page('E-104','ELECTRICAL LEGEND & DEVICE SCHEDULE')
light(d,2,28);d.text(5,28,'Lxx: illustrative LED luminaire, 40 VA each',11)
rec(d,2,25);d.text(5,25,'Rxx: duplex receptacle, 180 VA assumed per location',11)
d.circle(2,22,.25,'E-SWITCHES');d.text(5,22,'Sx: local lighting switch / control point',11)
d.rect(1.5,18.5,1,1,'E-POWER');d.text(5,19,'EQxx: dedicated equipment location (diagrammatic)',11)
d.rect(1.5,15,1,2,'E-POWER');d.text(5,16,'LP-1: conceptual panel location',11)
d.line((1,12),(4,12),'E-CIRCUITS',dash=True);d.text(5,12,'Dashed: switching association; DXF layer E-CIRCUITS',11)
notes(['DEVICE INVENTORY','L01-L15: 15 fixtures / 600 VA.','R01-R20: 20 locations / 3,600 VA.','S1-S5: 5 control points / no added load.','EQ01-EQ05: 5 items / 5,820 VA.','LP-1: 1 panel / loads tabulated on E-103.','','DXF LAYERS','A-WALLS, A-DOORS','E-LIGHTING, E-POWER','E-SWITCHES, E-CIRCUITS, E-TEXT','','UNITS & USE','DXF model-space units: feet (INSUNITS=2).','Open in AutoCAD and verify 40 x 30 ft.','Model-space annotations are provided.','No native DWG, layouts, or plot styles included.','DXF sheets use the same floor coordinates.'])
doc.saveas(OUT/'E-104.dxf');c.showPage()
doc,d=page('E-105','DESIGN BASIS, REVIEW ITEMS & METHODOLOGY')
notes(['01 / SCENARIO & BOUNDARY','Fictitious 40 x 30 ft commercial office. Architectural geometry is generated for this study, not surveyed.','Reception: 216 sq. ft.; conference: 144; kitchen: 120; washroom: 60; circulation: 120; open office: 540.','A single 120/208 V wye panel is assumed. Utility supply and base-building distribution are unverified.','','02 / CALCULATION METHOD','Connected VA = sum of device quantities x assumed VA per device, plus dedicated equipment VA.','Demand VA = connected VA x user-configured factor (1.00 in this study; not a prescribed code factor).','Branch current = branch VA / 120 V. Phase current = sum of line-to-neutral branch VA on that phase / 120 V.','Circuit numbering convention: positions 1/2=A, 3/4=B, 5/6=C, repeating. All loads assumed single pole.','','03 / OPEN ENGINEERING REVIEW ITEMS','Verify occupancy and applicable OESC rules, demand factors, continuous loads, loading and circuit limits.','Confirm equipment nameplates, protection, conductor ampacity, derating, voltage drop, bonding and grounding.','Review fault levels, interrupting ratings, coordination, feeder capacity, neutral loading and harmonics.','Coordinate exits, emergency lighting, fire alarm, accessibility, ceiling services and wet-location protection.','Establish measured photometric performance and lighting control / energy requirements.','Complete circuit rebalancing, tenant/base-building scope, spare capacity and architectural coordination.','','04 / AUTHORSHIP & VALIDATION','Created with Python, ezdxf and ReportLab using documented sample assumptions. Automated checks verify','device counts, unique identifiers, load totals, phase totals, PDF page count and DXF file integrity.','No independent engineering review or AutoCAD application review has been completed.','','05 / REFERENCE FOR SUBSEQUENT CODE REVIEW','Electrical Safety Authority - Ontario Electrical Safety Code information: https://esasafe.com/role/oesc/','Ontario regulation: https://www.ontario.ca/laws/regulation/990164','These references identify the review framework; no clauses or code-derived sizing rules are applied here.'],50,680)
c.save()
with (OUT/'panel-schedule.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['Circuit','Phase','Description','Device IDs','Connected VA','Demand factor','Demand VA','Branch V','Estimated A','Breaker','Conductor'])
    for n,desc,va,dev in loads:w.writerow([n,phase(n),desc,dev,va,1,va,120,round(va/120,3),'Requires review','Requires review'])
(OUT/'load-summary.json').write_text(json.dumps({'status':'CONCEPTUAL - NOT FOR CONSTRUCTION','connected_va':TOTAL,'demand_factor':1,'demand_va':TOTAL,'phase_va':PHASES,'phase_current_a':{p:v/120 for p,v in PHASES.items()},'equipment_assumptions':loads},indent=2))
# A device coordinate table also supports future BIM data work.
with (OUT/'device-inventory.csv').open('w',newline='') as f:
    w=csv.writer(f);w.writerow(['ID','Type','X ft','Y ft','Circuit'])
    for i,(x,y) in enumerate(lights,1):w.writerow([f'L{i:02}','LED',x,y,1 if i<=6 else 3 if i<=12 else 5])
    for i,(x,y) in enumerate(receps,1):w.writerow([f'R{i:02}','Duplex',x,y,2 if i<=5 else 4 if i<=10 else 6 if i<=15 else 7])
    for x,y,name,n in equip:w.writerow([name,'Equipment',x,y,n])
print('Generated',TOTAL,PHASES)
