import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config.settings import settings


class EmailService:

    @staticmethod
    async def _send_email(to: str, subject: str, html_body: str):
        if not settings.SMTP_HOST or not settings.SMTP_USER:
            print(f"[EMAIL FALLBACK] To: {to} | Subject: {subject}")
            print(f"[EMAIL FALLBACK] Body preview: {html_body[:200]}")
            return

        msg = MIMEMultipart("alternative")
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL or settings.SMTP_USER}>"
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))

        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )

    @staticmethod
    async def send_verification_otp(email: str, otp: str):
        print(f"OTP for {email}: {otp}")

        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto; padding: 32px;">
            <h2 style="color: #0f172a; margin-bottom: 8px;">Verify Your Email</h2>
            <p style="color: #64748b; font-size: 14px;">
                Use the code below to verify your account on the Longevity & Optimization Platform.
            </p>
            <div style="background: #f1f5f9; border-radius: 12px; padding: 24px; text-align: center; margin: 24px 0;">
                <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #0f172a;">{otp}</span>
            </div>
            <p style="color: #94a3b8; font-size: 12px;">
                This code expires in 10 minutes. If you didn't request this, please ignore this email.
            </p>
        </div>
        """

        await EmailService._send_email(email, f"Your verification code: {otp}", html)

    @staticmethod
    async def send_password_reset_otp(email: str, otp: str):
        print(f"Password reset OTP for {email}: {otp}")

        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto; padding: 32px;">
            <h2 style="color: #0f172a; margin-bottom: 8px;">Reset Your Password</h2>
            <p style="color: #64748b; font-size: 14px;">
                Use the code below to reset your password.
            </p>
            <div style="background: #f1f5f9; border-radius: 12px; padding: 24px; text-align: center; margin: 24px 0;">
                <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #0f172a;">{otp}</span>
            </div>
            <p style="color: #94a3b8; font-size: 12px;">
                This code expires in 10 minutes. If you didn't request this, please ignore this email.
            </p>
        </div>
        """

        await EmailService._send_email(email, f"Password reset code: {otp}", html)
