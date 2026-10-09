from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path
import csv
BASE=Path(__file__).resolve().parent

def shade(cell, fill='203957'):
    tcPr=cell._tc.get_or_add_tcPr(); shd=OxmlElement('w:shd'); shd.set(qn('w:fill'),fill); tcPr.append(shd)
def set_cell_text(cell,text,bold=False,color=None,size=8):
    cell.text=''; p=cell.paragraphs[0]; p.paragraph_format.space_after=Pt(0)
    r=p.add_run(str(text)); r.bold=bold; r.font.size=Pt(size)
    if color: r.font.color.rgb=RGBColor(*color)

def table(doc, headers, rows, widths=None, fontsize=8):
    t=doc.add_table(rows=1, cols=len(headers)); t.style='Table Grid'
    for i,h in enumerate(headers): shade(t.rows[0].cells[i]); set_cell_text(t.rows[0].cells[i],h,True,(255,255,255),fontsize)
    for ri,row in enumerate(rows):
        cells=t.add_row().cells
        for i,v in enumerate(row):
            if ri%2==1: shade(cells[i],'EDF3F8')
            set_cell_text(cells[i],v,False,None,fontsize)
    if widths:
        for row in t.rows:
            for i,w in enumerate(widths): row.cells[i].width=Inches(w)
    doc.add_paragraph().paragraph_format.space_after=Pt(1)
    return t

doc=Document(); sec=doc.sections[0]; sec.top_margin=Inches(.55); sec.bottom_margin=Inches(.55); sec.left_margin=Inches(.6); sec.right_margin=Inches(.6)
styles=doc.styles; styles['Normal'].font.name='Aptos'; styles['Normal'].font.size=Pt(9); styles['Normal'].font.color.rgb=RGBColor(39,53,73)
for sty in ['Title','Heading 1','Heading 2','Heading 3']:
 styles[sty].font.name='Aptos Display'; styles[sty].font.color.rgb=RGBColor(31,77,105)
styles['Heading 1'].font.size=Pt(18); styles['Heading 2'].font.size=Pt(13); styles['Heading 3'].font.size=Pt(10)

p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run('SECUREVAULT'); r.bold=True; r.font.size=Pt(28); r.font.color.rgb=RGBColor(25,126,133)
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run('Software Requirements, Test Matrix & Test Summary Report'); r.bold=True; r.font.size=Pt(16); r.font.color.rgb=RGBColor(39,62,101)
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
p.add_run('School of Computer Science Engineering and Information Systems\nFall Semester 2026–2027 · ISWE305P Software Testing\nVIT Vellore · Version 1.0 · 9 October 2026')
doc.add_paragraph('Prepared as a project documentation template. Replace the cover-page team/student details and attach your own application and performance-tool screenshots before submission.')
doc.add_heading('1. Project Overview',1)
doc.add_paragraph('SecureVault is a Flask-based cybersecurity web application for authenticated file encryption and decryption. It provides AES-256-GCM, ECC/ECDH-derived AES-GCM, and Hybrid AES–ECC workflows. The application supports registration/login, uploads and downloads, SHA-256 integrity checks, operation history, and a modern responsive dashboard.')
doc.add_heading('2. Problem Statement',1)
doc.add_paragraph('Files transferred or stored without encryption may expose confidential information. A useful educational solution should demonstrate authenticated encryption, key agreement, safe key protection, integrity verification, controlled error handling and measurable performance. The project addresses this need by comparing standalone password-derived AES, an ECC/ECDH-based key agreement workflow, and a hybrid workflow that separates file encryption from key protection.')
doc.add_heading('3. Scope and Proposed Solution',1)
doc.add_paragraph('The user signs in, selects an encryption strategy, uploads a file, enters a password and downloads a SecureVault container. During decryption, the application identifies the stored strategy, derives or unwraps the required key, verifies the GCM authentication tag and checks the recovered SHA-256 digest before returning the original bytes. Operation metadata is saved per user. The application is a coursework prototype, not a certified production security product.')
doc.add_heading('4. Six Application Modules',1)
table(doc,['ID','Module','Responsibilities'],[
('M1','User Authentication','Register, password hashing, login/session, protected routes.'),('M2','AES Encryption/Decryption','Scrypt key derivation, AES-256-GCM, password verification.'),('M3','ECC Key Management','P-256 ECDH, HKDF, private-key protection inside container.'),('M4','Hybrid AES–ECC','Random AES data key, AES-GCM file encryption, ECDH-derived key wrapping.'),('M5','File Management','Upload, validate, encrypt/decrypt and download files; size limit.'),('M6','Encryption History','Record operation, algorithm, file name/size, elapsed time, status and digest.')],fontsize=8)
doc.add_heading('5. Software Requirements Summary',1)
doc.add_paragraph('Functional requirements: FR-01 registration; FR-02 login/access control; FR-03 upload validation; FR-04 AES-GCM; FR-05 ECC/ECDH mode; FR-06 hybrid mode; FR-07 metadata and SHA-256; FR-08 strategy-aware decryption; FR-09 wrong-password/corruption rejection; FR-10 digest verification; FR-11 browser downloads; FR-12 operation logging; FR-13 key-management explanations; FR-14 size-limit handling. Non-functional requirements cover security, integrity, usability, performance, reliability, compatibility, auditability and maintainability.')
doc.add_heading('6. Screen Design Inventory',1)
table(doc,['Screen','Primary controls / expected behavior'],[
('Authentication','Username/password form; registration and sign-in; invalid credentials show clear feedback.'),('Overview dashboard','Navigation to all strategies, hybrid feature card, stats and recent activity.'),('AES encryption','File drop/browse, password/confirmation, encryption action and .svlt download.'),('ECC encryption','File upload, password-protected key container, ECDH-based workflow.'),('Hybrid AES–ECC','File upload, password/confirmation, random AES key and ECC-based key wrapping.'),('Decryption','Encrypted file upload, password, automatic strategy detection and verified download.'),('Key management','Explains scrypt, ECDH, HKDF, AES-GCM and the hybrid workflow.'),('File activity / audit history','Shows operation status, algorithm, file metadata, elapsed time and digest.')],fontsize=8)
doc.add_heading('7. Requirements Traceability Matrix (RTM)',1)
rtm=[('FR-01','Registration and validation','BB-01, WEB-01','User account created or validation message'),('FR-02','Protected routes/login','BB-02, WEB-02','Unauthenticated dashboard redirects to login'),('FR-03','Upload required','BB-03','Missing file rejected'),('FR-04','AES-256-GCM','CR-01–CR-04','Round-trip and integrity pass'),('FR-05','ECC/ECDH workflow','CR-05–CR-08','Round-trip and integrity pass'),('FR-06','Hybrid key wrapping','CR-09–CR-12','Round-trip and integrity pass'),('FR-07','Metadata + digest','CR-13','Digest recorded and compared'),('FR-08','Strategy-aware decryption','CR-01–CR-12','Correct strategy detected from container'),('FR-09','Wrong password/tampering','CR-14–CR-17','Invalid input rejected'),('FR-10','SHA-256 equality','CR-01–CR-12','Recovered bytes match source digest'),('FR-11','Download result','WEB-03','HTTP attachment returned'),('FR-12','Audit history','WEB-04','Operation record visible in history'),('FR-13','Key-management screen','UI-01','Key details page renders'),('FR-14','Upload size limit','BB-04','Oversized upload receives readable error')]
table(doc,['Requirement','Requirement summary','Mapped tests','Expected verification'],rtm,fontsize=7)
doc.add_heading('8. Black-Box Test Matrix and Actual Results',1)
doc.add_paragraph('The following results are actual results from the cryptographic unit-test run executed in the build environment. Web-route tests are included in the ZIP but were not executed in this environment because Flask was not installed and package downloads were unavailable. Run the complete suite on your computer after installing requirements and update the WEB/UI rows with observed results.')
rows=[
('CR-01','AES encrypt/decrypt; short text','Valid bytes + valid password','Original bytes recovered; digest matches','Round-trip recovered original bytes; digest matched','PASS'),
('CR-02','AES empty-file boundary','Zero bytes + valid password','Empty output recovered; digest matches','Empty bytes recovered; digest matched','PASS'),
('CR-03','AES binary input','256-byte pattern repeated 16 times','Binary bytes preserved exactly','4096-byte binary payload recovered exactly','PASS'),
('CR-04','AES arbitrary binary','Null, high-bit bytes and newline','Binary bytes preserved exactly','Binary payload recovered exactly','PASS'),
('CR-05','ECC short text round-trip','Valid bytes + valid password','Original bytes recovered; digest matches','Round-trip recovered original bytes; digest matched','PASS'),
('CR-06','ECC empty-file boundary','Zero bytes + valid password','Empty output recovered; digest matches','Empty bytes recovered; digest matched','PASS'),
('CR-07','ECC binary input','256-byte pattern repeated 16 times','Binary bytes preserved exactly','4096-byte binary payload recovered exactly','PASS'),
('CR-08','ECC arbitrary binary','Null, high-bit bytes and newline','Binary bytes preserved exactly','Binary payload recovered exactly','PASS'),
('CR-09','Hybrid short text round-trip','Valid bytes + valid password','Original bytes recovered; digest matches','Round-trip recovered original bytes; digest matched','PASS'),
('CR-10','Hybrid empty-file boundary','Zero bytes + valid password','Empty output recovered; digest matches','Empty bytes recovered; digest matched','PASS'),
('CR-11','Hybrid binary input','256-byte pattern repeated 16 times','Binary bytes preserved exactly','4096-byte binary payload recovered exactly','PASS'),
('CR-12','Hybrid arbitrary binary','Null, high-bit bytes and newline','Binary bytes preserved exactly','Binary payload recovered exactly','PASS'),
('CR-13','Digest and strategy metadata','Encrypt then decrypt','Digest and algorithm preserved','Digest matched; reported algorithm matched','PASS'),
('CR-14','Wrong AES password','Valid container + wrong password','Decryption rejected','ValueError raised; no plaintext returned','PASS'),
('CR-15','Wrong password for all modes','AES, ECC and Hybrid containers','Each mode rejects wrong password','All three modes raised ValueError','PASS'),
('CR-16','Tampered ciphertext','Flip one ciphertext bit','Authentication/integrity error','Decryption rejected damaged ciphertext','PASS'),
('CR-17','Invalid encrypted header','Plain text instead of .svlt','Invalid format rejected','ValueError raised for invalid header','PASS'),
('CR-18','Truncated metadata','Truncated container bytes','Malformed input rejected','ValueError raised for incomplete header','PASS'),
('CR-19','Algorithm/metadata mismatch','AES container metadata changed to Hybrid','Incompatible strategy rejected','ValueError raised for incompatible metadata','PASS'),
('CR-20','Missing encryption password','Empty password','Encryption rejected','ValueError raised; password required','PASS'),
('CR-21','Cross-strategy recovery','Each algorithm uses its own metadata','Matching workflow recovers original','12 parameterized round-trips passed across modes and payloads','PASS'),
('WEB-01','Register/login and dashboard','Valid registration; invalid login','Workspace opens; invalid login rejected','NOT RUN in build environment: Flask unavailable','PENDING'),
('WEB-02','Authentication route guard','Request dashboard while signed out','Redirect to login','NOT RUN in build environment: Flask unavailable','PENDING'),
('WEB-03','Upload/encrypt/download/decrypt','Upload file through browser routes','Encrypted download then original recovered','NOT RUN in build environment: Flask unavailable','PENDING'),
('WEB-04','Audit history display','Perform operation then open history','Event appears with status/time','NOT RUN in build environment: Flask unavailable','PENDING'),
('UI-01','Responsive screen review','Desktop and mobile browser sizes','Navigation and controls remain usable','MANUAL TEST REQUIRED','PENDING'),
('BB-04','100 MB request-size limit','Upload above configured cap','Readable size-limit message','MANUAL TEST REQUIRED','PENDING')]
table(doc,['Test ID','Test case','Input / action','Expected output','Actual output','Status'],rows,fontsize=6)
doc.add_heading('9. Unit Test Results',1)
doc.add_paragraph('Executed command: `python -m pytest tests/test_crypto_engine.py -q`. Actual output: `21 passed in 1.45s`. These tests cover all three encryption strategies, text/binary/empty payloads, wrong passwords, corrupted ciphertext, invalid headers, truncated containers, metadata/strategy mismatch and missing password.')
doc.add_picture(str(BASE/'docs'/'test_results_pie.png'),width=Inches(4.7))
doc.paragraphs[-1].alignment=WD_ALIGN_PARAGRAPH.CENTER
doc.add_heading('10. Non-Functional Performance Results',1)
doc.add_paragraph('A local microbenchmark was executed against the cryptographic service using random payloads of 1 KiB, 100 KiB and 1 MiB. Each algorithm/size pair was run three times; average encryption and decryption times are shown below. All recovered payloads matched the original bytes. These are cryptographic microbenchmark measurements, not a concurrent HTTP load test. Values depend on the machine and installed libraries.')
with open(BASE/'benchmark_results.csv',newline='') as f: bench=list(csv.DictReader(f))
bench_rows=[]
for r in bench: bench_rows.append((r['Algorithm'],r['Input bytes'],r['Encrypted bytes'],r['Encrypt mean seconds'],r['Decrypt mean seconds'],r['Recovery verified']))
table(doc,['Strategy','Input bytes','Container bytes','Mean encrypt (s)','Mean decrypt (s)','Recovery'],bench_rows,fontsize=7)
doc.add_paragraph('Interpretation: container size includes metadata and cryptographic fields, so it is larger than the input file. On these small files, scrypt and per-operation key setup contribute noticeable fixed overhead. Do not conclude that one algorithm is universally faster from this small local sample. For course-required UI/volume/stress evidence, run the included Locust script, capture the Statistics and Charts pages, record user count/spawn rate/duration and append the screenshots. The HTTP load test has not been executed here.')
doc.add_heading('11. Test Execution Closure / Test Summary',1)
table(doc,['Item','Current result'],[
('Scope','Cryptographic core and encrypted container validation.'),('Executed unit tests','21 passed; 0 failed in the crypto-only pytest run.'),('Web integration tests','Included but pending execution on a machine with Flask installed.'),('Performance microbenchmark','9 algorithm/file-size combinations; 3 iterations each; all recovered bytes verified.'),('UI / concurrent load test','Pending; run Locust and attach actual screenshots.'),('Open issues','Web tests not run here; UI tests manual; current file handling is in-memory and not chunked; production hardening remains.'),('Exit recommendation','Do not claim the full application has passed end-to-end testing until WEB/UI tests and Locust evidence are executed and results are updated.')],fontsize=8)
doc.add_heading('12. How to Run and Verify',1)
for s in ['Extract the project ZIP to a folder.','Open Command Prompt in the `securevault_web` folder.','Run `py -m venv .venv` and `.venv\\Scripts\\activate`.','Run `pip install -r requirements.txt`.','Run `python app.py`, then open http://127.0.0.1:5000.','Register a user; test AES, ECC and Hybrid AES–ECC by encrypting a sample file, saving the `.svlt` download and decrypting it with the same password.','Run `python -m pytest -v`; review failures and update actual-output/status fields.','For performance screenshots, install Locust, start the app, run `locust -f performance_locust.py --host http://127.0.0.1:5000`, then use http://127.0.0.1:8089.']:
 doc.add_paragraph(s,style='List Number')
doc.add_heading('13. Limitations and Academic Honesty Note',1)
doc.add_paragraph('This report separates measured results from pending tests. The 21 passing tests and cryptographic microbenchmarks were actually executed. Flask route tests, browser UI checks and concurrent Locust testing still need to be run on the submission machine. Add screenshots from your own run, identify the environment, and do not mark pending tests as passed without evidence.')
# footer
for section in doc.sections:
    f=section.footer.paragraphs[0]; f.alignment=WD_ALIGN_PARAGRAPH.CENTER
    rr=f.add_run('SECUREVAULT · ISWE305P · SOFTWARE TESTING PROJECT'); rr.font.size=Pt(8); rr.font.color.rgb=RGBColor(105,127,153)
out=BASE/'docs'/'SecureVault_Testing_Report.docx'; doc.save(out); print(out)
