import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format("postgres", "postgres", "localhost:5432", self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    Write at least one test for each test for successful operation and for expected errors.
    """
    #----------------------------------------------------------------------------#
    # get_categories
    #----------------------------------------------------------------------------#
    def test_get_categories_success(self):
        # Insert some categories into the database
        # category1 = Category(type='Category 1')
        # category2 = Category(type='Category 2')
        # with self.app.app_context():
        #     self.db.session.add(category1)
        #     self.db.session.add(category2)
        #     self.db.session.commit()

        response = self.client.get('/')
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
        # Insert some questions and categories into the database
        # category1 = Category(type='Category 1')
        # category2 = Category(type='Category 2')
        # question1 = Question(question='Question 1', answer='Answer 1', category='Category 1', difficulty=1)
        # question2 = Question(question='Question 2', answer='Answer 2', category='Category 2', difficulty=2)
        # with self.app.app_context():
        #     self.db.session.add(category1)
        #     self.db.session.add(category2)
        #     self.db.session.add(question1)
        #     self.db.session.add(question2)
        #     self.db.session.commit()

        response = self.client.get('/?page=1')
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
            response = self.client.get('/?page=1')
            data = response.get_json()

            self.assertEqual(response.status_code, 500)
            self.assertFalse(data['success'])

    #----------------------------------------------------------------------------#
    # delete_question
    #----------------------------------------------------------------------------#
    def test_delete_question_success(self):
        # Insert a question into the database
        # question = Question(question='Question 1', answer='Answer 1', category='Category 1', difficulty=1)
        # self.db.session.add(question)
        # self.db.session.commit()

        response = self.client.delete(f'/2')
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Question deleted successfully')

    def test_delete_question_not_found(self):
        # Try to delete a question that does not exist
        response = self.client.delete('/404404')
        data = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Question not found')

    def test_delete_question_error(self):
        # Simulate an error by causing an exception
        with self.app.app_context():
            self.db.session.remove() # Close the DB connection to cause an exception
            response = self.client.delete('/1')  # Assuming question with ID 1 exists
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
            'category': 'Science',
            'difficulty': 1
        }
        response = self.client.post('/add', data=json.dumps(data), content_type='application/json')
        data = response.get_json()

        self.assertEqual(response.status_code, 201)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Question created successfully')
        self.assertTrue('question' in data)

    def test_create_question_missing_fields(self):
        data = {
            'question': 'Sample Question 1',
            'answer': 'Sample Answer 1',
        }
        response = self.client.post('/add', data=json.dumps(data), content_type='application/json')
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
                'category': 'Science',
                'difficulty': 1
            }
            response = self.client.post('/add', data=json.dumps(data), content_type='application/json')
            data = response.get_json()

            self.assertEqual(response.status_code, 500)
            self.assertFalse(data['success'])

    #----------------------------------------------------------------------------#
    # search_questions
    #----------------------------------------------------------------------------#
    def test_search_questions_success(self):
        # Insert a sample question into the database
        # with self.app.app_context():
        #     sample_question = Question(
        #         question='What is a sample question?',
        #         answer='This is a sample answer.',
        #         category='Science',
        #         difficulty=1
        #     )
        #     self.db.session.add(sample_question)
        #     self.db.session.commit()

        data = {'searchTerm': 'autobiography'}
        response = self.client.post('/', data=json.dumps(data), content_type='application/json')
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Questions retrieved successfully')
        self.assertTrue('questions' in data)
        self.assertEqual(len(data['questions']), 1)  # Expect one matching question

    def test_search_questions_no_results(self):
        data = {'searchTerm': 'nonexistent'}
        response = self.client.post('/', data=json.dumps(data), content_type='application/json')
        data = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'No questions found')
        self.assertTrue('questions' in data)
        self.assertEqual(len(data['questions']), 0)  # No matching questions

    def test_search_questions_missing_search_term(self):
        data = {}  # Missing 'searchTerm' in the request
        response = self.client.post('/', data=json.dumps(data), content_type='application/json')
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Search term is required')

    def test_search_questions_error(self):
        # Simulate an error by causing an exception
        with self.app.app_context():
            self.db.session.remove()  # Close the database connection to cause an exception
            data = {'searchTerm': 'What'}
            response = self.client.post('/', data=json.dumps(data), content_type='application/json')
            data = response.get_json()

            self.assertEqual(response.status_code, 500)
            self.assertFalse(data['success'])

    #----------------------------------------------------------------------------#
    # get_questions_by_category
    #----------------------------------------------------------------------------#
    def test_get_questions_by_category(self):
        data = {'category': 'Science'}
        response = self.client.get('/', data=json.dumps(data), content_type='application/json')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Questions retrieved successfully')
        self.assertTrue('questions' in data)
        self.assertTrue(len(data['questions']) >= 1)

    def test_get_questions_by_category_not_found(self):
        data = {'category': 'non_existing_category'}
        response = self.client.get('/', data=json.dumps(data), content_type='application/json')
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
            data = {'category': 'Science'}
            response = self.client.get('/', data=json.dumps(data), content_type='application/json')
            data = response.get_json()

            self.assertEqual(response.status_code, 500)
            self.assertFalse(data['success'])


    #----------------------------------------------------------------------------#
    # get_playing_question
    #----------------------------------------------------------------------------#
    def test_get_playing_question(self):
        data = {
            'category': 'Science', 
            'previous_questions': []  
        }
        response = self.client.post('/play', data=json.dumps(data), content_type='application/json')
        data = response.get_json()
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue('question' in data)
        self.assertIsNotNone(data['question'])

    def test_get_playing_question_no_more_questions(self):
        with self.app.app_context():
            question_ids = self.db.session.query(Question.id).filter(Question.category.ilike('Science')).all()
            data = {
                'category': 'Science',
                'previous_questions': question_ids
            }
            response = self.client.post('/play', data=json.dumps(data), content_type='application/json')
            data = response.get_json()
                    
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertTrue('question' in data)
            self.assertIsNone(data['question'])

    def test_get_playing_question_error(self):
        # Simulate an error by causing an exception
        with self.app.app_context():
            self.db.session.remove()  # Close the database connection to cause an exception
            data = {
                'category': 'Science',  
                'previous_questions': [1] 
            }
            response = self.client.post('/', data=json.dumps(data), content_type='application/json')
            data = response.get_json()

            self.assertEqual(response.status_code, 500)
            self.assertFalse(data['success'])
            self.assertEqual(data['message'], "An error occurred while retrieving a quiz question.")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()