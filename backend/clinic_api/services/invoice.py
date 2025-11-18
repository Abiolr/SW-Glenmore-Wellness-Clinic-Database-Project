from typing import List, Optional
from datetime import date
from ..database import Database
from ..models import (
    Invoice, InvoiceCreate,
    InvoiceLine, InvoiceLineCreate,
    Payment, PaymentCreate
)


class InvoiceCRUD:
    collection_name = "Invoice"
    
    @classmethod
    def create(cls, invoice: InvoiceCreate) -> Invoice:
        """Create a new invoice"""
        collection = Database.get_collection(cls.collection_name)
        
        # Get next invoice ID
        invoice_id = Database.get_next_sequence("invoice_id")
        
        invoice_dict = invoice.model_dump()
        invoice_dict["invoice_id"] = invoice_id
        invoice_dict["invoice_date"] = invoice_dict["invoice_date"].isoformat()
        
        collection.insert_one(invoice_dict)
        
        return Invoice(**invoice_dict)
    
    @classmethod
    def get(cls, invoice_id: int) -> Optional[Invoice]:
        """Get an invoice by ID"""
        collection = Database.get_collection(cls.collection_name)
        invoice_data = collection.find_one({"invoice_id": invoice_id}, {"_id": 0})
        
        if invoice_data:
            invoice_data["invoice_date"] = date.fromisoformat(invoice_data["invoice_date"])
            return Invoice(**invoice_data)
        return None
    
    @classmethod
    def get_all(cls, skip: int = 0, limit: int = 100) -> List[Invoice]:
        """Get all invoices with pagination"""
        collection = Database.get_collection(cls.collection_name)
        invoices_data = collection.find({}, {"_id": 0}).skip(skip).limit(limit)
        
        invoices = []
        for data in invoices_data:
            data["invoice_date"] = date.fromisoformat(data["invoice_date"])
            invoices.append(Invoice(**data))
        
        return invoices
    
    @classmethod
    def get_by_patient(cls, patient_id: int) -> List[Invoice]:
        """Get all invoices for a specific patient"""
        collection = Database.get_collection(cls.collection_name)
        invoices_data = collection.find({"patient_id": patient_id}, {"_id": 0}).sort("invoice_date", -1)
        
        invoices = []
        for data in invoices_data:
            data["invoice_date"] = date.fromisoformat(data["invoice_date"])
            invoices.append(Invoice(**data))
        
        return invoices
    
    @classmethod
    def get_by_status(cls, status: str) -> List[Invoice]:
        """Get all invoices by status"""
        collection = Database.get_collection(cls.collection_name)
        invoices_data = collection.find({"status": status}, {"_id": 0})
        
        invoices = []
        for data in invoices_data:
            data["invoice_date"] = date.fromisoformat(data["invoice_date"])
            invoices.append(Invoice(**data))
        
        return invoices
    
    @classmethod
    def update(cls, invoice_id: int, invoice: InvoiceCreate) -> Optional[Invoice]:
        """Update an invoice"""
        collection = Database.get_collection(cls.collection_name)
        
        invoice_dict = invoice.model_dump()
        invoice_dict["invoice_date"] = invoice_dict["invoice_date"].isoformat()
        
        result = collection.update_one(
            {"invoice_id": invoice_id},
            {"$set": invoice_dict}
        )
        
        if result.modified_count > 0:
            return cls.get(invoice_id)
        return None
    
    @classmethod
    def update_status(cls, invoice_id: int, status: str) -> Optional[Invoice]:
        """Update invoice status"""
        collection = Database.get_collection(cls.collection_name)
        
        result = collection.update_one(
            {"invoice_id": invoice_id},
            {"$set": {"status": status}}
        )
        
        if result.modified_count > 0:
            return cls.get(invoice_id)
        return None
    
    @classmethod
    def delete(cls, invoice_id: int) -> bool:
        """Delete an invoice"""
        collection = Database.get_collection(cls.collection_name)
        result = collection.delete_one({"invoice_id": invoice_id})
        return result.deleted_count > 0


class InvoiceLineCRUD:
    collection_name = "InvoiceLine"
    
    @classmethod
    def create(cls, invoice_line: InvoiceLineCreate) -> InvoiceLine:
        """Add a line item to an invoice"""
        collection = Database.get_collection(cls.collection_name)
        
        # Get next line number for this invoice
        existing_lines = collection.find({"invoice_id": invoice_line.invoice_id}).sort("line_no", -1).limit(1)
        line_no = 1
        for line in existing_lines:
            line_no = line["line_no"] + 1
        
        invoice_line_dict = invoice_line.model_dump()
        invoice_line_dict["line_no"] = line_no
        
        collection.insert_one(invoice_line_dict)
        
        return InvoiceLine(**invoice_line_dict)
    
    @classmethod
    def get_by_invoice(cls, invoice_id: int) -> List[InvoiceLine]:
        """Get all line items for a specific invoice"""
        collection = Database.get_collection(cls.collection_name)
        lines_data = collection.find({"invoice_id": invoice_id}, {"_id": 0}).sort("line_no", 1)
        
        return [InvoiceLine(**data) for data in lines_data]
    
    @classmethod
    def delete(cls, invoice_id: int, line_no: int) -> bool:
        """Remove a line item from an invoice"""
        collection = Database.get_collection(cls.collection_name)
        result = collection.delete_one({"invoice_id": invoice_id, "line_no": line_no})
        return result.deleted_count > 0


class PaymentCRUD:
    collection_name = "Payment"
    
    @classmethod
    def create(cls, payment: PaymentCreate) -> Payment:
        """Create a new payment and TRIGGER invoice status update"""
        collection = Database.get_collection(cls.collection_name)
        
        # 1. Create Payment
        payment_id = Database.get_next_sequence("payment_id")
        payment_dict = payment.model_dump()
        payment_dict["payment_id"] = payment_id
        payment_dict["payment_date"] = payment_dict["payment_date"].isoformat()
        
        collection.insert_one(payment_dict)
        
        # 2. TRIGGER LOGIC: Check Invoice Balance
        if payment.invoice_id:
            cls.check_and_update_invoice_status(payment.invoice_id)
            
        return Payment(**payment_dict)

    @classmethod
    def check_and_update_invoice_status(cls, invoice_id: int):
        """Simulates a DB Trigger to update status based on balance"""
        inv_collection = Database.get_collection("Invoice")
        pay_collection = Database.get_collection("Payment")
        
        invoice = inv_collection.find_one({"invoice_id": invoice_id})
        if not invoice:
            return

        # Calculate total paid
        payments = pay_collection.find({"invoice_id": invoice_id})
        total_paid = sum(p["amount"] for p in payments)
        
        # Determine target total (patient portion usually)
        target_amount = invoice.get("patient_portion", invoice.get("total_amount", 0))
        
        new_status = invoice["status"]
        if total_paid >= target_amount:
            new_status = "paid"
        elif total_paid > 0:
            new_status = "partial"
            
        if new_status != invoice["status"]:
            inv_collection.update_one(
                {"invoice_id": invoice_id},
                {"$set": {"status": new_status}}
            )
    
    @classmethod
    def get(cls, payment_id: int) -> Optional[Payment]:
        """Get a payment by ID"""
        collection = Database.get_collection(cls.collection_name)
        payment_data = collection.find_one({"payment_id": payment_id}, {"_id": 0})
        
        if payment_data:
            payment_data["payment_date"] = date.fromisoformat(payment_data["payment_date"])
            return Payment(**payment_data)
        return None
    
    @classmethod
    def get_all(cls, skip: int = 0, limit: int = 100) -> List[Payment]:
        """Get all payments with pagination"""
        collection = Database.get_collection(cls.collection_name)
        payments_data = collection.find({}, {"_id": 0}).skip(skip).limit(limit)
        
        payments = []
        for data in payments_data:
            data["payment_date"] = date.fromisoformat(data["payment_date"])
            payments.append(Payment(**data))
        
        return payments
    
    @classmethod
    def get_by_patient(cls, patient_id: int) -> List[Payment]:
        """Get all payments for a specific patient"""
        collection = Database.get_collection(cls.collection_name)
        payments_data = collection.find({"patient_id": patient_id}, {"_id": 0}).sort("payment_date", -1)
        
        payments = []
        for data in payments_data:
            data["payment_date"] = date.fromisoformat(data["payment_date"])
            payments.append(Payment(**data))
        
        return payments
    
    @classmethod
    def get_by_invoice(cls, invoice_id: int) -> List[Payment]:
        """Get all payments for a specific invoice"""
        collection = Database.get_collection(cls.collection_name)
        payments_data = collection.find({"invoice_id": invoice_id}, {"_id": 0}).sort("payment_date", -1)
        
        payments = []
        for data in payments_data:
            data["payment_date"] = date.fromisoformat(data["payment_date"])
            payments.append(Payment(**data))
        
        return payments
    
    @classmethod
    def delete(cls, payment_id: int) -> bool:
        """Delete a payment"""
        collection = Database.get_collection(cls.collection_name)
        result = collection.delete_one({"payment_id": payment_id})
        return result.deleted_count > 0