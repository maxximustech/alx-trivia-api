import os
from flask import Flask, request, abort, jsonify, json
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def add_pagination(req, arr):
    cur_page = req.args.get('page', 1, type=int)
    start = (cur_page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in arr]
    cur_questions = questions[start:end]
    return cur_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(res):
        res.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        res.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return res

    @app.route("/categories")
    def get_all_categories():
        categories = list(map(Category.format, Category.query.all()))
        result = {
            "success": True,
            "categories": categories
        }
        return jsonify(result)

    @app.route('/questions')
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        cur_questions = add_pagination(request, questions)
        categories = list(map(Category.format, Category.query.all()))

        if len(cur_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': categories,
            'questions': cur_questions,
            'total_questions': Question.query.count(),
            'current_category': None,
        })

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.filter_by(id=question_id).one_or_none()
        if question is None:
            abort(404)
        try:
            question.delete()
            questions = Question.query.order_by(Question.id).all()
            cur_questions = add_pagination(request, questions)

            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': cur_questions,
                'total_questions': Question.query.count()
            })

        except:
            abort(422)

    @app.route("/questions", methods=['POST'])
    def post_question():
        try:
            body = request.get_json()

            question = body.get('question', None)
            answer = body.get('answer', None)
            category = body.get('category', None)
            difficulty = body.get('difficulty', None)

            question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
            question.insert()

            return jsonify({
                'success': True,
                'created': question.id,
                'total_questions': Question.query.count()
            })

        except:
            abort(422)

    @app.route("/searchQuestions", methods=['POST'])
    def search_questions():
        if request.data:
            cur_page = 1
            if request.args.get('page'):
                cur_page = int(request.args.get('page'))
            data = json.loads(request.data.decode('utf-8'))
            if 'searchTerm' in data:
                query = Question.query.filter(
                    Question.question.ilike(
                        '%' +
                        data['searchTerm'] +
                        '%')).paginate(
                    cur_page,
                    QUESTIONS_PER_PAGE,
                    False)
                questions = list(map(Question.format, query.items))
                if len(questions) > 0:
                    return jsonify({
                        "success": True,
                        "questions": questions,
                        "total_questions": query.total,
                        "current_category": None,
                    })
            abort(404)
        abort(422)

    @app.route("/categories/<int:category_id>/questions")
    def get_question_by_category(category_id):
        cur_category = Category.query.filter_by(id=category_id).one_or_none()
        if cur_category is None:
            abort(404)
        cur_page = 1
        if request.args.get('page'):
            cur_page = int(request.args.get('page'))
        categories = list(map(Category.format, Category.query.all()))
        query = Question.query.filter_by(
            category=category_id).paginate(
            cur_page, QUESTIONS_PER_PAGE, False)
        questions = list(map(Question.format, query.items))
        if len(questions) > 0:
            return ({
                "success": True,
                "questions": questions,
                "total_questions": query.total,
                "categories": categories,
                "current_category": Category.format(cur_category),
            })
        abort(404)

    @app.route("/quizzes", methods=['POST'])
    def post_quiz_questions():
        if request.data:
            jsonData = json.loads(request.data.decode('utf-8'))
            if (('quiz_category' in jsonData
                 and 'id' in jsonData['quiz_category'])
                    and 'previous_questions' in jsonData):
                query = Question.query.filter_by(
                    category=jsonData['quiz_category']['id']
                ).filter(
                    Question.id.notin_(jsonData["previous_questions"])
                ).all()
                question_count = len(query)
                if question_count > 0:
                    result = {
                        "success": True,
                        "question": Question.format(
                            query[random.randrange(
                                0,
                                question_count
                            )]
                        )
                    }
                else:
                    result = {
                        "success": True,
                        "question": None
                    }
                return jsonify(result)
            abort(404)
        abort(422)

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            'error': 400,
            "message": "Bad request sent"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            'error': 404,
            "message": "Data could not be found"
        }), 404

    @app.errorhandler(422)
    def not_processed(error):
        return jsonify({
            "success": False,
            'error': 422,
            "message": "Could not be processed"
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            'error': 500,
            "message": "Internal server error"
        }), 500

    return app
