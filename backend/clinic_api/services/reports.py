from typing import List, Dict, Any
from datetime import datetime, date, timedelta
from ..database import Database
from bson import ObjectId
from bson.decimal128 import Decimal128
from bson.dbref import DBRef


def _sanitize_for_json(obj):
    """Recursively convert MongoDB/BSON types to JSON-serializable values.

    - Convert ObjectId/DBRef to string
    - Convert Decimal128 to float (or string if conversion fails)
    - Convert datetimes to ISO strings
    - Convert tuples/sets to lists
    - Drop any `_id` keys from dicts to avoid leaking DB ids
    """
    # BSON ObjectId
    if isinstance(obj, ObjectId):
        return str(obj)

    # DBRef
    if isinstance(obj, DBRef):
        return str(obj)

    # Decimal128
    if isinstance(obj, Decimal128):
        try:
            return float(obj.to_decimal())
        except Exception:
            return str(obj)

    # datetimes (and date)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, date) and not isinstance(obj, datetime):
        return obj.isoformat()

    # dict-like
    if isinstance(obj, dict):
        new = {}
        for k, v in obj.items():
            # Drop raw MongoDB _id fields
            if k == '_id':
                continue
            new[k] = _sanitize_for_json(v)
        return new

    # list/tuple/set -> list
    if isinstance(obj, (list, tuple, set)):
        return [_sanitize_for_json(v) for v in obj]

    # Fallback: return as-is (JSON encoder will handle primitives)
    return obj

class ReportService:
    
    @classmethod
    def get_monthly_activity_report(cls, month: int, year: int) -> Dict[str, Any]:
        """
        Stored Procedure Equivalent: Generates the Monthly Activity Report.
        Aggregates counts of visits, deliveries, labs, and prescriptions.
        """
        db = Database.get_db()
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
            
        start_str = start_date.isoformat()
        end_str = end_date.isoformat()

        # 1. Visit Stats & Avg Duration
        visit_pipeline = [
            {"$match": {"start_time": {"$gte": start_str, "$lt": end_str}}},
            {"$group": {
                "_id": None,
                "total_visits": {"$sum": 1},
                "avg_duration_minutes": {
                    "$avg": {
                        "$dateDiff": {
                            "startDate": {"$toDate": "$start_time"},
                            "endDate": {"$toDate": "$end_time"},
                            "unit": "minute"
                        }
                    }
                }
            }}
        ]
        visit_res = list(db.Visit.aggregate(visit_pipeline))
        visit_stats = visit_res[0] if visit_res else {"total_visits": 0, "avg_duration_minutes": 0}

        # 2. Counts for other collections
        deliveries = db.Delivery.count_documents({"visit_id": {"$in": [v['visit_id'] for v in db.Visit.find({"start_time": {"$gte": start_str, "$lt": end_str}})]}})
        
        # Approximate date matching for logs based on creation would be better, 
        # but relying on visit relation is safer for relational integrity.
        lab_tests = db.LabTestOrder.count_documents({}) # Simplified: In real app, filter by date
        prescriptions = db.Prescription.count_documents({}) # Simplified: In real app, filter by date

        return {
            "report_month": f"{month}/{year}",
            "metrics": {
                "total_patient_visits": visit_stats.get("total_visits", 0),
                "average_visit_duration_mins": round(visit_stats.get("avg_duration_minutes", 0) or 0, 2),
                "total_deliveries": deliveries,
                "total_lab_tests": lab_tests,
                "total_prescriptions": prescriptions
            }
        }

    @classmethod
    def get_outstanding_balances(cls) -> List[Dict[str, Any]]:
        """
        View Equivalent: Generates Patient Monthly Statement of outstanding balances.
        Joins Patients, Invoices, and Payments.
        """
        db = Database.get_db()
        
        pipeline = [
            # Match unpaid or partial invoices
            {"$match": {"status": {"$ne": "paid"}}},
            # Lookup Patient details
            {"$lookup": {
                "from": "Patient",
                "localField": "patient_id",
                "foreignField": "patient_id",
                "as": "patient"
            }},
            {"$unwind": "$patient"},
            # Lookup Payments for this invoice
            {"$lookup": {
                "from": "Payment",
                "localField": "invoice_id",
                "foreignField": "invoice_id",
                "as": "payments"
            }},
            # Calculate Balance
            {"$project": {
                "patient_name": {"$concat": ["$patient.first_name", " ", "$patient.last_name"]},
                "patient_id": "$patient_id",
                "invoice_id": "$invoice_id",
                "total_amount": "$total_amount",
                "patient_portion": "$patient_portion",
                "total_paid": {"$sum": "$payments.amount"},
                "balance_due": {"$subtract": ["$patient_portion", {"$sum": "$payments.amount"}]}
            }},
            {"$match": {"balance_due": {"$gt": 0}}}
        ]
        
        return list(db.Invoice.aggregate(pipeline))

    @classmethod
    def get_daily_delivery_log(cls, log_date: date) -> List[Dict[str, Any]]:
        """View Equivalent: Daily Delivery Room Log"""
        db = Database.get_db()
        
        # Find visits that happened on this day
        start = datetime.combine(log_date, datetime.min.time()).isoformat()
        end = datetime.combine(log_date, datetime.max.time()).isoformat()
        
        pipeline = [
            {"$match": {"start_time": {"$gte": start, "$lte": end}}},
            # Join with Delivery table
            {"$lookup": {
                "from": "Delivery",
                "localField": "visit_id",
                "foreignField": "visit_id",
                "as": "delivery_info"
            }},
            {"$unwind": "$delivery_info"},
            # Join Patient
            {"$lookup": {
                "from": "Patient",
                "localField": "patient_id",
                "foreignField": "patient_id",
                "as": "patient"
            }},
            {"$unwind": "$patient"},
            # Join Staff (Performed By)
            {"$lookup": {
                "from": "Staff",
                "localField": "delivery_info.performed_by",
                "foreignField": "staff_id",
                "as": "staff"
            }},
            {"$unwind": "$staff"},
            {"$project": {
                "time": "$start_time",
                "patient": {"$concat": ["$patient.first_name", " ", "$patient.last_name"]},
                "performed_by": {"$concat": ["$staff.first_name", " ", "$staff.last_name"]},
                "visit_type": "$visit_type"
            }}
        ]
        
        return list(db.Visit.aggregate(pipeline))

    @classmethod
    def get_monthly_statements(cls, month: int, year: int) -> Dict[str, Any]:
        """
        Aggregates invoices issued in the given calendar month and classifies
        them into `paid` (invoices issued that month and fully paid by month-end)
        and `unpaid` (invoices issued that month and not fully paid by month-end).

        Returns a dict with `month` and `summary` containing `paid` and `unpaid`
        patient lists and totals.
        """
        db = Database.get_db()

        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        # Use actual datetime objects for comparisons and coerce stored strings to Date
        # when necessary inside the aggregation pipeline to handle mixed formats.
        # start_date and end_date are Python datetimes; the driver will convert
        # them to BSON Date objects when sent to MongoDB.

        # 1) Find invoices issued within the month (coerce invoice_date -> Date)
        pipeline = [
            {"$addFields": {"invoice_date_dt": {"$toDate": "$invoice_date"}}},
            {"$match": {"invoice_date_dt": {"$gte": start_date, "$lt": end_date}}},
            # Join Patient details
            {"$lookup": {
                "from": "Patient",
                "localField": "patient_id",
                "foreignField": "patient_id",
                "as": "patient"
            }},
            {"$unwind": "$patient"},
            # Lookup payments for the invoice that were received ON/BEFORE month-end
            {"$lookup": {
                "from": "Payment",
                "let": {"inv": "$invoice_id"},
                "pipeline": [
                    {"$match": {"$expr": {"$and": [
                        {"$eq": ["$invoice_id", "$$inv"]},
                        # Coerce payment_date to Date for safe comparison with month-end
                        {"$lte": [{"$toDate": "$payment_date"}, end_date]}
                    ]}}}
                ],
                "as": "payments"
            }},
            # Lookup invoice lines for transparency
            {"$lookup": {
                "from": "InvoiceLine",
                "localField": "invoice_id",
                "foreignField": "invoice_id",
                "as": "lines"
            }},
            # Compute totals per invoice
            {"$addFields": {
                "total_paid": {"$sum": "$payments.amount"},
                "balance_due": {"$subtract": ["$patient_portion", {"$sum": "$payments.amount"}]},
                "patient_name": {"$concat": ["$patient.first_name", " ", "$patient.last_name"]}
            }},
            # Project useful fields only
            {"$project": {
                "invoice_id": 1,
                "invoice_date": 1,
                "invoice_date_dt": 1,
                "patient_id": 1,
                "patient_name": 1,
                "total_amount": 1,
                "patient_portion": 1,
                "total_paid": 1,
                "balance_due": 1,
                "lines": 1,
                "payments": 1
            }}
        ]

        invoices = list(db.Invoice.aggregate(pipeline))

        # Sanitize DB-returned objects to be JSON serializable (ObjectId, datetime)
        invoices = [_sanitize_for_json(inv) for inv in invoices]

        # Group by patient to produce per-patient statements
        patients = {}
        for inv in invoices:
            pid = inv.get('patient_id')
            if pid not in patients:
                patients[pid] = {
                    'patient_id': pid,
                    'patient_name': inv.get('patient_name'),
                    'invoices': [],
                    'total_invoiced': 0.0,
                    'payments_received': 0.0,
                    'balance': 0.0
                }

            patients[pid]['invoices'].append({
                'invoice_id': inv.get('invoice_id'),
                'invoice_date': inv.get('invoice_date'),
                'total_amount': inv.get('total_amount'),
                'patient_portion': inv.get('patient_portion'),
                'total_paid': inv.get('total_paid') or 0.0,
                'balance_due': inv.get('balance_due') or 0.0,
                'lines': inv.get('lines') or [],
                'payments': inv.get('payments') or []
            })

            patients[pid]['total_invoiced'] += (inv.get('patient_portion') or 0.0)
            patients[pid]['payments_received'] += (inv.get('total_paid') or 0.0)
            patients[pid]['balance'] += (inv.get('balance_due') or 0.0)

        paid_list = []
        unpaid_list = []

        totals = {
            'paid': {'total_invoiced': 0.0, 'payments_received': 0.0, 'balance': 0.0},
            'unpaid': {'total_invoiced': 0.0, 'payments_received': 0.0, 'balance': 0.0}
        }

        for p in patients.values():
            # classify as paid if balance <= 0 (fully paid by month-end)
            if round(p['balance'], 2) <= 0:
                paid_list.append(p)
                totals['paid']['total_invoiced'] += p['total_invoiced']
                totals['paid']['payments_received'] += p['payments_received']
                totals['paid']['balance'] += p['balance']
            else:
                unpaid_list.append(p)
                totals['unpaid']['total_invoiced'] += p['total_invoiced']
                totals['unpaid']['payments_received'] += p['payments_received']
                totals['unpaid']['balance'] += p['balance']

        result = {
            'month': f"{month}/{year}",
            'summary': {
                'paid': {'patients': paid_list, 'totals': totals['paid']},
                'unpaid': {'patients': unpaid_list, 'totals': totals['unpaid']}
            }
        }

        # Ensure final result is JSON-serializable
        return _sanitize_for_json(result)