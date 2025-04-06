# ThinkHive API Documentation

## Base URL

---

## Endpoints

### 1. GET /

- Loads the frontend submission page.

### 2. POST /submit

- Submits a project to the backend.

#### Request Type:
POST

#### Content-Type:
application/json

#### Body Example:
```json
{
  "student_name": "John Doe",
  "department": "Computer Science",
  "title": "AI-Based Attendance System",
  "problem_statement": "Manual attendance is inefficient.",
  "drawbacks": "Depends on camera accuracy",
  "code_link": "https://github.com/johndoe/project"
}
## Data Model

| Field              | Type     | Required |
|-------------------|----------|----------|
| id                | Integer  | Auto     |
| student_name      | String   | Yes      |
| department        | String   | Yes      |
| title             | String   | Yes      |
| problem_statement | Text     | Yes      |
| drawbacks         | Text     | No       |
| code_link         | String   | No       |
