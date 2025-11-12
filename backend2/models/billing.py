# backend/models/billing.py
"""Invoice, InvoiceLine, and Payment models"""

from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, validator
from enum import Enum
from .base import MongoBaseModel


class PaymentMethod(str, Enum):
    """Payment method options"""
    OUT_OF_POCKET = "out_of_pocket"
    INSURANCE = "insurance"
    GOVERNMENT = "government"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    CASH = "cash"
    CHECK = "check"
    E_TRANSFER = "e_transfer"


class InvoiceStatus(str, Enum):
    """Invoice status options"""
    DRAFT = "draft"
    PENDING = "pending"
    SENT = "sent"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, Enum):
    """Payment status options"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class LineItemType(str, Enum):
    """Line item type options"""
    CONSULTATION = "consultation"
    PROCEDURE = "procedure"
    PRESCRIPTION = "prescription"
    LAB_TEST = "lab_test"
    VACCINE = "vaccine"
    MEDICAL_SUPPLY = "medical_supply"
    OTHER = "other"


class Invoice(MongoBaseModel):
    """Invoice collection model"""
    invoice_id: str = Field(..., description="Unique invoice identifier")
    invoice_number: str = Field(..., description="Human-readable invoice number")
    patient_id: str = Field(..., description="Reference to Patient")
    visit_id: Optional[str] = Field(None, description="Reference to Visit if applicable")
    
    # Invoice dates
    invoice_date: date = Field(default_factory=date.today)
    due_date: date = Field(..., description="Payment due date")
    
    # Status
    status: InvoiceStatus = Field(default=InvoiceStatus.PENDING)
    
    # Amounts
    subtotal: Decimal = Field(default=Decimal("0.00"), description="Total before tax/adjustments")
    tax_amount: Decimal = Field(default=Decimal("0.00"), description="Tax amount")
    discount_amount: Decimal = Field(default=Decimal("0.00"), description="Total discount")
    total_amount: Decimal = Field(..., description="Final amount due")
    amount_paid: Decimal = Field(default=Decimal("0.00"), description="Amount already paid")
    balance_due: Decimal = Field(..., description="Remaining balance")
    
    # Payment information
    payment_method: PaymentMethod = Field(..., description="Expected payment method")
    
    # Insurance information (if applicable)
    insurance_claim_number: Optional[str] = Field(None, description="Insurance claim reference")
    insurance_provider: Optional[str] = Field(None, description="Insurance company name")
    insurance_policy_number: Optional[str] = Field(None, description="Patient's policy number")
    insurance_group_number: Optional[str] = Field(None, description="Group number")
    co_pay_amount: Optional[Decimal] = Field(None, description="Patient co-payment amount")
    insurance_covered_amount: Optional[Decimal] = Field(None, description="Amount covered by insurance")
    insurance_claim_status: Optional[str] = Field(None, description="Status of insurance claim")
    insurance_claim_submitted_at: Optional[datetime] = None
    insurance_payment_received_at: Optional[datetime] = None
    
    # Government billing (if applicable)
    government_health_number: Optional[str] = Field(None, description="Patient's health card number")
    government_claim_number: Optional[str] = Field(None, description="Government claim reference")
    government_claim_status: Optional[str] = Field(None, description="Status of government claim")
    
    # Billing address
    billing_name: str = Field(..., description="Name on invoice")
    billing_address: str = Field(..., max_length=500)
    billing_city: str = Field(..., max_length=100)
    billing_province: str = Field(..., max_length=50)
    billing_postal_code: str = Field(...)
    billing_email: Optional[str] = Field(None, description="Email for invoice delivery")
    
    # Notes
    notes: Optional[str] = Field(None, description="Internal notes")
    patient_notes: Optional[str] = Field(None, description="Notes visible to patient")
    
    # Tracking
    sent_at: Optional[datetime] = Field(None, description="When invoice was sent")
    reminder_sent_at: Optional[datetime] = Field(None, description="When payment reminder sent")
    
    @validator('balance_due', always=True)
    def calculate_balance(cls, v, values):
        total = values.get('total_amount', Decimal("0.00"))
        paid = values.get('amount_paid', Decimal("0.00"))
        return total - paid
    
    @validator('due_date')
    def validate_due_date(cls, v, values):
        if 'invoice_date' in values and v < values['invoice_date']:
            raise ValueError('Due date must be on or after invoice date')
        return v
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "invoice_id": "INV001",
                "invoice_number": "2024-0001",
                "patient_id": "PAT001",
                "visit_id": "VIS001",
                "invoice_date": "2024-02-01",
                "due_date": "2024-03-01",
                "status": "pending",
                "subtotal": 250.00,
                "tax_amount": 32.50,
                "total_amount": 282.50,
                "balance_due": 282.50,
                "payment_method": "insurance",
                "billing_name": "Jane Smith",
                "billing_address": "123 Main St",
                "billing_city": "Calgary",
                "billing_province": "AB",
                "billing_postal_code": "T2P 1J9"
            }
        }


class InvoiceLine(MongoBaseModel):
    """InvoiceLine collection model"""
    line_id: str = Field(..., description="Unique line item identifier")
    invoice_id: str = Field(..., description="Reference to Invoice")
    line_number: int = Field(..., description="Line number for ordering")
    
    # Item details
    item_type: LineItemType = Field(..., description="Type of line item")
    item_id: Optional[str] = Field(None, description="Reference to specific item (procedure_id, drug_id, etc.)")
    item_code: Optional[str] = Field(None, description="Item code (CPT, drug code, etc.)")
    description: str = Field(..., max_length=500)
    
    # Quantities and amounts
    quantity: Decimal = Field(default=Decimal("1"), description="Quantity")
    unit_price: Decimal = Field(..., description="Price per unit")
    subtotal: Decimal = Field(..., description="Line subtotal before adjustments")
    
    # Adjustments
    discount_percentage: Optional[Decimal] = Field(None, description="Discount percentage")
    discount_amount: Optional[Decimal] = Field(None, description="Discount amount")
    tax_rate: Optional[Decimal] = Field(None, description="Tax rate percentage")
    tax_amount: Optional[Decimal] = Field(None, description="Tax amount")
    total: Decimal = Field(..., description="Final line total")
    
    # Insurance coverage
    is_covered_by_insurance: bool = Field(default=False)
    insurance_coverage_percentage: Optional[Decimal] = Field(None, description="Percentage covered")
    insurance_covered_amount: Optional[Decimal] = Field(None, description="Amount covered")
    patient_responsibility: Optional[Decimal] = Field(None, description="Patient's portion")
    
    # Notes
    notes: Optional[str] = Field(None, description="Line item notes")
    
    @validator('subtotal', always=True)
    def calculate_subtotal(cls, v, values):
        quantity = values.get('quantity', Decimal("1"))
        unit_price = values.get('unit_price', Decimal("0"))
        return quantity * unit_price
    
    @validator('total', always=True)
    def calculate_total(cls, v, values):
        subtotal = values.get('subtotal', Decimal("0"))
        discount = values.get('discount_amount', Decimal("0"))
        tax = values.get('tax_amount', Decimal("0"))
        return subtotal - discount + tax
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "line_id": "LIN001",
                "invoice_id": "INV001",
                "line_number": 1,
                "item_type": "procedure",
                "item_id": "PRO001",
                "item_code": "99213",
                "description": "Office visit, established patient",
                "quantity": 1,
                "unit_price": 150.00,
                "subtotal": 150.00,
                "total": 150.00
            }
        }


class Payment(MongoBaseModel):
    """Payment collection model"""
    payment_id: str = Field(..., description="Unique payment identifier")
    invoice_id: str = Field(..., description="Reference to Invoice")
    patient_id: str = Field(..., description="Reference to Patient")
    
    # Payment details
    payment_date: datetime = Field(default_factory=datetime.utcnow)
    amount: Decimal = Field(..., description="Payment amount")
    payment_method: PaymentMethod = Field(..., description="How payment was made")
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    
    # Transaction details
    transaction_id: Optional[str] = Field(None, description="External transaction reference")
    reference_number: Optional[str] = Field(None, description="Check number, e-transfer ref, etc.")
    
    # Credit/Debit card details (if applicable)
    card_last_four: Optional[str] = Field(None, max_length=4, description="Last 4 digits of card")
    card_type: Optional[str] = Field(None, description="Visa, Mastercard, etc.")
    
    # Insurance payment details (if applicable)
    insurance_claim_number: Optional[str] = Field(None, description="Related insurance claim")
    insurance_check_number: Optional[str] = Field(None, description="Insurance payment reference")
    eob_date: Optional[date] = Field(None, description="Explanation of Benefits date")
    
    # Government payment details (if applicable)
    government_claim_number: Optional[str] = Field(None, description="Related government claim")
    government_payment_reference: Optional[str] = Field(None, description="Government payment ref")
    
    # Processing information
    processed_by: Optional[str] = Field(None, description="Staff ID who processed payment")
    processed_at: Optional[datetime] = None
    deposited_date: Optional[date] = Field(None, description="When payment was deposited")
    
    # Refund information (if applicable)
    is_refund: bool = Field(default=False)
    refund_reason: Optional[str] = Field(None, description="Reason for refund")
    original_payment_id: Optional[str] = Field(None, description="If refund, original payment ID")
    
    # Notes
    notes: Optional[str] = Field(None, description="Payment notes")
    
    @validator('card_last_four')
    def validate_card_digits(cls, v):
        if v and not v.isdigit():
            raise ValueError('Card last four must be digits only')
        return v
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "payment_id": "PAY001",
                "invoice_id": "INV001",
                "patient_id": "PAT001",
                "payment_date": "2024-02-15T10:30:00",
                "amount": 50.00,
                "payment_method": "credit_card",
                "status": "completed",
                "transaction_id": "TXN123456",
                "card_last_four": "1234",
                "card_type": "Visa",
                "processed_by": "STF003"
            }
        }


# Request models for API
class InvoiceCreateRequest(BaseModel):
    """Request model for creating an invoice"""
    patient_id: str
    visit_id: Optional[str] = None
    due_date: date
    payment_method: PaymentMethod
    line_items: List[dict]  # List of line item details
    notes: Optional[str] = None


class PaymentCreateRequest(BaseModel):
    """Request model for creating a payment"""
    invoice_id: str
    amount: Decimal
    payment_method: PaymentMethod
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class InsuranceClaimRequest(BaseModel):
    """Request model for submitting insurance claim"""
    invoice_id: str
    insurance_provider: str
    policy_number: str
    group_number: Optional[str] = None
    claim_details: dict


class MonthlyStatementRequest(BaseModel):
    """Request model for generating monthly statement"""
    patient_id: str
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020)
    include_paid: bool = False