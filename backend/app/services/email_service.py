"""
Email notification service for SkillForge Global.
Supports multiple providers: SendGrid, AWS SES, SMTP.
"""
from typing import Optional, Dict, Any
from datetime import datetime
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications."""
    
    def __init__(self):
        """Initialize email service based on configuration."""
        self.provider = getattr(settings, "EMAIL_PROVIDER", "smtp").lower()
        self.from_email = getattr(settings, "EMAIL_FROM", "noreply@skillforge.global")
        self.from_name = getattr(settings, "EMAIL_FROM_NAME", "SkillForge Global")
        
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email using the configured provider.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML body content
            text_content: Plain text body content (optional, extracted from HTML if not provided)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            if self.provider == "sendgrid":
                return await self._send_with_sendgrid(to_email, subject, html_content, text_content)
            elif self.provider == "ses":
                return await self._send_with_ses(to_email, subject, html_content, text_content)
            else:  # Default to SMTP
                return await self._send_with_smtp(to_email, subject, html_content, text_content)
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    async def _send_with_smtp(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send email using SMTP."""
        try:
            smtp_host = getattr(settings, "SMTP_HOST", "smtp.gmail.com")
            smtp_port = getattr(settings, "SMTP_PORT", 587)
            smtp_user = getattr(settings, "SMTP_USER", "")
            smtp_password = getattr(settings, "SMTP_PASSWORD", "")
            # In development, allow unauthenticated SMTP (Mailhog) on localhost:1025
            allow_unauth_local = (str(smtp_host) in ("localhost", "127.0.0.1") and int(smtp_port) in (1025,))

            if not smtp_user or not smtp_password:
                if not allow_unauth_local:
                    logger.warning("SMTP credentials not configured, skipping email")
                    return False
                else:
                    logger.debug("Using unauthenticated local SMTP (Mailhog) at %s:%s", smtp_host, smtp_port)
            
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = to_email
            
            # Attach parts
            if text_content:
                msg.attach(MIMEText(text_content, "plain"))
            msg.attach(MIMEText(html_content, "html"))
            
            # Send email. If using local Mailhog (no auth), skip STARTTLS and login.
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                if not allow_unauth_local:
                    try:
                        server.starttls()
                    except Exception:
                        logger.debug("STARTTLS failed or unsupported; continuing without TLS")

                    if smtp_user and smtp_password:
                        server.login(smtp_user, smtp_password)

                server.send_message(msg)
            
            logger.info(f"Email sent to {to_email} via SMTP")
            return True
            
        except Exception as e:
            logger.error(f"SMTP error: {str(e)}")
            return False
    
    async def _send_with_sendgrid(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send email using SendGrid API."""
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail, Email, To, Content
            
            sg_api_key = getattr(settings, "SENDGRID_API_KEY", "")
            if not sg_api_key:
                logger.warning("SendGrid API key not configured, skipping email")
                return False
            
            sg = sendgrid.SendGridAPIClient(api_key=sg_api_key)
            
            from_email = Email(self.from_email, self.from_name)
            to_email_obj = To(to_email)
            content = Content("text/html", html_content)
            
            mail = Mail(from_email, to_email_obj, subject, content)
            
            response = sg.client.mail.send.post(request_body=mail.get())
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent to {to_email} via SendGrid")
                return True
            else:
                logger.error(f"SendGrid error: {response.status_code}")
                return False
                
        except ImportError:
            logger.error("SendGrid library not installed. Install with: pip install sendgrid")
            return False
        except Exception as e:
            logger.error(f"SendGrid error: {str(e)}")
            return False
    
    async def _send_with_ses(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send email using AWS SES."""
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            aws_region = getattr(settings, "AWS_REGION", "us-east-1")
            
            client = boto3.client('ses', region_name=aws_region)
            
            response = client.send_email(
                Source=f"{self.from_name} <{self.from_email}>",
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {
                        'Html': {'Data': html_content, 'Charset': 'UTF-8'},
                    }
                }
            )
            
            logger.info(f"Email sent to {to_email} via AWS SES")
            return True
            
        except ImportError:
            logger.error("Boto3 library not installed. Install with: pip install boto3")
            return False
        except ClientError as e:
            logger.error(f"AWS SES error: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            logger.error(f"AWS SES error: {str(e)}")
            return False
    
    # --- Templated Email Methods ---
    
    async def send_session_confirmation(
        self,
        to_email: str,
        mentor_name: str,
        student_name: str,
        session_date: datetime,
        session_duration: int,
        meeting_url: str,
        session_id: int
    ) -> bool:
        """Send session confirmation email."""
        subject = f"Session Confirmed with {mentor_name}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Session Confirmed! 🎉</h2>
                
                <p>Hi {student_name},</p>
                
                <p>Your mentoring session with <strong>{mentor_name}</strong> has been confirmed!</p>
                
                <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #1f2937;">Session Details</h3>
                    <p><strong>Date & Time:</strong> {session_date.strftime('%B %d, %Y at %I:%M %p')}</p>
                    <p><strong>Duration:</strong> {session_duration} minutes</p>
                    <p><strong>Session ID:</strong> #{session_id}</p>
                </div>
                
                <p>
                    <a href="{meeting_url}" 
                       style="display: inline-block; background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0;">
                        Join Meeting
                    </a>
                </p>
                
                <p style="color: #6b7280; font-size: 14px;">
                    <strong>Important:</strong> Please join the meeting 5 minutes before the scheduled time. 
                    Make sure your camera and microphone are working.
                </p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                
                <p style="color: #6b7280; font-size: 12px;">
                    Need to reschedule? Contact your mentor or visit your dashboard.<br>
                    SkillForge Global - Empowering Your Learning Journey
                </p>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)
    
    async def send_session_reminder(
        self,
        to_email: str,
        recipient_name: str,
        other_person_name: str,
        session_date: datetime,
        meeting_url: str,
        session_id: int
    ) -> bool:
        """Send session reminder email (24h before)."""
        subject = f"Reminder: Session Tomorrow with {other_person_name}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #f59e0b;">Session Reminder ⏰</h2>
                
                <p>Hi {recipient_name},</p>
                
                <p>This is a friendly reminder about your upcoming mentoring session with <strong>{other_person_name}</strong>.</p>
                
                <div style="background: #fef3c7; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f59e0b;">
                    <h3 style="margin-top: 0; color: #92400e;">Tomorrow at {session_date.strftime('%I:%M %p')}</h3>
                    <p style="margin-bottom: 0;"><strong>Session ID:</strong> #{session_id}</p>
                </div>
                
                <p>
                    <a href="{meeting_url}" 
                       style="display: inline-block; background: #f59e0b; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0;">
                        View Session Details
                    </a>
                </p>
                
                <p style="color: #6b7280; font-size: 14px;">
                    <strong>Preparation Tips:</strong><br>
                    • Test your camera and microphone<br>
                    • Prepare any questions or materials<br>
                    • Find a quiet space for the session<br>
                    • Join 5 minutes early
                </p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                
                <p style="color: #6b7280; font-size: 12px;">
                    SkillForge Global - Empowering Your Learning Journey
                </p>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)
    
    async def send_session_cancellation(
        self,
        to_email: str,
        recipient_name: str,
        other_person_name: str,
        session_date: datetime,
        reason: Optional[str],
        session_id: int
    ) -> bool:
        """Send session cancellation email."""
        subject = f"Session Cancelled: {other_person_name}"
        
        reason_text = f"<p><strong>Reason:</strong> {reason}</p>" if reason else ""
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #dc2626;">Session Cancelled</h2>
                
                <p>Hi {recipient_name},</p>
                
                <p>We're sorry to inform you that your mentoring session with <strong>{other_person_name}</strong> has been cancelled.</p>
                
                <div style="background: #fee2e2; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #dc2626;">
                    <h3 style="margin-top: 0; color: #991b1b;">Cancelled Session</h3>
                    <p><strong>Original Date:</strong> {session_date.strftime('%B %d, %Y at %I:%M %p')}</p>
                    <p><strong>Session ID:</strong> #{session_id}</p>
                    {reason_text}
                </div>
                
                <p>Any payment for this session will be refunded within 5-7 business days.</p>
                
                <p>
                    <a href="{settings.FRONTEND_ORIGIN}/mentors" 
                       style="display: inline-block; background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0;">
                        Find Another Mentor
                    </a>
                </p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                
                <p style="color: #6b7280; font-size: 12px;">
                    Questions? Contact support at support@skillforge.global<br>
                    SkillForge Global - Empowering Your Learning Journey
                </p>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)
    
    async def send_payment_receipt(
        self,
        to_email: str,
        student_name: str,
        mentor_name: str,
        amount: float,
        session_date: datetime,
        session_id: int,
        payment_intent_id: str
    ) -> bool:
        """Send payment receipt email."""
        subject = f"Payment Receipt - Session #{session_id}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #059669;">Payment Successful ✓</h2>
                
                <p>Hi {student_name},</p>
                
                <p>Thank you for your payment. Your mentoring session with <strong>{mentor_name}</strong> has been confirmed.</p>
                
                <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #1f2937;">Payment Details</h3>
                    <p><strong>Amount Paid:</strong> ${amount:.2f}</p>
                    <p><strong>Session Date:</strong> {session_date.strftime('%B %d, %Y at %I:%M %p')}</p>
                    <p><strong>Session ID:</strong> #{session_id}</p>
                    <p><strong>Payment ID:</strong> {payment_intent_id}</p>
                    <p><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
                </div>
                
                <p style="color: #6b7280; font-size: 14px;">
                    This receipt has been sent to your email. Keep it for your records.
                </p>
                
                <p>
                    <a href="{settings.FRONTEND_ORIGIN}/dashboard" 
                       style="display: inline-block; background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0;">
                        View Dashboard
                    </a>
                </p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                
                <p style="color: #6b7280; font-size: 12px;">
                    Questions about your payment? Contact support at support@skillforge.global<br>
                    SkillForge Global - Empowering Your Learning Journey
                </p>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)
    
    async def send_mentor_approved(
        self,
        to_email: str,
        mentor_name: str
    ) -> bool:
        """Send mentor application approval email."""
        subject = "Congratulations! Your Mentor Application is Approved 🎉"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #059669;">Welcome to Our Mentor Community! 🎉</h2>
                
                <p>Hi {mentor_name},</p>
                
                <p>Great news! Your application to become a mentor on SkillForge Global has been <strong>approved</strong>!</p>
                
                <div style="background: #d1fae5; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #059669;">
                    <h3 style="margin-top: 0; color: #065f46;">Next Steps</h3>
                    <ol style="margin-bottom: 0;">
                        <li>Complete your mentor profile</li>
                        <li>Set your availability schedule</li>
                        <li>Set your hourly rate</li>
                        <li>Start accepting session requests</li>
                    </ol>
                </div>
                
                <p>
                    <a href="{settings.FRONTEND_ORIGIN}/mentors/dashboard" 
                       style="display: inline-block; background: #059669; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0;">
                        Go to Mentor Dashboard
                    </a>
                </p>
                
                <p style="color: #6b7280; font-size: 14px;">
                    <strong>Resources for Mentors:</strong><br>
                    • Mentor Guidelines & Best Practices<br>
                    • Setting Your Availability<br>
                    • Pricing Your Sessions<br>
                    • Building Your Reputation
                </p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                
                <p style="color: #6b7280; font-size: 12px;">
                    Questions? Reach out to our mentor support team at mentors@skillforge.global<br>
                    SkillForge Global - Empowering Your Learning Journey
                </p>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)
    
    async def send_mentor_rejected(
        self,
        to_email: str,
        mentor_name: str,
        reason: Optional[str] = None
    ) -> bool:
        """Send mentor application rejection email."""
        subject = "Update on Your Mentor Application"
        
        reason_text = f"<p><strong>Feedback:</strong> {reason}</p>" if reason else ""
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #1f2937;">Mentor Application Update</h2>
                
                <p>Hi {mentor_name},</p>
                
                <p>Thank you for your interest in becoming a mentor on SkillForge Global.</p>
                
                <p>After careful review, we're unable to approve your application at this time.</p>
                
                {reason_text}
                
                <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #1f2937;">You Can Reapply</h3>
                    <p style="margin-bottom: 0;">
                        We encourage you to reapply in the future after gaining more experience 
                        or addressing the feedback provided. We're always looking for great mentors!
                    </p>
                </div>
                
                <p>
                    <a href="{settings.FRONTEND_ORIGIN}/mentors/become" 
                       style="display: inline-block; background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0;">
                        Reapply as Mentor
                    </a>
                </p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                
                <p style="color: #6b7280; font-size: 12px;">
                    Questions? Contact us at mentors@skillforge.global<br>
                    SkillForge Global - Empowering Your Learning Journey
                </p>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)
    
    async def send_welcome_email(
        self,
        to_email: str,
        user_name: str
    ) -> bool:
        """Send welcome email to new user."""
        subject = "Welcome to SkillForge Global! 🚀"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #2563eb; margin-bottom: 10px;">Welcome to SkillForge Global! 🚀</h1>
                    <p style="color: #6b7280; font-size: 18px;">Your learning journey starts here</p>
                </div>
                
                <p>Hi {user_name},</p>
                
                <p>Thank you for joining <strong>SkillForge Global</strong>! We're excited to have you as part of our learning community.</p>
                
                <div style="background: #eff6ff; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2563eb;">
                    <h3 style="margin-top: 0; color: #1e40af;">Get Started in 3 Easy Steps</h3>
                    <ol style="margin-bottom: 0;">
                        <li><strong>Explore Courses</strong> - Browse our curated learning paths</li>
                        <li><strong>Take Quizzes</strong> - Test your knowledge with AI-generated quizzes</li>
                        <li><strong>Connect with Mentors</strong> - Get personalized guidance</li>
                    </ol>
                </div>
                
                <p>
                    <a href="{settings.FRONTEND_ORIGIN}/paths" 
                       style="display: inline-block; background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 10px 10px 0;">
                        Browse Learning Paths
                    </a>
                    <a href="{settings.FRONTEND_ORIGIN}/dashboard" 
                       style="display: inline-block; background: #059669; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0;">
                        Go to Dashboard
                    </a>
                </p>
                
                <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #1f2937;">🎁 New User Bonus</h3>
                    <p style="margin-bottom: 0;">
                        You've received <strong>100 Forge Coins</strong> to get started! 
                        Use them for AI quizzes, mentor sessions, and more.
                    </p>
                </div>
                
                <p style="color: #6b7280; font-size: 14px;">
                    <strong>Need Help?</strong><br>
                    Check out our <a href="{settings.FRONTEND_ORIGIN}/faq" style="color: #2563eb;">FAQ</a> 
                    or contact us at support@skillforge.global
                </p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                
                <p style="color: #6b7280; font-size: 12px; text-align: center;">
                    SkillForge Global - Empowering Your Learning Journey<br>
                    <a href="{settings.FRONTEND_ORIGIN}" style="color: #2563eb;">skillforge.global</a>
                </p>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)
    
        async def send_login_notification(self, to_email: str, ip: Optional[str] = None, time: Optional[str] = None) -> None:
            """Send a notification email after a successful login (useful for security alerts)."""
            subject = f"New sign-in to {self.frontend_name}"
            time_text = time or datetime.utcnow().isoformat() + "Z"
            ip_text = ip or "Unknown"
            html_body = (
                f"<p>Hi,</p>"
                f"<p>We noticed a sign-in to your {self.frontend_name} account.</p>"
                f"<p><strong>Time:</strong> {time_text}<br>"
                f"<strong>IP:</strong> {ip_text}</p>"
                f"<p>If this was you, no action is needed. If you did not sign in, please reset your password immediately: "
                f"<a href=\"{self.frontend_url}/reset-password\">Reset password</a></p>"
            )
            await self.send_email(to_email, subject, html_body)
    
    async def send_password_reset_email(
        self,
        to_email: str,
        user_name: str,
        reset_token: str
    ) -> bool:
        """Send password reset email."""
        subject = "Reset Your SkillForge Password"
        
        reset_url = f"{settings.FRONTEND_ORIGIN}/reset-password?token={reset_token}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #1f2937;">Password Reset Request 🔒</h2>
                
                <p>Hi {user_name},</p>
                
                <p>We received a request to reset your password for your SkillForge Global account.</p>
                
                <div style="background: #fef3c7; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f59e0b;">
                    <p style="margin: 0;"><strong>⚠️ Security Notice:</strong> This link expires in 1 hour</p>
                </div>
                
                <p>Click the button below to reset your password:</p>
                
                <p>
                    <a href="{reset_url}" 
                       style="display: inline-block; background: #dc2626; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0;">
                        Reset Password
                    </a>
                </p>
                
                <p style="color: #6b7280; font-size: 14px;">
                    If the button doesn't work, copy and paste this link into your browser:<br>
                    <a href="{reset_url}" style="color: #2563eb; word-break: break-all;">{reset_url}</a>
                </p>
                
                <div style="background: #fee2e2; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0; color: #991b1b;">
                        <strong>Didn't request this?</strong><br>
                        If you didn't request a password reset, please ignore this email. 
                        Your password will remain unchanged.
                    </p>
                </div>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                
                <p style="color: #6b7280; font-size: 12px;">
                    For security, this link expires in 1 hour.<br>
                    If you have questions, contact us at support@skillforge.global<br>
                    SkillForge Global - Empowering Your Learning Journey
                </p>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)
    
    async def send_job_application_reminder(
        self,
        to_email: str,
        user_name: str,
        company_name: str,
        position: str,
        days_since_apply: int,
        application_id: int
    ) -> bool:
        """Send job application follow-up reminder."""
        subject = f"Follow-up Reminder: {position} at {company_name}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #f59e0b;">Application Follow-up Reminder ⏰</h2>
                
                <p>Hi {user_name},</p>
                
                <p>It's been <strong>{days_since_apply} days</strong> since you applied for <strong>{position}</strong> at <strong>{company_name}</strong>.</p>
                
                <div style="background: #fef3c7; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f59e0b;">
                    <h3 style="margin-top: 0; color: #92400e;">Time to Follow Up!</h3>
                    <p style="margin-bottom: 0;">
                        Following up shows initiative and keeps your application top of mind. 
                        Consider sending a polite email to the hiring manager or recruiter.
                    </p>
                </div>
                
                <p>
                    <a href="{settings.FRONTEND_ORIGIN}/job-tracker/{application_id}" 
                       style="display: inline-block; background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0;">
                        View Application Details
                    </a>
                </p>
                
                <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #1f2937;">✉️ Follow-up Email Template</h3>
                    <p style="font-size: 14px; font-style: italic; margin-bottom: 0;">
                        "Dear [Hiring Manager],<br><br>
                        I hope this email finds you well. I wanted to follow up on my application for the {position} position 
                        that I submitted on [date]. I remain very interested in this opportunity and would welcome 
                        the chance to discuss how my skills and experience align with your team's needs.<br><br>
                        Thank you for your consideration.<br><br>
                        Best regards,<br>
                        {user_name}"
                    </p>
                </div>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                
                <p style="color: #6b7280; font-size: 12px;">
                    Managing your job search with SkillForge Global Job Tracker<br>
                    Stay organized and never miss a follow-up!
                </p>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)
    
    async def send_reference_check_request(
        self,
        to_email: str,
        reference_name: str,
        candidate_name: str,
        position: str,
        company_name: str,
        reference_check_id: int,
        response_deadline: datetime
    ) -> bool:
        """Send reference check request email."""
        subject = f"Reference Request for {candidate_name}"
        
        # Create response link (would integrate with actual reference check form)
        response_link = f"{settings.FRONTEND_ORIGIN}/reference-check/{reference_check_id}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Reference Request</h2>
                
                <p>Dear {reference_name},</p>
                
                <p><strong>{candidate_name}</strong> has applied for the position of <strong>{position}</strong> at <strong>{company_name}</strong> 
                and has listed you as a professional reference.</p>
                
                <div style="background: #eff6ff; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2563eb;">
                    <h3 style="margin-top: 0; color: #1e40af;">We'd Appreciate Your Input</h3>
                    <p style="margin-bottom: 0;">
                        Your feedback will help us make an informed hiring decision. The reference form 
                        takes approximately 5-10 minutes to complete and all responses are confidential.
                    </p>
                </div>
                
                <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>Candidate:</strong> {candidate_name}</p>
                    <p style="margin: 5px 0;"><strong>Position:</strong> {position}</p>
                    <p style="margin: 5px 0;"><strong>Response Deadline:</strong> {response_deadline.strftime('%B %d, %Y')}</p>
                </div>
                
                <p>
                    <a href="{response_link}" 
                       style="display: inline-block; background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0;">
                        Complete Reference Form
                    </a>
                </p>
                
                <p style="color: #6b7280; font-size: 14px;">
                    <strong>Questions We'll Ask:</strong><br>
                    • How long have you worked with {candidate_name}?<br>
                    • What were their key strengths?<br>
                    • What areas could they improve?<br>
                    • Would you recommend them for this role?
                </p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                
                <p style="color: #6b7280; font-size: 12px;">
                    This is an automated reference check request from SkillForge Global.<br>
                    If you have questions or concerns, please contact hr@skillforge.global
                </p>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, html_content)


# Singleton instance
email_service = EmailService()
