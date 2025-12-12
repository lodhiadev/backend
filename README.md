        # Backend (FastAPI + Motor + MongoDB)


        ## Local setup (docker-compose)


        1. `docker-compose up --build`
2. Backend will be at http://localhost:8000


        ## Endpoints


        - POST `/org/create` -> { organization_name, email, password }
- GET `/org/get?organization_name=...`
- PUT `/org/update` -> same payload as create
- DELETE `/org/delete?organization_name=...&admin_email=...`
- POST `/admin/login` -> { email, password } -> returns { access_token }


        ## Notes


        - Passwords hashed using bcrypt via passlib.
- JWT includes `sub` (email) and `org` (organization name).
- For production, use HTTPS, stronger secrets, restricted CORS, and rotate keys.
