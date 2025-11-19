/**
 * MongoDB Views API Client
 * Endpoints for accessing pre-computed MongoDB views
 */

import { get } from './client';

// ============================================
// TYPES
// ============================================

export interface PatientFullDetails {
  _id: string;
  patient_id: number;
  first_name: string;
  last_name: string;
  full_name: string;
  date_of_birth: string;
  phone: string;
  email: string;
  gov_card_no?: string;
  insurance_no?: string;
  total_visits: number;
  completed_visits: number;
  total_appointments: number;
  last_visit_date?: string;
  has_active_visits: boolean;
}

export interface StaffAppointmentsSummary {
  _id: string;
  staff_id: number;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  phone: string;
  active: boolean;
  total_appointments: number;
  total_visits: number;
  walkin_appointments: number;
  scheduled_appointments: number;
}

export interface ActiveVisitOverview {
  _id: string;
  visit_id: number;
  patient_id: number;
  patient_name: string;
  patient_phone: string;
  staff_id: number;
  staff_name: string;
  visit_type: string;
  start_time: string;
  notes?: string;
  appointment_id?: number;
}

export interface InvoicePaymentSummary {
  _id: string;
  invoice_id: number;
  patient_id: number;
  patient_name: string;
  patient_email?: string;
  invoice_date: string;
  status: string;
  total_amount: number;
  total_paid: number;
  balance: number;
  payment_count: number;
  line_item_count: number;
  is_fully_paid: boolean;
}

export interface AppointmentCalendarView {
  _id: string;
  appointment_id: number;
  patient_id: number;
  patient_name: string;
  patient_phone: string;
  patient_email?: string;
  staff_id: number;
  staff_name: string;
  scheduled_start: string;
  scheduled_end: string;
  is_walkin: boolean;
  appointment_type: string;
  created_at: string;
  calendar_title: string;
  color: string;
}

export interface ViewsStatus {
  patient_full_details: { exists: boolean; document_count: number };
  staff_appointments_summary: { exists: boolean; document_count: number };
  active_visits_overview: { exists: boolean; document_count: number };
  invoice_payment_summary: { exists: boolean; document_count: number };
  appointment_calendar_view: { exists: boolean; document_count: number };
}

// ============================================
// VIEW 1: PATIENT FULL DETAILS
// ============================================

/**
 * Get all patients with comprehensive details and statistics
 */
export const getAllPatientsFullDetails = async (): Promise<PatientFullDetails[]> => {
  return get<PatientFullDetails[]>('/api/views/patients/full-details');
};

/**
 * Get patients with active visits only
 */
export const getActivePatientsFullDetails = async (): Promise<PatientFullDetails[]> => {
  return get<PatientFullDetails[]>('/api/views/patients/active');
};

/**
 * Get full details and statistics for a specific patient
 */
export const getPatientStats = async (patientId: number): Promise<PatientFullDetails> => {
  return get<PatientFullDetails>(`/api/views/patients/stats/${patientId}`);
};

// ============================================
// VIEW 2: STAFF APPOINTMENTS SUMMARY
// ============================================

/**
 * Get staff workload summary
 * @param activeOnly - Filter to active staff only (default: true)
 */
export const getStaffSummary = async (activeOnly: boolean = true): Promise<StaffAppointmentsSummary[]> => {
  return get<StaffAppointmentsSummary[]>(`/api/views/staff/summary?active_only=${activeOnly}`);
};

/**
 * Get staff sorted by workload (most appointments first)
 */
export const getStaffWorkload = async (): Promise<StaffAppointmentsSummary[]> => {
  return get<StaffAppointmentsSummary[]>('/api/views/staff/workload');
};

/**
 * Get statistics for a specific staff member
 */
export const getStaffStats = async (staffId: number): Promise<StaffAppointmentsSummary> => {
  return get<StaffAppointmentsSummary>(`/api/views/staff/stats/${staffId}`);
};

// ============================================
// VIEW 3: ACTIVE VISITS OVERVIEW
// ============================================

/**
 * Get all currently active visits (not completed)
 */
export const getActiveVisits = async (): Promise<ActiveVisitOverview[]> => {
  return get<ActiveVisitOverview[]>('/api/views/visits/active');
};

/**
 * Get active visits by type
 * @param visitType - checkup, immunization, illness, prenatal, postnatal
 */
export const getActiveVisitsByType = async (visitType: string): Promise<ActiveVisitOverview[]> => {
  return get<ActiveVisitOverview[]>(`/api/views/visits/by-type/${visitType}`);
};

/**
 * Get active visits for a specific staff member
 */
export const getActiveVisitsByStaff = async (staffId: number): Promise<ActiveVisitOverview[]> => {
  return get<ActiveVisitOverview[]>(`/api/views/visits/by-staff/${staffId}`);
};

/**
 * Get active visits for a specific patient
 */
export const getActiveVisitsByPatient = async (patientId: number): Promise<ActiveVisitOverview[]> => {
  return get<ActiveVisitOverview[]>(`/api/views/visits/by-patient/${patientId}`);
};

// ============================================
// VIEW 4: INVOICE PAYMENT SUMMARY
// ============================================

/**
 * Get invoice overview with payment details
 */
export const getInvoiceSummary = async (): Promise<InvoicePaymentSummary[]> => {
  return get<InvoicePaymentSummary[]>('/api/views/invoices/summary');
};

/**
 * Get invoices that are not fully paid
 */
export const getUnpaidInvoices = async (): Promise<InvoicePaymentSummary[]> => {
  return get<InvoicePaymentSummary[]>('/api/views/invoices/unpaid');
};

/**
 * Get invoices with outstanding balance
 */
export const getInvoicesWithBalance = async (): Promise<InvoicePaymentSummary[]> => {
  return get<InvoicePaymentSummary[]>('/api/views/invoices/with-balance');
};

/**
 * Get invoice summary for a specific patient
 */
export const getPatientInvoiceSummary = async (patientId: number): Promise<InvoicePaymentSummary[]> => {
  return get<InvoicePaymentSummary[]>(`/api/views/invoices/by-patient/${patientId}`);
};

/**
 * Get overall invoice statistics
 */
export const getInvoiceStats = async (): Promise<{
  total_invoices: number;
  total_amount: number;
  total_paid: number;
  total_balance: number;
  fully_paid_count: number;
  unpaid_count: number;
}> => {
  return get('/api/views/invoices/stats');
};

// ============================================
// VIEW 5: APPOINTMENT CALENDAR VIEW
// ============================================

/**
 * Get appointments formatted for calendar display
 */
export const getCalendarAppointments = async (): Promise<AppointmentCalendarView[]> => {
  return get<AppointmentCalendarView[]>('/api/views/appointments/calendar');
};

/**
 * Get walk-in appointments only
 */
export const getWalkinAppointments = async (): Promise<AppointmentCalendarView[]> => {
  return get<AppointmentCalendarView[]>('/api/views/appointments/walkins');
};

/**
 * Get scheduled appointments only
 */
export const getScheduledAppointments = async (): Promise<AppointmentCalendarView[]> => {
  return get<AppointmentCalendarView[]>('/api/views/appointments/scheduled');
};

/**
 * Get appointments for a specific staff member
 */
export const getStaffCalendarAppointments = async (staffId: number): Promise<AppointmentCalendarView[]> => {
  return get<AppointmentCalendarView[]>(`/api/views/appointments/staff/${staffId}`);
};

/**
 * Get appointments for a specific patient
 */
export const getPatientCalendarAppointments = async (patientId: number): Promise<AppointmentCalendarView[]> => {
  return get<AppointmentCalendarView[]>(`/api/views/appointments/patient/${patientId}`);
};

/**
 * Get appointments within a date range
 * @param startDate - Start date in ISO format (YYYY-MM-DD)
 * @param endDate - End date in ISO format (YYYY-MM-DD)
 */
export const getAppointmentsByDateRange = async (
  startDate: string,
  endDate: string
): Promise<AppointmentCalendarView[]> => {
  return get<AppointmentCalendarView[]>(
    `/api/views/appointments/date-range?start_date=${startDate}&end_date=${endDate}`
  );
};

// ============================================
// ADMIN: VIEWS MANAGEMENT
// ============================================

/**
 * Check status of all MongoDB views
 */
export const getViewsStatus = async (): Promise<ViewsStatus> => {
  return get<ViewsStatus>('/api/views/status');
};

/**
 * Force recreation of all views (admin only)
 */
export const recreateAllViews = async (): Promise<{
  message: string;
  results: Record<string, boolean>;
}> => {
  return get('/api/views/recreate');
};

/**
 * Lightweight helper used by frontend hooks to fetch available views
 * returns array of view names for display or selection
 */
export const fetchViews = async (): Promise<string[]> => {
  try {
    const status = await getViewsStatus();
    return Object.keys(status).filter((k) => Object.prototype.hasOwnProperty.call(status, k));
  } catch (err) {
    console.warn('fetchViews failed, returning empty array', err);
    return [];
  }
};

// ============================================
// COMBINED QUERIES
// ============================================

/**
 * Get comprehensive dashboard data using multiple views
 */
export const getDashboardData = async (): Promise<{
  activePatients: PatientFullDetails[];
  staffWorkload: StaffAppointmentsSummary[];
  activeVisits: ActiveVisitOverview[];
  unpaidInvoices: InvoicePaymentSummary[];
  todayAppointments: AppointmentCalendarView[];
  stats: {
    totalPatients: number;
    activeVisits: number;
    staffOnDuty: number;
    unpaidInvoices: number;
  };
}> => {
  // Fetch all data in parallel
  const [
    activePatients,
    staffWorkload,
    activeVisits,
    unpaidInvoices,
    todayAppointments,
  ] = await Promise.all([
    getActivePatientsFullDetails(),
    getStaffSummary(true),
    getActiveVisits(),
    getUnpaidInvoices(),
    getCalendarAppointments(), // You can filter by date in component
  ]);

  return {
    activePatients,
    staffWorkload,
    activeVisits,
    unpaidInvoices,
    todayAppointments,
    stats: {
      totalPatients: activePatients.length,
      activeVisits: activeVisits.length,
      staffOnDuty: staffWorkload.length,
      unpaidInvoices: unpaidInvoices.length,
    },
  };
};

/**
 * Get weekly schedule data
 */
export const getWeeklyScheduleData = async (
  startDate: string,
  endDate: string
): Promise<{
  appointments: AppointmentCalendarView[];
  staffSummary: StaffAppointmentsSummary[];
}> => {
  const [appointments, staffSummary] = await Promise.all([
    getAppointmentsByDateRange(startDate, endDate),
    getStaffSummary(true),
  ]);

  return { appointments, staffSummary };
};

/**
 * Get patient complete profile (for billing/statements)
 */
export const getPatientCompleteProfile = async (patientId: number): Promise<{
  patient: PatientFullDetails;
  invoices: InvoicePaymentSummary[];
  appointments: AppointmentCalendarView[];
  activeVisits: ActiveVisitOverview[];
}> => {
  const [patient, invoices, appointments, activeVisits] = await Promise.all([
    getPatientStats(patientId),
    getPatientInvoiceSummary(patientId),
    getPatientCalendarAppointments(patientId),
    getActiveVisitsByPatient(patientId),
  ]);

  return { patient, invoices, appointments, activeVisits };
};

// Export all as viewsApi namespace
export const viewsApi = {
  // Patient views
  getAllPatientsFullDetails,
  getActivePatientsFullDetails,
  getPatientStats,
  
  // Staff views
  getStaffSummary,
  getStaffWorkload,
  getStaffStats,
  
  // Visit views
  getActiveVisits,
  getActiveVisitsByType,
  getActiveVisitsByStaff,
  getActiveVisitsByPatient,
  
  // Invoice views
  getInvoiceSummary,
  getUnpaidInvoices,
  getInvoicesWithBalance,
  getPatientInvoiceSummary,
  getInvoiceStats,
  
  // Appointment views
  getCalendarAppointments,
  getWalkinAppointments,
  getScheduledAppointments,
  getStaffCalendarAppointments,
  getPatientCalendarAppointments,
  getAppointmentsByDateRange,
  
  // Admin
  getViewsStatus,
  recreateAllViews,
  
  // Combined
  getDashboardData,
  getWeeklyScheduleData,
  getPatientCompleteProfile,
};