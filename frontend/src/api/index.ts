/**
 * API Index - Central export for all API modules
 * SW Glenmore Wellness Clinic
 */

// Export base client and utilities
export { default as apiClient, checkHealth } from './client';
export { get, post, put, patch, del, apiRequest } from './client';

// Export Views API (namespace)
export { viewsApi } from './views';

// Export Functions API (namespace)
export { functionsApi } from './functions';

// ============================================
// SYSTEM API
// ============================================

import { get } from './client';

export interface SystemStatus {
  status: 'healthy' | 'unhealthy';
  database: {
    connected: boolean;
    name: string;
  };
  views: {
    all_exist: boolean;
    details: Record<string, boolean>;
  };
  stored_functions: {
    all_exist: boolean;
    details: Record<string, boolean>;
  };
  statistics: {
    total_patients: number;
    total_staff: number;
    total_appointments: number;
  };
}

/**
 * Get complete system status
 */
export const getSystemStatus = async (): Promise<SystemStatus> => {
  return get<SystemStatus>('/api/system/status');
};

// ============================================
// COMBINED API NAMESPACE
// ============================================

import { viewsApi } from './views';
import { functionsApi } from './functions';

/**
 * Main API object combining all modules
 */
export const api = {
  // System
  system: {
    getStatus: getSystemStatus,
  },
  
  // Views
  views: viewsApi,
  
  // Stored Functions
  functions: functionsApi,
};

export default api;

// ============================================
// TYPE EXPORTS
// ============================================

// Re-export all types for convenience
export type {
  // View types
  PatientFullDetails,
  StaffAppointmentsSummary,
  ActiveVisitOverview,
  InvoicePaymentSummary,
  AppointmentCalendarView,
  ViewsStatus,
} from './views';

export type {
  // Function types
  PatientAgeResponse,
  PatientAgeWithDetailsResponse,
  PatientVisitCountResponse,
  PatientStatsResponse,
  InvoiceTotalResponse,
  InvoiceCalculatedTotalResponse,
  StaffAppointmentCountResponse,
  StaffStatsResponse,
  AppointmentAvailabilityRequest,
  AppointmentAvailabilityResponse,
  AppointmentValidationRequest,
  AppointmentValidationResponse,
  StoredFunction,
  FunctionsListResponse,
  FunctionStatus,
  FunctionsStatusResponse,
  FunctionTestResult,
  FunctionsTestResponse,
} from './functions';