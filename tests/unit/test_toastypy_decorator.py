import unittest
from src.toastypy.toastypy import toasty


def test_toasty_warming():
    def to_be_decorated():
        pass

    decorated_func = toasty(to_be_decorated)
    decorated_func({"type": "toasty"}, {})


def test_toasty_real_invocation():
    def to_be_decorated():
        pass

    decorated_func = toasty(to_be_decorated)
    decorated_func({"type": "toasty"}, {})
