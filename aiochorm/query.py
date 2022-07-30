from math import ceil

from infi.clickhouse_orm.query import (Operator, SimpleOperator, InOperator, LikeOperator, IExactOperator,
                                       NotOperator, BetweenOperator, register_operator, FOV, Q, QuerySet,
                                       AggregateQuerySet)


class Page:
    """Page implementation for pagination."""

    def __init__(self, objects, total_objects, total_pages):
        self.objects = objects
        self.total_objects = total_objects
        self.total_pages = total_pages



class AsyncCountMixin:
    """Mixin with async meta methods."""

    async def _count_subquery(self):
        sql = u'SELECT count() FROM (%s)' % self.as_sql()
        raw = await self._database.raw(sql)
        return int(raw[0][0])

    async def count(self):
        """Async cout objects in qs."""
        if self._distinct or self._limits:
            return await self._count_subquery()

        conditions = (self._where_q & self._prewhere_q).to_sql(self._model_cls)
        return await self._database.count(self._model_cls, conditions)

    async def paginate(self, page_num=1, page_size=100):
        """
        Returns a single page of model instances that match the queryset.
        Note that `order_by` should be used first, to ensure a correct
        partitioning of records into pages.

        - `page_num`: the page number (1-based), or -1 to get the last page.
        - `page_size`: number of records to return per page.

        The result is a dataclass containing `objects`, `total_objects`,
        `total_pages`.
        """
        count = await self.count()
        pages_total = int(ceil(count / float(page_size)))
        if page_num == -1:
            page_num = pages_total
        if page_num < 1:
            raise ValueError('Invalid page number: %d' % page_num)
        start = (page_num - 1) * page_size
        end = start + page_size
        return Page(
            objects=await self[start:end].execute(),
            total_objects=count,
            total_pages=pages_total,
        )


class AsyncAggregateQuerySet(AsyncCountMixin, AggregateQuerySet):
    async def execute(self):
        return await self._database.select(self.as_sql())

    async def count(self):
        return await self._count_subquery()


class AsyncQuerySet(AsyncCountMixin, QuerySet):
    async def execute(self):
        return await self._database.select(self.as_sql(), self._model_cls)

    def aggregate(self, *args, **kwargs):
        """
        Returns an `AggregateQuerySet` over this query, with `args` serving as
        grouping fields and `kwargs` serving as calculated fields. At least one
        calculated field is required. For example:
        ```
            await Event.objects_in(database).filter(
                date__gt='2017-08-01').aggregate('event_type', count='count()')
        ```
        is equivalent to:
        ```
            SELECT event_type, count() AS count FROM event
            WHERE data > '2017-08-01'
            GROUP BY event_type
        ```
        """
        return AsyncAggregateQuerySet(self, args, kwargs)


