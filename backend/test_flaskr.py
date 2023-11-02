import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category, db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('student', 'student','127.0.0.1:5432', self.database_name)
        self.app = create_app(test_config=True, test_db_url=self.database_path)
        self.client = self.app.test_client()
        self.db = db

    def tearDown(self):
        """Executed after reach test"""
        with self.app.app_context():
            self.db.session.remove()
        pass

    """
    Write at least one test for each test for successful operation and for expected errors.
    """
    #----------------------------------------------------------------------------#
    # get_categories
    #----------------------------------------------------------------------------#
    def test_get_categories_success(self):
        response = self.client.get('/categories')
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['categories']) >= 2) # At least 2 categories are expected

    def test_get_categories_error(self):
        # Simulate an error by causing an exception
        with self.app.app_context():
            self.db.session.remove() # Close the DB connection to cause an exception
            response = self.client.get('/')
            data = response.get_json()
            
            self.assertEqual(response.status_code, 500)
            self.assertFalse(data['success'])

    #----------------------------------------------------------------------------#
    # get_questions
    #----------------------------------------------------------------------------#
    def test_get_questions_success(self):
        response = self.client.get('/questions?page=1')
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']) >= 2)
        self.assertTrue(data['total_questions'] >= 2)
        self.assertTrue('categories' in data)

    def test_get_questions_error(self):
        # Simulate an error by causing an exception
        with self.app.app_context():
            self.db.session.remove() # Close the DB connection to cause an exception
            response = self.client.get('/questions?page=1')
            data = response.get_json()

            self.assertEqual(response.status_code, 500)
            self.assertFalse(data['success'])

    #----------------------------------------------------------------------------#
    # delete_question
    #----------------------------------------------------------------------------#
    def test_delete_question_success(self):
        with self.app.app_context():
            qids = self.db.session.query(Question.id).first()
            qid = qids[0]
            response = self.client.delete(f'/questions/{qid}')
            data = response.get_json()

            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['message'], 'Question deleted successfully')

    def test_delete_question_not_found(self):
        # Try to delete a question that does not exist
        response = self.client.delete('/questions/404404')
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Question not found')

    def test_delete_question_error(self):
        # Simulate an error by causing an exception
        with self.app.app_context():
            self.db.session.remove() # Close the DB connection to cause an exception
            response = self.client.delete('/questions/2')  # Assuming question with ID 1 exists
            data = response.get_json()

            self.assertEqual(response.status_code, 500)
            self.assertFalse(data['success'])

    #----------------------------------------------------------------------------#
    # create_question
    #----------------------------------------------------------------------------#
    def test_create_question_success(self):
        data = {
            'question': 'Sample Question 1',
            'answer': 'Sample Answer 1',
            'category': 1,
            'difficulty': 1
        }
        response = self.client.post('/questions', data=json.dumps(data), content_type='application/json')
        data = response.get_json()

        self.assertEqual(response.status_code, 201)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Question created successfully')
        self.assertTrue('question' in data)

    def test_create_question_missing_fields(self):
        data = {
            'question': 'Sample Question 1',
            'answer': 'Sample Answer 1',
            'category': None,
            'difficulty': None
        }
        response = self.client.post('/questions', data=json.dumps(data), content_type='application/json')
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Question, answer, and category are required fields')

    def test_create_question_error(self):
        # Simulate an error by causing an exception
        with self.app.app_context():
            self.db.session.remove()  # Close the database connection to cause an exception
            data = {
                'question': 'Sample Question 2',
                'answer': 'Sample Answer 2',
                'category': 1,
                'difficulty': 1
            }
            response = self.client.post('/questions', data=json.dumps(data), content_type='application/json')
            data = response.get_json()

            self.assertEqual(response.status_code, 500)
            self.assertFalse(data['success'])

    #----------------------------------------------------------------------------#
    # search_questions
    #----------------------------------------------------------------------------#
    def test_search_questions_success(self):
        data = {'searchTerm': 'Sample'}
        response = self.client.post('/questions/search', data=json.dumps(data), content_type='application/json')
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Questions retrieved successfully')
        self.assertTrue('questions' in data)
        self.assertTrue(len(data['questions']) >= 1) 

    def test_search_questions_no_results(self):
        data = {'searchTerm': 'nonexistent'}
        response = self.client.post('/questions/search', data=json.dumps(data), content_type='application/json')
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'No questions found')
        self.assertTrue('questions' in data)
        self.assertEqual(len(data['questions']), 0)  # No matching questions

    def test_search_questions_missing_search_term(self):
        data = {'searchTerm': None} # Missing 'searchTerm' in the request
        response = self.client.post('/questions/search', data=json.dumps(data), content_type='application/json')
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Search term is required')

    def test_search_questions_error(self):
        # Simulate an error by causing an exception
        with self.app.app_context():
            self.db.session.remove()  # Close the database connection to cause an exception
            data = {'searchTerm': 'autobiography'}
            response = self.client.post('/questions/search', data=json.dumps(data), content_type='application/json')
            data = response.get_json()

            self.assertEqual(response.status_code, 500)
            self.assertFalse(data['success'])

    #----------------------------------------------------------------------------#
    # get_questions_by_category
    #----------------------------------------------------------------------------#
    def test_get_questions_by_category(self):
        data = {'category': 1}
        response = self.client.get('/categories/1/questions', data=json.dumps(data), content_type='application/json')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Questions retrieved successfully')
        self.assertTrue('questions' in data)
        self.assertTrue(len(data['questions']) >= 1)

    def test_get_questions_by_category_not_found(self):
        data = {'category': 404}
        response = self.client.get('/categories/404/questions', data=json.dumps(data), content_type='application/json')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'No questions found in the category')
        self.assertTrue('questions' in data)
        self.assertEqual(len(data['questions']), 0)  # No question

    def test_get_questions_by_category_error(self):
        # Simulate an error by causing an exception
        with self.app.app_context():
            self.db.session.remove()  # Close the database connection to cause an exception
            data = {'category': 1}
            response = self.client.get('/categories/1/questions', data=json.dumps(data), content_type='application/json')
            data = response.get_json()

            self.assertEqual(response.status_code, 500)
            self.assertFalse(data['success'])


    #----------------------------------------------------------------------------#
    # get_quiz
    #----------------------------------------------------------------------------#
    def test_get_quiz(self):
        data = {
            'previous_questions': [],
            'quiz_category': {'type': 'Science', 'id': 1}
        }
        response = self.client.post('/quizzes', data=json.dumps(data), content_type='application/json')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue('question' in data)
        self.assertIsNotNone(data['question'])

    def test_get_quiz_no_more_questions(self):
        with self.app.app_context():
            question_ids = self.db.session.query(Question.id).filter_by(category=1).all()
            ids = [qid[0] for qid in question_ids] 
            data = {
                'previous_questions': ids,
                'quiz_category': {'type': 'Science', 'id': 1}
            }
            response = self.client.post('/quizzes', data=json.dumps(data), content_type='application/json')
            data = response.get_json()
                    
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertTrue('question' in data)
            self.assertIsNone(data['question'])

    def test_get_quiz_error(self):
        # Simulate an error by causing an exception
        with self.app.app_context():
            self.db.session.remove()  # Close the database connection to cause an exception
            data = {
                'previous_questions': [],
                'quiz_category': {'type': 'Sports', 'id': '6'}
            }
            response = self.client.post('/quizzes', data=json.dumps(data), content_type='application/json')
            data = response.get_json()

            self.assertEqual(response.status_code, 500)
            self.assertFalse(data['success'])
            self.assertEqual(data['message'], "An error occurred while retrieving a quiz question.")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()