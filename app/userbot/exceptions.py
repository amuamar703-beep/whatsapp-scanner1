class UserbotError(Exception):
    pass

class SessionError(UserbotError):
    pass

class SessionExpiredError(SessionError):
    pass

class SessionInvalidError(SessionError):
    pass

class ResolverError(UserbotError):
    pass

class SourceNotFoundError(ResolverError):
    pass

class SourceInvalidError(ResolverError):
    pass

class AccessError(UserbotError):
    pass

class AccessDeniedError(AccessError):
    pass

class AccessRestrictedError(AccessError):
    pass

class ReadNotAllowedError(AccessError):
    pass

class ScannerError(UserbotError):
    pass

class ScanRateLimitError(ScannerError):
    pass

class ScanTimeoutError(ScannerError):
    pass

class FloodWaitError(ScannerError):
    def __init__(self, wait_seconds: int):
        self.wait_seconds = wait_seconds
        super().__init__(f"Flood wait required: {wait_seconds} seconds")

class ExtractorError(UserbotError):
    pass

class NormalizerError(UserbotError):
    pass

class DeduplicatorError(UserbotError):
    pass