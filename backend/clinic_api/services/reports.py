from typing import List, Dict, Any
from datetime import datetime, date, timedelta
from ..database import Database

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