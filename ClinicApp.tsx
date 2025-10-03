import React, { useEffect, useState } from "react";

// ClinicApp.tsx
// Single-file React + TypeScript front-end demo for the SW Glenmore Wellness Clinic project.
// - Tailwind CSS assumed available
// - Uses simple REST endpoints: /api/patients, /api/appointments, /api/billing, /api/staff
// - This file is intended as a production-ready starting point for a group project UI.

/*********************
 * Types
 *********************/
interface Patient {
  id: number;
  firstName: string;
  lastName: string;
  dob: string; // ISO date
  phone?: string;
  email?: string;
  address?: string;
  medicalCardNumber?: string | null; // government coverage id
}

interface Practitioner {
  id: number;
  name: string;
  role: "Physician" | "Nurse" | "Midwife" | "NP" | "Pharmacist" | "Tech";
  specialty?: string;
}

interface Appointment {
  id: number;
  patientId: number;
  practitionerId: number;
  startTime: string; // ISO datetime
  durationMins: number;
  type: string; // checkup, immunization, walk-in...
  notes?: string;
}

interface Billing {
  id: number;
  patientId: number;
  appointmentId?: number | null;
  amount: number;
  paid: number;
  payMethod?: string; // cash, insurance, government
  balance: number;
}

/*********************
 * Utility helpers
 *********************/
const isoNow = () => new Date().toISOString().slice(0, 16); // suitable for input[type=datetime-local]

/*********************
 * Main App
 *********************/
export default function ClinicApp() {
  const [view, setView] = useState<"patients" | "appointments" | "billing" | "schedules" | "reports">("patients");

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <aside className="w-64 bg-white border-r p-4">
        <h2 className="text-xl font-semibold mb-4">SW Glenmore Clinic</h2>
        <nav className="space-y-2">
          <NavButton active={view === "patients"} onClick={() => setView("patients")}>Patients</NavButton>
          <NavButton active={view === "appointments"} onClick={() => setView("appointments")}>Appointments</NavButton>
          <NavButton active={view === "billing"} onClick={() => setView("billing")}>Billing</NavButton>
          <NavButton active={view === "schedules"} onClick={() => setView("schedules")}>Schedules</NavButton>
          <NavButton active={view === "reports"} onClick={() => setView("reports")}>Reports</NavButton>
        </nav>
      </aside>

      <main className="flex-1 p-6">
        <header className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold">{viewToTitle(view)}</h1>
          <div className="text-sm text-gray-600">Demo UI — connected to /api endpoints</div>
        </header>

        <section className="bg-white rounded-lg shadow-sm p-6">
          {view === "patients" && <PatientsPanel />}
          {view === "appointments" && <AppointmentsPanel />}
          {view === "billing" && <BillingPanel />}
          {view === "schedules" && <SchedulesPanel />}
          {view === "reports" && <ReportsPanel />}
        </section>
      </main>
    </div>
  );
}

function viewToTitle(v: string) {
  switch (v) {
    case "patients": return "Patients";
    case "appointments": return "Appointments";
    case "billing": return "Billing & Payments";
    case "schedules": return "Practitioner Schedules";
    case "reports": return "Reports";
    default: return "";
  }
}

/*********************
 * NavButton
 *********************/
function NavButton({ children, onClick, active }: { children: React.ReactNode; onClick: () => void; active?: boolean }) {
  return (
    <button
      onClick={onClick}
      className={`block w-full text-left px-3 py-2 rounded ${active ? "bg-sky-500 text-white" : "text-gray-700 hover:bg-gray-100"}`}
    >
      {children}
    </button>
  );
}

/*********************
 * PatientsPanel
 *********************/
function PatientsPanel() {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [editing, setEditing] = useState<Patient | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => { fetchPatients(); }, []);

  async function fetchPatients() {
    setLoading(true);
    try {
      const res = await fetch("/api/patients");
      if (!res.ok) throw new Error("Failed to load");
      const data = await res.json();
      setPatients(data);
    } catch (e) {
      console.error(e);
      // In a real app, show UI error
    } finally { setLoading(false); }
  }

  async function savePatient(p: Patient) {
    const method = p.id ? "PUT" : "POST";
    const url = p.id ? `/api/patients/${p.id}` : "/api/patients";
    const res = await fetch(url, { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(p) });
    if (!res.ok) throw new Error("Save failed");
    await fetchPatients();
    setEditing(null);
  }

  async function deletePatient(id: number) {
    if (!confirm("Delete patient? This will also remove related appointments and billing.")) return;
    const res = await fetch(`/api/patients/${id}`, { method: "DELETE" });
    if (!res.ok) console.error("Delete failed");
    await fetchPatients();
  }

  return (
    <div className="grid grid-cols-3 gap-6">
      <div className="col-span-2">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Patient List</h3>
          <button className="btn" onClick={() => setEditing({ id: 0, firstName: "", lastName: "", dob: "2000-01-01", phone: "", email: "", address: "" })}>New Patient</button>
        </div>

        {loading ? <div>Loading...</div> : (
          <table className="w-full text-sm">
            <thead className="text-left text-gray-600">
              <tr>
                <th className="pb-2">Name</th>
                <th className="pb-2">DOB</th>
                <th className="pb-2">Phone</th>
                <th className="pb-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {patients.map(p => (
                <tr key={p.id} className="border-t">
                  <td className="py-2">{p.firstName} {p.lastName}</td>
                  <td className="py-2">{p.dob}</td>
                  <td className="py-2">{p.phone}</td>
                  <td className="py-2">
                    <button className="text-sky-600 mr-3" onClick={() => setEditing(p)}>Edit</button>
                    <button className="text-red-600" onClick={() => deletePatient(p.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div>
        {editing ? (
          <PatientForm patient={editing} onCancel={() => setEditing(null)} onSave={savePatient} />
        ) : (
          <div className="p-4 text-gray-600">Select a patient to edit or click <strong>New Patient</strong>.</div>
        )}
      </div>
    </div>
  );
}

function PatientForm({ patient, onCancel, onSave }: { patient: Patient; onCancel: () => void; onSave: (p: Patient) => Promise<void> }) {
  const [p, setP] = useState<Patient>(patient);

  useEffect(() => { setP(patient); }, [patient]);

  function update<K extends keyof Patient>(key: K, value: Patient[K]) { setP(prev => ({ ...prev, [key]: value })); }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    // Basic validation
    if (!p.firstName || !p.lastName) { alert("Name required"); return; }
    await onSave(p);
  }

  return (
    <form onSubmit={submit} className="space-y-3">
      <h4 className="font-semibold">{p.id ? "Edit Patient" : "New Patient"}</h4>
      <div>
        <label className="block text-sm">First name</label>
        <input value={p.firstName} onChange={e => update("firstName", e.target.value)} className="input" />
      </div>
      <div>
        <label className="block text-sm">Last name</label>
        <input value={p.lastName} onChange={e => update("lastName", e.target.value)} className="input" />
      </div>
      <div>
        <label className="block text-sm">Date of birth</label>
        <input type="date" value={p.dob} onChange={e => update("dob", e.target.value)} className="input" />
      </div>
      <div>
        <label className="block text-sm">Phone</label>
        <input value={p.phone} onChange={e => update("phone", e.target.value)} className="input" />
      </div>
      <div className="flex gap-2">
        <button type="submit" className="btn btn-primary">Save</button>
        <button type="button" className="btn" onClick={onCancel}>Cancel</button>
      </div>
    </form>
  );
}

/*********************
 * AppointmentsPanel
 *********************/
function AppointmentsPanel() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [patients, setPatients] = useState<Patient[]>([]);
  const [practitioners, setPractitioners] = useState<Practitioner[]>([]);
  const [editing, setEditing] = useState<Appointment | null>(null);

  useEffect(() => { fetchAll(); }, []);

  async function fetchAll() {
    const [aRes, pRes, prRes] = await Promise.all([fetch("/api/appointments"), fetch("/api/patients"), fetch("/api/staff")]);
    if (aRes.ok) setAppointments(await aRes.json());
    if (pRes.ok) setPatients(await pRes.json());
    if (prRes.ok) setPractitioners(await prRes.json());
  }

  async function save(a: Appointment) {
    const method = a.id ? "PUT" : "POST";
    const url = a.id ? `/api/appointments/${a.id}` : "/api/appointments";
    const res = await fetch(url, { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(a) });
    if (!res.ok) throw new Error("Save failed");
    await fetchAll();
    setEditing(null);
  }

  return (
    <div className="grid grid-cols-3 gap-6">
      <div className="col-span-2">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Appointments</h3>
          <button className="btn" onClick={() => setEditing({ id: 0, patientId: patients[0]?.id ?? 0, practitionerId: practitioners[0]?.id ?? 0, startTime: isoNow(), durationMins: 10, type: "Checkup" })}>New</button>
        </div>

        <table className="w-full text-sm">
          <thead className="text-left text-gray-600">
            <tr>
              <th className="pb-2">Time</th>
              <th className="pb-2">Patient</th>
              <th className="pb-2">Practitioner</th>
              <th className="pb-2">Type</th>
              <th className="pb-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {appointments.map(a => (
              <tr key={a.id} className="border-t">
                <td className="py-2">{new Date(a.startTime).toLocaleString()}</td>
                <td className="py-2">{patients.find(p => p.id === a.patientId)?.firstName ?? "(loading)"}</td>
                <td className="py-2">{practitioners.find(pr => pr.id === a.practitionerId)?.name ?? "(loading)"}</td>
                <td className="py-2">{a.type}</td>
                <td className="py-2">
                  <button className="text-sky-600 mr-3" onClick={() => setEditing(a)}>Edit</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div>
        {editing ? (
          <AppointmentForm appointment={editing} patients={patients} practitioners={practitioners} onCancel={() => setEditing(null)} onSave={save} />
        ) : (
          <div className="p-4 text-gray-600">Select an appointment to edit or create a new one.</div>
        )}
      </div>
    </div>
  );
}

function AppointmentForm({ appointment, patients, practitioners, onCancel, onSave }: { appointment: Appointment; patients: Patient[]; practitioners: Practitioner[]; onCancel: () => void; onSave: (a: Appointment) => Promise<void> }) {
  const [a, setA] = useState<Appointment>(appointment);
  useEffect(() => setA(appointment), [appointment]);

  function update<K extends keyof Appointment>(key: K, value: Appointment[K]) { setA(prev => ({ ...prev, [key]: value })); }

  async function submit(e: React.FormEvent) { e.preventDefault(); if (!a.patientId || !a.practitionerId) { alert("Choose patient and practitioner"); return; } await onSave(a); }

  return (
    <form onSubmit={submit} className="space-y-3">
      <h4 className="font-semibold">{a.id ? "Edit Appointment" : "New Appointment"}</h4>

      <label className="block text-sm">Patient</label>
      <select value={a.patientId} onChange={e => update("patientId", Number(e.target.value))} className="input">
        {patients.map(p => <option key={p.id} value={p.id}>{p.firstName} {p.lastName}</option>)}
      </select>

      <label className="block text-sm">Practitioner</label>
      <select value={a.practitionerId} onChange={e => update("practitionerId", Number(e.target.value))} className="input">
        {practitioners.map(pr => <option key={pr.id} value={pr.id}>{pr.name} — {pr.role}</option>)}
      </select>

      <label className="block text-sm">Start time</label>
      <input type="datetime-local" value={a.startTime.slice(0,16)} onChange={e => update("startTime", new Date(e.target.value).toISOString())} className="input" />

      <label className="block text-sm">Duration (mins)</label>
      <input type="number" value={a.durationMins} onChange={e => update("durationMins", Number(e.target.value))} className="input" />

      <div className="flex gap-2">
        <button type="submit" className="btn btn-primary">Save</button>
        <button type="button" className="btn" onClick={onCancel}>Cancel</button>
      </div>
    </form>
  );
}

/*********************
 * BillingPanel
 *********************/
function BillingPanel() {
  const [bills, setBills] = useState<Billing[]>([]);
  const [patients, setPatients] = useState<Patient[]>([]);

  useEffect(() => { fetchData(); }, []);

  async function fetchData() {
    const [bRes, pRes] = await Promise.all([fetch("/api/billing"), fetch("/api/patients")]);
    if (bRes.ok) setBills(await bRes.json());
    if (pRes.ok) setPatients(await pRes.json());
  }

  async function applyPayment(id: number) {
    const amountStr = prompt("Enter payment amount:");
    if (!amountStr) return; const amt = Number(amountStr);
    if (isNaN(amt) || amt <= 0) { alert("Invalid"); return; }
    const res = await fetch(`/api/billing/${id}/payment`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ amount: amt }) });
    if (!res.ok) alert("Payment failed");
    await fetchData();
  }

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">Outstanding Balances</h3>
      <table className="w-full text-sm">
        <thead className="text-left text-gray-600">
          <tr><th>Patient</th><th>Amount</th><th>Paid</th><th>Balance</th><th>Actions</th></tr>
        </thead>
        <tbody>
          {bills.map(b => (
            <tr key={b.id} className="border-t">
              <td className="py-2">{patients.find(p => p.id === b.patientId)?.firstName ?? "(loading)"}</td>
              <td className="py-2">${b.amount.toFixed(2)}</td>
              <td className="py-2">${b.paid.toFixed(2)}</td>
              <td className="py-2">${b.balance.toFixed(2)}</td>
              <td className="py-2"><button className="btn" onClick={() => applyPayment(b.id)}>Apply Payment</button></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/*********************
 * SchedulesPanel
 *********************/
function SchedulesPanel() {
  // This demo requests a view that combines staff and appointments
  const [daily, setDaily] = useState<any[]>([]);

  useEffect(() => { fetchSchedule(); }, []);

  async function fetchSchedule() {
    const res = await fetch("/api/views/practitioner_daily_schedule");
    if (!res.ok) return;
    setDaily(await res.json());
  }

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4">Practitioner Daily Schedule</h3>
      <table className="w-full text-sm">
        <thead className="text-left text-gray-600"><tr><th>Practitioner</th><th>Time</th><th>Patient</th><th>Type</th></tr></thead>
        <tbody>
          {daily.map((r, i) => (
            <tr className="border-t" key={i}>
              <td className="py-2">{r.practitioner}</td>
              <td className="py-2">{new Date(r.startTime).toLocaleString()}</td>
              <td className="py-2">{r.patient}</td>
              <td className="py-2">{r.type}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/*********************
 * ReportsPanel
 *********************/
function ReportsPanel() {
  const [monthly, setMonthly] = useState<any | null>(null);

  async function runMonthly() {
    const res = await fetch("/api/reports/monthly_activity");
    if (!res.ok) { alert("Report failed"); return; }
    setMonthly(await res.json());
  }

  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <button className="btn btn-primary" onClick={runMonthly}>Run Monthly Activity Report</button>
      </div>

      {monthly ? (
        <div className="space-y-3">
          <div>Visits: {monthly.visits}</div>
          <div>Deliveries: {monthly.deliveries}</div>
          <div>Lab Tests: {monthly.lab_tests}</div>
          <div>Avg Visit Duration (mins): {monthly.avg_visit_mins}</div>
        </div>
      ) : (
        <div className="text-gray-600">No report run yet.</div>
      )}
    </div>
  );
}

/*********************
 * Small UI helpers (simple Tailwind utility classes)
 *********************/
// In a real app, extract these to a shared component library
const btnBase = "px-3 py-1 rounded border text-sm";

declare global { interface Window { __TAILWIND_PLACEHOLDER__?: boolean } }

// small helpers used in JSX (keeping className strings short for readability)
// .btn, .btn-primary, .input classes assumed to be provided by a global stylesheet or Tailwind config

/*
Example CSS (put into your global stylesheet if not using a UI kit):

.btn { @apply px-3 py-1 rounded border text-sm; }
.btn-primary { @apply bg-sky-600 text-white; }
.input { @apply w-full border rounded px-2 py-1 text-sm; }
*/
