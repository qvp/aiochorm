# aiochorm
Async ClickHouse ORM. Based on [infi.clickhouse_orm](https://github.com/Infinidat/infi.clickhouse_orm) and [aioch](https://github.com/mymarilyn/aioch).


## Installation
To install, simply use pip
```
pip install aiochorm
```

## Create the model

```python
from aiochorm.models import Model
from aiochorm.fields import *
from aiochorm.engines import Memory


class EventLog(Model):
    timestamp = DateTimeField()
    device = StringField()
    status = UInt8Field()

    engine = Memory()
```

## Migrations
Note: migrations makes in sync mode.
```python
from aiochorm.database import Database

db = Database(
    db_name='example',
    db_url='http://localhost:8123/')

db.create_table(EventLog)
```

## Async example
```python
import json

from aiohttp import web
from aiochorm.database import AsyncDatabase
from aiochorm import utils

db = AsyncDatabase(
    db_name='example',
    db_host='localhost',
    db_port=9000,
)


async def handle(request):
    queryset = EventLog.objects_in_async(db)

    if request.path == '/':
        queryset = queryset.filter(status=STATUS_NEW)

    events = await queryset.execute()
    return web.json_response(text=json.dumps(events, cls=utils.JSONEncoder))


app = web.Application()
app.add_routes([
    web.get('/', handle),
])

web.run_app(app)
```

API aiochorm almost completely matches the infi.clickhouse_orm, with the exception of asynchronous capabilities.

To learn more please visit the [documentation](https://github.com/Infinidat/infi.clickhouse_orm/blob/develop/docs/toc.md).
