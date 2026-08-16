class WorkerError(Exception):
    pass

class QueueError(WorkerError):
    pass

class QueueConnectionError(QueueError):
    pass

class QueueFullError(QueueError):
    pass

class JobNotFoundError(WorkerError):
    pass

class JobAlreadyRunningError(WorkerError):
    pass

class WorkerNotStartedError(WorkerError):
    pass

class WorkerAlreadyStartedError(WorkerError):
    pass

class ScanWorkerError(WorkerError):
    pass

class AnalysisWorkerError(WorkerError):
    pass

class ExportWorkerError(WorkerError):
    pass

class CleanupWorkerError(WorkerError):
    pass

class RescanWorkerError(WorkerError):
    pass