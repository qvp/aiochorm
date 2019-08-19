import pytz

from six import iteritems
from infi.clickhouse_orm.models import ModelBase, Model as _Model, BufferModel, MergeModel, DistributedModel

from .query import AsyncQuerySet


class Model(_Model):
    @classmethod
    def objects_in_async(cls, database):
        return AsyncQuerySet(cls, database)

    @classmethod
    def from_list(cls, line, field_names, timezone_in_use=pytz.utc, database=None):
        from six import next
        values = iter(line)
        kwargs = {}
        for name in field_names:
            field = getattr(cls, name)
            kwargs[name] = field.to_python(next(values), timezone_in_use)

        obj = cls(**kwargs)
        if database is not None:
            obj.set_database(database)

        return obj
