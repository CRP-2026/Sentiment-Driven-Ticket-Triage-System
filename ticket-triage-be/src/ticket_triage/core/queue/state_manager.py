from enum import Enum

class TicketState(str, Enum):
    NEW = "new"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"

class InvalidStateTransitionError(ValueError):
    """Lỗi khi thực hiện chuyển đổi trạng thái không hợp lệ."""
    pass

class StateManager:
    """Quản trị máy trạng thái vòng đời 4 bước của ticket."""

    ALLOWED_TRANSITIONS: dict[str, set[str]] = {
        TicketState.NEW.value: {TicketState.ASSIGNED.value, TicketState.IN_PROGRESS.value},
        TicketState.ASSIGNED.value: {TicketState.IN_PROGRESS.value, TicketState.NEW.value},
        TicketState.IN_PROGRESS.value: {TicketState.RESOLVED.value, TicketState.ASSIGNED.value},
        TicketState.RESOLVED.value: {TicketState.NEW.value},  # Mở lại ticket nếu khách phản hồi tiếp
    }

    @classmethod
    def can_transition(cls, current_state: str, next_state: str) -> bool:
        if current_state == next_state:
            return True
        allowed = cls.ALLOWED_TRANSITIONS.get(current_state, set())
        return next_state in allowed

    @classmethod
    def validate_transition(cls, current_state: str, next_state: str) -> None:
        if not cls.can_transition(current_state, next_state):
            raise InvalidStateTransitionError(
                f"Chuyển trạng thái không hợp lệ: '{current_state}' -> '{next_state}'. "
                f"Các trạng thái được phép: {cls.ALLOWED_TRANSITIONS.get(current_state, set())}"
            )
