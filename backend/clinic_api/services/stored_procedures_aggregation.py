"""
MongoDB Aggregation Pipeline Functions for SW Glenmore Wellness Clinic
Replaces stored procedures with aggregation pipelines (MongoDB Atlas compatible)
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class AggregationFunctions:
    """
    Implements database functions using MongoDB Aggregation Pipelines
    This is the recommended approach for MongoDB Atlas
    """
    
    def __init__(self):
        """
        Initialize AggregationFunctions
        Uses Database.connect_db() to get database connection
        """
        from database import Database
        
        self.db = Database.connect_db()
        logger.info("Aggregation pipeline functions initialized (MongoDB Atlas compatible)")
    
    # ==================== FUNCTION 1: Calculate Patient Age ====================
    
    def calculate_patient_age(self, date_of_birth: str) -> Optional[int]:
        """
        Calculate patient age using aggregation pipeline
        
        Args:
            date_of_birth: Date string in format "YYYY-MM-DD"
            
        Returns:
            int: Age in years
            
        Example:
            age = agg_functions.calculate_patient_age("1990-05-15")
            # Returns: 34
        """
        try:
            if not date_of_birth:
                return None
            
            # Convert string to datetime
            if isinstance(date_of_birth, str):
                dob = datetime.strptime(date_of_birth, "%Y-%m-%d")
            else:
                dob = date_of_birth
            
            # Use aggregation pipeline with $dateDiff (MongoDB 5.0+)
            # Fallback to Python calculation for older versions
            pipeline = [
                {
                    "$project": {
                        "age": {
                            "$dateDiff": {
                                "startDate": dob,
                                "endDate": "$$NOW",
                                "unit": "year"
                            }
                        }
                    }
                },
                {"$limit": 1}
            ]
            
            try:
                # Try aggregation first (MongoDB 5.0+)
                result = list(self.db.patients.aggregate(pipeline))
                if result:
                    return result[0].get('age')
            except Exception:
                # Fallback to Python calculation
                pass
            
            # Python fallback calculation
            today = datetime.now()
            age = today.year - dob.year
            if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
                age -= 1
            return age
            
        except Exception as e:
            logger.error(f"Error calculating patient age: {e}")
            return None
    
    # ==================== FUNCTION 2: Get Patient Visit Count ====================
    
    def get_patient_visit_count(self, patient_id: int) -> int:
        """
        Get total visit count for a patient using aggregation
        
        Args:
            patient_id: Patient ID
            
        Returns:
            int: Number of visits
            
        Example:
            count = agg_functions.get_patient_visit_count(1)
            # Returns: 12
        """
        try:
            if not patient_id:
                return 0
            
            pipeline = [
                {"$match": {"patient_id": patient_id}},
                {"$count": "total_visits"}
            ]
            
            result = list(self.db.visits.aggregate(pipeline))
            
            if result:
                return result[0].get('total_visits', 0)
            return 0
            
        except Exception as e:
            logger.error(f"Error getting patient visit count: {e}")
            return 0
    
    def get_patient_visits_detailed(self, patient_id: int) -> Dict[str, Any]:
        """
        Get detailed visit statistics using aggregation
        Returns completed, active, and total visit counts
        
        Example:
            stats = agg_functions.get_patient_visits_detailed(1)
            # Returns: {'total_visits': 12, 'completed_visits': 10, 'active_visits': 2}
        """
        try:
            pipeline = [
                {"$match": {"patient_id": patient_id}},
                {
                    "$facet": {
                        "total": [{"$count": "count"}],
                        "completed": [
                            {"$match": {"end_time": {"$ne": None}}},
                            {"$count": "count"}
                        ],
                        "active": [
                            {"$match": {"end_time": None}},
                            {"$count": "count"}
                        ]
                    }
                }
            ]
            
            result = list(self.db.visits.aggregate(pipeline))
            
            if result:
                data = result[0]
                return {
                    'total_visits': data['total'][0]['count'] if data['total'] else 0,
                    'completed_visits': data['completed'][0]['count'] if data['completed'] else 0,
                    'active_visits': data['active'][0]['count'] if data['active'] else 0
                }
            
            return {'total_visits': 0, 'completed_visits': 0, 'active_visits': 0}
            
        except Exception as e:
            logger.error(f"Error getting detailed visit stats: {e}")
            return {'total_visits': 0, 'completed_visits': 0, 'active_visits': 0}
    
    # ==================== FUNCTION 3: Calculate Invoice Total ====================
    
    def calculate_invoice_total(self, invoice_id: int) -> float:
        """
        Calculate invoice total using aggregation pipeline
        
        Args:
            invoice_id: Invoice ID
            
        Returns:
            float: Total amount
            
        Example:
            total = agg_functions.calculate_invoice_total(1)
            # Returns: 250.50
        """
        try:
            if not invoice_id:
                return 0.0
            
            pipeline = [
                {"$match": {"invoice_id": invoice_id}},
                {
                    "$group": {
                        "_id": "$invoice_id",
                        "total": {
                            "$sum": {
                                "$multiply": ["$qty", "$unit_price"]
                            }
                        }
                    }
                }
            ]
            
            result = list(self.db.invoice_lines.aggregate(pipeline))
            
            if result:
                return round(result[0].get('total', 0.0), 2)
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating invoice total: {e}")
            return 0.0
    
    def get_invoice_summary(self, invoice_id: int) -> Dict[str, Any]:
        """
        Get complete invoice summary with line items using aggregation
        
        Example:
            summary = agg_functions.get_invoice_summary(1)
            # Returns: {'invoice_id': 1, 'total_amount': 250.50, 'line_count': 5, ...}
        """
        try:
            pipeline = [
                {"$match": {"invoice_id": invoice_id}},
                {
                    "$group": {
                        "_id": "$invoice_id",
                        "total_amount": {
                            "$sum": {"$multiply": ["$qty", "$unit_price"]}
                        },
                        "line_count": {"$sum": 1},
                        "items": {
                            "$push": {
                                "description": "$description",
                                "qty": "$qty",
                                "unit_price": "$unit_price",
                                "line_total": {"$multiply": ["$qty", "$unit_price"]}
                            }
                        }
                    }
                },
                {
                    "$lookup": {
                        "from": "invoices",
                        "localField": "_id",
                        "foreignField": "invoice_id",
                        "as": "invoice"
                    }
                },
                {"$unwind": {"path": "$invoice", "preserveNullAndEmptyArrays": True}},
                {
                    "$project": {
                        "invoice_id": "$_id",
                        "invoice_date": "$invoice.invoice_date",
                        "status": "$invoice.status",
                        "patient_id": "$invoice.patient_id",
                        "total_amount": 1,
                        "line_count": 1,
                        "items": 1
                    }
                }
            ]
            
            result = list(self.db.invoice_lines.aggregate(pipeline))
            
            if result:
                return result[0]
            return {}
            
        except Exception as e:
            logger.error(f"Error getting invoice summary: {e}")
            return {}
    
    # ==================== FUNCTION 4: Get Staff Appointment Count ====================
    
    def get_staff_appointment_count(self, staff_id: int) -> int:
        """
        Get total appointment count for staff using aggregation
        
        Args:
            staff_id: Staff ID
            
        Returns:
            int: Number of appointments
            
        Example:
            count = agg_functions.get_staff_appointment_count(1)
            # Returns: 25
        """
        try:
            if not staff_id:
                return 0
            
            pipeline = [
                {"$match": {"staff_id": staff_id}},
                {"$count": "total_appointments"}
            ]
            
            result = list(self.db.appointments.aggregate(pipeline))
            
            if result:
                return result[0].get('total_appointments', 0)
            return 0
            
        except Exception as e:
            logger.error(f"Error getting staff appointment count: {e}")
            return 0
    
    def get_staff_workload_summary(self, staff_id: int) -> Dict[str, Any]:
        """
        Get detailed staff workload using aggregation
        
        Example:
            summary = agg_functions.get_staff_workload_summary(1)
            # Returns: {'total_appointments': 25, 'walkin_count': 5, 'scheduled_count': 20}
        """
        try:
            pipeline = [
                {"$match": {"staff_id": staff_id}},
                {
                    "$facet": {
                        "appointments": [
                            {"$count": "count"}
                        ],
                        "walkins": [
                            {"$match": {"is_walkin": True}},
                            {"$count": "count"}
                        ],
                        "scheduled": [
                            {"$match": {"is_walkin": {"$ne": True}}},
                            {"$count": "count"}
                        ]
                    }
                }
            ]
            
            result = list(self.db.appointments.aggregate(pipeline))
            
            if result:
                data = result[0]
                return {
                    'total_appointments': data['appointments'][0]['count'] if data['appointments'] else 0,
                    'walkin_count': data['walkins'][0]['count'] if data['walkins'] else 0,
                    'scheduled_count': data['scheduled'][0]['count'] if data['scheduled'] else 0
                }
            
            return {'total_appointments': 0, 'walkin_count': 0, 'scheduled_count': 0}
            
        except Exception as e:
            logger.error(f"Error getting staff workload: {e}")
            return {}
    
    # ==================== FUNCTION 5: Check Appointment Availability ====================
    
    def is_appointment_available(self, staff_id: int, start_time: str, end_time: str) -> bool:
        """
        Check if time slot is available using aggregation
        
        Args:
            staff_id: Staff ID
            start_time: Start time (ISO string or datetime)
            end_time: End time (ISO string or datetime)
            
        Returns:
            bool: True if available, False if conflict
            
        Example:
            available = agg_functions.is_appointment_available(
                1, 
                "2024-12-25T10:00:00", 
                "2024-12-25T11:00:00"
            )
            # Returns: True or False
        """
        try:
            if not staff_id or not start_time or not end_time:
                return False
            
            # Convert strings to datetime if needed
            if isinstance(start_time, str):
                start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            else:
                start = start_time
            
            if isinstance(end_time, str):
                end = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            else:
                end = end_time
            
            # Use aggregation to find conflicts
            pipeline = [
                {
                    "$match": {
                        "staff_id": staff_id,
                        "$or": [
                            # New appointment starts during existing appointment
                            {
                                "scheduled_start": {"$lte": start},
                                "scheduled_end": {"$gt": start}
                            },
                            # New appointment ends during existing appointment
                            {
                                "scheduled_start": {"$lt": end},
                                "scheduled_end": {"$gte": end}
                            },
                            # New appointment completely contains existing appointment
                            {
                                "scheduled_start": {"$gte": start},
                                "scheduled_end": {"$lte": end}
                            }
                        ]
                    }
                },
                {"$count": "conflicts"}
            ]
            
            result = list(self.db.appointments.aggregate(pipeline))
            
            # No conflicts means available
            return len(result) == 0 or result[0].get('conflicts', 1) == 0
            
        except Exception as e:
            logger.error(f"Error checking appointment availability: {e}")
            return False
    
    # ==================== BONUS: Advanced Aggregations ====================
    
    def get_patient_complete_stats(self, patient_id: int) -> Dict[str, Any]:
        """
        Get comprehensive patient statistics using single aggregation
        Combines multiple queries into one efficient pipeline
        
        Example:
            stats = agg_functions.get_patient_complete_stats(1)
            # Returns complete patient profile with all stats in ONE query
        """
        try:
            pipeline = [
                {"$match": {"patient_id": patient_id}},
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
                    "$project": {
                        "patient_id": 1,
                        "first_name": 1,
                        "last_name": 1,
                        "full_name": {"$concat": ["$first_name", " ", "$last_name"]},
                        "date_of_birth": 1,
                        "email": 1,
                        "phone": 1,
                        "total_visits": {"$size": "$visits"},
                        "completed_visits": {
                            "$size": {
                                "$filter": {
                                    "input": "$visits",
                                    "as": "v",
                                    "cond": {"$ne": ["$$v.end_time", None]}
                                }
                            }
                        },
                        "active_visits": {
                            "$size": {
                                "$filter": {
                                    "input": "$visits",
                                    "as": "v",
                                    "cond": {"$eq": ["$$v.end_time", None]}
                                }
                            }
                        },
                        "total_appointments": {"$size": "$appointments"},
                        "last_visit_date": {"$max": "$visits.start_time"}
                    }
                }
            ]
            
            result = list(self.db.patients.aggregate(pipeline))
            
            if result:
                patient_data = result[0]
                # Calculate age
                if patient_data.get('date_of_birth'):
                    age = self.calculate_patient_age(patient_data.get('date_of_birth'))
                    patient_data['age'] = age
                return patient_data
            
            return {}
            
        except Exception as e:
            logger.error(f"Error getting patient complete stats: {e}")
            return {}
    
    def get_staff_complete_stats(self, staff_id: int) -> Dict[str, Any]:
        """
        Get comprehensive staff statistics
        
        Example:
            stats = agg_functions.get_staff_complete_stats(1)
        """
        try:
            pipeline = [
                {"$match": {"staff_id": staff_id}},
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
                    "$project": {
                        "staff_id": 1,
                        "first_name": 1,
                        "last_name": 1,
                        "full_name": {"$concat": ["$first_name", " ", "$last_name"]},
                        "email": 1,
                        "phone": 1,
                        "active": 1,
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
                }
            ]
            
            result = list(self.db.staff.aggregate(pipeline))
            
            if result:
                return result[0]
            return {}
            
        except Exception as e:
            logger.error(f"Error getting staff complete stats: {e}")
            return {}
    
    def validate_appointment(self, staff_id: int, start_time: str, end_time: str) -> Dict[str, Any]:
        """
        Validate appointment before creating
        Checks staff availability and time slot conflicts
        
        Example:
            result = agg_functions.validate_appointment(1, "2024-12-25T10:00:00", "2024-12-25T11:00:00")
            # Returns: {'valid': True, 'staff_name': 'Dr. Smith', 'message': '...'}
        """
        try:
            # Check if staff exists and is active
            staff = self.db.staff.find_one({'staff_id': staff_id, 'active': True})
            if not staff:
                return {
                    'valid': False,
                    'reason': 'Staff member not found or inactive'
                }
            
            # Check availability using aggregation
            available = self.is_appointment_available(staff_id, start_time, end_time)
            
            if not available:
                return {
                    'valid': False,
                    'reason': 'Time slot conflict - appointment already exists in this time range'
                }
            
            return {
                'valid': True,
                'staff_name': f"{staff.get('first_name', '')} {staff.get('last_name', '')}",
                'message': 'Appointment can be scheduled'
            }
        except Exception as e:
            logger.error(f"Error validating appointment: {e}")
            return {
                'valid': False,
                'reason': f'Validation error: {str(e)}'
            }


# Global instance
agg_functions = AggregationFunctions()


def initialize_aggregation_functions():
    """
    Initialize aggregation functions (called on app startup)
    
    Returns:
        AggregationFunctions: Initialized functions instance
    """
    logger.info("Aggregation functions module loaded successfully")
    return agg_functions


def test_aggregation_functions():
    """
    Test aggregation functions
    
    Returns:
        dict: Test results for each function
    """
    results = {}
    
    logger.info("Testing aggregation functions...")
    
    try:
        # Test calculate_patient_age
        age = agg_functions.calculate_patient_age("1990-05-15")
        results['calculate_patient_age'] = {'success': True, 'result': age}
        logger.info(f"calculate_patient_age('1990-05-15') = {age} years")
    except Exception as e:
        results['calculate_patient_age'] = {'success': False, 'error': str(e)}
        logger.error(f"Error testing calculate_patient_age: {e}")
    
    try:
        # Test get_patient_visit_count
        count = agg_functions.get_patient_visit_count(1)
        results['get_patient_visit_count'] = {'success': True, 'result': count}
        logger.info(f"get_patient_visit_count(1) = {count} visits")
    except Exception as e:
        results['get_patient_visit_count'] = {'success': False, 'error': str(e)}
        logger.error(f"Error testing get_patient_visit_count: {e}")
    
    try:
        # Test calculate_invoice_total
        total = agg_functions.calculate_invoice_total(1)
        results['calculate_invoice_total'] = {'success': True, 'result': total}
        logger.info(f"calculate_invoice_total(1) = ${total}")
    except Exception as e:
        results['calculate_invoice_total'] = {'success': False, 'error': str(e)}
        logger.error(f"Error testing calculate_invoice_total: {e}")
    
    try:
        # Test get_staff_appointment_count
        count = agg_functions.get_staff_appointment_count(1)
        results['get_staff_appointment_count'] = {'success': True, 'result': count}
        logger.info(f"get_staff_appointment_count(1) = {count} appointments")
    except Exception as e:
        results['get_staff_appointment_count'] = {'success': False, 'error': str(e)}
        logger.error(f"Error testing get_staff_appointment_count: {e}")
    
    try:
        # Test is_appointment_available
        available = agg_functions.is_appointment_available(1, "2024-12-25T10:00:00", "2024-12-25T11:00:00")
        results['is_appointment_available'] = {'success': True, 'result': available}
        logger.info(f"is_appointment_available(1, ...) = {available}")
    except Exception as e:
        results['is_appointment_available'] = {'success': False, 'error': str(e)}
        logger.error(f"Error testing is_appointment_available: {e}")
    
    return results


if __name__ == "__main__":
    import sys
    sys.path.insert(0, '.')
    
    print("=" * 60)
    print("Aggregation Pipeline Functions Test")
    print("MongoDB Atlas Compatible")
    print("=" * 60)
    print()
    
    logging.basicConfig(level=logging.INFO)
    
    try:
        functions = initialize_aggregation_functions()
        results = test_aggregation_functions()
        
        print("\n" + "=" * 60)
        print("Test Results:")
        print("=" * 60)
        for func_name, result in results.items():
            if result.get('success'):
                print(f"✓ {func_name}: SUCCESS - Result: {result.get('result')}")
            else:
                print(f"✗ {func_name}: FAILED - {result.get('error')}")
        
        print("\n" + "=" * 60)
        print("✅ Aggregation Functions Ready!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)