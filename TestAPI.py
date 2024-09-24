import unittest
import json
import requests

# Unitest for a few cases.
class TestAPI(unittest.TestCase):

    URL = "http://127.0.0.1:5000/measured_compounds?RT=18"
    URL_delete = "http://127.0.0.1:5000/delete"
    input_data = {
        "compound_id": "50000",
        "compound_name": "NADPH",
        "retention_time": "15",
        "retention_time_comment": "bad peak shape",
        "adduct_name": "M+H",
        "user": "Admin",
        "password": "1111",
        "molecular_formula": "C21H30N7O17P3 ",
        "type": "metabolites"
    }

    output_data = [
        [
            {
                "Added measured compound": 1,
                "Adduct ID": 1,
                "Compound ID": 50000,
                "Ion formula": "C21H31N7O17P3",
                "Ion mass": 746.0984,
                "Measured Compound ID": 1605,
                "Retention Time ID": "C50000:RT15.0"
            }
        ],
        [
            {
                "Added compound": 1,
                "Compound ID": 50000,
                "Compound name": "NADPH",
                "Neutral formula": "C21H30N7O17P3 ",
                "Neutral mass": 745.0911,
                "Type": "metabolites"
            }
        ]
    ]

    # Test the GET endpoint
    def test_query_RT_18(self):
        # Simulate a GET request to /greet
        response = requests.get(self.URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)

        print("Test 1 completed! RT query is working")

    # Test the POST endpoint
    def test_update_NADPH(self):
        # Simulate a GET request to /greet
        response = requests.post(self.URL, json= self.input_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), self.output_data)

        print("Test 2 completed! Updating new compound is working!")

    # Test delete
    def test_delete(self):
        # Simulate a GET request to /greet
        response = requests.delete(self.URL_delete)
        self.assertEqual(response.status_code, 200)

        print("Test 3 completed! Newly added compound deleted!")


if __name__ == '__main__':
    tester = TestAPI()
    tester.test_query_RT_18()
    tester.test_update_NADPH()
    tester.test_delete()