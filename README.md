# Project Repository

This repository contains a Role-Based Learning Management System (LMS) with:
- FastAPI backend (Supabase for data + storage)
- React frontend

Backend Supabase Setup
- See fastapi_backend/README.md for complete Supabase SQL, RLS policies, and storage bucket setup.
- Copy fastapi_backend/.env.example to fastapi_backend/.env and populate with your Supabase keys.

Running Backend
- Install deps: pip install -r fastapi_backend/requirements.txt
- Generate OpenAPI: python -m src.api.generate_openapi (from fastapi_backend folder)
- Start: uvicorn src.api.main:app --host 0.0.0.0 --port 3001

APIs Summary
- Lessons: GET /lessons, POST /lessons, PUT /lessons/{id}, DELETE /lessons/{id}
- Quizzes: GET /quizzes, POST /quizzes, PUT /quizzes/{id}, DELETE /quizzes/{id}
- Assignments: POST /assign, GET /assignments/{employee_id}
- Completion: POST /complete
- Progress: GET /progress/{employee_id}
- Upload: POST /upload