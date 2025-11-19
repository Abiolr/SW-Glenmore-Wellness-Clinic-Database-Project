# 🎯 Frontend API Client - Complete Package

## ✅ What's Included

4 TypeScript files providing complete API integration for MongoDB Views and Stored Procedures.

### 📦 Files

| File | Lines | Description |
|------|-------|-------------|
| `client.ts` | 180 | Base Axios client with interceptors |
| `views.ts` | 380 | MongoDB Views API (5 views, 26 endpoints) |
| `functions.ts` | 420 | Stored Procedures API (5 functions, 17 endpoints) |
| `index.ts` | 90 | Main export file |
| **Total** | **1,070 lines** | **Complete API integration** |

---

## 🚀 Quick Setup

### 1. Copy Files

```bash
cd frontend/src
mkdir -p api
cp client.ts views.ts functions.ts index.ts api/
```

### 2. Install Dependencies

```bash
npm install axios
```

### 3. Configure Environment

Create `.env` file:
```env
VITE_API_URL=http://localhost:8000
```

### 4. Use in Components

```typescript
import api from '@/api';

// Get all patients
const patients = await api.views.getAllPatientsFullDetails();

// Calculate patient age
const age = await api.functions.calculatePatientAge('1990-05-15');

// Check system status
const status = await api.system.getStatus();
```

---

## 📊 API Coverage

### MongoDB Views (5 views)
- ✅ patient_full_details
- ✅ staff_appointments_summary
- ✅ active_visits_overview
- ✅ invoice_payment_summary
- ✅ appointment_calendar_view

### Stored Procedures (5 functions)
- ✅ calculatePatientAge
- ✅ getPatientVisitCount
- ✅ calculateInvoiceTotal
- ✅ getStaffAppointmentCount
- ✅ isAppointmentAvailable

### Total Endpoints: 43+
- Views: 26 endpoints
- Functions: 17 endpoints
- System: 1 endpoint
- Plus batch operations and combined queries

---

## 🎨 Features

### ✨ Automatic Error Handling
- Global error interceptor
- Status code handling (401, 403, 404, 500)
- Automatic logging
- Token management

### 🔒 Authentication Ready
- Token storage
- Auto-attach to requests
- Redirect on 401

### 📝 Full TypeScript Support
- All types exported
- Autocomplete everywhere
- Compile-time type checking

### 🚀 React Query Compatible
- Works seamlessly with React Query
- Optimistic updates
- Cache management

### ⚡ Performance Optimized
- Batch operations
- Combined queries
- Parallel requests

---

## 📚 Usage Examples

### Basic Usage
```typescript
import api from '@/api';

// Views
const patients = await api.views.getAllPatientsFullDetails();
const appointments = await api.views.getCalendarAppointments();

// Functions
const age = await api.functions.calculatePatientAge('1990-05-15');
const available = await api.functions.checkAppointmentAvailability({
  staff_id: 1,
  start_time: '2024-12-25T10:00:00',
  end_time: '2024-12-25T11:00:00',
});
```

### With React Query
```typescript
import { useQuery } from '@tanstack/react-query';
import api from '@/api';

function Dashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: api.views.getDashboardData,
  });

  if (isLoading) return <div>Loading...</div>;

  return (
    <div>
      <h1>Active Patients: {data.stats.totalPatients}</h1>
      <h2>Active Visits: {data.stats.activeVisits}</h2>
    </div>
  );
}
```

### Appointment Validation
```typescript
const result = await api.functions.validateAndCheckAppointment({
  staff_id: 1,
  scheduled_start: '2024-12-25T10:00:00',
  scheduled_end: '2024-12-25T11:00:00',
});

if (!result.validation.valid) {
  alert(result.validation.reason);
}
```

---

## 🔧 Configuration

### Environment Variables
```env
VITE_API_URL=http://localhost:8000  # Backend URL
```

### Request Timeout
Default: 30 seconds

Change in `client.ts`:
```typescript
const apiClient = axios.create({
  timeout: 30000, // milliseconds
});
```

### Business Hours
Default: 8 AM - 6 PM

Change when calling:
```typescript
const isOpen = api.functions.isWithinBusinessHours(
  startTime,
  endTime,
  9,  // Start at 9 AM
  17  // End at 5 PM
);
```

---

## 📖 Documentation

See **[API_USAGE_GUIDE.md](./API_USAGE_GUIDE.md)** for:
- Complete API reference
- All function signatures
- Code examples
- Best practices
- React Query integration
- Error handling patterns

---

## ✅ Checklist

- [x] Copy all 4 files to `src/api/`
- [ ] Install axios: `npm install axios`
- [ ] Create `.env` with API URL
- [ ] Test import: `import api from '@/api'`
- [ ] Test system status: `api.system.getStatus()`
- [ ] Start using in components!

---

## 🎉 You're Ready!

All API functionality is ready to use:
- ✅ Type-safe
- ✅ Error handling
- ✅ Authentication ready
- ✅ React Query compatible
- ✅ 43+ endpoints ready

Start building your features! 🚀