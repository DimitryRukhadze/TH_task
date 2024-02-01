from django.db import connection
from django.utils.encoding import force_str
from functools import reduce, wraps
import logging


def log_queries(func):
    @wraps(func)
    def modified_func(*args, **kwargs):
        def force_queries(queries):
            return [{"sql": force_str(query["sql"]), "time": query["time"]} for query in queries]

        result = func(*args, **kwargs)

        logging.basicConfig("SQLlogging.log", level=logging.DEBUG)
        queries = connection.queries

        logging.info("db queries log for %s:\n" % (func.__name__))

        for query in force_queries(queries):
            logging.info(f"Query: {query['sql']}")
            logging.info(f"Query time: {query['time']}")

        logging.info("TOTAL QUERIES: %s" % len(queries))
        logging.info("TOTAL TIME:  %s\n" % reduce(lambda x, y: x + float(y["time"]), queries,))

        return result
    return modified_func


class DbQueryLogger(object):
    def __init__(self, get_response):
        self.get_response = get_response
        self.handler_info = {}

    def process_view(self, request, view_func, view_args, view_kwargs):
        self.handler_info["func_name"] = f"{view_func}"

    def modified_func(self, *args, **kwargs):
        result = self.get_response(*args, **kwargs)
        logging.basicConfig(filename="SQLlog.log", level=logging.DEBUG)

        logging.info("db queries log for %s:\n" % (self.handler_info.get("func_name")))

        for q in connection.queries:
            logging.info(f"Query: {q['sql']}")
            logging.info(f"Query time: {q['time']}")

        logging.info("TOTAL QUERIES: %s" % len(connection.queries))
        logging.info("TOTAL TIME:  %s\n" % reduce(lambda x, y: x + float(y["time"]), connection.queries, 0.0))

        return result

    def __call__(self, request):
        response = self.modified_func(request)
        return response
