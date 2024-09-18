from passlib.context import CryptContext

crypt_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
