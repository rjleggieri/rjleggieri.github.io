"""Check preservation and published-copy consistency for the document refresh."""
from pathlib import Path
import re
import hashlib
from pypdf import PdfReader
from PIL import Image
from generate_nli_report import MNLI_METRICS, MNLI_CLASSES, HANS

ROOT=Path(__file__).resolve().parents[1]
original=PdfReader(ROOT/'docs/archive/Making-DeBERTa-Smarter-original.pdf')
revised=PdfReader(ROOT/'output/pdf/Making-DeBERTa-Smarter.pdf')
resume=PdfReader(ROOT/'output/pdf/Robert-Leggieri-Resume.pdf')

def normalize(text):return re.sub(r'\s+','',text)
old_text=normalize(''.join(p.extract_text() or '' for p in original.pages))
new_text=normalize(''.join(p.extract_text() or '' for p in revised.pages[:-1]))
for row in MNLI_METRICS:
    assert normalize(''.join(row[1:])) in old_text, ('Original MNLI metric mismatch',row)
    assert normalize(''.join(row[1:])) in new_text, ('Revised MNLI metric mismatch',row)
for row in MNLI_CLASSES:
    expected=normalize(''.join(row[1:]))
    assert expected in old_text, ('Original class mismatch',row)
    assert expected in new_text, ('Revised class mismatch',row)
for row in HANS[:-1]:
    expected=normalize(''.join(row[1:]))
    assert expected in old_text, ('Original HANS mismatch',row)
    assert expected in new_text, ('Revised HANS mismatch',row)
assert '77.49%78.59%' in new_text

# The appendix is the original reference page, not a transcription of its errors.
assert original.pages[-1].get_contents().get_data()==revised.pages[-1].get_contents().get_data()
assert original.pages[-1].extract_text()==revised.pages[-1].extract_text()
original_image=original.pages[3].images[0].image.convert('RGB')
stored_image=Image.open(ROOT/'paper/figures/original-mnli-data-map.png').convert('RGB')
assert original_image.size==stored_image.size and original_image.tobytes()==stored_image.tobytes()
embedded=[image.image.convert('RGB') for page in revised.pages for image in page.images]
assert any(im.size==original_image.size and im.tobytes()==original_image.tobytes() for im in embedded)
assert len(resume.pages)==1, 'Resume must remain one page'
resume_text=normalize(resume.pages[0].extract_text())
assert 'APPLIEDAI&NLPDEVELOPMENT' in resume_text
assert 'TECHNOLOGYLEADERSHIP' not in resume_text
assert '80%sensitivity' not in resume_text
for name in ['Making-DeBERTa-Smarter.pdf','Robert-Leggieri-Resume.pdf']:
    copies=[ROOT/f'{folder}/{name}' for folder in ['docs','public/docs','output/pdf']]
    hashes={hashlib.sha256(p.read_bytes()).hexdigest() for p in copies}
    assert len(hashes)==1, ('Published document copies differ',name)
for folder in ['docs/archive','public/docs/archive']:
    p=ROOT/folder/'Making-DeBERTa-Smarter-original.pdf'
    assert p.read_bytes()==(ROOT/'docs/archive/Making-DeBERTa-Smarter-original.pdf').read_bytes()
print('PASS: all result rows, original figure pixels, bibliography facsimile, one-page resume, and published copies.')
