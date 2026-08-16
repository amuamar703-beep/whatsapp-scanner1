class AppException(Exception):
    def __init__(self, message: str = "", code: str = "UNKNOWN_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)

class ValidationError(AppException):
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, "VALIDATION_ERROR", 400)

class AuthenticationError(AppException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, "AUTHENTICATION_ERROR", 401)

class PermissionError(AppException):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, "PERMISSION_ERROR", 403)

class NotFoundError(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, "NOT_FOUND", 404)

class ConflictError(AppException):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, "CONFLICT_ERROR", 409)

class RateLimitError(AppException):
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, "RATE_LIMIT_ERROR", 429)

class ServiceUnavailableError(AppException):
    def __init__(self, message: str = "Service unavailable"):
        super().__init__(message, "SERVICE_UNAVAILABLE", 503)

class DatabaseError(AppException):
    def __init__(self, message: str = "Database error"):
        super().__init__(message, "DATABASE_ERROR", 500)

class TelegramError(AppException):
    def __init__(self, message: str = "Telegram API error"):
        super().__init__(message, "TELEGRAM_ERROR", 500)

class WhatsAppError(AppException):
    def __init__(self, message: str = "WhatsApp API error"):
        super().__init__(message, "WHATSAPP_ERROR", 500)

class JobError(AppException):
    def __init__(self, message: str = "Job processing error"):
        super().__init__(message, "JOB_ERROR", 500)

class SessionError(AppException):
    def __init__(self, message: str = "Session error"):
        super().__init__(message, "SESSION_ERROR", 401)

class ConfigurationError(AppException):
    def __init__(self, message: str = "Configuration error"):
        super().__init__(message, "CONFIGURATION_ERROR", 500)

class RateLimiterError(AppException):
    def __init__(self, message: str = "Rate limiter error"):
        super().__init__(message, "RATE_LIMITER_ERROR", 429)

class FloodWaitError(AppException):
    def __init__(self, wait_seconds: int):
        self.wait_seconds = wait_seconds
        super().__init__(f"Flood wait required: {wait_seconds} seconds", "FLOOD_WAIT", 429)

class AnalysisError(AppException):
    def __init__(self, message: str = "Analysis error"):
        super().__init__(message, "ANALYSIS_ERROR", 500)