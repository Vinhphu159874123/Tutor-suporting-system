# Entity Relationship Diagram - Tutor Support System

## Database Schema với AI Matching và Time Request Flow

```mermaid
erDiagram
    User ||--o{ Student : "is-a"
    User ||--o{ Tutor : "is-a"
    User ||--o{ Coordinator : "is-a"
    
    Student ||--o{ SessionRequest : "creates"
    Student ||--o{ Session : "attends"
    Student ||--o{ SessionFeedback : "gives"
    
    Tutor ||--o{ TutorAvailability : "defines"
    Tutor ||--o{ SessionMatch : "receives"
    Tutor ||--o{ Session : "teaches"
    Tutor ||--o{ SessionFeedback : "receives"
    
    SessionRequest ||--|| SessionMatch : "matched to"
    SessionMatch }o--|| TutorAvailability : "uses time slot"
    SessionMatch ||--o| Session : "creates when accepted"
    
    Coordinator ||--o{ MatchingLog : "performs"
    MatchingLog }o--|| SessionRequest : "logs matching for"
    
    Session ||--o{ SessionFeedback : "has"
    Session ||--o{ SessionMaterial : "includes"

    User {
        int user_id PK
        string email UK "unique, @hcmut.edu.vn"
        string hashed_password
        string full_name
        string phone
        enum role "student, tutor, coordinator, admin"
        string avatar_url
        boolean is_active
        boolean is_verified
        datetime created_at
        datetime updated_at
    }

    Student {
        int student_id PK
        int user_id FK "references User"
        string student_code UK "MSSV: 2112345"
        string faculty
        string major
        int year "1-5"
        json preferences "learning preferences"
    }

    Tutor {
        int tutor_id PK
        int user_id FK "references User"
        string staff_code UK "nullable for student tutors"
        string faculty
        json subjects "array of subjects"
        decimal hourly_rate "per hour price"
        text bio
        float rating "avg 0-5"
        int total_sessions "completed sessions count"
        boolean is_verified "approved by coordinator"
        json teaching_experience
    }

    Coordinator {
        int coordinator_id PK
        int user_id FK "references User"
        string department
        json assigned_subjects "responsible subjects"
        int assigned_requests "current workload"
    }

    TutorAvailability {
        int availability_id PK
        int tutor_id FK "references Tutor"
        int day_of_week "0-6: Monday-Sunday"
        time start_time "HH:MM:SS format"
        time end_time "HH:MM:SS format"
        boolean is_recurring "true for weekly slots"
        date specific_date "nullable, for one-time slots"
        enum status "available, booked, blocked"
        datetime created_at
        datetime updated_at
    }

    SessionRequest {
        int request_id PK
        int student_id FK "references Student"
        string subject
        text description "learning goals"
        date preferred_date
        time preferred_time_start
        time preferred_time_end
        int duration "hours: 1-4"
        decimal budget "max price willing to pay"
        enum urgency "high, medium, low"
        enum status "pending, matched, confirmed, cancelled"
        text special_requirements
        datetime created_at
        datetime updated_at
    }

    SessionMatch {
        int match_id PK
        int request_id FK UK "references SessionRequest"
        int tutor_id FK "references Tutor"
        int availability_id FK "references TutorAvailability"
        int matched_by FK "coordinator_id or NULL for AI"
        float match_score "AI confidence 0-100"
        datetime suggested_time "AI suggested datetime"
        enum tutor_status "pending, accepted, rejected, requested_new_time"
        text rejection_reason "nullable"
        datetime new_time_request "tutor's counter-proposal"
        boolean student_approved_new_time "nullable"
        datetime matched_at
        datetime responded_at "tutor response time"
    }

    Session {
        int session_id PK
        int match_id FK UK "references SessionMatch"
        int student_id FK "references Student"
        int tutor_id FK "references Tutor"
        string subject
        date scheduled_date
        time start_time
        time end_time
        enum location_type "online, offline, hybrid"
        string meeting_link "Zoom, Meet, etc"
        string physical_address "nullable"
        enum status "scheduled, ongoing, completed, cancelled"
        datetime actual_start "actual start time"
        datetime actual_end "actual end time"
        decimal price "agreed price"
        enum payment_status "pending, paid, refunded"
        text session_notes "tutor notes"
        datetime created_at
        datetime updated_at
    }

    SessionFeedback {
        int feedback_id PK
        int session_id FK "references Session"
        int reviewer_id FK "references User"
        enum reviewer_type "student, tutor"
        int rating "1-5 stars"
        text comment
        json tags "array: helpful, clear, patient, etc"
        boolean is_public "show on profile"
        datetime created_at
    }

    SessionMaterial {
        int material_id PK
        int session_id FK "references Session"
        string file_name
        string file_url "cloud storage URL"
        string file_type "pdf, docx, pptx, etc"
        int file_size "bytes"
        int uploaded_by FK "user_id"
        datetime uploaded_at
    }

    MatchingLog {
        int log_id PK
        int request_id FK "references SessionRequest"
        int coordinator_id FK "nullable, references Coordinator"
        string algorithm_version "AI model version"
        json candidates "array of {tutor_id, score, reasoning}"
        int final_choice FK "selected tutor_id"
        text matching_criteria "used filters"
        float processing_time "seconds"
        datetime timestamp
    }
```

## Quan hệ chính (Cardinality)

- **User** `1` ─── `*` **Student** (IS-A relationship)
- **User** `1` ─── `*` **Tutor** (IS-A relationship)
- **User** `1` ─── `*` **Coordinator** (IS-A relationship)
- **Tutor** `1` ─── `*` **TutorAvailability** (Tutor có nhiều time slots)
- **Student** `1` ─── `*` **SessionRequest** (Student tạo nhiều requests)
- **SessionRequest** `1` ─── `1` **SessionMatch** (Mỗi request được match 1 lần)
- **SessionMatch** `*` ─── `1` **Tutor** (Nhiều matches cho 1 tutor)
- **SessionMatch** `*` ─── `1` **TutorAvailability** (Sử dụng 1 time slot)
- **SessionMatch** `1` ─── `0..1` **Session** (Chỉ tạo session khi tutor accept)
- **Session** `1` ─── `*` **SessionFeedback** (1 session có feedback từ student + tutor)
- **Session** `1` ─── `*` **SessionMaterial** (1 session có nhiều tài liệu)

## Business Rules

1. **Tutor Availability:**
   - Tutor phải tạo ít nhất 3 time slots để nhận requests
   - Recurring slots tự động tạo hàng tuần
   - Status `booked` khi có SessionMatch accepted

2. **Session Request Flow:**
   ```
   Student creates SessionRequest (status: pending)
        ↓
   AI/Coordinator creates SessionMatch
        ↓
   Tutor receives notification
        ↓
   ┌─────────────┬─────────────┬──────────────────┐
   │   Accept    │   Reject    │  Request New Time│
   ↓             ↓             ↓
   Create Session  Match again  Student approve?
   (status: scheduled)          ↓           ↓
                            Yes: Session  No: Match again
   ```

3. **Matching Criteria (AI):**
   - Subject expertise match
   - Time availability overlap
   - Price compatibility (budget vs hourly_rate)
   - Rating & experience
   - Geographic proximity (if offline)
   - Student preferences

4. **Session Lifecycle:**
   ```
   scheduled → ongoing → completed
        ↓         ↓         ↓
   cancelled  cancelled  feedback required
   ```

5. **Payment Flow:**
   - Price set at Session creation (from SessionMatch)
   - Payment due before session start
   - Auto-refund if cancelled >24h before

## Indexes (Performance)

```sql
-- User lookup
CREATE INDEX idx_user_email ON User(email);
CREATE INDEX idx_user_role ON User(role);

-- Availability search
CREATE INDEX idx_availability_tutor_status ON TutorAvailability(tutor_id, status);
CREATE INDEX idx_availability_day_time ON TutorAvailability(day_of_week, start_time);

-- Request matching
CREATE INDEX idx_request_status ON SessionRequest(status);
CREATE INDEX idx_request_subject_date ON SessionRequest(subject, preferred_date);

-- Session queries
CREATE INDEX idx_session_student ON Session(student_id, status);
CREATE INDEX idx_session_tutor ON Session(tutor_id, status);
CREATE INDEX idx_session_date ON Session(scheduled_date);

-- Matching optimization
CREATE INDEX idx_match_tutor_status ON SessionMatch(tutor_id, tutor_status);
```

## Sample Data Flow

### Example 1: Successful Match
```
1. Tutor creates TutorAvailability:
   - Monday 14:00-16:00 (recurring)
   - Wednesday 10:00-12:00 (recurring)

2. Student creates SessionRequest:
   - Subject: "Calculus 1"
   - Preferred: Monday 15:00-17:00
   - Budget: 150,000 VND

3. AI creates SessionMatch:
   - Matches with Tutor's Monday 14:00-16:00 slot
   - Suggests: Monday 15:00-17:00
   - match_score: 85.5
   - tutor_status: pending

4. Tutor accepts:
   - tutor_status: accepted
   - Session created:
     - scheduled_date: next Monday
     - start_time: 15:00
     - price: 100,000 VND (tutor's hourly_rate)

5. Session completed:
   - Both give SessionFeedback
   - Tutor rating updated
```

### Example 2: New Time Request
```
1-3. (Same as Example 1)

4. Tutor requests new time:
   - tutor_status: requested_new_time
   - new_time_request: Wednesday 10:30-12:30
   - rejection_reason: "Schedule conflict"

5. Student approves:
   - student_approved_new_time: true
   - Session created with new time

6. (If student rejects, AI matches again with different tutor)
```

