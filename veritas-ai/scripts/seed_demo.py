"""
VERITAS AI — Demo Data Seeder
Generates realistic banking documents and seeds databases
"""

import os
import sys
import random
import json
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("seed")

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
DEMO_DIR = DATA_DIR / "demo"
REG_DIR = DATA_DIR / "regulations"

DEMO_DIR.mkdir(parents=True, exist_ok=True)
REG_DIR.mkdir(parents=True, exist_ok=True)

try:
    from fpdf import FPDF
    HAS_PDF = True
except ImportError:
    HAS_PDF = False
    log.warning("fpdf2 not installed — creating text files instead of PDFs")


def create_pdf_or_txt(filename: str, content: str):
    """Save demo document as .txt (OCR service reads both)."""
    # Always save as .txt for demo reliability
    txt_path = DEMO_DIR / Path(filename).with_suffix(".txt").name
    txt_path.write_text(content.strip(), encoding="utf-8")
    log.info(f"  Created: {txt_path.name}")



def seed_land_records():
    log.info("Seeding land records...")

    # Normal land record
    create_pdf_or_txt("land_record_plot47.pdf", """
GOVERNMENT OF MAHARASHTRA
DEPARTMENT OF REVENUE AND LAND RECORDS

LAND RECORD CERTIFICATE
Record Number: MH/2023/PROP/78234

Property Details:
Plot No: 47
Location: Andheri West, Mumbai - 400053
Survey No: 123/A
Area: 1200 sq. ft.
Date of Registration: 15/03/2020

Owner Details:
Name: Rajesh Kumar
Father's Name: Ramesh Kumar
PAN: ABCPK1234D
Aadhaar: XXXX XXXX 5678
Address: 12, Sai Nagar, Andheri West, Mumbai - 400053

Sale Deed Details:
Deed Number: MH-2020-456789
Registration Date: 15/03/2020
Purchase Price: Rs. 75,00,000
Stamp Duty Paid: Rs. 4,50,000

Current Status: CLEAR TITLE - No Encumbrance
Signature of Registrar: [SIGNED]
Date: 15/03/2020
""")

    # TAMPERED land record (intentional anomalies)
    create_pdf_or_txt("land_record_tampered_plot47.pdf", """
GOVERNMENT OF MAHARASHTRA
DEPARTMENT OF REVENUE AND LAND RECORDS

LAND RECORD CERTIFICATE
Record Number: MH/2023/PROP/78234

Property Details:
Plot No: 47
Location: Andheri West, Mumbai - 400053
Survey No: 123/A
Area: 1200 sq. ft.
Date of Registration: 15/03/2020

Owner Details:
Name: Suresh Patel
Father's Name: Rajesh Patel
PAN: XYZSP9876K
Aadhaar: XXXX XXXX 1234
Address: SP Real Estate LLP, Surat - 395001

CORRECTION (WHITEOUT APPLIED): Previous owner: Rajesh Kumar
Transfer via Gift Deed: MH-2023-GIFT-001
Relinquishment Deed: MH-2023-REL-002
Assignment Deed: MH-2023-ASS-003
Sale Deed: MH-2023-SALE-004

Current Status: MORTGAGED - Canara Bank (overwritten: SBI Bank)
Mortgage Amount: Rs. 90,00,00,000,00 (NINE HUNDRED CRORE - FICTITIOUS)
Shell Company: RK Holdings Pvt Ltd (benami)
Stamp Duty Paid: Rs. 0 (EXEMPTION - FORGED)

Creator: Adobe Photoshop 24.0
Modified: 2024-01-15T03:22:18Z
Created: 2020-03-15T09:00:00Z
""")


def seed_financial_statements():
    log.info("Seeding financial statements...")

    create_pdf_or_txt("financial_statement_normal.pdf", """
AUDITED FINANCIAL STATEMENT
M/s Priya Sharma Enterprises
FY 2023-24

Income Statement:
Revenue from Operations: Rs. 45,00,000
Other Income: Rs. 2,50,000
Total Revenue: Rs. 47,50,000

Expenses:
Cost of Goods Sold: Rs. 28,00,000
Administrative Expenses: Rs. 6,50,000
Depreciation: Rs. 1,20,000
Total Expenses: Rs. 35,70,000

Profit Before Tax: Rs. 11,80,000
Tax Provision: Rs. 3,90,000
Net Profit: Rs. 7,90,000

Balance Sheet Summary:
Total Assets: Rs. 28,50,000
Total Liabilities: Rs. 12,00,000
Net Worth: Rs. 16,50,000

Auditor: M/s. Sharma & Associates, CA
Date: 31/03/2024
""")

    # Tampered with unrealistic numbers
    create_pdf_or_txt("financial_statement_anomaly.pdf", """
AUDITED FINANCIAL STATEMENT
M/s Suresh Patel Constructions
FY 2023-24

Income Statement:
Revenue from Operations: Rs. 99,00,00,000,000 (NINETY NINE THOUSAND CRORE)
Other Income: Rs. 1,00,00,000
Total Revenue: Rs. 99,00,01,00,000

CORRECTION (overwritten): Previous Revenue was Rs. 9,90,00,000

Expenses:
Cost of Goods Sold: Rs. 1,00,000
Administrative Expenses: Rs. 50,000
Total Expenses: Rs. 1,50,000

Net Profit: Rs. 98,99,99,50,000

Assets:
Fictitious receivables from shell company SP Real Estate LLP: Rs. 50,00,00,000
Benami property (undisclosed): Rs. 9,00,00,000

Auditor: Dummy Audit Firm Pvt Ltd (UNREGISTERED)
Date: 01/01/2024
""")


def seed_kyc_documents():
    log.info("Seeding KYC documents...")

    create_pdf_or_txt("kyc_rajesh_kumar.pdf", """
KYC DOCUMENT — INDIVIDUAL

Customer Name: Rajesh Kumar
Date of Birth: 12/05/1975
PAN Number: ABCPK1234D
Aadhaar Number: XXXX XXXX 5678

Address (As per Aadhaar):
12, Sai Nagar, Andheri West, Mumbai - 400053
Maharashtra, India

Current Address:
RK Holdings Pvt Ltd
4th Floor, Business Center, BKC, Mumbai - 400051

Identity Proof: Aadhaar Card
Address Proof: Utility Bill (March 2024)
Photograph: Attached

Bank Account: Canara Bank, BKC Branch
Account No: 456789012345
IFSC: CNRB0001234

Customer Risk Category: HIGH (flagged for review)
KYC Status: Under Enhanced Due Diligence
Last KYC Update: 01/12/2023

Verified By: Branch Manager
Signature: [SIGNED]
Date: 01/12/2023
""")

    create_pdf_or_txt("kyc_priya_sharma.pdf", """
KYC DOCUMENT — INDIVIDUAL

Customer Name: Priya Sharma
Date of Birth: 22/08/1985
PAN Number: DEFPS5678G
Aadhaar Number: XXXX XXXX 9012

Address:
45, Green Park, New Delhi - 110016

Identity Proof: Passport (No: P1234567)
Address Proof: Aadhaar Card

Bank Account: Canara Bank, Connaught Place
Account No: 789012345678
IFSC: CNRB0005678

Customer Risk Category: LOW
KYC Status: Complete and Verified
Last KYC Update: 15/03/2024

Verified By: Branch Manager
Date: 15/03/2024
""")


def seed_compliance_reports():
    log.info("Seeding compliance reports...")

    create_pdf_or_txt("compliance_q3_2024.pdf", """
QUARTERLY COMPLIANCE REPORT
Q3 FY 2024-25 (October - December 2024)

Prepared for: Canara Bank, MSME Division
Compliance Period: 01-Oct-2024 to 31-Dec-2024

1. KYC Compliance Status:
   - Total customers reviewed: 1,250
   - High-risk customers with updated KYC: 98.4%
   - Pending KYC updates: 20
   - Action: Complete by 15-Jan-2025

2. Suspicious Transaction Reports (STR):
   - STRs filed this quarter: 3
   - Average filing time: 5.2 days (within 7-day limit)
   - FIU-IND acknowledgements received: 3/3

3. SEBI LODR Compliance:
   - Board meeting disclosures: Filed within 30 minutes ✓
   - Financial results submitted: Within 45 days ✓
   - Related Party Transactions: Disclosed as per regulation ✓

4. Beneficial Ownership Audit:
   Status: IN PROGRESS
   Entities audited: 45/60
   Non-compliant entities: 3 (action pending)

Overall Compliance Score: 87/100
Compliance Officer: Mr. Anil Mehta (CA, CAIIB)
Date: 15-Jan-2025
""")


def seed_regulations():
    log.info("Seeding regulation documents...")

    (REG_DIR / "rbi_kyc_directions.txt").write_text("""
RBI MASTER DIRECTION ON KYC (RBI/2023-24/10)

1. CUSTOMER DUE DILIGENCE (CDD)
All banks must conduct Customer Due Diligence at the time of account opening
and on an ongoing basis. Documents required:
- Proof of Identity (Aadhaar, PAN, Passport, Driving License)
- Proof of Address (Utility bill, Bank statement)
- Recent photograph

2. RECORD KEEPING
KYC records must be maintained for a minimum of 5 years after the
business relationship has ended or the transaction has been completed.

3. RISK CATEGORIZATION
Customers shall be categorized as Low, Medium, or High risk.
- High risk: PEPs, NRIs, entities in high-risk jurisdictions
- Periodic update: High-risk (2 years), Medium (8 years), Low (10 years)

4. ENHANCED DUE DILIGENCE (EDD)
EDD is mandatory for: Politically Exposed Persons, Non-Face-to-Face customers,
accounts of correspondent banks, and customers in high-risk countries.

5. SUSPICIOUS TRANSACTION REPORTING
Banks must file Suspicious Transaction Reports (STR) with FIU-IND within 7 days
of forming a reasonable ground for suspicion.
""", encoding="utf-8")

    (REG_DIR / "sebi_lodr_2015.txt").write_text("""
SEBI LISTING OBLIGATIONS AND DISCLOSURE REQUIREMENTS (LODR) REGULATIONS 2015

REGULATION 27: COMPLIANCE REPORT ON CORPORATE GOVERNANCE
Listed entities shall submit a quarterly compliance report on corporate governance
to the stock exchange within 21 days from the end of each quarter.

REGULATION 30: DISCLOSURE OF EVENTS
Listed entities must disclose to the stock exchanges all events or information
which, in the opinion of the board, are material, within 24 hours.

Board meeting outcomes must be disclosed within 30 minutes of conclusion.

REGULATION 33: FINANCIAL RESULTS
Listed entities shall submit financial results within:
- Quarterly results: 45 days from end of quarter
- Annual results: 60 days from end of financial year

RELATED PARTY TRANSACTIONS
All material RPTs shall require shareholder approval through ordinary resolution.
RPTs must be disclosed in quarterly/annual financial results.
""", encoding="utf-8")


def seed_chromadb():
    log.info("Seeding ChromaDB with regulations...")
    try:
        sys.path.insert(0, str(ROOT / "backend"))
        from services.vector_store import VectorStoreService

        vs = VectorStoreService()
        if vs.count() > 0:
            log.info(f"  ChromaDB already has {vs.count()} documents — skipping")
            return

        from backend.data.regulations import SAMPLE_REGULATIONS
        documents = [
            {
                "id": r["id"],
                "content": r["content"],
                "metadata": r["metadata"],
            }
            for r in SAMPLE_REGULATIONS
        ]
        count = vs.ingest_documents(documents)
        log.info(f"  Ingested {count} regulations into ChromaDB")
    except Exception as e:
        log.warning(f"  ChromaDB seeding skipped: {e}")


def seed_graph():
    log.info("Graph data is seeded at runtime by GraphService — skipping separate seed")


if __name__ == "__main__":
    log.info("═" * 50)
    log.info("VERITAS AI — Demo Data Seeder")
    log.info("═" * 50)

    seed_land_records()
    seed_financial_statements()
    seed_kyc_documents()
    seed_compliance_reports()
    seed_regulations()
    seed_chromadb()
    seed_graph()

    log.info("")
    log.info("✅ Demo data seeded successfully!")
    log.info(f"   Files in: {DEMO_DIR}")
    log.info(f"   Regulations in: {REG_DIR}")
