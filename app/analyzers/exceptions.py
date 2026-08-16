class AnalyzerError(Exception):
    pass

class AnalysisFailedError(AnalyzerError):
    pass

class AnalysisTimeoutError(AnalyzerError):
    pass

class AnalysisRateLimitError(AnalyzerError):
    pass

class AdapterError(AnalyzerError):
    pass

class AdapterConnectionError(AdapterError):
    pass

class AdapterTimeoutError(AdapterError):
    pass

class ClassifierError(AnalyzerError):
    pass

class ValidatorError(AnalyzerError):
    pass

class RetryManagerError(AnalyzerError):
    pass

class RateLimiterError(AnalyzerError):
    pass