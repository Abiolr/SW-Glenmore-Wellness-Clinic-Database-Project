"""
MongoDB Views Module for SW Glenmore Wellness Clinic
5 NEW Business Intelligence Views
Based on actual collection structure
"""

import logging

logger = logging.getLogger(__name__)


class ViewsManager:
    """Manages MongoDB views creation and access"""
    
    def __init__(self):
        """Initialize ViewsManager with Database connection"""
        from clinic_api.database import Database
        
        self.db = Database.connect_db()
        # Cache available collection names
        try:
            self.collections = set(self.db.list_collection_names())
        except Exception:
            self.collections = set()

        # NEW VIEW NAMES
        self.views = [
            'visit_complete_details',
            'patient_financial_summary',
            'staff_workload_analysis',
            'daily_clinic_schedule',
            'patient_clinical_history'
        ]
    
    def view_exists(self, view_name):
        """Check if a view exists"""
        try:
            collections = self.db.list_collection_names()
            return view_name in collections
        except Exception as e:
            logger.error(f"Error checking if view exists: {e}")
            return False
    
    def drop_view(self, view_name):
        """Drop a view if it exists"""
        try:
            if self.view_exists(view_name):
                self.db[view_name].drop()
                logger.info(f"Dropped view: {view_name}")
        except Exception as e:
            logger.error(f"Error dropping view {view_name}: {e}")
    
    def create_visit_complete_details(self):
        """
        VIEW 1: Complete Visit Details
        
        Shows all visits with:
        - Patient info (name, phone, email)
        - Staff info (name, email, phone)
        - Visit details (type, times, status)
        - Prescriptions count
        - Lab tests count
        - Delivery info (if maternity visit)
        
        Use case: Clinical dashboard, visit tracking, patient care coordination
        """
        view_name = "visit_complete_details"
        
        try:
            self.drop_view(view_name)
            
            pipeline = [
                # Join patient info
                {
                    "$lookup": {
                        "from": "Patient",
                        "localField": "patient_id",
                        "foreignField": "patient_id",
                        "as": "patient"
                    }
                },
                # Join staff info
                {
                    "$lookup": {
                        "from": "Staff",
                        "localField": "staff_id",
                        "foreignField": "staff_id",
                        "as": "staff"
                    }
                },
                # Join prescriptions
                {
                    "$lookup": {
                        "from": "Prescription",
                        "localField": "visit_id",
                        "foreignField": "Visit_Id",
                        "as": "prescriptions"
                    }
                },
                # Join lab tests
                {
                    "$lookup": {
                        "from": "LabTestOrder",
                        "localField": "visit_id",
                        "foreignField": "Visit_Id",
                        "as": "lab_tests"
                    }
                },
                # Join delivery info
                {
                    "$lookup": {
                        "from": "Delivery",
                        "localField": "visit_id",
                        "foreignField": "Visit_Id",
                        "as": "delivery"
                    }
                },
                # Unwind patient and staff (required fields)
                {
                    "$unwind": {
                        "path": "$patient",
                        "preserveNullAndEmptyArrays": True
                    }
                },
                {
                    "$unwind": {
                        "path": "$staff",
                        "preserveNullAndEmptyArrays": True
                    }
                },
                # Calculate fields
                {
                    "$addFields": {
                        "prescription_count": {"$size": "$prescriptions"},
                        "lab_test_count": {"$size": "$lab_tests"},
                        "has_delivery": {"$gt": [{"$size": "$delivery"}, 0]},
                        "visit_duration_minutes": {
                            "$cond": {
                                "if": {"$ne": ["$end_time", None]},
                                "then": {
                                    "$divide": [
                                        {"$subtract": ["$end_time", "$start_time"]},
                                        60000  # Convert milliseconds to minutes
                                    ]
                                },
                                "else": None
                            }
                        }
                    }
                },
                # Shape final output
                {
                    "$project": {
                        "visit_id": 1,
                        "patient_id": 1,
                        "patient_name": {
                            "$concat": [
                                {"$ifNull": ["$patient.first_name", ""]},
                                " ",
                                {"$ifNull": ["$patient.last_name", ""]}
                            ]
                        },
                        "patient_phone": "$patient.phone",
                        "patient_email": "$patient.email",
                        "staff_id": 1,
                        "staff_name": {
                            "$concat": [
                                {"$ifNull": ["$staff.first_name", ""]},
                                " ",
                                {"$ifNull": ["$staff.last_name", ""]}
                            ]
                        },
                        "staff_email": "$staff.email",
                        "visit_type": 1,
                        "start_time": 1,
                        "end_time": 1,
                        "visit_status": {
                            "$cond": {
                                "if": {"$eq": ["$end_time", None]},
                                "then": "Active",
                                "else": "Completed"
                            }
                        },
                        "visit_duration_minutes": 1,
                        "prescription_count": 1,
                        "lab_test_count": 1,
                        "has_delivery": 1,
                        "notes": 1
                    }
                },
                # Sort by most recent first
                {
                    "$sort": {"start_time": -1}
                }
            ]
            
            self.db.command({
                "create": view_name,
                "viewOn": "Visit",
                "pipeline": pipeline
            })
            
            logger.info(f"Created view: {view_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating view {view_name}: {e}")
            return False
    
    def create_patient_financial_summary(self):
        """
        VIEW 2: Patient Financial Summary
        
        Shows each patient's complete financial status:
        - Total invoiced amount
        - Total paid amount
        - Outstanding balance
        - Number of invoices
        - Number of payments
        - Insurance vs patient portions
        - Payment methods used
        
        Use case: Billing, collections, financial reports
        """
        view_name = "patient_financial_summary"
        
        try:
            self.drop_view(view_name)
            
            pipeline = [
                # Join invoices
                {
                    "$lookup": {
                        "from": "Invoice",
                        "localField": "patient_id",
                        "foreignField": "patient_id",
                        "as": "invoices"
                    }
                },
                # Join payments
                {
                    "$lookup": {
                        "from": "Payment",
                        "localField": "patient_id",
                        "foreignField": "patient_id",
                        "as": "payments"
                    }
                },
                # Calculate financial metrics
                {
                    "$addFields": {
                        "total_invoiced": {"$sum": "$invoices.total_amount"},
                        "total_insurance_portion": {"$sum": "$invoices.insurance_portion"},
                        "total_patient_portion": {"$sum": "$invoices.patient_portion"},
                        "total_paid": {"$sum": "$payments.amount"},
                        "invoice_count": {"$size": "$invoices"},
                        "payment_count": {"$size": "$payments"},
                        
                        # Count invoices by status
                        "paid_invoices": {
                            "$size": {
                                "$filter": {
                                    "input": "$invoices",
                                    "as": "inv",
                                    "cond": {"$eq": ["$$inv.status", "paid"]}
                                }
                            }
                        },
                        "pending_invoices": {
                            "$size": {
                                "$filter": {
                                    "input": "$invoices",
                                    "as": "inv",
                                    "cond": {"$ne": ["$$inv.status", "paid"]}
                                }
                            }
                        },
                        
                        # Payment methods breakdown
                        "cash_payments": {
                            "$size": {
                                "$filter": {
                                    "input": "$payments",
                                    "as": "pmt",
                                    "cond": {"$eq": ["$$pmt.method", "cash"]}
                                }
                            }
                        },
                        "card_payments": {
                            "$size": {
                                "$filter": {
                                    "input": "$payments",
                                    "as": "pmt",
                                    "cond": {"$in": ["$$pmt.method", ["credit_card", "debit_card"]]}
                                }
                            }
                        }
                    }
                },
                # Calculate outstanding balance
                {
                    "$addFields": {
                        "outstanding_balance": {
                            "$subtract": ["$total_invoiced", "$total_paid"]
                        }
                    }
                },
                # Shape output
                {
                    "$project": {
                        "patient_id": 1,
                        "first_name": 1,
                        "last_name": 1,
                        "full_name": {"$concat": ["$first_name", " ", "$last_name"]},
                        "phone": 1,
                        "email": 1,
                        "insurance_no": 1,
                        
                        # Financial summary
                        "total_invoiced": 1,
                        "total_insurance_portion": 1,
                        "total_patient_portion": 1,
                        "total_paid": 1,
                        "outstanding_balance": 1,
                        
                        # Counts
                        "invoice_count": 1,
                        "payment_count": 1,
                        "paid_invoices": 1,
                        "pending_invoices": 1,
                        
                        # Payment methods
                        "cash_payments": 1,
                        "card_payments": 1,
                        
                        # Status flags
                        "has_outstanding_balance": {"$gt": ["$outstanding_balance", 0]},
                        "is_current": {"$lte": ["$outstanding_balance", 0]}
                    }
                },
                # Sort by outstanding balance (highest first)
                {
                    "$sort": {"outstanding_balance": -1}
                }
            ]
            
            self.db.command({
                "create": view_name,
                "viewOn": "Patient",
                "pipeline": pipeline
            })
            
            logger.info(f"Created view: {view_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating view {view_name}: {e}")
            return False
    
    def create_staff_workload_analysis(self):
        """
        VIEW 3: Staff Workload Analysis
        
        Shows staff performance and workload metrics:
        - Total appointments (scheduled vs walk-in)
        - Total visits
        - Active visits count
        - Total prescriptions written
        - Total lab tests ordered
        - Total deliveries performed
        
        Use case: Staff management, resource allocation, performance reviews
        """
        view_name = "staff_workload_analysis"
        
        try:
            self.drop_view(view_name)
            
            pipeline = [
                # Join appointments
                {
                    "$lookup": {
                        "from": "Appointment",
                        "localField": "staff_id",
                        "foreignField": "staff_id",
                        "as": "appointments"
                    }
                },
                # Join visits
                {
                    "$lookup": {
                        "from": "Visit",
                        "localField": "staff_id",
                        "foreignField": "staff_id",
                        "as": "visits"
                    }
                },
                # Join deliveries
                {
                    "$lookup": {
                        "from": "Delivery",
                        "localField": "staff_id",
                        "foreignField": "Delivered_By",
                        "as": "deliveries"
                    }
                },
                # Calculate metrics
                {
                    "$addFields": {
                        # Appointment metrics
                        "total_appointments": {"$size": "$appointments"},
                        "walk_in_appointments": {
                            "$size": {
                                "$filter": {
                                    "input": "$appointments",
                                    "as": "apt",
                                    "cond": {"$eq": ["$$apt.is_walkin", True]}
                                }
                            }
                        },
                        "scheduled_appointments": {
                            "$size": {
                                "$filter": {
                                    "input": "$appointments",
                                    "as": "apt",
                                    "cond": {"$eq": ["$$apt.is_walkin", False]}
                                }
                            }
                        },
                        
                        # Visit metrics
                        "total_visits": {"$size": "$visits"},
                        "active_visits": {
                            "$size": {
                                "$filter": {
                                    "input": "$visits",
                                    "as": "visit",
                                    "cond": {"$eq": ["$$visit.end_time", None]}
                                }
                            }
                        },
                        "completed_visits": {
                            "$size": {
                                "$filter": {
                                    "input": "$visits",
                                    "as": "visit",
                                    "cond": {"$ne": ["$$visit.end_time", None]}
                                }
                            }
                        },
                        
                        # Clinical activity
                        "total_deliveries": {"$size": "$deliveries"}
                    }
                },
                # Shape output
                {
                    "$project": {
                        "staff_id": 1,
                        "first_name": 1,
                        "last_name": 1,
                        "full_name": {"$concat": ["$first_name", " ", "$last_name"]},
                        "email": 1,
                        "phone": 1,
                        "active": 1,
                        
                        # Appointment metrics
                        "total_appointments": 1,
                        "walk_in_appointments": 1,
                        "scheduled_appointments": 1,
                        
                        # Visit metrics
                        "total_visits": 1,
                        "active_visits": 1,
                        "completed_visits": 1,
                        
                        # Clinical activity
                        "total_deliveries": 1,
                        
                        # Performance indicators
                        "is_busy": {"$gt": ["$active_visits", 0]},
                        "workload_score": {
                            "$add": [
                                {"$multiply": ["$active_visits", 10]},
                                {"$multiply": ["$total_appointments", 1]}
                            ]
                        }
                    }
                },
                # Sort by workload score
                {
                    "$sort": {"workload_score": -1}
                }
            ]
            
            self.db.command({
                "create": view_name,
                "viewOn": "Staff",
                "pipeline": pipeline
            })
            
            logger.info(f"Created view: {view_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating view {view_name}: {e}")
            return False
    
    def create_daily_clinic_schedule(self):
        """
        VIEW 4: Daily Clinic Schedule
        
        Combines appointments into a unified schedule:
        - All appointments
        - Patient and staff details
        - Time slots
        - Type indicators (scheduled/walk-in)
        
        Use case: Front desk operations, daily planning, resource coordination
        """
        view_name = "daily_clinic_schedule"
        
        try:
            self.drop_view(view_name)
            
            pipeline = [
                # Join patient info
                {
                    "$lookup": {
                        "from": "Patient",
                        "localField": "patient_id",
                        "foreignField": "patient_id",
                        "as": "patient"
                    }
                },
                # Join staff info
                {
                    "$lookup": {
                        "from": "Staff",
                        "localField": "staff_id",
                        "foreignField": "staff_id",
                        "as": "staff"
                    }
                },
                # Unwind patient and staff
                {
                    "$unwind": {
                        "path": "$patient",
                        "preserveNullAndEmptyArrays": True
                    }
                },
                {
                    "$unwind": {
                        "path": "$staff",
                        "preserveNullAndEmptyArrays": True
                    }
                },
                # Shape output
                {
                    "$project": {
                        "appointment_id": 1,
                        "patient_id": 1,
                        "patient_name": {
                            "$concat": [
                                {"$ifNull": ["$patient.first_name", ""]},
                                " ",
                                {"$ifNull": ["$patient.last_name", ""]}
                            ]
                        },
                        "patient_phone": "$patient.phone",
                        "patient_email": "$patient.email",
                        
                        "staff_id": 1,
                        "staff_name": {
                            "$concat": [
                                {"$ifNull": ["$staff.first_name", ""]},
                                " ",
                                {"$ifNull": ["$staff.last_name", ""]}
                            ]
                        },
                        "staff_email": "$staff.email",
                        "staff_phone": "$staff.phone",
                        
                        "scheduled_start": 1,
                        "scheduled_end": 1,
                        "is_walkin": 1,
                        "appointment_type": {
                            "$cond": {
                                "if": "$is_walkin",
                                "then": "Walk-in",
                                "else": "Scheduled"
                            }
                        },
                        "created_at": 1,
                        
                        # Calendar display fields
                        "title": {
                            "$concat": [
                                {"$cond": {
                                    "if": "$is_walkin",
                                    "then": "🚶 ",
                                    "else": "📅 "
                                }},
                                {"$ifNull": ["$patient.first_name", ""]},
                                " ",
                                {"$ifNull": ["$patient.last_name", ""]}
                            ]
                        },
                        "color": {
                            "$cond": {
                                "if": "$is_walkin",
                                "then": "#ff9f40",  # Orange for walk-ins
                                "else": "#4285f4"   # Blue for scheduled
                            }
                        },
                        
                        # Day of week
                        "day_of_week": {
                            "$dayOfWeek": "$scheduled_start"
                        },
                        "hour_of_day": {
                            "$hour": "$scheduled_start"
                        }
                    }
                },
                # Sort by scheduled start time
                {
                    "$sort": {"scheduled_start": 1}
                }
            ]
            
            self.db.command({
                "create": view_name,
                "viewOn": "Appointment",
                "pipeline": pipeline
            })
            
            logger.info(f"Created view: {view_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating view {view_name}: {e}")
            return False
    
    def create_patient_clinical_history(self):
        """
        VIEW 5: Patient Clinical History
        
        Complete medical history for each patient:
        - All visits (count, dates, types)
        - Financial summary
        
        Use case: Clinical review, medical records, patient care planning
        """
        view_name = "patient_clinical_history"
        
        try:
            self.drop_view(view_name)
            
            pipeline = [
                # Join visits
                {
                    "$lookup": {
                        "from": "Visit",
                        "localField": "patient_id",
                        "foreignField": "patient_id",
                        "as": "visits"
                    }
                },
                # Join invoices for financial summary
                {
                    "$lookup": {
                        "from": "Invoice",
                        "localField": "patient_id",
                        "foreignField": "patient_id",
                        "as": "invoices"
                    }
                },
                # Join payments
                {
                    "$lookup": {
                        "from": "Payment",
                        "localField": "patient_id",
                        "foreignField": "patient_id",
                        "as": "payments"
                    }
                },
                # Calculate metrics
                {
                    "$addFields": {
                        # Visit metrics
                        "total_visits": {"$size": "$visits"},
                        "active_visits": {
                            "$size": {
                                "$filter": {
                                    "input": "$visits",
                                    "as": "v",
                                    "cond": {"$eq": ["$$v.end_time", None]}
                                }
                            }
                        },
                        "completed_visits": {
                            "$size": {
                                "$filter": {
                                    "input": "$visits",
                                    "as": "v",
                                    "cond": {"$ne": ["$$v.end_time", None]}
                                }
                            }
                        },
                        "last_visit_date": {"$max": "$visits.start_time"},
                        
                        # Financial metrics
                        "total_invoiced": {"$sum": "$invoices.total_amount"},
                        "total_paid": {"$sum": "$payments.amount"}
                    }
                },
                # Calculate balance
                {
                    "$addFields": {
                        "outstanding_balance": {
                            "$subtract": ["$total_invoiced", "$total_paid"]
                        }
                    }
                },
                # Shape output
                {
                    "$project": {
                        "patient_id": 1,
                        "first_name": 1,
                        "last_name": 1,
                        "full_name": {"$concat": ["$first_name", " ", "$last_name"]},
                        "date_of_birth": 1,
                        "phone": 1,
                        "email": 1,
                        "gov_card_no": 1,
                        "insurance_no": 1,
                        
                        # Visit summary
                        "total_visits": 1,
                        "active_visits": 1,
                        "completed_visits": 1,
                        "last_visit_date": 1,
                        "has_active_visit": {"$gt": ["$active_visits", 0]},
                        
                        # Financial summary
                        "total_invoiced": 1,
                        "total_paid": 1,
                        "outstanding_balance": 1,
                        "has_outstanding_balance": {"$gt": ["$outstanding_balance", 0]},
                        
                        # Risk flags
                        "needs_follow_up": {
                            "$or": [
                                {"$gt": ["$active_visits", 0]},
                                {"$gt": ["$outstanding_balance", 100]}
                            ]
                        }
                    }
                },
                # Sort by last visit date (most recent first)
                {
                    "$sort": {"last_visit_date": -1}
                }
            ]
            
            self.db.command({
                "create": view_name,
                "viewOn": "Patient",
                "pipeline": pipeline
            })
            
            logger.info(f"Created view: {view_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating view {view_name}: {e}")
            return False
    
    def create_all_views(self):
        """Create all MongoDB views"""
        results = {}
        
        logger.info("Creating all MongoDB views...")
        
        results['visit_complete_details'] = self.create_visit_complete_details()
        results['patient_financial_summary'] = self.create_patient_financial_summary()
        results['staff_workload_analysis'] = self.create_staff_workload_analysis()
        results['daily_clinic_schedule'] = self.create_daily_clinic_schedule()
        results['patient_clinical_history'] = self.create_patient_clinical_history()
        
        success_count = sum(1 for v in results.values() if v)
        logger.info(f"Created {success_count}/{len(results)} views successfully")
        
        return results
    
    def ensure_views_exist(self):
        """Check if all views exist, create them if they don't"""
        missing_views = []
        
        for view_name in self.views:
            if not self.view_exists(view_name):
                missing_views.append(view_name)
        
        if missing_views:
            logger.info(f"Missing views: {missing_views}")
            logger.info("Creating missing views...")
            results = self.create_all_views()
            return all(results.values())
        else:
            logger.info("All views exist")
            return True


def initialize_views():
    """Initialize MongoDB views (called on app startup)"""
    views_manager = ViewsManager()
    views_manager.ensure_views_exist()
    return views_manager


def recreate_all_views():
    """Force recreation of all views"""
    views_manager = ViewsManager()
    return views_manager.create_all_views()


def get_database():
    """Get database connection using Database class"""
    from clinic_api.database import Database
    return Database.connect_db()