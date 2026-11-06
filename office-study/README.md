# Commercial Office Electrical Design - Conceptual Study

A Python-generated drawing and calculation package for a fictitious 40 x 30 ft (1,200 sq. ft.) office. Conceptual design - not for construction. No code compliance or AutoCAD application proficiency is claimed.

## Deliverables

The downloads folder contains a five-sheet 17 x 11 in PDF set, E-101 through E-104 model-space DXF files, a panel CSV, device inventory CSV and calculation JSON. E-105 is the PDF design-basis and review sheet. DXF units are feet; verify a 40 x 30 unit perimeter after import. DXF is editable CAD exchange data, not a native DWG. Files have not yet been opened or reviewed in AutoCAD.

## Assumptions and calculations

- 15 luminaires at 40 VA = 600 VA; no manufacturer or photometric performance assumed.
- 20 duplex receptacle locations at an illustrative 180 VA each = 3,600 VA. This is a chosen sample allowance, not a verified OESC rule.
- Sample dedicated equipment: refrigerator 600 VA, microwave 1,500 VA, dishwasher 1,200 VA, 120 V HVAC terminal 2,400 VA and exhaust fan 120 VA.
- Total: 10,020 VA. Illustrative demand factor: 100%, not a code-derived selection.
- Assumed supply: 120/208 V, three-phase, four-wire wye; all branches 120 V line-to-neutral.
- Circuit positions 1/2=A, 3/4=B, 5/6=C, repeating. Phase totals A=2,640 VA, B=3,840 VA, C=3,540 VA; respective currents 22, 32 and 29.5 A. Allocation is unbalanced and requires review. No feeder is sized using an averaged three-phase current.
- Real kW, breaker and conductor sizes, service capacity, fault levels and compliance remain unverified.
- Excludes central HVAC, water heating, emergency systems, fire alarm, communications and future loads. This is not a complete service calculation.

## Reproduce

Python 3.9+; install dependencies from requirements.txt, then run `python src/generate.py` from this directory. Run `python src/test_design.py` to check calculated values, CAD integrity and output coordination. Outputs go to the repository downloads directory. PDF generation uses ReportLab, CAD generation uses ezdxf; PyMuPDF supports visual QA.

## Before claiming AutoCAD design work

Open all DXFs in AutoCAD, confirm feet units, inspect layers, check device/circuit labels, confirm clearances and room dimensions, create layouts/plot styles as needed and save reviewed DWGs. Review every design assumption and complete applicable code and engineering checks with qualified supervision. Record revisions and your design decisions.

Reference framework: https://esasafe.com/role/oesc/ and https://www.ontario.ca/laws/regulation/990164 . These links are provided for further review; no code clauses are applied in the sample calculations.
