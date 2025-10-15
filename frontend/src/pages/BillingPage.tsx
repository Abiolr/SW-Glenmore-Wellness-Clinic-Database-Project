/**
 * BILLING PAGE
 * 
 * Purpose:
 * - Manage all financial transactions and billing operations
 * - Handle multiple payment methods and insurance claims
 * 
 * Features:
 * - View all billing records with filters:
 *   - By patient
 *   - By date range
 *   - By payment status (paid, pending, overdue)
 *   - By payment method
 * - Create new bills for services:
 *   - Link to appointments/visits
 *   - Add procedures and diagnoses
 *   - Calculate fees
 *   - Apply insurance or government coverage
 * - Record payments:
 *   - Out-of-pocket (immediate or end-of-month)
 *   - Insurance (record co-pay, submit claim)
 *   - Government health coverage (medical card verification)
 * - Update billing records
 * - Generate invoices and receipts
 * - Track insurance claims:
 *   - Submitted claims
 *   - Pending reimbursements
 *   - Paid claims
 * - View outstanding balances by patient
 * - Process prescription billing (from pharmacy)
 * - Display payment breakdown:
 *   - Total charges
 *   - Amount paid by patient
 *   - Amount paid by insurance
 *   - Amount paid by government
 *   - Outstanding balance
 * 
 * Components:
 * - Billing records table
 * - Payment entry form
 * - Invoice generator
 * - Insurance claim submission form
 * - Outstanding balance dashboard
 * - Payment method selector
 * 
 * Data Requirements:
 * - Billing/invoice records
 * - Payment records
 * - Patient information (including insurance/medical card)
 * - Service/procedure codes and fees
 * - Insurance claim status
 * - Prescription charges
 * 
 * Database Operations:
 * - INSERT new billing records and payments
 * - UPDATE payment status and claim information
 * - SELECT billing data with joins to patients, appointments, procedures
 * - Calculate totals and balances (potential views)
 * - Track payment history
 * 
 * Business Rules:
 * - Medical care available to all regardless of payment ability
 * - Insurance patients pay co-pay immediately
 * - Government coverage patients pay nothing (clinic billed later)
 * - Out-of-pocket patients can pay immediately or receive end-of-month bill
 */