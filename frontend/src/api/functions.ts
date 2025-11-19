/**
 * MongoDB Stored Functions (Procedures) API Client
 * Endpoints for calling server-side stored functions
 */

import { get, post } from './client';

// ============================================
// TYPES
// ============================================

export interface PatientAgeResponse {
  date_of_birth: string;
  age: number;
}

export interface PatientAgeWithDetailsResponse {
  patient_id: number;
  name: string;
  date_of_birth: string;
  age: number;
}

export interface PatientVisitCountResponse {
  patient_id: number;
  visit_count: number;
}

export interface PatientStatsResponse {
  patient_id: number;
  name: string;
  age: number;
  total_visits: number;
  email?: string;
  phone?: string;
}

export interface InvoiceTotalResponse {
  invoice_id: number;
  total: number;
}

export interface InvoiceCalculatedTotalResponse {
  invoice_id: number;
  invoice_date: string;
  status: string;
  calculated_total: number;
  line_items_count: number;
}

export interface StaffAppointmentCountResponse {
  staff_id: number;
  appointment_count: number;
}

export interface StaffStatsResponse {
  staff_id: number;
  name: string;
  email: string;
  active: boolean;
  total_appointments: number;
}

export interface AppointmentAvailabilityRequest {
  staff_id: number;
  start_time: string; // ISO format: "2024-12-25T10:00:00"
  end_time: string;   // ISO format: "2024-12-25T11:00:00"
}

export interface AppointmentAvailabilityResponse {
  staff_id: number;
  start_time: string;
  end_time: string;
  available: boolean;
  message: string;
}

export interface AppointmentValidationRequest {
  staff_id: number;
  scheduled_start: string;
  scheduled_end: string;
}

export interface AppointmentValidationResponse {
  valid: boolean;
  reason?: string;
  staff_name?: string;
  message?: string;
}

export interface StoredFunction {
  name: string;
  exists: boolean;
}

export interface FunctionsListResponse {
  count: number;
  functions: StoredFunction[];
}

export interface FunctionStatus {
  exists: boolean;
  status: string;
}

export interface FunctionsStatusResponse {
  all_functions_exist: boolean;
  functions: Record<string, FunctionStatus>;
}

export interface FunctionTestResult {
  success: boolean;
  result?: any;
  error?: string;
}

export interface FunctionsTestResponse {
  all_tests_passed: boolean;
  test_results: Record<string, FunctionTestResult>;
}

// ============================================
// FUNCTION 1: CALCULATE PATIENT AGE
// ============================================

/**
 * Calculate age from date of birth
 * @param dateOfBirth - Date in format "YYYY-MM-DD"
 */
export const calculatePatientAge = async (dateOfBirth: string): Promise<PatientAgeResponse> => {
  return get<PatientAgeResponse>(`/api/functions/patient-age/${dateOfBirth}`);
};

/**
 * Get age for a specific patient
 * @param patientId - Patient ID
 */
export const getPatientAge = async (patientId: number): Promise<PatientAgeWithDetailsResponse> => {
  return get<PatientAgeWithDetailsResponse>(`/api/patients/${patientId}/age`);
};

// ============================================
// FUNCTION 2: GET PATIENT VISIT COUNT
// ============================================

/**
 * Get total visit count for a patient
 * @param patientId - Patient ID
 */
export const getPatientVisitCount = async (patientId: number): Promise<PatientVisitCountResponse> => {
  return get<PatientVisitCountResponse>(`/api/functions/patient-visits/${patientId}`);
};

/**
 * Get comprehensive patient statistics
 * @param patientId - Patient ID
 */
export const getPatientStats = async (patientId: number): Promise<PatientStatsResponse> => {
  return get<PatientStatsResponse>(`/api/patients/${patientId}/stats`);
};

// ============================================
// FUNCTION 3: CALCULATE INVOICE TOTAL
// ============================================

/**
 * Calculate invoice total from line items
 * @param invoiceId - Invoice ID
 */
export const calculateInvoiceTotal = async (invoiceId: number): Promise<InvoiceTotalResponse> => {
  return get<InvoiceTotalResponse>(`/api/functions/invoice-total/${invoiceId}`);
};

/**
 * Get invoice with calculated total
 * @param invoiceId - Invoice ID
 */
export const getInvoiceCalculatedTotal = async (invoiceId: number): Promise<InvoiceCalculatedTotalResponse> => {
  return get<InvoiceCalculatedTotalResponse>(`/api/invoices/${invoiceId}/calculated-total`);
};

// ============================================
// FUNCTION 4: GET STAFF APPOINTMENT COUNT
// ============================================

/**
 * Get appointment count for a staff member
 * @param staffId - Staff ID
 */
export const getStaffAppointmentCount = async (staffId: number): Promise<StaffAppointmentCountResponse> => {
  return get<StaffAppointmentCountResponse>(`/api/functions/staff-appointments/${staffId}`);
};

/**
 * Get comprehensive staff statistics
 * @param staffId - Staff ID
 */
export const getStaffStats = async (staffId: number): Promise<StaffStatsResponse> => {
  return get<StaffStatsResponse>(`/api/staff/${staffId}/stats`);
};

// ============================================
// FUNCTION 5: CHECK APPOINTMENT AVAILABILITY
// ============================================

/**
 * Check if a time slot is available for scheduling
 * @param data - Appointment availability request
 */
export const checkAppointmentAvailability = async (
  data: AppointmentAvailabilityRequest
): Promise<AppointmentAvailabilityResponse> => {
  return post<AppointmentAvailabilityResponse>('/api/functions/check-availability', data);
};

/**
 * Validate appointment before creating
 * @param data - Appointment validation request
 */
export const validateAppointment = async (
  data: AppointmentValidationRequest
): Promise<AppointmentValidationResponse> => {
  return post<AppointmentValidationResponse>('/api/appointments/validate', data);
};

// ============================================
// ADMIN: FUNCTIONS MANAGEMENT
// ============================================

/**
 * List all stored functions in the database
 */
export const listStoredFunctions = async (): Promise<FunctionsListResponse> => {
  return get<FunctionsListResponse>('/api/functions/list');
};

/**
 * Check status of all expected stored functions
 */
export const getFunctionsStatus = async (): Promise<FunctionsStatusResponse> => {
  return get<FunctionsStatusResponse>('/api/functions/status');
};

/**
 * Force recreation of all stored functions (admin only)
 */
export const recreateAllFunctions = async (): Promise<{
  message: string;
  results: Record<string, boolean>;
}> => {
  return post('/api/functions/recreate');
};

/**
 * Test all stored functions with sample data
 */
export const testAllFunctions = async (): Promise<FunctionsTestResponse> => {
  return get<FunctionsTestResponse>('/api/functions/test');
};

/**
 * Generic function caller for arbitrary stored functions on the server
 * @param name - Function name
 * @param payload - Optional payload
 */
export const callFunction = async (name: string, payload?: any): Promise<any> => {
  return post(`/api/functions/${name}`, payload);
};

// ============================================
// COMBINED QUERIES
// ============================================

/**
 * Get complete patient profile using stored functions
 * @param patientId - Patient ID
 */
export const getPatientCompleteProfile = async (patientId: number): Promise<{
  stats: PatientStatsResponse;
  age: PatientAgeWithDetailsResponse;
  visitCount: PatientVisitCountResponse;
}> => {
  const [stats, age, visitCount] = await Promise.all([
    getPatientStats(patientId),
    getPatientAge(patientId),
    getPatientVisitCount(patientId),
  ]);

  return { stats, age, visitCount };
};

/**
 * Get complete staff profile using stored functions
 * @param staffId - Staff ID
 */
export const getStaffCompleteProfile = async (staffId: number): Promise<{
  stats: StaffStatsResponse;
  appointmentCount: StaffAppointmentCountResponse;
}> => {
  const [stats, appointmentCount] = await Promise.all([
    getStaffStats(staffId),
    getStaffAppointmentCount(staffId),
  ]);

  return { stats, appointmentCount };
};

/**
 * Validate and check availability for an appointment
 * @param data - Appointment data
 */
export const validateAndCheckAppointment = async (
  data: AppointmentValidationRequest
): Promise<{
  validation: AppointmentValidationResponse;
  availability: AppointmentAvailabilityResponse;
}> => {
  const [validation, availability] = await Promise.all([
    validateAppointment(data),
    checkAppointmentAvailability({
      staff_id: data.staff_id,
      start_time: data.scheduled_start,
      end_time: data.scheduled_end,
    }),
  ]);

  return { validation, availability };
};

/**
 * Get multiple patients' ages at once
 * @param patientIds - Array of patient IDs
 */
export const getMultiplePatientsAges = async (
  patientIds: number[]
): Promise<PatientAgeWithDetailsResponse[]> => {
  const promises = patientIds.map((id) => getPatientAge(id));
  return Promise.all(promises);
};

/**
 * Get multiple staff appointment counts at once
 * @param staffIds - Array of staff IDs
 */
export const getMultipleStaffAppointmentCounts = async (
  staffIds: number[]
): Promise<StaffAppointmentCountResponse[]> => {
  const promises = staffIds.map((id) => getStaffAppointmentCount(id));
  return Promise.all(promises);
};

/**
 * Calculate totals for multiple invoices
 * @param invoiceIds - Array of invoice IDs
 */
export const calculateMultipleInvoiceTotals = async (
  invoiceIds: number[]
): Promise<InvoiceTotalResponse[]> => {
  const promises = invoiceIds.map((id) => calculateInvoiceTotal(id));
  return Promise.all(promises);
};

/**
 * Check availability for multiple time slots
 * @param slots - Array of time slot requests
 */
export const checkMultipleTimeSlots = async (
  slots: AppointmentAvailabilityRequest[]
): Promise<AppointmentAvailabilityResponse[]> => {
  const promises = slots.map((slot) => checkAppointmentAvailability(slot));
  return Promise.all(promises);
};

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Format date for API calls
 * @param date - JavaScript Date object
 * @returns ISO format string "YYYY-MM-DDTHH:mm:ss"
 */
export const formatDateForAPI = (date: Date): string => {
  return date.toISOString().slice(0, 19);
};

/**
 * Calculate end time based on duration
 * @param startTime - Start time in ISO format
 * @param durationMinutes - Duration in minutes
 * @returns End time in ISO format
 */
export const calculateEndTime = (startTime: string, durationMinutes: number): string => {
  const start = new Date(startTime);
  const end = new Date(start.getTime() + durationMinutes * 60000);
  return formatDateForAPI(end);
};

/**
 * Check if time slot is during business hours
 * @param startTime - Start time in ISO format
 * @param endTime - End time in ISO format
 * @param businessStart - Business start hour (default: 8)
 * @param businessEnd - Business end hour (default: 18)
 */
export const isWithinBusinessHours = (
  startTime: string,
  endTime: string,
  businessStart: number = 8,
  businessEnd: number = 18
): boolean => {
  const start = new Date(startTime);
  const end = new Date(endTime);
  
  const startHour = start.getHours();
  const endHour = end.getHours();
  const endMinutes = end.getMinutes();
  
  return (
    startHour >= businessStart &&
    (endHour < businessEnd || (endHour === businessEnd && endMinutes === 0))
  );
};

// Export all as functionsApi namespace
export const functionsApi = {
  // Patient functions
  calculatePatientAge,
  getPatientAge,
  getPatientVisitCount,
  getPatientStats,
  
  // Invoice functions
  calculateInvoiceTotal,
  getInvoiceCalculatedTotal,
  
  // Staff functions
  getStaffAppointmentCount,
  getStaffStats,
  
  // Appointment functions
  checkAppointmentAvailability,
  validateAppointment,
  
  // Admin
  listStoredFunctions,
  getFunctionsStatus,
  recreateAllFunctions,
  testAllFunctions,
  
  // Combined queries
  getPatientCompleteProfile,
  getStaffCompleteProfile,
  validateAndCheckAppointment,
  getMultiplePatientsAges,
  getMultipleStaffAppointmentCounts,
  calculateMultipleInvoiceTotals,
  checkMultipleTimeSlots,
  
  // Utilities
  formatDateForAPI,
  calculateEndTime,
  isWithinBusinessHours,
};