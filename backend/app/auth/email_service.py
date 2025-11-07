"""
Email Service for Authentication

Handles sending authentication-related emails such as:
- Password reset emails
- Email verification
- Welcome emails
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

from ..config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending authentication emails."""
    
    @staticmethod
    def _send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email using SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text fallback content
            
        Returns:
            True if email sent successfully, False otherwise
        """
        # Skip if SMTP is not configured
        if not settings.smtp_server:
            logger.warning("=" * 80)
            logger.warning(f"SMTP not configured. Email would be sent to {to_email}")
            logger.warning(f"Subject: {subject}")
            logger.warning("-" * 80)
            logger.warning("EMAIL CONTENT:")
            logger.warning(html_content)
            logger.warning("-" * 80)
            # Extract verification link if it's a verification email
            if "verify-email" in html_content or "Verify Email" in html_content:
                import re
                link_match = re.search(r'href="([^"]+)"', html_content)
                if link_match:
                    verification_link = link_match.group(1)
                    logger.warning(f"🔗 VERIFICATION LINK: {verification_link}")
                    logger.warning("=" * 80)
            return True  # Return True in development to not block the flow
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = settings.smtp_username or "noreply@aptora.com"
            message["To"] = to_email
            
            # Add plain text and HTML parts
            if text_content:
                part1 = MIMEText(text_content, "plain")
                message.attach(part1)
            
            part2 = MIMEText(html_content, "html")
            message.attach(part2)
            
            # Send email
            with smtplib.SMTP(settings.smtp_server, settings.smtp_port or 587) as server:
                server.starttls()
                if settings.smtp_username and settings.smtp_password:
                    server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(message)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    @staticmethod
    def send_password_reset_email(email: str, reset_token: str) -> bool:
        """
        Send a password reset email.
        
        Args:
            email: User's email address
            reset_token: Password reset token
            
        Returns:
            True if email sent successfully, False otherwise
        """
        reset_link = f"{settings.frontend_url}/reset-password?token={reset_token}"
        
        subject = "Reset Your Aptora Password"
        
        html_content = f"""
        <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>You requested to reset your password for your Aptora account.</p>
                <p>Click the link below to reset your password:</p>
                <p><a href="{reset_link}">Reset Password</a></p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this, please ignore this email.</p>
                <br>
                <p>Best regards,<br>The Aptora Team</p>
            </body>
        </html>
        """
        
        text_content = f"""
        Password Reset Request
        
        You requested to reset your password for your Aptora account.
        
        Visit this link to reset your password:
        {reset_link}
        
        This link will expire in 1 hour.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        The Aptora Team
        """
        
        return EmailService._send_email(email, subject, html_content, text_content)
    
    @staticmethod
    def send_verification_email(email: str, verification_token: str) -> bool:
        """
        Send an email verification email.
        
        Args:
            email: User's email address
            verification_token: Email verification token
            
        Returns:
            True if email sent successfully, False otherwise
        """
        verification_link = f"{settings.frontend_url}/verify-email?token={verification_token}"
        
        subject = "Verify Your Aptora Email"
        
        html_content = f"""
        <html>
            <body>
                <h2>Welcome to Aptora!</h2>
                <p>Thank you for signing up. Please verify your email address to get started.</p>
                <p>Click the link below to verify your email:</p>
                <p><a href="{verification_link}">Verify Email</a></p>
                <p>This link will expire in 24 hours.</p>
                <br>
                <p>Best regards,<br>The Aptora Team</p>
            </body>
        </html>
        """
        
        text_content = f"""
        Welcome to Aptora!
        
        Thank you for signing up. Please verify your email address to get started.
        
        Visit this link to verify your email:
        {verification_link}
        
        This link will expire in 24 hours.
        
        Best regards,
        The Aptora Team
        """
        
        return EmailService._send_email(email, subject, html_content, text_content)
    
    @staticmethod
    def send_welcome_email(email: str, first_name: str) -> bool:
        """
        Send a welcome email to a new user.
        
        Args:
            email: User's email address
            first_name: User's first name
            
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = "Welcome to Aptora!"
        
        html_content = f"""
        <html>
            <body>
                <h2>Welcome to Aptora, {first_name}!</h2>
                <p>Your account has been successfully created.</p>
                <p>Aptora helps you create personalized study plans by optimizing time management.</p>
                <p>Get started by:</p>
                <ul>
                    <li>Adding your courses</li>
                    <li>Creating assignments and deadlines</li>
                    <li>Setting your availability</li>
                    <li>Generating your optimized study schedule</li>
                </ul>
                <p><a href="{settings.frontend_url}/dashboard">Go to Dashboard</a></p>
                <br>
                <p>Best regards,<br>The Aptora Team</p>
            </body>
        </html>
        """
        
        text_content = f"""
        Welcome to Aptora, {first_name}!
        
        Your account has been successfully created.
        
        Aptora helps you create personalized study plans by optimizing time management.
        
        Get started by:
        - Adding your courses
        - Creating assignments and deadlines
        - Setting your availability
        - Generating your optimized study schedule
        
        Visit: {settings.frontend_url}/dashboard
        
        Best regards,
        The Aptora Team
        """
        
        return EmailService._send_email(email, subject, html_content, text_content)
