from fastapi import HTTPException
from app.depedencies import cursor, pwd_context
from app.models.users import User, TokenResponse, LoginRequest
from fastapi import APIRouter

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
async def create_user(user: User):
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (user.username,))
    if cursor.fetchone()[0] > 0:
        raise HTTPException(status_code=401, detail="User already exists")

    cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (user.email,))
    if cursor.fetchone()[0] > 0:
        raise HTTPException(status_code=402, detail="Email already used")

    hashed_password = pwd_context.hash(user.password)
    cursor.execute(
        """
        INSERT INTO users (home_id, username, email, password, created_at)
        VALUES (%s, %s, %s, %s, NOW())
        RETURNING id
        """,
        (user.home_id, user.username, user.email, hashed_password),
    )
    user_id = cursor.fetchone()[0]
    cursor.connection.commit()
    return { "user_id": user_id }

@router.post("/login", response_model=TokenResponse)
async def login(login_request: LoginRequest):
    cursor.execute("SELECT id, password FROM users WHERE username = %s", (login_request.username,))
    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    user_id, hashed_password = result

    if not pwd_context.verify(login_request.password, hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {"user_id": user_id}
