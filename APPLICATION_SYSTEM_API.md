# Application Management System API Documentation

## Overview
The Application Management System provides comprehensive functionality for managing job applications, including resume optimization based on job descriptions and application tracking.

## Features
- ✅ Create, read, update, delete job applications
- ✅ Resume optimization for specific job applications
- ✅ Application status tracking with history
- ✅ Analytics and reporting
- ✅ Integration with existing resume system

## API Endpoints

### 1. Create Application
**POST** `/applications`

Creates a new job application.

**Request Body:**
```json
{
  "resume_id": "uuid (optional)",
  "job_title": "Software Engineer",
  "company_name": "Tech Corp",
  "job_description": "Full job description text...",
  "application_date": "2024-01-15",
  "status": "applied",
  "source": "linkedin",
  "salary_range": "$80,000 - $100,000",
  "location": "San Francisco, CA",
  "notes": "Referred by John Doe"
}
```

**Response:**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "resume_id": "uuid",
  "job_title": "Software Engineer",
  "company_name": "Tech Corp",
  "job_description": "Full job description text...",
  "application_date": "2024-01-15",
  "status": "applied",
  "source": "linkedin",
  "salary_range": "$80,000 - $100,000",
  "location": "San Francisco, CA",
  "notes": "Referred by John Doe",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "status_history": [...]
}
```

### 2. Get Applications
**GET** `/applications`

Retrieves user's applications with optional filtering.

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100, max: 1000)
- `status`: Filter by status (optional)
- `company`: Filter by company name (partial match, optional)

**Response:**
```json
[
  {
    "id": "uuid",
    "job_title": "Software Engineer",
    "company_name": "Tech Corp",
    "status": "applied",
    "application_date": "2024-01-15",
    // ... other fields
  }
]
```

### 3. Get Specific Application
**GET** `/applications/{application_id}`

Retrieves a specific application with resume details.

**Response:**
```json
{
  "id": "uuid",
  "job_title": "Software Engineer",
  "company_name": "Tech Corp",
  "resume": {
    "id": "uuid",
    "title": "My Resume",
    "personal_info": {...},
    "experiences": [...],
    // ... resume details
  },
  "status_history": [
    {
      "id": "uuid",
      "status": "applied",
      "notes": "Application created",
      "changed_at": "2024-01-15T10:30:00Z"
    }
  ]
  // ... other fields
}
```

### 4. Update Application
**PUT** `/applications/{application_id}`

Updates an existing application.

**Request Body:**
```json
{
  "status": "under_review",
  "notes": "Received confirmation email",
  "salary_range": "$85,000 - $105,000"
}
```

### 5. Delete Application
**DELETE** `/applications/{application_id}`

Deletes an application.

**Response:**
```json
{
  "message": "Application deleted successfully"
}
```

### 6. Optimize Resume for Application
**POST** `/applications/{application_id}/optimize-resume`

Optimizes or generates a resume specifically for the job application.

**Request Body:**
```json
{
  "application_id": "uuid",
  "generate_new_resume": false
}
```

**Response:**
```json
{
  "message": "Resume optimized successfully",
  "application_id": "uuid",
  "resume_id": "uuid",
  "resume_title": "Software Engineer - Tech Corp"
}
```

### 7. Get Application Analytics
**GET** `/applications/analytics`

Provides analytics and insights about user's applications.

**Response:**
```json
{
  "total_applications": 25,
  "applications_by_status": {
    "applied": 15,
    "under_review": 5,
    "interview": 3,
    "rejected": 2,
    "accepted": 0
  },
  "applications_by_month": {
    "2024-01": 8,
    "2024-02": 12,
    "2024-03": 5
  },
  "top_companies": [
    {"company": "Tech Corp", "applications": 3},
    {"company": "StartupXYZ", "applications": 2}
  ],
  "response_rate": 40.0,
  "average_days_to_response": 7.5
}
```

### 8. Get Status History
**GET** `/applications/{application_id}/status-history`

Retrieves status change history for an application.

**Response:**
```json
[
  {
    "id": "uuid",
    "status": "applied",
    "notes": "Application created",
    "changed_at": "2024-01-15T10:30:00Z"
  },
  {
    "id": "uuid",
    "status": "under_review",
    "notes": "Received confirmation email",
    "changed_at": "2024-01-16T14:20:00Z"
  }
]
```

## Application Statuses

Valid status values:
- `applied` - Initial application submitted
- `under_review` - Application being reviewed
- `interview` - Interview scheduled/in progress
- `rejected` - Application rejected
- `accepted` - Job offer received
- `withdrawn` - Application withdrawn by user

## Resume Optimization Flow

### Option 1: Optimize Existing Resume
1. Application must have a `resume_id` attached
2. Application must have a `job_description`
3. System optimizes the existing resume for the specific job

### Option 2: Generate New Resume
1. Set `generate_new_resume: true`
2. System generates a new resume from user profile data
3. Optimizes it for the specific job description
4. Creates a new resume and attaches it to the application

## Database Schema

### Applications Table
```sql
CREATE TABLE applications (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    resume_id UUID REFERENCES resumes(id),
    job_title VARCHAR NOT NULL,
    company_name VARCHAR NOT NULL,
    job_description TEXT,
    application_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR DEFAULT 'applied',
    source VARCHAR,
    salary_range VARCHAR,
    location VARCHAR,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Application Status History Table
```sql
CREATE TABLE application_status_history (
    id UUID PRIMARY KEY,
    application_id UUID NOT NULL REFERENCES applications(id),
    status VARCHAR NOT NULL,
    notes TEXT,
    changed_at TIMESTAMP DEFAULT NOW()
);
```

## Error Handling

The API returns appropriate HTTP status codes:
- `200` - Success
- `201` - Created
- `400` - Bad Request (invalid data)
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

## Authentication

All endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

## Usage Examples

### Complete Application Flow
1. **Create Application:**
```bash
curl -X POST "/applications" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "job_title": "Full Stack Developer",
    "company_name": "InnovateTech",
    "job_description": "We are looking for a full stack developer...",
    "source": "company_website"
  }'
```

2. **Optimize Resume:**
```bash
curl -X POST "/applications/{app_id}/optimize-resume" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "generate_new_resume": true
  }'
```

3. **Update Status:**
```bash
curl -X PUT "/applications/{app_id}" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "status": "under_review",
    "notes": "Received confirmation email"
  }'
```

4. **Get Analytics:**
```bash
curl -X GET "/applications/analytics" \
  -H "Authorization: Bearer <token>"
```

## Integration with Existing Systems

- **Resume System:** Applications can be linked to existing resumes or generate new ones
- **Optimization System:** Uses the same optimization engine for resume enhancement
- **User Management:** Integrates with existing user authentication and profiles
- **PDF Generation:** Can generate PDFs of optimized resumes for applications

## Future Enhancements

- [ ] Email notifications for status changes
- [ ] Calendar integration for interviews
- [ ] Document upload for cover letters
- [ ] Advanced analytics with charts
- [ ] Bulk operations for applications
- [ ] Integration with job boards
- [ ] Automated job matching suggestions
