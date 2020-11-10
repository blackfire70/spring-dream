# spring-dream
Django REST API Backend

### Setup
Edit and copy keys.json.sample into keys.json

Run these commands:

`$ pip install -r requirements.txt`


`$ python manage.py migrate --settings=spring_dream.settings.dev`


`$ python manage.py runserver --settings=spring_dream.settings.dev`



### User creation endpoint
`POST /api/v1/users/`

### User activation endpoint
`PATCH /api/v1/users/<pk>/`

### Change password endpoint
`PATCH /api/v1/users/<pk>/`

### Login
`POST /api/v1/api-token-auth/`
