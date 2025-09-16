"""Trivia API Flask application factory and routes.

 This module defines `create_app()` which configures the Flask application for
 the Udacity Trivia project. It sets up:
 - the database via `setup_db`
 - CORS for API routes
 - REST endpoints for categories, questions, search, and quizzes
 - consistent JSON error handlers

 It also includes the `paginate(request, collection)` helper and the
 `QUESTIONS_PER_PAGE` constant used for pagination.
 """
import os
import random
from dotenv import load_dotenv
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from models import setup_db, Question, Category  # , db

# load environment variables
load_dotenv()
QUESTIONS_PER_PAGE = 10

# helper function


def paginate(request, collection):
    """
    Return a fixed number of items from a collection
    based on page number and QUESTIONS_PER_PAGE
    Args:
        request: the request object whcih provides the page number
        collection: the collection to paginate
    Returns:
        a list of Dict using format() method applied to the collection objects
    """
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    current_collection = [c.format() for c in collection]
    return current_collection[start:end]


def create_app(test_config=None):
    """Create and configure the Flask application."""
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        db = setup_db(app=app, database_path=os.getenv("DATABASE_URI"))
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        db = setup_db(app=app, database_path=database_path)

    # @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    with app.app_context():
        db.create_all()
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # CORS Headers - Use the after_request decorator to set
    # Access-Control-Allow

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,PATCH"
        )
        return response

    # endpoints
    # ------------------------------------

    # GET all available categories.

    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.all()
        if not categories:
            abort(404)
        return jsonify({'success': True, 'categories': {
                       category.id: category.type for category in categories}})

    # GET all questions, including pagination (every 10 questions).

    @app.route('/questions', methods=['GET'])
    def get_questions():
        """return a list of questions, number of total questions, current category, categories"""
        questions = Question.query.all()
        if not questions:
            abort(404)
        current_questions = paginate(request, questions)
        return jsonify({
            'success': True,
            'questions': current_questions,
            'current_category': None,
            'total_questions': len(questions),
            'categories': {category.id: category.type for category in Category.query.all()},
        })

    # GET question based on an question ID

    @app.route('/questions/<int:question_id>', methods=['GET'])
    def get_question(question_id):
        """return the question with id question_id,
        number of total questions, current category, categories"""
        question = db.session.get(Question, question_id)
        if question is None:
            abort(404)
        questions = Question.query.all()
        return jsonify({
            'success': True,
            'questions': [question.format()],
            'current_category': question.category,
            'total_questions': len(questions),
            'categories': {category.id: category.type for category in Category.query.all()},
        })

    # DELETE question using a question ID.

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = db.session.get(Question, question_id)
        if question is None:
            abort(404)
        question.delete()
        questions = Question.query.all()
        return jsonify({
            'success': True,
            'deleted': question_id,
            'total_questions': len(questions),
        })

    # POST a new question with question, answer text, category, and difficulty
    # score.
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        required_fields = {"question", "answer", "category", "difficulty"}
        if not body or not required_fields.issubset(body):
            abort(400)
        try:
            # will throw an error if one of the field is missing leading to a
            # 422 error
            new_question = Question(
                **{field: body[field] for field in required_fields})
            new_question.insert()
            questions = Question.query.all()
            return jsonify({
                'success': True,
                'created': new_question.id,
                'total_questions': len(questions),
            })
        except BaseException:
            abort(422)

    # get questions based on a search term.
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        if not body or 'searchTerm' not in body:
            abort(400)

        searchTerm = body['searchTerm']
        selection = Question.query.filter(
            Question.question.ilike(
                f'%{searchTerm}%')).all()
        current_questions = paginate(request, selection)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'current_category': None,
        })

    # get questions based on category.
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def select_questions_by_category(category_id):
        """get questions based on category.
        Args:
            category_id (int): id of the category
        """
        if category_id not in [c.id for c in Category.query.all()]:
            abort(404)

        # category field in Question is str, so convert category_id to str
        selection = Question.query.filter(
            Question.category == str(category_id)).all()
        current_questions = paginate(request, selection)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'current_category': category_id,
            'total_questions': len(selection)
        })

    # get questions to play the quiz.
    @app.route("/quizzes", methods=['POST'])
    def play_quiz():
        body = request.get_json()

        # check that the body is not empty and that it contains
        # the required fields (previous_questions and quiz_category)
        if not body or 'previous_questions' not in body or 'quiz_category' not in body:
            abort(400)

        # check that the category field is a dict with id and type (required
        # keys)
        if 'id' not in body['quiz_category'] or 'type' not in body['quiz_category']:
            abort(400)

        # convert category_id to int to prevent input data type issue
        # Aligned with id int type of Category model
        category_id = int(body['quiz_category']['id'])
        # check that the selected category exists including 0 for 'ALL'
        # selection
        if category_id not in [c.id for c in Category.query.all()] + [0]:
            abort(404)

        previous_questions = body['previous_questions']

        # 'ALL' category selected for the quizz
        if category_id == 0:
            selection = Question.query.filter(
                Question.id.notin_(previous_questions)).all()
        # a specific category was selected for the quizz
        else:
            # category field in Question is str, so convert category_id to str
            selection = Question.query.filter(
                Question.category == str(category_id),
                Question.id.notin_(previous_questions)).all()

        # check that a new question is available
        if len(selection) == 0:
            return jsonify({
                'success': True,
                'message': (
                    f'No more questions available in the category {body["quiz_category"]["type"]} '
                    f'(Select another category to continue'
                    if category_id != 0
                    else 'No more questions available - Add new (question, answer) pairs to continue'
                ),
                'question': None
            })

        # randomly select a new question from the selection
        new_question = random.choice(selection)
        # update the list of previous questions
        previous_questions.append(new_question.id)

        return jsonify({
            'success': True,
            'message': (
                f"New random question successfully retrieved from category "
                f"{body['quiz_category']['type']}"
                if category_id != 0
                else "New random question successfully retrieved"
            ),
            'question': new_question.format(),
            'previous_questions': previous_questions
        })

    # error handlers
    # ---------------------------------------

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            "success": False,
            "error": 401,
            "message": "unauthorized"
        }), 401

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "not allowed"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 500

    return app
