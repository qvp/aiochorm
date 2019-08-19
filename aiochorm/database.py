import pytz

from aioch import Client
from infi.clickhouse_orm.models import ModelBase
from infi.clickhouse_orm.database import Database, Page, DatabaseException, ServerError


class AsyncDatabase(Database):
    def __init__(self, db_name='default', db_host='127.0.0.1', db_port='9000',
                 username='default', password='', timeout=60):
        self.db_name = db_name
        self.db_host = db_host
        self.readonly = False
        self.timeout = timeout
        self.client = Client(host=db_host, port=db_port, database=db_name, user=username, password=password)
        self.settings = {}
        self.db_exists = False
        self.server_timezone = pytz.utc

    async def raw(self, query, settings=None, stream=False):
        '''
        Performs a query and returns its output as text.

        - `query`: the SQL query to execute.
        - `settings`: query settings to send as HTTP GET parameters
        - `stream`: if true, the HTTP response from ClickHouse will be streamed.
        '''
        query = self._substitute(query, None)
        return await self._send(query, settings=settings, stream=stream)

    async def count(self, model_class, conditions=None):
        '''
        Counts the number of records in the model's table.

        - `model_class`: the model to count.
        - `conditions`: optional SQL conditions (contents of the WHERE clause).
        '''
        query = 'SELECT count() FROM $table'
        if conditions:
            query += ' WHERE ' + conditions
        query = self._substitute(query, model_class)
        r = await self._send(query)
        return int(r[0][0])

    async def select(self, query, model_class=None, settings=None):
        '''
        Performs a query and returns a generator of model instances.

        - `query`: the SQL query to execute.
        - `model_class`: the model class matching the query's table,
          or `None` for getting back instances of an ad-hoc model.
        - `settings`: query settings to send as HTTP GET parameters
        '''
        query = self._substitute(query, model_class)
        lines, columns = await self._send(query, settings, with_column_types=True)
        field_names = [c[0] for c in columns]
        field_types = [c[1] for c in columns]
        model_class = model_class or ModelBase.create_ad_hoc_model(zip(field_names, field_types))
        return [model_class.from_list(line, field_names, self.server_timezone, self) for line in lines if line]

    async def _send(self, data, settings=None, stream=False, with_column_types=False):
        return await self.client.execute(data, settings, with_column_types=with_column_types)

    async def insert_async(self, model_instances, batch_size=1000):
        '''
        Insert records into the database.

        - `model_instances`: any iterable containing instances of a single model class.
        - `batch_size`: number of records to send per chunk (use a lower number if your records are very large).
        '''
        from six import next
        i = iter(model_instances)
        try:
            first_instance = next(i)
        except StopIteration:
            return  # model_instances is empty
        first_instance.set_database(self)
        model_class = first_instance.__class__

        if first_instance.is_read_only() or first_instance.is_system_model():
            raise DatabaseException("You can't insert into read only and system tables")

        fields_list = ','.join(
            ['`%s`' % name for name in first_instance.fields(writable=True)])

        def gen():
            values = list()
            values.append(first_instance.to_dict(include_readonly=False))
            # Collect lines in batches of batch_size
            lines = 2
            for instance in i:
                instance.set_database(self)
                values.append(instance.to_dict(include_readonly=False))
                lines += 1
                if lines >= batch_size:
                    # Return the current batch of lines
                    yield values
                    # Start a new batch
                    values = list()
                    lines = 0
            # Return any remaining lines in partial batch
            if lines:
                yield values

        for butch in gen():
            query = self._substitute('INSERT INTO $table (%s) VALUES ' % fields_list, model_class)
            await self._send(query, settings=butch)
