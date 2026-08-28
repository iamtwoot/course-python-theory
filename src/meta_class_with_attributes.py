from datetime import UTC, datetime


class CreatedAtMeta(type):
    def __new__(mcs, name, bases, attrs):
        attrs.update(created_at=datetime.now(UTC))
        return super().__new__(mcs, name, bases, attrs)


class CreatedAt(metaclass=CreatedAtMeta):
    pass


obj = CreatedAt()
print(obj.created_at)
