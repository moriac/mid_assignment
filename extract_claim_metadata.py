"""
Extract key metadata from insurance claim PDF documents.

This module extracts critical information (dates, amounts, names, numbers)
from claim documents and attaches them as metadata to ensure accurate retrieval.
"""

import re
from typing import Dict, Optional, Any
from pathlib import Path
from llama_index.core import Document
from llama_index.readers.file import PyMuPDFReader


def extract_claim_dates(text: str) -> Dict[str, Optional[str]]:
    """
    Extract key dates from claim document.
    Converts dates to standard format with default times for MCP tool compatibility.
    
    Args:
        text: Full text of the claim document
        
    Returns:
        Dictionary with extracted dates in 'YYYY-MM-DD HH:MM:SS' format
    """
    from datetime import datetime
    
    dates = {
        'incident_date': None,
        'incident_date_display': None,  # Human-readable format
        'claim_filed_date': None,
        'claim_filed_date_display': None,  # Human-readable format
        'policy_effective_date': None,
        'policy_expiry_date': None
    }
    
    # Helper function to convert date to ISO format with time
    def convert_to_iso_datetime(date_str: str, time_str: str = None) -> tuple:
        """
        Convert 'March 12, 2024' or 'March 12, 2024 - 2:47 AM' to '2024-03-12 02:47:00' format.
        
        Args:
            date_str: Date string like "March 12, 2024"
            time_str: Optional time string like "2:47 AM"
            
        Returns:
            Tuple of (iso_format, display_format)
        """
        try:
            # Parse the date
            parsed_date = datetime.strptime(date_str.strip(), "%B %d, %Y")
            
            # Parse time if provided
            if time_str:
                # Handle formats like "2:47 AM" or "10:30 AM"
                time_str = time_str.strip()
                try:
                    parsed_time = datetime.strptime(time_str, "%I:%M %p")
                    iso_format = parsed_date.strftime("%Y-%m-%d") + " " + parsed_time.strftime("%H:%M:%S")
                    display_format = f"{date_str.strip()} at {time_str}"
                except:
                    # If time parsing fails, use default time
                    iso_format = parsed_date.strftime("%Y-%m-%d 00:00:00")
                    display_format = date_str.strip()
            else:
                # No time provided, use midnight
                iso_format = parsed_date.strftime("%Y-%m-%d 00:00:00")
                display_format = date_str.strip()
            
            return iso_format, display_format
        except:
            return None, None
    
    # Pattern for "March 12, 2024 - 2:47 AM** *(Primary Loss Event)*"
    # This captures the actual incident time from the chronological timeline
    incident_time_patterns = [
        r'([A-Za-z]+\s+\d{1,2},\s*\d{4})\s*-\s*(\d{1,2}:\d{2}\s*(?:AM|PM))\s*\*{0,2}\s*\*?\s*\(Primary Loss Event\)',
        r'Primary Loss Event[^\n]*?([A-Za-z]+\s+\d{1,2},\s*\d{4})\s*-\s*(\d{1,2}:\d{2}\s*(?:AM|PM))',
    ]
    
    for pattern in incident_time_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            iso_date, display_date = convert_to_iso_datetime(match.group(1), match.group(2))
            if iso_date:
                dates['incident_date'] = iso_date
                dates['incident_date_display'] = display_date
                break
    
    # If no time found, try without time
    if not dates['incident_date']:
        incident_patterns = [
            r'Incident Date[:\*\s]+([A-Za-z]+\s+\d{1,2},\s*\d{4})',
            r'Date of (?:Loss|Incident)[:\*\s]+([A-Za-z]+\s+\d{1,2},\s*\d{4})',
            r'Loss Date[:\*\s]+([A-Za-z]+\s+\d{1,2},\s*\d{4})'
        ]
        
        for pattern in incident_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                iso_date, display_date = convert_to_iso_datetime(match.group(1))
                if iso_date:
                    dates['incident_date'] = iso_date
                    dates['incident_date_display'] = display_date
                    break
    
    # Pattern for claim filing with time
    # Look for "March 15, 2024 - 11:00 AM** Formal claim filed"
    filed_time_patterns = [
        r'([A-Za-z]+\s+\d{1,2},\s*\d{4})\s*-\s*(\d{1,2}:\d{2}\s*(?:AM|PM))\s*\*{0,2}\s*[^\n]*?Formal claim filed',
        r'([A-Za-z]+\s+\d{1,2},\s*\d{4})\s*-\s*(\d{1,2}:\d{2}\s*(?:AM|PM))\s*\*{0,2}[^\n]*(?:submitted|filed)[^\n]*(?:preliminary claim notice|claim)',
        r'(?:submitted|filed)[^\n]*(?:preliminary claim notice|claim)[^\n]*?([A-Za-z]+\s+\d{1,2},\s*\d{4})\s*-\s*(\d{1,2}:\d{2}\s*(?:AM|PM))',
    ]
    
    for pattern in filed_time_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            iso_date, display_date = convert_to_iso_datetime(match.group(1), match.group(2))
            if iso_date:
                dates['claim_filed_date'] = iso_date
                dates['claim_filed_date_display'] = display_date
                break
    
    # If no time found, try without time
    if not dates['claim_filed_date']:
        filed_patterns = [
            r'Claim Date Filed[:\*\s]+([A-Za-z]+\s+\d{1,2},\s*\d{4})',
            r'Claim Filed[:\*\s]+([A-Za-z]+\s+\d{1,2},\s*\d{4})',
            r'Filing Date[:\*\s]+([A-Za-z]+\s+\d{1,2},\s*\d{4})'
        ]
        
        for pattern in filed_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                iso_date, display_date = convert_to_iso_datetime(match.group(1))
                if iso_date:
                    dates['claim_filed_date'] = iso_date
                    dates['claim_filed_date_display'] = display_date
                    break
    
    # Pattern for "Policy Effective Date: January 1, 2023"
    effective_patterns = [
        r'Policy Effective Date[:\*\s]+([A-Za-z]+\s+\d{1,2},\s*\d{4})',
        r'Effective Date[:\*\s]+([A-Za-z]+\s+\d{1,2},\s*\d{4})'
    ]
    
    for pattern in effective_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            iso_date, _ = convert_to_iso_datetime(match.group(1))
            if iso_date:
                dates['policy_effective_date'] = iso_date
                break
    
    # Pattern for "Policy Expiry Date: December 31, 2024"
    expiry_patterns = [
        r'Policy Expiry Date[:\*\s]+([A-Za-z]+\s+\d{1,2},\s*\d{4})',
        r'Expiry Date[:\*\s]+([A-Za-z]+\s+\d{1,2},\s*\d{4})',
        r'Expiration Date[:\*\s]+([A-Za-z]+\s+\d{1,2},\s*\d{4})'
    ]
    
    for pattern in expiry_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            iso_date, _ = convert_to_iso_datetime(match.group(1))
            if iso_date:
                dates['policy_expiry_date'] = iso_date
                break
    
    return dates


def extract_claim_identifiers(text: str) -> Dict[str, Optional[str]]:
    """
    Extract claim and policy identifiers.
    
    Args:
        text: Full text of the claim document
        
    Returns:
        Dictionary with extracted identifiers
    """
    identifiers = {
        'claim_number': None,
        'policy_number': None
    }
    
    # Pattern for "Claim #2024-CP-087456" or "Claim Number: 2024-CP-087456"
    claim_patterns = [
        r'Claim\s*#\s*([A-Z0-9\-]+)',
        r'Claim Number[:\*\s]+([A-Z0-9\-]+)',
        r'Claim ID[:\*\s]+([A-Z0-9\-]+)'
    ]
    
    for pattern in claim_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            identifiers['claim_number'] = match.group(1).strip()
            break
    
    # Pattern for "Policy Number:** CP-4827-2023" or "Policy: CP-4827-2023"
    policy_patterns = [
        r'Policy Number[:\*\s]+([A-Z0-9\-]+)',
        r'Policy[:\*\s]+([A-Z0-9\-]+)',
        r'Policy ID[:\*\s]+([A-Z0-9\-]+)'
    ]
    
    for pattern in policy_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            identifiers['policy_number'] = match.group(1).strip()
            break
    
    return identifiers


def extract_claim_parties(text: str) -> Dict[str, Optional[str]]:
    """
    Extract parties involved in the claim.
    
    Args:
        text: Full text of the claim document
        
    Returns:
        Dictionary with extracted party information
    """
    parties = {
        'claimant': None,
        'policyholder': None,
        'insured': None
    }
    
    # Pattern for "Claimant:** Precision Manufacturing Ltd."
    claimant_patterns = [
        r'Claimant[:\*\s]+([^\n*]+?)(?:\n|\*\*)',
        r'Claimant Name[:\*\s]+([^\n*]+?)(?:\n|\*\*)'
    ]
    
    for pattern in claimant_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            parties['claimant'] = match.group(1).strip()
            break
    
    # Pattern for "Policyholder: Company Name"
    policyholder_patterns = [
        r'Policyholder[:\*\s]+([^\n*]+?)(?:\n|\*\*)',
        r'Policy Holder[:\*\s]+([^\n*]+?)(?:\n|\*\*)'
    ]
    
    for pattern in policyholder_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            parties['policyholder'] = match.group(1).strip()
            break
    
    # Pattern for "Insured: Company Name"
    insured_patterns = [
        r'Insured[:\*\s]+([^\n*]+?)(?:\n|\*\*)',
        r'Named Insured[:\*\s]+([^\n*]+?)(?:\n|\*\*)'
    ]
    
    for pattern in insured_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            parties['insured'] = match.group(1).strip()
            break
    
    return parties


def extract_claim_amounts(text: str) -> Dict[str, Optional[str]]:
    """
    Extract monetary amounts from the claim.
    
    Args:
        text: Full text of the claim document
        
    Returns:
        Dictionary with extracted amounts
    """
    amounts = {
        'claim_amount': None,
        'estimated_loss': None,
        'policy_limit': None
    }
    
    # Pattern for "Claim Amount:** $387,500"
    claim_amount_patterns = [
        r'Claim Amount[:\*\s]+\$?([\d,]+(?:\.\d{2})?)',
        r'Total Claim[:\*\s]+\$?([\d,]+(?:\.\d{2})?)',
        r'Amount Claimed[:\*\s]+\$?([\d,]+(?:\.\d{2})?)'
    ]
    
    for pattern in claim_amount_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amounts['claim_amount'] = match.group(1).replace(',', '')
            break
    
    # Pattern for estimated loss
    loss_patterns = [
        r'Estimated Loss[:\*\s]+\$?([\d,]+(?:\.\d{2})?)',
        r'Loss Amount[:\*\s]+\$?([\d,]+(?:\.\d{2})?)'
    ]
    
    for pattern in loss_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amounts['estimated_loss'] = match.group(1).replace(',', '')
            break
    
    # Pattern for policy limit
    limit_patterns = [
        r'Policy Limit[:\*\s]+\$?([\d,]+(?:\.\d{2})?)',
        r'Coverage Limit[:\*\s]+\$?([\d,]+(?:\.\d{2})?)'
    ]
    
    for pattern in limit_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amounts['policy_limit'] = match.group(1).replace(',', '')
            break
    
    return amounts


def extract_claim_location(text: str) -> Dict[str, Optional[str]]:
    """
    Extract location information from the claim.
    
    Args:
        text: Full text of the claim document
        
    Returns:
        Dictionary with extracted location
    """
    location = {
        'loss_location': None,
        'address': None
    }
    
    # Pattern for "Location:** 2847 Industrial Drive, Newark, NJ 07105"
    location_patterns = [
        r'Location[:\*\s]+([^\n*]+?)(?:\n|\*\*)',
        r'Loss Location[:\*\s]+([^\n*]+?)(?:\n|\*\*)',
        r'Property Location[:\*\s]+([^\n*]+?)(?:\n|\*\*)'
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            location['loss_location'] = match.group(1).strip()
            location['address'] = match.group(1).strip()
            break
    
    return location


def extract_claim_metadata(text: str) -> Dict[str, Any]:
    """
    Extract all key metadata from claim document.
    
    Args:
        text: Full text of the claim document
        
    Returns:
        Dictionary with all extracted metadata
    """
    metadata = {}
    
    # Extract all components
    metadata.update(extract_claim_dates(text))
    metadata.update(extract_claim_identifiers(text))
    metadata.update(extract_claim_parties(text))
    metadata.update(extract_claim_amounts(text))
    metadata.update(extract_claim_location(text))
    
    # Add document type
    metadata['document_type'] = 'insurance_claim'
    
    return metadata


def load_claim_document_with_metadata(file_path: str) -> Document:
    """
    Load claim PDF document and attach extracted metadata.
    
    Args:
        file_path: Path to the claim PDF file
        
    Returns:
        Document with metadata attached
    """
    print(f"📄 Loading claim document: {file_path}")
    
    # Load PDF using PyMuPDFReader
    loader = PyMuPDFReader()
    documents = loader.load(file_path=Path(file_path))
    
    if not documents:
        raise ValueError(f"No content found in {file_path}")
    
    # Get full text
    text = "\n\n".join([doc.get_content() for doc in documents])
    
    # Extract metadata
    print("🔍 Extracting metadata...")
    metadata = extract_claim_metadata(text)
    
    # Print extracted metadata
    print("\n✅ Extracted metadata:")
    for key, value in metadata.items():
        if value:
            print(f"   • {key}: {value}")
    
    # Create document with metadata
    document = Document(
        text=text,
        metadata=metadata
    )
    
    return document


if __name__ == "__main__":
    # Test the extraction
    import sys
    
    pdf_file = "insurance_claim_case.pdf"
    
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
    
    print("=" * 80)
    print("Claim Metadata Extraction Test")
    print("=" * 80)
    
    try:
        doc = load_claim_document_with_metadata(pdf_file)
        
        print("\n" + "=" * 80)
        print("✓ Metadata extraction completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
