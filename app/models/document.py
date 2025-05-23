from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    BANK_STATEMENT = "Bank Statement"
    PAYSLIP = "Payslip"
    IRP = "Irish Residency Permit"
    PPSN = "Personal Public Service Number"
    TAX_RECORD = "Tax Record"


class Document(BaseModel):
    """Base model for all document types"""
    id: str
    type: DocumentType
    customer_name: str
    customer_dob: Optional[str] = None
    customer_address: Optional[str] = None
    upload_date: str
    
    # Document-specific fields - these will be populated based on document type
    # Bank Statement fields
    account_number: Optional[str] = None
    opening_balance: Optional[float] = None
    closing_balance: Optional[float] = None
    statement_date: Optional[str] = None
    
    # Payslip fields
    employer_name: Optional[str] = None
    gross_pay: Optional[float] = None
    net_pay: Optional[float] = None
    pay_date: Optional[str] = None
    
    # IRP fields
    irp_number: Optional[str] = None
    nationality: Optional[str] = None
    expiry_date: Optional[str] = None
    
    # PPSN fields
    ppsn_number: Optional[str] = None
    issue_date: Optional[str] = None
    
    # Tax Record fields
    tax_year: Optional[str] = None
    total_income: Optional[float] = None
    tax_paid: Optional[float] = None


class ValidationIssue(BaseModel):
    """Model representing a validation issue found in a document"""
    severity: str = Field(..., description="HIGH, MEDIUM, or LOW")
    category: str = Field(..., description="Category of the validation issue")
    description: str = Field(..., description="Description of the issue")
    recommendation: str = Field(..., description="Recommended action to resolve the issue")


class ValidationResult(BaseModel):
    """Model representing the result of document validation"""
    document_id: str
    document_type: DocumentType
    customer_name: str
    validation_date: str
    issues: List[ValidationIssue] = []
    is_valid: bool = True