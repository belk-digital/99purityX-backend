from pydantic import BaseModel, ConfigDict, EmailStr


class RegisterSchema(BaseModel):
    email: EmailStr
    password: str

    first_name: str
    last_name: str
    role: str = "PATIENT"
    
class VerifyEmailSchema(BaseModel):
    email: EmailStr
    otp: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str
    
class GoogleLoginSchema(BaseModel):
    id_token: str
    
class ResendOTPSchema(BaseModel):
    email: EmailStr
    
class ForgotPasswordSchema(BaseModel):
    email: EmailStr
    
class ResetPasswordSchema(BaseModel):
    email: EmailStr
    otp: str
    new_password: str   

class TokenResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponseSchema(BaseModel):
    id: str
    email: EmailStr
    first_name: str
    last_name: str

    model_config = ConfigDict(
        from_attributes=True
    )
    
class MeResponseSchema(BaseModel):
    id: str
    email: EmailStr
    role: str
    permissions: list[str]

    model_config = ConfigDict(
        from_attributes=True
    )
    
class RefreshTokenSchema(BaseModel):
    refresh_token: str


class LogoutSchema(BaseModel):
    refresh_token: str