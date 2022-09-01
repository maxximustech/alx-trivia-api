import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from settings import DB_NAME, DB_PASSWORD, DB_USER


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format(DB_USER+':'+DB_PASSWORD+'@localhost:5432', self.database_name)
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

    def test_get_all_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(len(data["categories"]))

    def test_get_questions(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["categories"]))
        self.assertTrue(len(data["questions"]))

    def test_delete_question(self):
        res = self.client().delete('/questions/9')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_delete_question_not_found(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Data could not be found")

    def test_post_question(self):
        post_data = {
            'question': 'a new question',
            'answer': 'this is the answer',
            'difficulty': 1,
            'category': 1
        }
        res = self.client().post('/questions', json=post_data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    def test_post_question_err(self):
        res = self.client().post('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Could not be processed")

    def test_search_questions(self):
        post_data = {
            'searchTerm': 'lake',
        }
        res = self.client().post('/searchQuestions', json=post_data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["questions"]))

    def test_search_questions_not_found(self):
        post_data = {
            'searchTerm': 'e',
        }
        res = self.client().post('/searchQuestions?page=1000', json=post_data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Data could not be found")

    def test_get_question_by_category(self):
        res = self.client().get('/categories/6/questions?page=1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["categories"]))
        self.assertTrue(len(data["questions"]))

    def test_get_question_by_category_not_found(self):
        res = self.client().get('/categories/1/questions?page=1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Data could not be found")

    def test_post_play_quiz(self):
        post_data = {
            'previous_questions': [],
            'quiz_category': {
                'type': 'History',
                'id': 4
            }
        }
        res = self.client().post('/quizzes', json=post_data)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])

    def test_422_post_play_quiz(self):
        res = self.client().post('/quizzes')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "Could not be processed")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
