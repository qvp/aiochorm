import json
import datetime

from infi.clickhouse_orm.utils import (SPECIAL_CHARS, SPECIAL_CHARS_REGEX, escape, unescape, parse_tsv, parse_array,
                                       import_submodules, comma_join)
from .models import Model


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Model):
            return obj.to_dict()
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)
