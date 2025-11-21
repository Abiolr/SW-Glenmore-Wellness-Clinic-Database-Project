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
  // Calculate age in the frontend to avoid calling MongoDB stored JS
  const dob = new Date(dateOfBirth);
  if (isNaN(dob.getTime())) throw new Error('Invalid date');
  const today = new Date();
  let age = today.getFullYear() - dob.getFullYear();
  const m = today.getMonth() - dob.getMonth();
  if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) {
    age--;
  }
  return { date_of_birth: dateOfBirth, age };
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
  // Backend provides appointments by patient; count them client-side
  const appointments = await get<any[]>(`/appointments/patient/${patientId}`);
  return { patient_id: patientId, visit_count: Array.isArray(appointments) ? appointments.length : 0 };
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
  // Backend does not currently expose /api/functions/invoice-total;
  // compute total from invoice line items via existing invoice lines endpoint.
  const lines = await get<any[]>(`/invoices/${invoiceId}/lines`);
  const total = lines.reduce((sum, l) => sum + ((l.qty || 0) * (l.unit_price || 0)), 0);
  return { invoice_id: invoiceId, total };
};

/**
 * Get invoice with calculated total
 * @param invoiceId - Invoice ID
 */
export const getInvoiceCalculatedTotal = async (invoiceId: number): Promise<InvoiceCalculatedTotalResponse> => {
  // Backend exposes invoice and invoice lines endpoints. Build the
  // calculated-total response by fetching both and computing the total.
  const invoice = await get<any>(`/invoices/${invoiceId}`);
  const lines = await get<any[]>(`/invoices/${invoiceId}/lines`);

  const calculated_total = lines.reduce((sum, l) => sum + ((l.qty || 0) * (l.unit_price || 0)), 0);
  const line_items_count = lines.length;

  return {
    invoice_id: invoice.invoice_id ?? invoiceId,
    invoice_date: invoice.invoice_date ?? invoice.created_at ?? '',
    status: invoice.status ?? 'unknown',
    calculated_total,
    line_items_count,
  };
};

// ============================================
// FUNCTION 4: GET STAFF APPOINTMENT COUNT
// ============================================

/**
 * Get appointment count for a staff member
 * @param staffId - Staff ID
 */
export const getStaffAppointmentCount = async (staffId: number): Promise<StaffAppointmentCountResponse> => {
  // Use appointments by staff endpoint and count client-side
  const appointments = await get<any[]>(`/appointments/staff/${staffId}`);
  return { staff_id: staffId, appointment_count: Array.isArray(appointments) ? appointments.length : 0 };
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
  // Perform availability check client-side by fetching staff appointments
  const { staff_id, start_time, end_time } = data;
  const appts = await get<any[]>(`/appointments/staff/${staff_id}`);
  const start = new Date(start_time);
  const end = new Date(end_time);

  const overlaps = (appts || []).some((a) => {
    const aStart = new Date(a.scheduled_start);
    const aEnd = new Date(a.scheduled_end);
    return (start < aEnd && end > aStart);
  });

  return {
    staff_id,
    start_time,
    end_time,
    available: !overlaps,
    message: overlaps ? 'Time slot conflicts with existing appointment' : 'Available'
  };
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

export interface DeliveryResponse {
  id: number;
  patient_id: number;
  practitioner_id: number;
  delivery_date: string;
  notes: string;
}

export const getDeliveryByVisit = async (visitId: number): Promise<DeliveryResponse> => {
  return get<DeliveryResponse>(`/deliveries/visit/${visitId}`);
};


export interface LabTestResponse {
  id: number;
  visit_id: number;
  test_name: string;
  result: string;
  practitioner_id: number;
  ordered_date: string;
}

export const getLabTestsByVisit = async (visitId: number): Promise<LabTestResponse[]> => {
  return get<LabTestResponse[]>(`/lab-tests/visit/${visitId}`);
};


export interface RecoveryStayResponse {
  stay_id: number;
  patient_id: number;
  admit_time: string;
  discharge_time?: string | null;
  discharged_by?: number | null;
}

export const getRecoveryStay = async (stayId: number): Promise<RecoveryStayResponse> => {
  return get<RecoveryStayResponse>(`/recovery-stays/${stayId}`);
};


export interface RecoveryObservationResponse {
  stay_id: number;
  text_on: string;
  observed_at?: string | null;
  notes: string;
}

export const createRecoveryObservation = async (data: {
  stay_id: number;
  // Accept either `text_on` (preferred) or `observation_time` and map it
  text_on?: string;
  observation_time?: string;
  notes: string;
}): Promise<RecoveryObservationResponse> => {
  const payload: any = {
    stay_id: data.stay_id,
    notes: data.notes,
  };
  // prefer text_on if provided, otherwise map observation_time -> text_on
  payload.text_on = data.text_on ?? data.observation_time ?? new Date().toISOString();
  return post<RecoveryObservationResponse>('/recovery-observations', payload);
};

/**
 * Update a recovery stay (used for discharge/sign-off)
 */
export const updateRecoveryStay = async (stayId: number, data: any): Promise<RecoveryStayResponse> => {
  return fetch(`${import.meta.env.VITE_API_URL || ''}/recovery-stays/${stayId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }).then((r) => {
    if (!r.ok) throw new Error('Failed to update stay');
    return r.json();
  });
};

/**
 * Create a recovery stay
 */
export const createRecoveryStay = async (data: any): Promise<any> => {
  return post<any>('/recovery-stays', data);
};

/**
 * Get observations for a recovery stay
 */
export const getRecoveryObservationsByStay = async (stayId: number): Promise<RecoveryObservationResponse[]> => {
  return get<RecoveryObservationResponse[]>(`/recovery-observations/stay/${stayId}`);
};

/**
 * Create lab test
 */
export const createLabTest = async (data: any): Promise<any> => {
  return post<any>('/lab-tests', data);
};

// ============================================
// Additional Billing & CRUD Wrappers
// ============================================

/**
 * Get aggregated invoice summary (server-side aggregation)
 */
export const getInvoiceAggregation = async (invoiceId: number): Promise<any> => {
  return get<any>(`/api/invoices/${invoiceId}/summary`);
};

/**
 * Insurer CRUD
 */
export const getInsurers = async (): Promise<any[]> => {
  return get<any[]>('/insurers');
};

export const createInsurer = async (data: any): Promise<any> => {
  return post<any>('/insurers', data);
};

/**
 * Prescriptions
 */
export const getPrescriptionsByVisit = async (visitId: number): Promise<any[]> => {
  return get<any[]>(`/prescriptions/visit/${visitId}`);
};

export const createPrescription = async (data: any): Promise<any> => {
  return post<any>('/prescriptions', data);
};

export const getPrescriptionDetails = async (prescriptionId: number): Promise<any> => {
  return get<any>(`/prescriptions/${prescriptionId}/details`);
};

/**
 * Drugs lookup
 */
export const getDrugs = async (): Promise<any[]> => {
  return get<any[]>('/drugs');
};

/**
 * Delivery create
 */
export const createDelivery = async (data: any): Promise<any> => {
  return post<any>('/deliveries', data);
};




// ============================================
// ADMIN: FUNCTIONS MANAGEMENT
// ============================================

/**
 * List all stored functions in the database
 */
export const listStoredFunctions = async (): Promise<FunctionsListResponse> => {
  // Listing stored JS functions is not supported on Atlas (frontend-only fallback)
  return Promise.reject(new Error('Listing stored functions is not supported in frontend-only mode'));
};

/**
 * Check status of all expected stored functions
 */
export const getFunctionsStatus = async (): Promise<FunctionsStatusResponse> => {
  // Use system status endpoint as a best-effort substitute
  try {
    const sys = await get<any>('/health');
    return {
      all_functions_exist: !!sys.stored_functions?.all_exist,
      functions: {},
    } as FunctionsStatusResponse;
  } catch (e) {
    return Promise.reject(new Error('Functions status not available'));
  }
};

/**
 * Force recreation of all stored functions (admin only)
 */
export const recreateAllFunctions = async (): Promise<{
  message: string;
  results: Record<string, boolean>;
}> => {
  return Promise.reject(new Error('Recreating stored JS functions is not supported from the frontend'));
};

/**
 * Test all stored functions with sample data
 */
export const testAllFunctions = async (): Promise<FunctionsTestResponse> => {
  return Promise.reject(new Error('Testing stored JS functions is not supported from the frontend'));
};

/**
 * Generic function caller for arbitrary stored functions on the server
 * @param name - Function name
 * @param payload - Optional payload
 */
export const callFunction = async (name: string, payload?: any): Promise<any> => {
  // Generic function invocations are unsupported in frontend-only mode
  return Promise.reject(new Error('Calling arbitrary stored functions is not supported in frontend-only mode'));
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