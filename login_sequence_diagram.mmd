%%{init: {'theme':'default'}}%%
sequenceDiagram
    actor U as User
    participant FE as Frontend (React)
    participant API as Auth API (FastAPI)
    participant SSO as HCMUT_SSO
    participant SVC as AuthService
    participant DB as Database

    U->>FE: Nhập email/password
    FE->>API: POST /auth/login {username, password}

    activate API
    API->>SSO: authenticate()
    activate SSO
    SSO-->>API: SSO user data hoặc lỗi
    deactivate SSO

    alt SSO thành công
        API->>SVC: login_with_sso()
        activate SVC
        SVC->>DB: get_by_email / create
        activate DB
        DB-->>SVC: user
        deactivate DB
        SVC->>SVC: create_access_token()
        SVC-->>API: token
        deactivate SVC
    else SSO thất bại
        API->>SVC: login(email, password)
        activate SVC
        SVC->>DB: get_by_email + verify
        activate DB
        DB-->>SVC: user/none
        deactivate DB
        alt Sai thông tin
            SVC-->>API: 401 Unauthorized
        else Đúng thông tin
            SVC->>SVC: create_access_token()
            SVC-->>API: token
        end
        deactivate SVC
    end

    API-->>FE: token
    deactivate API
    FE->>API: GET /auth/me
    activate API
    API->>DB: get user by token
    activate DB
    DB-->>API: user profile
    deactivate DB
    API-->>FE: user data
    deactivate API
    FE-->>U: Redirect to Dashboard
