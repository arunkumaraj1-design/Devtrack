from abc import ABC, abstractmethod
from datetime import datetime


class BaseEntity(ABC):
    @abstractmethod
    def validate(self):
        """Raise ValueError when the entity contains invalid data."""

    def to_dict(self):
        return dict(self.__dict__)


class Reporter(BaseEntity):
    def __init__(self, id, name, email, team):
        self.id = id
        self.name = name.strip() if isinstance(name, str) else name
        self.email = email.strip() if isinstance(email, str) else email
        self.team = team.strip() if isinstance(team, str) else team

    def validate(self):
        if not isinstance(self.id, int) or isinstance(self.id, bool) or self.id <= 0:
            raise ValueError('ID must be a positive integer')
        if not isinstance(self.name, str) or not self.name:
            raise ValueError('Name cannot be empty')
        if not isinstance(self.email, str) or '@' not in self.email:
            raise ValueError('Invalid email')
        local, _, domain = self.email.partition('@')
        if not local or not domain or '.' not in domain:
            raise ValueError('Invalid email')
        if not isinstance(self.team, str) or not self.team:
            raise ValueError('Team cannot be empty')


class Issue(BaseEntity):
    ALLOWED_STATUSES = {'open', 'in_progress', 'resolved', 'closed'}
    ALLOWED_PRIORITIES = {'low', 'medium', 'high', 'critical'}

    def __init__(self, id, title, description, status, priority, reporter_id, created_at=None):
        self.id = id
        self.title = title.strip() if isinstance(title, str) else title
        self.description = description if description is not None else ''
        self.status = status
        self.priority = priority
        self.reporter_id = reporter_id
        self.created_at = created_at or str(datetime.now())

    def validate(self):
        if not isinstance(self.id, int) or isinstance(self.id, bool) or self.id <= 0:
            raise ValueError('ID must be a positive integer')
        if not isinstance(self.title, str) or not self.title:
            raise ValueError('Title cannot be empty')
        if not isinstance(self.description, str):
            raise ValueError('Description must be text')
        if not isinstance(self.status, str) or self.status not in self.ALLOWED_STATUSES:
            raise ValueError('Invalid status')
        if not isinstance(self.priority, str) or self.priority not in self.ALLOWED_PRIORITIES:
            raise ValueError('Invalid priority')
        if not isinstance(self.reporter_id, int) or isinstance(self.reporter_id, bool) or self.reporter_id <= 0:
            raise ValueError('Reporter ID must be a positive integer')

    def describe(self):
        return f"{self.title} [{self.priority}]"


class CriticalIssue(Issue):
    def describe(self):
        return f"[URGENT] {self.title} \u2014 needs immediate attention"


class LowPriorityIssue(Issue):
    def describe(self):
        return f"{self.title} \u2014 low priority, handle when free"
