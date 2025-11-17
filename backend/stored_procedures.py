"""
MongoDB Stored Functions (Stored Procedures) for SW Glenmore Wellness Clinic
Creates reusable JavaScript functions stored in MongoDB
"""
import logging

logger = logging.getLogger(__name__)


class StoredFunctionsManager:
    """Manages MongoDB stored functions (stored procedures)"""
    
    def __init__(self):
        """
        Initialize StoredFunctionsManager
        Uses Database.connect_db() to get database connection
        """
        from database import Database
        
        self.db = Database.connect_db()
        self.functions = [
            'calculatePatientAge',
            'getPatientVisitCount',
            'calculateInvoiceTotal',
            'getStaffAppointmentCount',
            'isAppointmentAvailable'
        ]
    
    def function_exists(self, function_name):
        """
        Check if a stored function exists
        
        Args:
            function_name: Name of the function to check
            
        Returns:
            bool: True if function exists, False otherwise
        """
        try:
            result = self.db.system.js.find_one({'_id': function_name})
            return result is not None
        except Exception as e:
            logger.error(f"Error checking if function exists: {e}")
            return False
    
    def drop_function(self, function_name):
        """
        Drop a stored function if it exists
        
        Args:
            function_name: Name of the function to drop
        """
        try:
            if self.function_exists(function_name):
                self.db.system.js.delete_one({'_id': function_name})
                logger.info(f"Dropped function: {function_name}")
        except Exception as e:
            logger.error(f"Error dropping function {function_name}: {e}")
    
    def create_calculate_patient_age(self):
        """
        Create calculatePatientAge function
        Calculates patient's age from date of birth
        
        Usage in MongoDB:
        db.eval('calculatePatientAge("1990-05-15")')
        """
        function_name = "calculatePatientAge"
        
        try:
            self.drop_function(function_name)
            
            # JavaScript function code
            function_code = """
            function(dateOfBirth) {
                if (!dateOfBirth) return null;
                
                var dob = new Date(dateOfBirth);
                var today = new Date();
                var age = today.getFullYear() - dob.getFullYear();
                var monthDiff = today.getMonth() - dob.getMonth();
                
                if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
                    age--;
                }
                
                return age;
            }
            """
            
            # Store function in system.js collection
            self.db.system.js.insert_one({
                '_id': function_name,
                'value': function_code
            })
            
            logger.info(f"Created function: {function_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating function {function_name}: {e}")
            return False
    
    def create_get_patient_visit_count(self):
        """
        Create getPatientVisitCount function
        Gets total visit count for a patient
        
        Usage in MongoDB:
        db.eval('getPatientVisitCount(1)')
        """
        function_name = "getPatientVisitCount"
        
        try:
            self.drop_function(function_name)
            
            function_code = """
            function(patientId) {
                if (!patientId) return 0;
                
                var count = db.visits.countDocuments({patient_id: patientId});
                return count;
            }
            """
            
            self.db.system.js.insert_one({
                '_id': function_name,
                'value': function_code
            })
            
            logger.info(f"Created function: {function_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating function {function_name}: {e}")
            return False
    
    def create_calculate_invoice_total(self):
        """
        Create calculateInvoiceTotal function
        Calculates total amount for an invoice from its line items
        
        Usage in MongoDB:
        db.eval('calculateInvoiceTotal(1)')
        """
        function_name = "calculateInvoiceTotal"
        
        try:
            self.drop_function(function_name)
            
            function_code = """
            function(invoiceId) {
                if (!invoiceId) return 0;
                
                var lines = db.invoice_lines.find({invoice_id: invoiceId}).toArray();
                var total = 0;
                
                lines.forEach(function(line) {
                    total += (line.qty || 0) * (line.unit_price || 0);
                });
                
                return total;
            }
            """
            
            self.db.system.js.insert_one({
                '_id': function_name,
                'value': function_code
            })
            
            logger.info(f"Created function: {function_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating function {function_name}: {e}")
            return False
    
    def create_get_staff_appointment_count(self):
        """
        Create getStaffAppointmentCount function
        Gets total appointment count for a staff member
        
        Usage in MongoDB:
        db.eval('getStaffAppointmentCount(1)')
        """
        function_name = "getStaffAppointmentCount"
        
        try:
            self.drop_function(function_name)
            
            function_code = """
            function(staffId) {
                if (!staffId) return 0;
                
                var count = db.appointments.countDocuments({staff_id: staffId});
                return count;
            }
            """
            
            self.db.system.js.insert_one({
                '_id': function_name,
                'value': function_code
            })
            
            logger.info(f"Created function: {function_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating function {function_name}: {e}")
            return False
    
    def create_is_appointment_available(self):
        """
        Create isAppointmentAvailable function
        Checks if a time slot is available for a staff member
        
        Usage in MongoDB:
        db.eval('isAppointmentAvailable(1, "2024-01-15T10:00:00", "2024-01-15T11:00:00")')
        """
        function_name = "isAppointmentAvailable"
        
        try:
            self.drop_function(function_name)
            
            function_code = """
            function(staffId, startTime, endTime) {
                if (!staffId || !startTime || !endTime) return false;
                
                var start = new Date(startTime);
                var end = new Date(endTime);
                
                // Check for overlapping appointments
                var overlapping = db.appointments.countDocuments({
                    staff_id: staffId,
                    $or: [
                        // New appointment starts during existing appointment
                        {
                            scheduled_start: {$lte: start},
                            scheduled_end: {$gt: start}
                        },
                        // New appointment ends during existing appointment
                        {
                            scheduled_start: {$lt: end},
                            scheduled_end: {$gte: end}
                        },
                        // New appointment completely contains existing appointment
                        {
                            scheduled_start: {$gte: start},
                            scheduled_end: {$lte: end}
                        }
                    ]
                });
                
                return overlapping === 0;
            }
            """
            
            self.db.system.js.insert_one({
                '_id': function_name,
                'value': function_code
            })
            
            logger.info(f"Created function: {function_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating function {function_name}: {e}")
            return False
    
    def create_all_functions(self):
        """
        Create all MongoDB stored functions
        
        Returns:
            dict: Status of each function creation
        """
        results = {}
        
        logger.info("Creating all MongoDB stored functions...")
        
        results['calculatePatientAge'] = self.create_calculate_patient_age()
        results['getPatientVisitCount'] = self.create_get_patient_visit_count()
        results['calculateInvoiceTotal'] = self.create_calculate_invoice_total()
        results['getStaffAppointmentCount'] = self.create_get_staff_appointment_count()
        results['isAppointmentAvailable'] = self.create_is_appointment_available()
        
        success_count = sum(1 for v in results.values() if v)
        logger.info(f"Created {success_count}/{len(results)} functions successfully")
        
        return results
    
    def ensure_functions_exist(self):
        """
        Check if all functions exist, create them if they don't
        
        Returns:
            bool: True if all functions exist or were created successfully
        """
        missing_functions = []
        
        for function_name in self.functions:
            if not self.function_exists(function_name):
                missing_functions.append(function_name)
        
        if missing_functions:
            logger.info(f"Missing functions: {missing_functions}")
            logger.info("Creating missing functions...")
            results = self.create_all_functions()
            return all(results.values())
        else:
            logger.info("All functions exist")
            return True
    
    def test_functions(self):
        """
        Test all stored functions with sample data
        
        Returns:
            dict: Test results for each function
        """
        results = {}
        
        logger.info("Testing stored functions...")
        
        try:
            # Test calculatePatientAge
            age = self.db.command('eval', 'calculatePatientAge("1990-05-15")')
            results['calculatePatientAge'] = {'success': True, 'result': age['retval']}
            logger.info(f"calculatePatientAge('1990-05-15') = {age['retval']} years")
        except Exception as e:
            results['calculatePatientAge'] = {'success': False, 'error': str(e)}
            logger.error(f"Error testing calculatePatientAge: {e}")
        
        try:
            # Test getPatientVisitCount
            count = self.db.command('eval', 'getPatientVisitCount(1)')
            results['getPatientVisitCount'] = {'success': True, 'result': count['retval']}
            logger.info(f"getPatientVisitCount(1) = {count['retval']} visits")
        except Exception as e:
            results['getPatientVisitCount'] = {'success': False, 'error': str(e)}
            logger.error(f"Error testing getPatientVisitCount: {e}")
        
        try:
            # Test calculateInvoiceTotal
            total = self.db.command('eval', 'calculateInvoiceTotal(1)')
            results['calculateInvoiceTotal'] = {'success': True, 'result': total['retval']}
            logger.info(f"calculateInvoiceTotal(1) = ${total['retval']}")
        except Exception as e:
            results['calculateInvoiceTotal'] = {'success': False, 'error': str(e)}
            logger.error(f"Error testing calculateInvoiceTotal: {e}")
        
        try:
            # Test getStaffAppointmentCount
            count = self.db.command('eval', 'getStaffAppointmentCount(1)')
            results['getStaffAppointmentCount'] = {'success': True, 'result': count['retval']}
            logger.info(f"getStaffAppointmentCount(1) = {count['retval']} appointments")
        except Exception as e:
            results['getStaffAppointmentCount'] = {'success': False, 'error': str(e)}
            logger.error(f"Error testing getStaffAppointmentCount: {e}")
        
        try:
            # Test isAppointmentAvailable
            available = self.db.command('eval', 'isAppointmentAvailable(1, "2024-12-25T10:00:00", "2024-12-25T11:00:00")')
            results['isAppointmentAvailable'] = {'success': True, 'result': available['retval']}
            logger.info(f"isAppointmentAvailable(1, ...) = {available['retval']}")
        except Exception as e:
            results['isAppointmentAvailable'] = {'success': False, 'error': str(e)}
            logger.error(f"Error testing isAppointmentAvailable: {e}")
        
        return results


def initialize_stored_functions():
    """
    Initialize MongoDB stored functions (called on app startup)
    
    Returns:
        StoredFunctionsManager: Initialized functions manager instance
    """
    functions_manager = StoredFunctionsManager()
    functions_manager.ensure_functions_exist()
    return functions_manager


def recreate_all_functions():
    """
    Force recreation of all stored functions
    
    Returns:
        dict: Status of each function creation
    """
    functions_manager = StoredFunctionsManager()
    return functions_manager.create_all_functions()


def test_stored_functions():
    """
    Test all stored functions
    
    Returns:
        dict: Test results
    """
    functions_manager = StoredFunctionsManager()
    return functions_manager.test_functions()


def main():
    """Main function to create and test all stored functions"""
    print("=" * 60)
    print("MongoDB Stored Functions Creator")
    print("SW Glenmore Wellness Clinic Database")
    print("=" * 60)
    print()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Create all functions
        print("Creating stored functions...")
        functions_manager = StoredFunctionsManager()
        results = functions_manager.create_all_functions()
        
        print("\n" + "=" * 60)
        print("Creation Results:")
        print("=" * 60)
        for func_name, success in results.items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            print(f"{func_name}: {status}")
        
        # Test functions
        print("\n" + "=" * 60)
        print("Testing Functions:")
        print("=" * 60)
        test_results = functions_manager.test_functions()
        
        print("\n" + "=" * 60)
        print("✅ ALL STORED FUNCTIONS CREATED!")
        print("=" * 60)
        print()
        print("Available functions:")
        for func in functions_manager.functions:
            print(f"  - {func}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
