from enum import Enum

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"

class TelegramAccountStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    INVALID = "invalid"
    BANNED = "banned"

class SourceType(str, Enum):
    GROUP = "group"
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"
    USER = "user"

class AccessStatus(str, Enum):
    ACCESSIBLE = "accessible"
    JOINABLE = "joinable"
    REQUEST_REQUIRED = "request_required"
    PRIVATE = "private"
    RESTRICTED = "restricted"
    READ_NOT_ALLOWED = "read_not_allowed"
    NOT_FOUND = "not_found"
    UNKNOWN = "unknown"
    INVALID = "invalid"

class JobType(str, Enum):
    SOURCE_SCAN = "source_scan"
    LINK_ANALYSIS = "link_analysis"
    EXPORT = "export"
    CLEANUP = "cleanup"
    RESCAN = "rescan"

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class LinkStatus(str, Enum):
    DIRECT_JOIN = "direct_join"
    REQUEST_JOIN = "request_join"
    INVALID = "invalid"
    REVOKED_OR_CHANGED = "revoked_or_changed"
    TEMPORARY_ERROR = "temporary_error"
    UNKNOWN = "unknown"
    DISCOVERED = "discovered"
    PENDING_ANALYSIS = "pending_analysis"
    ANALYZING = "analyzing"

class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class WalletCategory(str, Enum):
    DIRECT_JOIN = "direct_join"
    REQUEST_JOIN = "request_join"

class ExportFormat(str, Enum):
    TXT = "txt"
    CSV = "csv"
    JSON = "json"
    XLSX = "xlsx"

class NotificationLevel(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    ACCESS = "access"

class ScanScope(str, Enum):
    ALL_MESSAGES = "all_messages"
    DATE_RANGE = "date_range"
    MESSAGE_RANGE = "message_range"