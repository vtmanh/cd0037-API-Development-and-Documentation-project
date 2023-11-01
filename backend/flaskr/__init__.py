#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func
import random

from models import db, setup_db, Question, Category


#----------------------------------------------------------------------------#
# Define
#----------------------------------------------------------------------------#
QUESTIONS_PER_PAGE = 10


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
def create_app(test_config=None, test_db_url=None):
    # create and configure the app
    app = Flask(__name__)
    with app.app_context():
        if test_config is None:
            setup_db(app)
        else:
            setup_db(app, database_path=test_db_url)
    CORS(app)

    # Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Use the after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response


#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
    """
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            # retrieve all categories from DB
            all_categories = Category.query.all()
            # Format the categories using the format() method
            categories = [
                category.format()
                for category in all_categories
                ]
            # Return the categories as a JSON response
            return jsonify({
                'success': True,
                'categories': categories
            })
        except:
            # Handle exceptions 
            return jsonify({
                'success': False,
                'message': 'An error occurred while retrieving categories',
            }), 500

#----------------------------------------------------------------------------#
    """
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
            # request data & process request data
            category = request.args.get('category', None)
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE

            # Query the database 
            if category is None:
                query = Question.query
            else:
                query = Question.query.filter_by(category=category)

            total_questions = query.count()
            current_questions = query.slice(start, end).all()
            
            # Format for response
            questions = [question.format() for question in current_questions]

            # Get a list of available categories
            all_categories = Category.query.all()
            category_list=[cat.format() for cat in all_categories]

            return jsonify({
                'success': True,
                'questions': questions,
                'total_questions': total_questions,
                'current_category': category,
                'categories': category_list,
            })
        except:
            return jsonify({
                'success': False,
                'message': 'An error occurred while retrieving questions',
            }), 500


#----------------------------------------------------------------------------#
    """
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        # Query the database to find the question by its ID
        question = Question.query.get(question_id)

        if question is None:
            return jsonify({
                'success': False,
                'message': 'Question not found'
            }), 404

        try:
            # Delete the question
            # deleting_question = Question(question)
            # deleting_question.delete()
            db.session.delete(question)
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Question deleted successfully'
            })
        except:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': 'An error occurred while deleting the question'
            }), 500
        finally:
            db.session.close()

#----------------------------------------------------------------------------#
    """
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        # get data from request
        data = request.get_json()
        question = data.get('question', '')
        answer = data.get('answer', '')
        category = data.get('category', '')
        difficulty = data.get('difficulty', 0)

        # check requirement
        if not question or not answer or not category:
            return jsonify({
                'success': False,
                'message': 'Question, answer, and category are required fields'
            }), 400
        try:
            # create new question
            new_question = Question(
                question=question,
                answer=answer,
                category=category,
                difficulty=difficulty
            )
            # submit db
            # db.session.add(new_question)
            # db.session.commit()
            new_question.insert()
            return jsonify({
                'success': True,
                'message': 'Question created successfully',
                'question': new_question.format()
            }), 201
        except:
            # error
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': 'An error occurred while creating the question'
            }), 500
        finally:
            db.session.close()

#----------------------------------------------------------------------------#
    """
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        # get data
        data = request.get_json()
        search_term = data.get('searchTerm', '')
        
        # check search term
        if not search_term:
            return jsonify({
                'success': False,
                'message': 'Search term is required'
            }), 400

        try:
            # Query the database (case-insensitive)
            matching_questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

            if not matching_questions:
                return jsonify({
                    'success': True,
                    'message': 'No questions found',
                    'questions': []
                })

            # format result
            questions = [question.format() for question in matching_questions]
            return jsonify({
                'success': True,
                'message': 'Questions retrieved successfully',
                'questions': questions
            })
        except:
            return jsonify({
                'success': False,
                'message': 'An error occurred while retrieving questions'
            }), 500

#----------------------------------------------------------------------------#
    """
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/<category_id>', methods=['GET'])
    def get_questions_by_category(category_id):
        try:
            # Query the database
            matching_questions = Question.query.filter_by(category=category_id).all()

            # not found
            if not matching_questions:
                return jsonify({
                    'success': True,
                    'message': 'No questions found in the category',
                    'questions': []
                })
            
            # format result
            questions=[question.format() for question in matching_questions]
            return jsonify({
                'success': True,
                'message': 'Questions retrieved successfully',
                'questions': questions
            })
        except:
            return jsonify({
                'success': False,
                'message': 'An error occurred while retrieving questions'
            }), 500

    """
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_quiz():
        data = request.get_json()
        category_id = data.get('category', None)
        previous_questions = data.get('previous_questions', [])

        try:
            # Query the database for a random question
            query = Question.query
            if category_id:
                query = query.filter_by(category=category_id)
            
            # Exclude previous questions
            if previous_questions:
                query = query.filter(Question.id.notin_(previous_questions))
            
            # Retrieve a random question
            random_question = query.order_by(func.random()).first()

            if random_question:
                question = random_question.format()
                return jsonify({
                    'success': True,
                    'question': question
                })
            else:
                return jsonify({
                    'success': True,
                    'question': None  # No more questions in the category
                })
        except:
            return jsonify({
                'success': False,
                'message': 'An error occurred while retrieving a quiz question.'
            }), 500

#----------------------------------------------------------------------------#
    """
    Create error handlers for all expected errors
    including 404 and 422.
    """
    # error handler for 400 (Bad Request)
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad Request'
        }), 400
    
    # error handler for 404 (Not Found)
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not found'
        }), 404

    # error handler for 422 (Unprocessable Entity)
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable entity'
        }), 422

    # error handler for 500 (Internal Server Error)
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal Server Error'
        }), 500

    return app
