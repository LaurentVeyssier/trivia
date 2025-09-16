"""Trivia API tests."""
import os
import json
import unittest
from dotenv import load_dotenv
from flaskr import create_app
from models import db, Question, Category

# load environment variables
load_dotenv()

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Initialize app and add some questions for testing."""
        # Create app with the test configuration
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": os.getenv("TEST_DATABASE_URI"),
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client

        # Bind the app to the current context and create all tables
        with self.app.app_context():
            db.create_all()

        # add some questions for testing
        with self.app.app_context():

            for category in ["Science", "Art", "Geography", "History", "Entertainment", "Sports"]:
                db.session.add(Category(type=category))

            db.session.add(Question(
                question="Who invented Python?",
                answer="Guido van Rossum",
                category="1",
                difficulty=4
            ))
            db.session.add(Question(
                question="Where is the HQ of OpenAI?",
                answer="San Francisco",
                category="3",
                difficulty=3
            ))
            db.session.add(Question(
                question="What is the capital of France?", 
                answer="Paris", 
                category="3", 
                difficulty=1
            ))
            db.session.add(Question(
                question="Who won the 2025 champions league?", 
                answer="PSG", 
                category="6", 
                difficulty=1
            ))

            db.session.commit()

        self.new_question = {
            "question": "Who painted the Mona Lisa?", 
            "answer": "Leonardo da Vinci", 
            "category": 2, 
            "difficulty": 1
            }
        
    def tearDown(self):
        """Executed after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)
        #---------- tests -----------------
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    def test_get_categories_not_allowed(self):
        res = self.client().post("/categories")
        data = json.loads(res.data)
        #---------- tests -----------------
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "not allowed")

    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)
        #---------- tests -----------------
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertEqual(data["total_questions"], 4)
        self.assertTrue(data["categories"])

    def test_delete_question(self):
        # best practice: first insert a valid question
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data) 
        new_question_id = data['created']
        # perform delete
        res = self.client().delete(f'/questions/{new_question_id}')
        data = json.loads(res.data)
        #---------- tests -----------------
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["deleted"], new_question_id)
        # check delete is persistent
        with self.app.app_context():
            self.assertIsNone(db.session.get(Question, new_question_id))

    def test_delete_question_not_found(self):
        res = self.client().delete('/questions/100')
        data = json.loads(res.data)
        #---------- tests -----------------
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        new_question_id = data["created"]
        #---------- tests -----------------
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["created"])
        # check insert is persistent
        with self.app.app_context():
            self.assertEqual(
                self.new_question["question"], 
                db.session.get(Question, new_question_id).question
            )

    def test_create_question_bad_request(self):
        res = self.client().post('/questions', json={})
        data = json.loads(res.data)
        #---------- tests -----------------
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "bad request")

    def test_search_questions(self):
        res = self.client().post('/questions/search', json={"searchTerm": "champions league"})
        data = json.loads(res.data)
        #---------- tests -----------------
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertEqual(data["total_questions"], 1)

    def test_search_questions_empty(self):
        res = self.client().post('/questions/search', json={"searchTerm": "hds_ffek_0"})
        data = json.loads(res.data)
        #---------- tests -----------------
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["questions"], [])
        self.assertEqual(data["total_questions"], 0)

    def test_get_questions_by_category(self):  #.......................................
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        #---------- tests -----------------
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["current_category"], 1)
        self.assertTrue(data["questions"])
        self.assertEqual(data["total_questions"], 1)

    def test_get_questions_by_category_not_found(self):
        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data)
        #---------- tests -----------------
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")

    def test_play_quiz(self):
        res = self.client().post('/quizzes', 
        json={
            "previous_questions": [], 
            "quiz_category": {"type": "Science", "id": "1"}
            })
        data = json.loads(res.data)
        #---------- tests -----------------
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"])
        self.assertTrue(data["previous_questions"])
        self.assertEqual(data["question"]["category"], "1")

    def test_play_quiz_not_found(self):
        res = self.client().post('/quizzes',
            json={
                "previous_questions": [], 
                "quiz_category": {"type": "Science", "id": 10}
            })
        data = json.loads(res.data)
        #---------- tests -----------------
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "resource not found")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
