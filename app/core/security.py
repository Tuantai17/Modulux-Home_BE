import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


def verify_password(plain_password: str, hashed_password: str) -> bool:
  """So sánh mật khẩu người dùng nhập với mật khẩu đã mã hóa trong DB."""
  try:
    return bcrypt.checkpw(
      plain_password.encode("utf-8"),
      hashed_password.encode("utf-8")
    )
  except ValueError:
    return False


def get_password_hash(password: str) -> str:
  """Mã hóa mật khẩu trước khi lưu vào DB."""
  return bcrypt.hashpw(
    password.encode("utf-8"),
    bcrypt.gensalt()
  ).decode("utf-8")


def create_access_token(
  data: dict,
  expires_delta: timedelta | None = None
) -> str:
  """Tạo JWT Token cho người dùng sau khi đăng nhập."""
  to_encode = data.copy()
  expire = datetime.now(timezone.utc) + (
    expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  )
  to_encode.update({"exp": expire})
  return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
