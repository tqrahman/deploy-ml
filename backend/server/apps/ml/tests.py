from django.test import TestCase
import inspect
from apps.ml.registry import MLRegistry

from apps.ml.income_classifier.random_forest import RandomForestClassifier
from apps.ml.income_classifier.extra_trees import ExtraTreesClassifier

class MLTests(TestCase):
    def test_rf_algorithm(self):
        input_data = {
            "age": 37,
            "workclass": "Private",
            "fnlwgt": 34146,
            "education": "HS-grad",
            "education-num": 9,
            "marital-status": "Married-civ-spouse",
            "occupation": "Craft-repair",
            "relationship": "Husband",
            "race": "White",
            "sex": "Male",
            "capital-gain": 0,
            "capital-loss": 0,
            "hours-per-week": 68,
            "native-country": "United-States"
        }
        my_alg = RandomForestClassifier()
        response = my_alg.compute_prediction(input_data)
        self.assertEqual('OK', response['status'])
        self.assertTrue('label' in response)
        self.assertEqual('<=50K', response['label'])

    def test_registry(self):
        
        # Create a new MLRegistry object
        registry = MLRegistry()
        
        # Check to see if empty registry has no endpoints
        self.assertEqual(len(registry.endpoints), 0)
        
        # Creating a name for endpoint
        endpoint_name = "income_classifier"
        
        # Creating an algorithm object
        algorithm_object = RandomForestClassifier()
        
        # Creating a name for the corresponding algo object
        algorithm_name = "random forest"
        
        # Creating status for the algo object
        algorithm_status = "production"

        # Creating version for the algo object
        algorithm_version = "0.0.1"

        # Tagging the owner of the algorithm object
        algorithm_owner = "TR"

        # Providing a description of the algorithm
        algorithm_description = "Random Forest with simple pre- and post-processing"
        
        # Inspecting
        algorithm_code = inspect.getsource(RandomForestClassifier)
        
        # Adding algorithm to registry
        registry.add_algorithm(
            endpoint_name, algorithm_object, algorithm_name,
            algorithm_status, algorithm_version, algorithm_owner,
            algorithm_description, algorithm_code
        )
        
        # Checking to see if there is one endpoint
        self.assertEqual(len(registry.endpoints), 1)

    def test_et_algorithm(self):
        input_data = {
            "age": 37,
            "workclass": "Private",
            "fnlwgt": 34146,
            "education": "HS-grad",
            "education-num": 9,
            "marital-status": "Married-civ-spouse",
            "occupation": "Craft-repair",
            "relationship": "Husband",
            "race": "White",
            "sex": "Male",
            "capital-gain": 0,
            "capital-loss": 0,
            "hours-per-week": 68,
            "native-country": "United-States"
        }
        my_alg = ExtraTreesClassifier()
        response = my_alg.compute_prediction(input_data)
        self.assertEqual('OK', response['status'])
        self.assertTrue('label' in response)
        self.assertEqual('<=50K', response['label'])