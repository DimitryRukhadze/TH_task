from django.db import connection
from functools import reduce


class DbQueryLogger(object):
    def __init__(self, get_response):
        self.get_response = get_response
        self.handler_info = {}

    def process_view(self, request, view_func, view_args, view_kwargs):
        self.handler_info["func_name"] = f"{view_func.__name__}, {view_func.__module__}"

    def modified_func(self, *args, **kwargs):
        result = self.get_response(*args, **kwargs)
        print("db queries log for %s:\n" % (self.handler_info["func_name"]))
        for q in connection.queries:
            print("Query: ", q["sql"])
            print("Query time: ", q["time"])
        print("TOTAL QUERIES: %s" % len(connection.queries))
        print("TOTAL TIME:  %s\n" % reduce(lambda x, y: x + float(y["time"]), connection.queries, 0.0))
        return result

    def __call__(self, request):
        response = self.modified_func(request)
        return response
