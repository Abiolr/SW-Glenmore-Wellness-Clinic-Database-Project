/**
 * STAFF PAGE
 * 
 * Purpose:
 * - Manage medical and administrative staff information
 * - Handle staff scheduling and assignments
 * 
 * Features:
 * - View all staff members with their roles:
 *   - Physicians (with specializations: pediatrics, internal medicine, midwifery)
 *   - Nurse Practitioners
 *   - Registered Nurses
 *   - Midwives
 *   - Pharmacist
 *   - Medical Technician
 *   - Office Administrator
 *   - Receptionist
 *   - Bookkeeper
 * - Add new staff members
 * - Edit staff information
 * - Remove/deactivate staff
 * - View staff details:
 *   - Personal information
 *   - Role and specialization
 *   - Contact information
 *   - License/certification numbers
 * - Manage weekly coverage schedule:
 *   - Assign staff to specific days/shifts
 *   - Set on-call assignments
 *   - Ensure minimum coverage (2 physicians or 1 physician + 1 NP, 1 RN, 1 midwife)
 * - View individual staff schedules
 * - Track staff availability
 * 
 * Components:
 * - Staff directory table/grid
 * - Staff add/edit form
 * - Weekly schedule grid
 * - On-call assignment interface
 * - Staff detail view panel
 * 
 * Data Requirements:
 * - Staff table (all professional and non-professional staff)
 * - Staff roles/types
 * - Specializations
 * - Weekly schedule assignments
 * - On-call schedule
 * 
 * Database Operations:
 * - INSERT new staff members
 * - UPDATE staff information and schedules
 * - DELETE/deactivate staff
 * - SELECT staff with filters by role/specialization
 * - Manage schedule assignments
 */