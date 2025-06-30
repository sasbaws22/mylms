"""
LMS Backend Application Package
"""

from app.routes import (analytics,auth, certificates, courses,modules, notifications, quizzes, users, webinars,progress,audit)
from fastapi import FastAPI, APIRouter


from app.core.config import settings
from app.middleware import register_middleware 

api_router = APIRouter()
version = "v1"
version_prefix =f"/{version}"

app = FastAPI(
    title="LMS Backend API",
    description="API for LMS Backend API",
    version=version,
    license_info={"name": "MIT License", "url": "https://opensource.org/license/mit"},
    contact={
        "url": "https://github.com/sasbaws22",
        "email": "ssako@faabsystems.com",
    },
    terms_of_service="https://example.com/tos",
    openapi_url=f"{version_prefix}/openapi.json",
    docs_url=f"{version_prefix}/docs",
    redoc_url=f"{version_prefix}/redoc"
) 

register_middleware(app)

# Include all routers with their prefixes
api_router.include_router(auth.router, prefix=f"{version_prefix}/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix=f"{version_prefix}/users", tags=["User Management"])
api_router.include_router(courses.router, prefix=f"{version_prefix}/courses", tags=["Courses"])
api_router.include_router(modules.router, prefix=f"{version_prefix}/modules", tags=["Modules"])
api_router.include_router(quizzes.router, prefix=f"{version_prefix}/quizzes", tags=["Quizzes"])
api_router.include_router(webinars.router, prefix=f"{version_prefix}/webinars", tags=["Webinars"])
api_router.include_router(notifications.notifications_router, prefix=f"{version_prefix}/notifications", tags=["Notifications"])
api_router.include_router(analytics.router, prefix=f"{version_prefix}/analytics", tags=["Analytics"])
api_router.include_router(progress.progress_router, prefix=f"{version_prefix}/progress", tags=["Progress Tracking"])
api_router.include_router(certificates.certificates_router, prefix=f"{version_prefix}/certificates", tags=["Certificates"]) 
api_router.include_router(audit.router, prefix=f"{version_prefix}/audit", tags=["Audit"])

app.include_router(api_router, prefix=settings.API_V1_STR)

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app_name": "LMS Backend API",
        "version": "1.0.0"
    }




