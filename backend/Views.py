"""
MongoDB Views Module for SW Glenmore Wellness Clinic
Automatically creates and manages MongoDB views
Integrates with Flask application using Database class
"""

import logging

logger = logging.getLogger(__name__)


class ViewsManager:
    """Manages MongoDB views creation and access"""
    
    def __init__(self):
        """
        Initialize ViewsManager
        Uses Database.connect_db() to get database connection
        """
        from database import Database
        
        self.db = Database.connect_db()
        self.views = [
            'patient_full_details',
            'staff_appointments_summary',
            'active_visits_overview',
            'invoice_payment_summary',
            'appointment_calendar_view'
        ]
    
    def view_exists(self, view_name):
        """
        Check if a view exists
        
        Args:
            view_name: Name of the view to check
            
        Returns:
            bool: True if view exists, False otherwise
        """
        try:
            collections = self.db.list_collection_names()
            return view_name in collections
        except Exception as e:
            logger.error(f"Error checking if view exists: {e}")
            return False
    
    def drop_view(self, view_name):
        """
        Drop a view if it exists
        
        Args:
            view_name: Name of the view to drop
        """
        try:
            if self.view_exists(view_name):
                self.db[view_name].drop()
                logger.info(f"Dropped view: {view_name}")
        except Exception as e:
            logger.error(f"Error dropping view {view_name}: {e}")
    
    def create_patient_full_details(self):
        """Create patient_full_details view"""
        view_name = "patient_full_details"
        
        try:
            self.drop_view(view_name)
            
            pipeline = [
                {
                    "$lookup": {
                        "from": "visits",
                        "localField": "patient_id",
                        "foreignField": "patient_id",
                        "as": "visits"
                    }
                },
                {
                    "$lookup": {
                        "from": "appointments",
                        "localField": "patient_id",
                        "foreignField": "patient_id",
                        "as": "appointments"
                    }
                },
                {
                    "$addFields": {
                        "total_visits": {"$size": "$visits"},
                        "total_appointments": {"$size": "$appointments"},
                        "last_visit_date": {"$max": "$visits.start_time"},
                        "completed_visits": {
                            "$size": {
                                "$filter": {
                                    "input": "$visits",
                                    "as": "visit",
                                    "cond": {"$ne": ["$$visit.end_time", None]}
                                }
                            }
                        }
                    }
                },
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
                        "total_visits": 1,
                        "completed_visits": 1,
                        "total_appointments": 1,
                        "last_visit_date": 1,
                        "has_active_visits": {"$gt": ["$total_visits", "$completed_visits"]}
                    }
                }
            ]
            
            self.db.command({
                "create": view_name,
                "viewOn": "patients",
                "pipeline": pipeline
            })
            
            logger.info(f"Created view: {view_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating view {view_name}: {e}")
            return False
    
    def create_staff_appointments_summary(self):
        """Create staff_appointments_summary view"""
        view_name = "staff_appointments_summary"
        
        try:
            self.drop_view(view_name)
            
            pipeline = [
                {
                    "$lookup": {
                        "from": "appointments",
                        "localField": "staff_id",
                        "foreignField": "staff_id",
                        "as": "appointments"
                    }
                },
                {
                    "$lookup": {
                        "from": "visits",
                        "localField": "staff_id",
                        "foreignField": "staff_id",
                        "as": "visits"
                    }
                },
                {
                    "$addFields": {
                        "total_appointments": {"$size": "$appointments"},
                        "total_visits": {"$size": "$visits"},
                        "walkin_appointments": {
                            "$size": {
                                "$filter": {
                                    "input": "$appointments",
                                    "as": "apt",
                                    "cond": {"$eq": ["$$apt.is_walkin", True]}
                                }
                            }
                        }
                    }
                },
                {
                    "$project": {
                        "staff_id": 1,
                        "first_name": 1,
                        "last_name": 1,
                        "full_name": {"$concat": ["$first_name", " ", "$last_name"]},
                        "email": 1,
                        "phone": 1,
                        "active": 1,
                        "total_appointments": 1,
                        "total_visits": 1,
                        "walkin_appointments": 1,
                        "scheduled_appointments": {"$subtract": ["$total_appointments", "$walkin_appointments"]}
                    }
                }
            ]
            
            self.db.command({
                "create": view_name,
                "viewOn": "staff",
                "pipeline": pipeline
            })
            
            logger.info(f"Created view: {view_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating view {view_name}: {e}")
            return False
    
    def create_active_visits_overview(self):
        """Create active_visits_overview view"""
        view_name = "active_visits_overview"
        
        try:
            self.drop_view(view_name)
            
            pipeline = [
                {
                    "$match": {
                        "end_time": None
                    }
                },
                {
                    "$lookup": {
                        "from": "patients",
                        "localField": "patient_id",
                        "foreignField": "patient_id",
                        "as": "patient"
                    }
                },
                {
                    "$lookup": {
                        "from": "staff",
                        "localField": "staff_id",
                        "foreignField": "staff_id",
                        "as": "staff"
                    }
                },
                {
                    "$unwind": "$patient"
                },
                {
                    "$unwind": "$staff"
                },
                {
                    "$project": {
                        "visit_id": 1,
                        "patient_id": 1,
                        "patient_name": {"$concat": ["$patient.first_name", " ", "$patient.last_name"]},
                        "patient_phone": "$patient.phone",
                        "staff_id": 1,
                        "staff_name": {"$concat": ["$staff.first_name", " ", "$staff.last_name"]},
                        "visit_type": 1,
                        "start_time": 1,
                        "notes": 1,
                        "appointment_id": 1
                    }
                },
                {
                    "$sort": {"start_time": -1}
                }
            ]
            
            self.db.command({
                "create": view_name,
                "viewOn": "visits",
                "pipeline": pipeline
            })
            
            logger.info(f"Created view: {view_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating view {view_name}: {e}")
            return False
    
    def create_invoice_payment_summary(self):
        """Create invoice_payment_summary view"""
        view_name = "invoice_payment_summary"
        
        try:
            self.drop_view(view_name)
            
            pipeline = [
                {
                    "$lookup": {
                        "from": "patients",
                        "localField": "patient_id",
                        "foreignField": "patient_id",
                        "as": "patient"
                    }
                },
                {
                    "$lookup": {
                        "from": "payments",
                        "localField": "invoice_id",
                        "foreignField": "invoice_id",
                        "as": "payments"
                    }
                },
                {
                    "$lookup": {
                        "from": "invoice_lines",
                        "localField": "invoice_id",
                        "foreignField": "invoice_id",
                        "as": "line_items"
                    }
                },
                {
                    "$unwind": {
                        "path": "$patient",
                        "preserveNullAndEmptyArrays": True
                    }
                },
                {
                    "$addFields": {
                        "total_amount": {
                            "$sum": {
                                "$map": {
                                    "input": "$line_items",
                                    "as": "line",
                                    "in": {"$multiply": ["$$line.qty", "$$line.unit_price"]}
                                }
                            }
                        },
                        "total_paid": {"$sum": "$payments.amount"},
                        "payment_count": {"$size": "$payments"}
                    }
                },
                {
                    "$addFields": {
                        "balance": {"$subtract": ["$total_amount", "$total_paid"]}
                    }
                },
                {
                    "$project": {
                        "invoice_id": 1,
                        "patient_id": 1,
                        "patient_name": {"$concat": ["$patient.first_name", " ", "$patient.last_name"]},
                        "patient_email": "$patient.email",
                        "invoice_date": 1,
                        "status": 1,
                        "total_amount": 1,
                        "total_paid": 1,
                        "balance": 1,
                        "payment_count": 1,
                        "line_item_count": {"$size": "$line_items"},
                        "is_fully_paid": {"$eq": ["$balance", 0]}
                    }
                },
                {
                    "$sort": {"invoice_date": -1}
                }
            ]
            
            self.db.command({
                "create": view_name,
                "viewOn": "invoices",
                "pipeline": pipeline
            })
            
            logger.info(f"Created view: {view_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating view {view_name}: {e}")
            return False
    
    def create_appointment_calendar_view(self):
        """Create appointment_calendar_view view"""
        view_name = "appointment_calendar_view"
        
        try:
            self.drop_view(view_name)
            
            pipeline = [
                {
                    "$lookup": {
                        "from": "patients",
                        "localField": "patient_id",
                        "foreignField": "patient_id",
                        "as": "patient"
                    }
                },
                {
                    "$lookup": {
                        "from": "staff",
                        "localField": "staff_id",
                        "foreignField": "staff_id",
                        "as": "staff"
                    }
                },
                {
                    "$unwind": "$patient"
                },
                {
                    "$unwind": "$staff"
                },
                {
                    "$project": {
                        "appointment_id": 1,
                        "patient_id": 1,
                        "patient_name": {"$concat": ["$patient.first_name", " ", "$patient.last_name"]},
                        "patient_phone": "$patient.phone",
                        "patient_email": "$patient.email",
                        "staff_id": 1,
                        "staff_name": {"$concat": ["$staff.first_name", " ", "$staff.last_name"]},
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
                        "calendar_title": {
                            "$concat": [
                                "$patient.first_name",
                                " ",
                                "$patient.last_name",
                                " - ",
                                "$staff.first_name",
                                " ",
                                "$staff.last_name"
                            ]
                        },
                        "color": {
                            "$cond": {
                                "if": "$is_walkin",
                                "then": "#ff9f40",
                                "else": "#4285f4"
                            }
                        }
                    }
                },
                {
                    "$sort": {"scheduled_start": 1}
                }
            ]
            
            self.db.command({
                "create": view_name,
                "viewOn": "appointments",
                "pipeline": pipeline
            })
            
            logger.info(f"Created view: {view_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating view {view_name}: {e}")
            return False
    
    def create_all_views(self):
        """
        Create all MongoDB views
        
        Returns:
            dict: Status of each view creation
        """
        results = {}
        
        logger.info("Creating all MongoDB views...")
        
        results['patient_full_details'] = self.create_patient_full_details()
        results['staff_appointments_summary'] = self.create_staff_appointments_summary()
        results['active_visits_overview'] = self.create_active_visits_overview()
        results['invoice_payment_summary'] = self.create_invoice_payment_summary()
        results['appointment_calendar_view'] = self.create_appointment_calendar_view()
        
        success_count = sum(1 for v in results.values() if v)
        logger.info(f"Created {success_count}/{len(results)} views successfully")
        
        return results
    
    def ensure_views_exist(self):
        """
        Check if all views exist, create them if they don't
        
        Returns:
            bool: True if all views exist or were created successfully
        """
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
    """
    Initialize MongoDB views (called on app startup)
    Uses Database.connect_db() internally
    
    Returns:
        ViewsManager: Initialized views manager instance
    """
    views_manager = ViewsManager()
    views_manager.ensure_views_exist()
    return views_manager


def recreate_all_views():
    """
    Force recreation of all views (useful for updates)
    Uses Database.connect_db() internally
    
    Returns:
        dict: Status of each view creation
    """
    views_manager = ViewsManager()
    return views_manager.create_all_views()


def get_database():
    """
    Get database connection using Database class
    
    Returns:
        MongoDB database instance
    """
    from database import Database
    return Database.connect_db()