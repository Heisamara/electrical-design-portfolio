import csv,json,unittest
from pathlib import Path
import ezdxf
from pypdf import PdfReader
OUT=Path(__file__).resolve().parents[2]/'downloads'
class DesignChecks(unittest.TestCase):
 def test_totals_and_currents(self):
  rows=list(csv.DictReader((OUT/'panel-schedule.csv').open()))
  self.assertEqual(len(rows),12);self.assertEqual(sum(int(r['Connected VA']) for r in rows),10020)
  phases={p:sum(int(r['Connected VA']) for r in rows if r['Phase']==p) for p in 'ABC'}
  self.assertEqual(phases,{'A':2640,'B':3840,'C':3540})
  for r in rows:self.assertAlmostEqual(float(r['Estimated A']),int(r['Connected VA'])/120,places=2)
  s=json.loads((OUT/'load-summary.json').read_text());self.assertEqual(s['phase_va'],phases)
 def test_inventory_coordination(self):
  rows=list(csv.DictReader((OUT/'device-inventory.csv').open()));self.assertEqual(len(rows),40)
  self.assertEqual(len({r['ID'] for r in rows}),40)
  for r in rows:
   self.assertTrue(0<=float(r['X ft'])<=40 and 0<=float(r['Y ft'])<=30)
   self.assertIn(int(r['Circuit']),range(1,13))
  for sheet,prefix in [('E-101','L'),('E-102','R')]:
   d=ezdxf.readfile(OUT/f'{sheet}.dxf');texts=[e.dxf.text for e in d.modelspace().query('TEXT')]
   for r in rows:
    if r['ID'].startswith(prefix):self.assertTrue(any(r['ID']+'/' in t or r['ID']+' /' in t for t in texts))
 def test_pdf_and_cad(self):
  pdf=PdfReader(OUT/'commercial-office-drawing-set.pdf');self.assertEqual(len(pdf.pages),5)
  for page in pdf.pages:self.assertIn('NOT FOR CONSTRUCTION',page.extract_text())
  for name in ['E-101','E-102','E-103','E-104']:
   d=ezdxf.readfile(OUT/f'{name}.dxf');self.assertEqual(d.units,2);self.assertFalse(d.audit().has_errors)
   for layer in ['A-WALLS','A-DOORS','E-LIGHTING','E-POWER','E-SWITCHES','E-CIRCUITS','E-TEXT']:self.assertIn(layer,d.layers)
if __name__=='__main__':unittest.main()
