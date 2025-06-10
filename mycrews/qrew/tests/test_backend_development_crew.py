import unittest
from crewAI.qrew.crews.backend_development_crew import BackendDevelopmentCrew

class TestBackendDevelopmentCrew(unittest.TestCase):

    def test_backend_dev_crew_instantiation_and_kickoff(self):
        """Test BackendDevelopmentCrew instantiation and kickoff."""
        try:
            crew_instance = BackendDevelopmentCrew()
        except Exception as e:
            self.fail(f"BackendDevelopmentCrew instantiation failed: {e}")

        inputs = {
            'feature_description': 'Order Processing Service',
            'endpoint_path': '/api/orders',
            'request_model_schema': 'OrderRequest.json',
            'response_model_schema': 'OrderResponse.json',
            'module_name': 'OrdersModule',
            'data_requirements': 'Order table, OrderItems table, Customer reference',
            'database_type': 'PostgreSQL',
            'auth_mechanism': 'OAuth 2.0 Client Credentials',
            'service_name': 'OrderService',
            'security_requirements': 'Input validation, role-based access',
            'queue_technology': 'Kafka',
            'task_type': 'OrderFulfilmentNotification',
            'message_payload_definition': 'OrderNotification.json'
        }

        try:
            result = crew_instance.crew().kickoff(inputs=inputs)
            self.assertIsNotNone(result, "Kickoff returned None.")
        except Exception as e:
            self.fail(f"BackendDevelopmentCrew kickoff failed: {e}")

if __name__ == '__main__':
    unittest.main()
