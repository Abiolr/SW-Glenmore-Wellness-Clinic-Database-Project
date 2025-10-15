/**
 * APPOINTMENT PAGE
 * 
 * Purpose:
 * - Schedule and manage patient appointments
 * - Handle both pre-scheduled appointments and walk-ins
 * 
 * Features:
 * - Calendar view showing daily/weekly schedules
 * - Book new appointments (select patient, practitioner, date/time, visit type)
 * - Modify existing appointments
 * - Cancel/delete appointments
 * - Mark appointments as completed
 * - Register walk-in patients
 * - Assign walk-ins to available practitioners
 * - View appointment details:
 *   - Patient information
 *   - Practitioner assigned
 *   - Appointment time (typically 10-minute slots)
 *   - Visit type (checkup, immunization, treatment, etc.)
 *   - Status (scheduled, completed, cancelled, no-show)
 * - Filter appointments by:
 *   - Date range
 *   - Practitioner
 *   - Patient
 *   - Status
 * 
 * Components:
 * - Calendar/schedule grid
 * - Appointment booking form
 * - Walk-in registration form
 * - Appointment list/table view
 * - Time slot selector
 * - Practitioner availability checker
 * 
 * Data Requirements:
 * - Appointments table
 * - Patient information (for selection)
 * - Staff/practitioner schedules
 * - Visit types
 * - Room availability
 * 
 * Database Operations:
 * - INSERT new appointments
 * - UPDATE appointment details and status
 * - DELETE/cancel appointments
 * - SELECT appointments with joins to patients and staff
 * - Check practitioner availability (potential stored procedure)
 */