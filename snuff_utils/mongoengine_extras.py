import datetime
import six
from mongoengine import StringField
from mongoengine.base import BaseField, get_document as get_model


class TimeField(StringField):
    """Time field.

    Note: Microseconds are rounded to the nearest millisecond.
      Pre UTC microsecond support is effectively broken.
      Use :class:`~mongoengine.fields.ComplexDateTimeField` if you
      need accurate microsecond support.
    """

    def validate(self, value):
        if not isinstance(value, datetime.time):
            self.error('cannot parse time "%s"' % repr(value))
        new_value = self.to_mongo(value)
        if not isinstance(new_value, six.string_types):
            self.error('cannot parse time "%s"' % repr(value))

    def to_mongo(self, value):
        if value is None:
            return value

        if isinstance(value, datetime.time):
            value = value
        elif callable(value):
            value = value()
        elif isinstance(value, six.string_types):
            value = self._parse_datetime(value)
        else:
            return None

        zone = "%z" if value.tzinfo else ""
        microseconds = ".%f" if value.microsecond else ""
        seconds = ":%S" if value.second else ""
        return value.strftime(f"%H:%M{seconds}{microseconds}{zone}")

    def to_python(self, value):
        return self._parse_datetime(value)

    @staticmethod
    def _parse_datetime(value):
        # Attempt to parse a time from a string
        value = value.strip()
        if not value:
            return None

        formats = [
            "%H:%M:%S.%f%z",
            "%H:%M:%S.%f",
            "%H:%M:%S%z",
            "%H:%M.%f%z",
            "%H:%M.%f",
            "%H:%M%z",
            "%H:%M:%S.%f %Z",
            "%H:%M:%S %Z",
            "%H:%M.%f %Z",
            "%H:%M %Z",
            "%H:%M:%S.%f%Z",
            "%H:%M:%S%Z",
            "%H:%M.%f%Z",
            "%H:%M%Z",
        ]
        for frmt in formats:
            try:
                value = datetime.datetime.strptime(value, frmt)
            except ValueError:
                continue
            break
        else:
            return None
        return datetime.time(value.hour, value.minute, value.second, value.microsecond, tzinfo=value.tzinfo)

    def prepare_query_value(self, op, value):
        return super().prepare_query_value(op, self.to_mongo(value))
