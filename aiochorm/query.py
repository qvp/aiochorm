from infi.clickhouse_orm.query import (Operator, SimpleOperator, InOperator, LikeOperator, IExactOperator,
                                       NotOperator, BetweenOperator, register_operator, FOV, Q, QuerySet,
                                       AggregateQuerySet)


class AsyncQuerySet(QuerySet):
    async def execute(self):
        return await self._database.select(self.as_sql(), self._model_cls)

    async def count(self):
        if self._distinct or self._limits:
            sql = u'SELECT count() FROM (%s)' % self.as_sql()
            raw = await self._database.raw(sql)
            return int(raw[0][0])
        conditions = (self._where_q & self._prewhere_q).to_sql(self._model_cls)
        return await self._database.count(self._model_cls, conditions)
