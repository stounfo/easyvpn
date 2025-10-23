from sqlalchemy.orm import exc


from sqlalchemy import inspect, exc
from typing import Any, Dict
from pydantic import BaseModel

from database.base_meta import Base


class BaseSQLAlchemyModel(Base):
    __abstract__ = True

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def update_by_pydantic(self, model: BaseModel):
        self.update(**model.dict(exclude_none=True))

    def __repr__(self) -> str:
        try:
            mapper = inspect(self.__class__)
        except Exception:
            return f"<{self.__class__.__name__} (unmapped)>"

        field_values: Dict[str, Any] = {}
        for attr in mapper.attrs:
            if not hasattr(attr, "columns"):
                continue
            key = attr.key
            try:
                field_values[key] = getattr(self, key)
            except exc.DetachedInstanceError:
                field_values[key] = "DetachedInstanceError"
        if not field_values:
            return f"<{self.__class__.__name__} {id(self)}>"
        fields_repr = ", ".join(f"{k}={v!r}" for k, v in field_values.items())
        return f"<{self.__class__.__name__}({fields_repr})>"

    def to_dict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}


