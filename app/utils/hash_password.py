from passlib.context import CryptContext

class Hash:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    @staticmethod
    def verify_password(plain_pwd, hashed_pwd) -> bool:
        return Hash.pwd_context.verify(plain_pwd, hashed_pwd)
    
    @staticmethod
    def hash_password(password: str) -> str:
        return Hash.pwd_context.hash(password)