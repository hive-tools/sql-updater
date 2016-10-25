import re


class Parser(object):
    def parse(self, value):
        raise Exception("parse method not implemented")


class HiveDatabaseParser(Parser):
    def parse(self, value):
        regex = "[EXISTS|TABLE|table|exists][\s]+([a-zA-Z0-9_`?]+\.[" \
                "a-z-A-Z0-9_`?]+)"
        items = re.findall(regex, value)

        if len(items) == 0:
            raise ValueError("No table or database found")

        return items[0].split('.')
