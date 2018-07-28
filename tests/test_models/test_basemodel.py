import unittest
from asterios.models.basemodel import *

from voluptuous import Schema, Invalid


class Model(ModelMixin):
    schema = Schema({
        'a1': int,
        'a2': str
    })

    def __init__(self, a1, a2):
        self.a1 = a1
        self.a2 = a2



class TestModel(unittest.TestCase):

    def test_from_dict_method_should_validate_input_using_schema(self):
        input_date = {'a1': 3, 'a2': 3}

        with self.assertRaises(Invalid) as exc_ctx:
            Model.from_dict(input_date)
        
        self.assertEqual(
            str(exc_ctx.exception), 
            "expected str for dictionary value @ data['a2']")

    def test_from_dict_method_should_instantiate_a_model(self):
        input_date = {'a1': 3, 'a2': 'c'}

        a_object = Model.from_dict(input_date)
        
        self.assertIsInstance(a_object, Model)
        self.assertEqual(a_object.a1, 3)
        self.assertEqual(a_object.a2, 'c')
  


class TestCollectionFunction(unittest.TestCase):

    def setUp(self):
        self.schema = Schema(collection(Model, min_length=1, max_length=2))
        self.cleaned = self.schema([{'a1': 3, 'a2': 'toto'}])

    def test_cleaned_should_be_a_list(self):
        self.assertIsInstance(self.cleaned, list)

    def test_cleaned_should_contain_a_model_instance(self):
        obj = self.cleaned[0]
        self.assertIsInstance(obj, Model)
        self.assertEqual(obj.a1, 3)
        self.assertEqual(obj.a2, 'toto')

    def test_schema_should_raise_if_length_is_greater_than_2(self):
        with self.assertRaises(Invalid) as exc_ctx:
            self.schema([{'a1': 3, 'a2': 'toto'}] * 3)

    def test_schema_should_raise_if_length_is_lower_than_1(self):
        with self.assertRaises(Invalid) as exc_ctx:
            self.schema([])


