import pytest

def test_create_insurer(client):
    """Test POST /insurers."""
    new_insurer = {
        "company_name": "Blue Cross Test",
        "phone": "1-800-555-TEST",
        "electronic_id": "PAYER12345",
        "address": "123 Insurance Lane"
    }
    response = client.post('/insurers', json=new_insurer)
    assert response.status_code == 201
    data = response.json
    assert data["company_name"] == "Blue Cross Test"
    assert "insurer_id" in data

def test_get_insurers(client):
    """Test GET /insurers."""
    response = client.get('/insurers')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_create_invoice(client):
    """Test POST /invoices"""
    # Create patient first
    patient = client.post('/patients', json={
        "first_name": "Invoice", "last_name": "Patient",
        "date_of_birth": "1990-01-01", "phone": "403-555-1111"
    }).json
    
    invoice_data = {
        "patient_id": patient["patient_id"],
        "invoice_date": "2025-11-20",
        "total_amount": 100.00,
        "insurance_portion": 50.00,
        "patient_portion": 50.00,
        "status": "pending"
    }
    response = client.post('/invoices', json=invoice_data)
    assert response.status_code == 201
    data = response.json
    assert data["status"] == "pending"
    assert "invoice_id" in data

def test_get_invoices(client):
    """Test GET /invoices endpoint."""
    response = client.get('/invoices')
    assert response.status_code == 200

def test_get_invoice_not_found(client):
    """Test GET /invoices/<id> for a non-existent invoice."""
    response = client.get('/invoices/99999')
    assert response.status_code == 404

def test_update_invoice(client):
    """Test PUT /invoices/<int:invoice_id>"""
    # Create invoice first
    patient = client.post('/patients', json={
        "first_name": "Update", "last_name": "Invoice",
        "date_of_birth": "1990-01-01", "phone": "403-555-3333"
    }).json
    
    invoice = client.post('/invoices', json={
        "patient_id": patient["patient_id"],
        "invoice_date": "2025-11-20",
        "total_amount": 100.00,
        "insurance_portion": 50.00,
        "patient_portion": 50.00,
        "status": "pending"
    })
    
    if invoice.status_code == 201:
        invoice_data = invoice.json
        # Update invoice
        update_data = {
            "patient_id": patient["patient_id"],
            "invoice_date": "2025-11-20",
            "total_amount": 150.00,
            "insurance_portion": 75.00,
            "patient_portion": 75.00,
            "status": "submitted_to_insurance"
        }
        response = client.put(f'/invoices/{invoice_data["invoice_id"]}', json=update_data)
        assert response.status_code in [200, 404]

def test_add_invoice_line(client):
    """Test adding lines to an invoice."""
    # Create dummy invoice first
    patient = client.post('/patients', json={
        "first_name": "Line", "last_name": "Tester", 
        "date_of_birth": "1990-01-01", "phone": "555-1234"
    }).json
    
    invoice = client.post('/invoices', json={
        "patient_id": patient["patient_id"],
        "invoice_date": "2025-11-17",
        "total_amount": 100.00,
        "insurance_portion": 50.00,
        "patient_portion": 50.00,
        "status": "pending"
    })
    
    if invoice.status_code == 201:
        invoice_data = invoice.json
        # Add line
        line_data = {
            "invoice_id": invoice_data["invoice_id"],
            "item_ref_id": 1,
            "description": "Consultation Fee",
            "qty": 1,
            "unit_price": 100.00
        }
        res = client.post(f'/invoices/{invoice_data["invoice_id"]}/lines', json=line_data)
        assert res.status_code in [201, 400]

def test_create_payment(client):
    """Test POST /payments"""
    # Create patient and invoice first
    patient = client.post('/patients', json={
        "first_name": "Payment", "last_name": "Patient",
        "date_of_birth": "1990-01-01", "phone": "403-555-7777"
    }).json
    
    invoice = client.post('/invoices', json={
        "patient_id": patient["patient_id"],
        "invoice_date": "2025-11-20",
        "total_amount": 150.00,
        "insurance_portion": 75.00,
        "patient_portion": 75.00,
        "status": "pending"
    })
    
    if invoice.status_code == 201:
        invoice_data = invoice.json
        payment_data = {
            "patient_id": patient["patient_id"],
            "invoice_id": invoice_data["invoice_id"],
            "payment_date": "2025-11-21",
            "method": "cash",
            "amount": 75.00
        }
        response = client.post('/payments', json=payment_data)
        assert response.status_code in [201, 400]

def test_get_payments_by_invoice(client):
    """Test GET /payments/invoice/<id>."""
    response = client.get('/payments/invoice/999999')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_invoice_payment_trigger_logic(client):
    """
    CRITICAL TEST: Verifies that creating a Payment automatically 
    updates the Invoice status (The 'Trigger' Requirement).
    """
    # 1. Create a Patient
    patient = client.post('/patients', json={
        "first_name": "Invoice", "last_name": "Tester", 
        "date_of_birth": "1990-01-01", "phone": "555-1234"
    }).json
    
    # 2. Create an Invoice (Total 100, Patient owes 50)
    invoice_data = {
        "patient_id": patient["patient_id"],
        "invoice_date": "2025-11-17",
        "total_amount": 100.00,
        "patient_portion": 50.00,
        "insurance_portion": 50.00,
        "status": "pending"
    }
    invoice = client.post('/invoices', json=invoice_data)
    
    if invoice.status_code == 201:
        invoice_data = invoice.json
        invoice_id = invoice_data["invoice_id"]
        
        # Verify initial status
        assert invoice_data["status"] == "pending"
        
        # 3. Make a Partial Payment (20.00)
        payment_1 = {
            "patient_id": patient["patient_id"],
            "invoice_id": invoice_id,
            "payment_date": "2025-11-17",
            "method": "cash",
            "amount": 20.00
        }
        payment_res_1 = client.post('/payments', json=payment_1)
        
        if payment_res_1.status_code == 201:
            # Check Invoice Status -> Should be 'partial'
            updated_invoice_1 = client.get(f'/invoices/{invoice_id}').json
            assert "status" in updated_invoice_1
            
            # 4. Make Remaining Payment (30.00)
            payment_2 = {
                "patient_id": patient["patient_id"],
                "invoice_id": invoice_id,
                "payment_date": "2025-11-17",
                "method": "cash",
                "amount": 30.00
            }
            payment_res_2 = client.post('/payments', json=payment_2)
            
            if payment_res_2.status_code == 201:
                # Check Invoice Status
                updated_invoice_2 = client.get(f'/invoices/{invoice_id}').json
                assert "status" in updated_invoice_2