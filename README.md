# TRIVIA Project Documentation

Final project implementation of module 3 "API Development" of the Udacity [Backend Developer with Python](https://www.udacity.com/course/backend-developer-with-python--ud188) 5-module nanodegree.

## introduction

The trivia app is a project allowing to manage a collection of trivia question-answer pairs following CRUD principles. 
The app allows to play quizz using question and answer pairs selected from the trivia question collection.
The trivia project is composed of:
- a frontend displaying a paginated trivia question collection (page of 10 questions) - page number starts from 1
- a backend providing API endpoints to manage the trivia question collection using Flask
- a postgres database storing the trivia collection

## project structure

The project is organized with
- a frontend folder containing the frontend code
- a backend folder containing the backend code
    - the backend folder contains a folder flaskr containing the flask application code

## Getting started

Front end:
- from the frontend folder, run the following commands to start the client: 
```
npm install // only once to install dependencies
npm start // this will start the front-end server - in case of error, run the backend server first
```

Back end:
- install required dependencies (requirements.txt) using uv or pip
    - in the project folder run ```uv init```
    - create the virtual environment with ```uv venv```
    - lastly, install the dependencies with ```uv add -r requirements.txt```
    - Note: you can activate the virtual environment with ```.venv/Scripts/activate```
- create and update your .env file with your postgres database path and other variables
    - the .env file declares the following variables:
        - FLASK_APP=flaskr
        - FLASK_ENV=development
        - DATABASE_URI: your postgres database url such as 'postgresql://{database_user}:{database_password}@{database_host}/{database_name}'
        - TEST_DATABASE_URI: your postgres database path for tests
- The .env file will be loaded on start-up using python-dotenv. 
- flaskr is declared as the folder where the app is located in the configuration file .env. The Flask-related variables will be automatically detected and used by Flask on start-up. You can also declare  using ```$env:FLASK_APP = "flaskr"``` (powershell user)
- the app will start in DEBUG mode by default. You can change the debug mode in the configuration .env file.
- the trivia database will be created and populated upon first run of the app
    - see Postgres database overview section below for details
- from the backend folder, run the following commands to start the app: 
```bash
uv run flask run
```


# API Documentation

## Getting started

Base URL:
- the app is hosted locally and is accessible at http://localhost:3000.
- All endpoints are accessible at http://localhost:5000.
- No required password or access key.


## Error handling

Error codes follow the standard http error codes.
The most common error codes are:
- 400: bad request
- 404: element not found
- 405: method not allowed
- 422: unprocessable request
- 500: internal server error

The project uses a custom error handler to return a json response with the error message and the error code.
Error message are returned with the following format together with the error code:
```json
{
    "success": false,
    "error": 404,
    "message": "resource not found"
}, 

error_code
```


## API Endpoints

Note: curl commands are provided for powershell users.

### GET /categories
- returns the list of available categories
- returns a 404 error if no categories are found

```bash
curl.exe http://127.0.0.1:5000/categories
```
response:
```json
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "success": true
}
```

### GET /questions
- Returns a list of questions for current page, success flag, current category (if applicable), all categories, total number of questions in the database
- Returns a 404 error if no questions are found

curl command (powershell): 
```bash
curl.exe http://localhost:5000/questions

//

curl.exe http://localhost:5000/questions?page=2
```


### GET /categories/category_id/questions
- Returns a list of questions for the specified category for current page, success flag, current category, total number of questions in the category
- Returns a 404 error if the category does not exists

```bash
curl.exe http://localhost:5000/categories/1/questions
```
response:

```json
{
  "current_category": 1,
  "questions": [
    {
      "answer": "The Liver",
      "category": 1,
      "difficulty": 4,
      "id": 20,
      "question": "What is the heaviest organ in the human body?"
    },
    {
      "answer": "Alexander Fleming",
      "category": 1,
      "difficulty": 3,
      "id": 21,
      "question": "Who discovered penicillin?"
    },
    {
      "answer": "Blood",
      "category": 1,
      "difficulty": 4,
      "id": 22,
      "question": "Hematology is a branch of medicine involving the study of what?"
    }
  ],
  "success": true,
  "total_questions": 3
}
```

### DELETE /questions/id
- Deletes a question with the specified id. 
- Returns the id of the deleted question and the total number of questions remaining.
- Returns a 404 error if the question is not found

```bash
curl -X DELETE http://localhost:5000/questions/19
```

response:
```json
{
    "success": true,
    "deleted": 19,
    "total_questions": 18 (int)
}
```

### POST /questions
- Take a new Trivia question, answer, category and difficulty, and add it to the database
- Returns success flag, id of the created question, updated total number of questions in the database
- Returns a 400 error in case of missing question, answer, category or difficulty attributes
- Returns a 422 error if one of the attributes is empty or invalid

```bash
 Invoke-RestMethod -Uri http://localhost:5000/questions `
    -Method POST `
    -Body '{"question":"what is the capital of France?", "answer":"Paris", "category":3, "difficulty":1}' `
    -ContentType "application/json"
```

response:
```json
{
    "success": true,
    "created": 20,
    "total questions": updated total (int)
}
```


### POST /questions/search
- Returns a list of questions with the question containing the search term, success flag, current category (None since not applicable), total number of matching questions
- Returns a 400 error if invalid data

curl command (bash):
```bash
curl http://localhost:5000/questions/search?searchTerm="title"
```

curl command (powershell):
```bash
Invoke-WebRequest -Uri http://localhost:5000/questions/search `                                         
    -Method POST `                                                                                                
    -Body '{"searchTerm": "title"}' `
    -ContentType "application/json" | Select-Object -ExpandProperty Content
```

response:
```json
{
  "current_category": null,
  "questions": [
    {
      "answer": "Maya Angelou",
      "category": 4,
      "difficulty": 2,
      "id": 5,
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?"
    },
    {
      "answer": "Edward Scissorhands",
      "category": 5,
      "difficulty": 3,                                                                                                    
      "id": 6,                                                                                                            
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
    }
  ],
  "success": true,
  "total_questions": 2
}
```

### POST /quizzes
- Based on the user selection (all categories or a specific category), returns a random question from the specified category which has not already been asked, success flag, a message and list of previous questions
- Returns a 400 error if invalid data or 404 in case the category does not exist

select 'ALL'

```bash
Invoke-WebRequest -Uri http://localhost:5000/quizzes `
-Method POST `
-Body '{"previous_questions": [], "quiz_category":{"type":"click","id":0}}' `
-ContentType "application/json" | Select-Object -ExpandProperty Content
```

returns

```json
{
  "message": "New random question successfully retrieved",
  "previous_questions": [
    22
  ],
  "question": {
    "answer": "Blood",
    "category": 1,
    "difficulty": 4,
    "id": 22,
    "question": "Hematology is a branch of medicine involving the study of what?"
  },
  "success": true
}
```

Select 'Science'

```bash
Invoke-WebRequest -Uri http://localhost:5000/quizzes `
-Method POST `
-Body '{"previous_questions": [], "quiz_category":{"type":"Science","id":1}}' `
-ContentType "application/json" | Select-Object -ExpandProperty Content
```

returns

```json
{
  "message": "New random question successfully retrieved from category Science",
  "previous_questions": [
    20
  ],
  "question": {
    "answer": "The Liver",
    "category": 1,
    "difficulty": 4,
    "id": 20,
    "question": "What is the heaviest organ in the human body?"
  },
  "success": true
}
```



# Postgres database overview

The app requires a postgres database to store the questions and categories. The database is created and populated using the trivia.psql file. It has two tables called questions and categories.

Steps to create the database:
- from the backend folder where trivia.psql file is located, enter postgres psql
```psql -h localhost -U postgres```
- enter your pwd (default is postgres)

- create db in psql console using
```CREATE DATABASE trivia;```

- connect to the database
```\c trivia```

- then populate the db using
```\i trivia.psql```

- check the db in the console with the following commands
```
\c trivia                           // connect to the db
\dt                                 // list tables
\d questions                        // describe table schema
select * from questions LIMIT 5;    // select first 5 questions
```
- the database can be removed using
```bash
DROP DATABASE trivia;
```

Note:
- category id is of integer type in Category Table
- category indice is of type str in the Question table
This should be taken into account for any filtering or search operation.


## Unit tests

For testing purpose, a test_flaskr.py file is provided in the backend folder. The tests uses unittest library. It can be run using the following command:
```bash
uv run python test_flaskr.py
```

**IMPORTANT**: you must first create a dedicated test database before running the tests.
(in psql, simply run: ```CREATE DATABASE trivia_test;```).
The test_flaskr.py script will use this dedicated test database, create the tables and populate it with some test data to test the endpoints.

The test_flaskr.py file is a unittest file that tests the following endpoints:
- GET /categories
- GET /questions
- GET /categories/\<id>/questions
- POST /questions
- DELETE /questions/\<id>
- POST /search
- POST /quizzes

