from collections import OrderedDict
from uuid import uuid4

from voluptuous import All, Length, Schema

from .errors import DoesntExist


class _MetaModel(type):
    """
    Ensure that `schema` is defined.
    """

    def __init__(cls, name, bases, attrs):  # pylint: disable=unused-argument
        if bases and not isinstance(cls.schema, Schema):
            raise AttributeError('{cls}.schema should be a voluptuous.Schema')


class ModelMixin(metaclass=_MetaModel):
    """
    Create Model objects validated with voluptuous.Schema stored
    in `schema` attribute.
    """

    schema = staticmethod(lambda value: value)

    @classmethod
    def from_dict(cls, values: dict):
        """
        Instantiate a new Model from `values` after validating `values`
        using schema.
        """
        cleaned = cls.schema(values)
        return cls(**cleaned)


def collection(model, min_length=None, max_length=None):
    """
    A collection defines a list of Model in a voluptuous schema.
    """
    return All([model.from_dict], Length(min=min_length, max=max_length))


class Collection:
    """
    Maps items with generated key.
    """

    not_exist_error = DoesntExist

    def __init__(self, iterable=()):
        self._objects = OrderedDict()
        for obj in iterable:
            self.append(obj)

    def generate_id(self, obj):
        """
        Generate a new key to map with item durring
        the append calling.
        """
        # pylint: disable=unused-argument, no-self-use
        # We keep this signature for subclass.
        return uuid4()

    def has_id(self, key):
        """
        Check if key is in collection.
        """
        return key in self._objects

    def delete(self, key):
        """
        remove an item from key
        """
        try:
            del self._objects[key]
        except KeyError:
            raise self.not_exist_error(key) from None

    def get_first_from_value(self, field, value):
        """
        Return the first item with item.field=value.
        """
        try:
            return next((item
                         for item in self
                         if getattr(item, field) == value))
        except StopIteration:
            raise self.not_exist_error(field, value) from None

    def append(self, obj):
        """
        Add an item to the collecton.
        """
        new_id = self.generate_id(obj)
        self._objects[new_id] = obj
        return new_id

    def clear(self):
        """
        Clear the collection.
        """
        self._objects.clear()

    def __getitem__(self, key):
        """
        Return the item mapped with key `key`.
        If the collection doesn't have the item it raises the error in
        `not_exist_error` attribute.
        """
        try:
            return self._objects[key]
        except KeyError:
            raise self.not_exist_error(key) from None

    def __iter__(self):
        return iter(self._objects.values())

    def __repr__(self):
        return repr(self._objects)
