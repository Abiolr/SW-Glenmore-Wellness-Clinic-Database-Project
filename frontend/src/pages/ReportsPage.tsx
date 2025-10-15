/**
 * REPORTS PAGE
 * 
 * Purpose:
 * - Generate and display various clinic reports for management and operations
 * - Meet project requirement of at least 3 meaningful reports
 * 
 * Available Reports:
 * 
 * 1. WEEKLY COVERAGE SCHEDULE
 *    - Lists staff assignments for each day of the week
 *    - Shows which practitioners are on duty
 *    - Displays emergency on-call contacts
 *    - Based on monthly schedules prepared by administrator
 * 
 * 2. DAILY MASTER SCHEDULE
 *    - Detailed schedule for all practitioners for a specific day
 *    - Shows all appointments with patient names and times
 *    - Indicates walk-in hours for each practitioner
 *    - Displays 10-minute time slots (flexible for extended care)
 * 
 * 3. INDIVIDUAL PRACTITIONER'S DAILY SCHEDULE
 *    - Personalized schedule for a selected practitioner
 *    - Lists all appointments with patient details
 *    - Shows available slots for walk-ins
 *    - Updated in real-time by nurses for walk-in assignments
 * 
 * 4. PHYSICIAN'S STATEMENT (for Insurance Forms)
 *    - Pre-printed receipt format
 *    - Includes clinic details and professional staff information
 *    - Shows visit types, procedures performed, and diagnoses
 *    - Displays diagnostic codes and fee details
 *    - Records payments received and outstanding balances
 *    - Used for insurance claim submission
 * 
 * 5. PATIENT MONTHLY STATEMENT
 *    - Summary of all services provided to patient in a month
 *    - Lists all charges, payments received, and dates
 *    - Shows outstanding balance
 *    - Generated for patients with unpaid accounts
 * 
 * 6. DAILY LABORATORY LOG
 *    - Records all lab tests conducted on a specific day
 *    - Shows patient names, test types, and ordering practitioners
 *    - Includes test results when available
 * 
 * 7. DAILY DELIVERY ROOM LOG
 *    - Tracks all deliveries performed on a specific day
 *    - Shows mother's information, delivery time, and outcomes
 *    - Lists attending midwife/physician
 * 
 * 8. RECOVERY ROOM LOG
 *    - Logs all recovery room usage
 *    - Includes patient details, admission/discharge times
 *    - Shows practitioner sign-offs
 *    - Records nurse observations and medical checks
 * 
 * 9. MONTHLY ACTIVITY REPORT
 *    - Comprehensive summary of clinic operations for the month
 *    - Includes:
 *      * Total number of patient visits
 *      * Number of surgeries performed
 *      * Number of deliveries
 *      * Number of lab tests conducted
 *      * Number of prescriptions filled
 *      * Average visit duration
 *      * Other key performance metrics (KPIs)
 *    - Used by management for operational analysis
 * 
 * Features:
 * - Report selection dropdown/menu
 * - Date range picker (for time-based reports)
 * - Practitioner selector (for individual schedules)
 * - Patient selector (for patient-specific reports)
 * - Export options (PDF, CSV, print)
 * - Preview before generating
 * - Save/email report functionality
 * 
 * Components:
 * - Report selector interface
 * - Filter/parameter inputs
 * - Report preview area
 * - Export buttons
 * - Print formatting
 * 
 * Data Requirements:
 * - Must use VIEWS for complex queries with JOINS (project requirement)
 * - Aggregate data from multiple tables
 * - Date-based filtering
 * - Grouping and calculations
 * 
 * Database Operations:
 * - SELECT from views (minimum 5 views required for project)
 * - Complex JOINs across multiple tables
 * - Aggregate functions (COUNT, AVG, SUM)
 * - Date range filtering
 * - GROUP BY for summaries
 * 
 * Notes:
 * - Reports must NOT be simple table dumps
 * - Must provide meaningful insights
 * - May require multiple database queries per report
 * - Should demonstrate use of views, joins, and aggregate functions
 */