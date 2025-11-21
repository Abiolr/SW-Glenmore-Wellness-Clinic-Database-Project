/**
 * Base Axios Client Configuration
 * SW Glenmore Wellness Clinic
 */

/// <reference types="vite/client" />

import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// API Base URL - adjust based on your environment
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Create axios instance with default configuration
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request Interceptor
 * Add authentication token, logging, etc.
 */
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Log request in development
    if (import.meta.env.DEV) {
      console.log('🚀 API Request:', {
        method: config.method?.toUpperCase(),
        url: config.url,
        data: config.data,
      });
    }

    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

/**
 * Response Interceptor
 * Handle errors globally, transform responses, etc.
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log response in development
    if (import.meta.env.DEV) {
      console.log('✅ API Response:', {
        status: response.status,
        url: response.config.url,
        data: response.data,
      });
    }

    return response;
  },
  (error: AxiosError) => {
    // Handle errors globally
    if (error.response) {
      // Server responded with error status
      console.error('❌ API Error:', {
        status: error.response.status,
        url: error.config?.url,
        message: error.response.data,
      });

      // Handle specific status codes
      switch (error.response.status) {
        case 401:
          // Unauthorized - redirect to login
          console.warn('Unauthorized - Session expired');
          // Clear token and redirect to login
          localStorage.removeItem('auth_token');
          window.location.href = '/login';
          break;
        
        case 403:
          // Forbidden
          console.warn('Forbidden - Insufficient permissions');
          break;
        
        case 404:
          // Not Found
          console.warn('Resource not found');
          break;
        
        case 500:
          // Internal Server Error
          console.error('Server error - Please try again later');
          break;
        
        default:
          console.error('API Error:', error.response.data);
      }
    } else if (error.request) {
      // Request made but no response received
      console.error('Network Error - No response from server');
    } else {
      // Error setting up request
      console.error('Request Error:', error.message);
    }

    return Promise.reject(error);
  }
);

/**
 * Generic API request method
 */
export const apiRequest = async <T = any>(
  config: AxiosRequestConfig
): Promise<T> => {
  try {
    const response = await apiClient.request<T>(config);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * GET request
 */
export const get = async <T = any>(
  url: string,
  config?: AxiosRequestConfig
): Promise<T> => {
  return apiRequest<T>({ ...config, method: 'GET', url });
};

/**
 * POST request
 */
export const post = async <T = any>(
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<T> => {
  return apiRequest<T>({ ...config, method: 'POST', url, data });
};

/**
 * PUT request
 */
export const put = async <T = any>(
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<T> => {
  return apiRequest<T>({ ...config, method: 'PUT', url, data });
};

/**
 * PATCH request
 */
export const patch = async <T = any>(
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<T> => {
  return apiRequest<T>({ ...config, method: 'PATCH', url, data });
};

/**
 * DELETE request
 */
export const del = async <T = any>(
  url: string,
  config?: AxiosRequestConfig
): Promise<T> => {
  return apiRequest<T>({ ...config, method: 'DELETE', url });
};

/**
 * Check API health
 */
export const checkHealth = async (): Promise<any> => {
  try {
    const response = await get('/health');
    return response;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

export default apiClient;