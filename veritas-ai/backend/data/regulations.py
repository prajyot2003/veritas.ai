"""
VERITAS AI — Sample Regulations Data
Used as fallback when ChromaDB is unavailable
"""

SAMPLE_REGULATIONS = [
    {
        "id": "rbi_kyc_001",
        "content": """RBI Master Direction on Know Your Customer (KYC) Norms.
All banks must maintain KYC records for a minimum period of 5 years after the business relationship has ended.
Documents required: Proof of identity, proof of address, recent photograph.
For entities: Certificate of incorporation, board resolution, and list of directors.
Periodic KYC update is required every 2 years for high-risk customers, every 8 years for medium-risk, and every 10 years for low-risk.""",
        "metadata": {"source": "RBI", "type": "KYC", "ref": "RBI/2023-24/10"},
    },
    {
        "id": "rbi_aml_001",
        "content": """RBI Guidelines on Anti-Money Laundering (AML) Measures.
Banks must file Suspicious Transaction Reports (STR) with the Financial Intelligence Unit-India (FIU-IND) within 7 days.
Cash Transaction Reports (CTR) must be filed for transactions above INR 10 lakhs.
Non-Profit Organizations must be monitored for possible terror financing.
Politically Exposed Persons (PEPs) must be subject to enhanced due diligence.""",
        "metadata": {"source": "RBI", "type": "AML", "ref": "PMLA 2002, Rule 8"},
    },
    {
        "id": "rbi_collateral_001",
        "content": """RBI Guidelines on Collateral Management for Agricultural Loans.
Banks must verify ownership of land collateral with state revenue records before disbursement.
Duplicate mortgages on the same collateral by different banks is prohibited.
Physical inspection of immovable property is mandatory for loans above INR 1 crore.
Title verification by a government-registered legal expert is required.""",
        "metadata": {"source": "RBI", "type": "Collateral", "ref": "RPCD.PLNFS.No.BC.61"},
    },
    {
        "id": "sebi_lodr_001",
        "content": """SEBI Listing Obligations and Disclosure Requirements (LODR) Regulations 2015.
Listed entities must disclose material information immediately and not later than 24 hours.
Board meeting outcomes must be disclosed within 30 minutes of conclusion.
Related Party Transactions above a threshold require shareholder approval.
Financial results must be submitted quarterly within 45 days of quarter-end.""",
        "metadata": {"source": "SEBI", "type": "LODR", "ref": "SEBI/LODR/2015/27"},
    },
    {
        "id": "pmla_beneficial_001",
        "content": """Prevention of Money Laundering Act 2002 - Beneficial Ownership Norms.
Any entity holding more than 25% of the shares of a company must be identified as a beneficial owner.
Banks must verify beneficial ownership for all accounts opened by legal entities.
Failure to disclose beneficial ownership is an offense under PMLA with penalty up to INR 1 lakh per day.
Shell companies with no genuine business activity must be flagged for enhanced due diligence.""",
        "metadata": {"source": "MCA", "type": "Beneficial Ownership", "ref": "PMLA 2002 Section 12A"},
    },
]
