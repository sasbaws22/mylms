import logging
from typing import Optional, List, Dict

from app.core.config import settings
from app.utils.elasticmail import elasticmail_client

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending emails using ElasticMail"""
    
    def __init__(self):
        # No longer need SMTP details, ElasticMailClient handles it
        self.from_email = settings.ELASTICMAIL_FROM_EMAIL
        self.from_name = settings.ELASTICMAIL_FROM_NAME
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str, 
        html_body: Optional[str] = None,
        cc_emails: Optional[List[str]] = None, 
        bcc_emails: Optional[List[str]] = None 
    ) -> bool:
        """Send email to recipient(s) using ElasticMail"""
        try:
            # ElasticMail primarily uses HTML content. If only plain body is provided, use it as HTML.
            content_to_send = html_body if html_body else body
            
            response = await elasticmail_client.send_email(
                to_email=to_email,
                subject=subject,
                html_content=content_to_send
            )
            
            if response and response.get("messageid"): 
                logger.info(f"Email sent successfully to {to_email} via ElasticMail. MessageID: {response.get('messageid')}")
                return True
            else:
                logger.error(f"Failed to send email to {to_email} via ElasticMail. Response: {response}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email} via ElasticMail: {str(e)}")
            return False
    
    async def send_welcome_email(self, user_email: str, user_name: str) -> bool:
        """Send welcome email to new user"""
        subject = f"Welcome to {settings.APP_NAME}!"
        
        html_body = f"""
        <html>
        <body>
            <h2>Welcome to {settings.APP_NAME}!</h2>
            <p>Hello {user_name},</p>
            <p>Welcome to {settings.APP_NAME}! We're excited to have you join our learning community.</p>
            <p>You can now access your learning dashboard and start exploring our courses.</p>
            <p>If you have any questions, please don't hesitate to contact our support team.</p>
            <p>Best regards,<br>The {settings.APP_NAME} Team</p>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, "", html_body) 
    
    async def send_course_assignment_email(
        self, 
        user_email: str, 
        user_name: str, 
        course_title: str,
        due_date: Optional[str] = None
    ) -> bool:
        """Send course assignment notification email"""
        subject = f"New Course Assignment: {course_title}"
        
        due_date_text = f" The course should be completed by {due_date}." if due_date else ""
        
        html_body = f"""
        <html>
        <body>
            <h2>New Course Assignment</h2>
            <p>Hello {user_name},</p>
            <p>You have been assigned a new course: <strong>{course_title}</strong></p>
            {f"<p>The course should be completed by <strong>{due_date}</strong>.</p>" if due_date else ""}
            <p>Please log in to your learning dashboard to start the course.</p>
            <p>Best regards,<br>The {settings.APP_NAME} Team</p>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, "", html_body)
    
    async def send_course_completion_email(
        self, 
        user_email: str, 
        user_name: str, 
        course_title: str,
        certificate_url: Optional[str] = None
    ) -> bool:
        """Send course completion congratulations email"""
        subject = f"Congratulations! You completed {course_title}"
        
        html_body = f"""
        <html>
        <body>
            <h2>Congratulations!</h2>
            <p>Hello {user_name},</p>
            <p>Congratulations! You have successfully completed the course: <strong>{course_title}</strong></p>
            {f"<p>Your certificate is available <a href='{certificate_url}'>here</a>.</p>" if certificate_url else ""}
            <p>Keep up the great work and continue your learning journey!</p>
            <p>Best regards,<br>The {settings.APP_NAME} Team</p>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, "", html_body)
    
    async def send_webinar_reminder_email(
        self, 
        user_email: str, 
        user_name: str, 
        webinar_title: str,
        webinar_date: str,
        webinar_url: Optional[str] = None
    ) -> bool:
        """Send webinar reminder email"""
        subject = f"Reminder: {webinar_title} - {webinar_date}"
        
        html_body = f"""
        <html>
        <body>
            <h2>Webinar Reminder</h2>
            <p>Hello {user_name},</p>
            <p>This is a reminder that you are registered for the upcoming webinar:</p>
            <p><strong>Title:</strong> {webinar_title}<br>
               <strong>Date:</strong> {webinar_date}</p>
            {f"<p><a href='{webinar_url}'>Join the webinar</a></p>" if webinar_url else ""}
            <p>We look forward to seeing you there!</p>
            <p>Best regards,<br>The {settings.APP_NAME} Team</p>
        </body>
        </html>
        """
        
        return await self.send_email(user_email, subject, "", html_body)
    
    async def send_bulk_email(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> Dict[str, int]:
        """Send bulk email to multiple recipients"""
        success_count = 0
        failure_count = 0
        
        # ElasticMail's send_email method is for single recipients. 
        # For bulk, we iterate and send individually or use a dedicated bulk API if available.
        # The provided elasticmail.py doesn't have a bulk send method, so we'll iterate.
        for recipient in recipients:
            success = await self.send_email(recipient, subject, body, html_body)
            if success:
                success_count += 1
            else:
                failure_count += 1
        
        return {
            "success_count": success_count,
            "failure_count": failure_count,
            "total_recipients": len(recipients)
        }



