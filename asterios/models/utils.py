from contextlib import contextmanager
from datetime import datetime


class UTCNow():
    """
    Factory that build a callable returning the utc time.

    You can change the returning value using the patch method.

    >>> utcnow = UTCNow()
    >>> with utcnow.patch(datetime(2018, 7, 29, 9, 0)):
    ...    utcnow()
    datetime.datetime(2018, 7, 29, 9, 0)
    """

    def __init__(self):
        self.mocked = None

    def __call__(self):
        if self.mocked is None:
            return datetime.utcnow()
        return self.mocked

    @contextmanager
    def patch(self, return_value):
        """
        Change the returned value when object is called.
        """
        self.mocked = return_value
        yield
        self.mocked = None


utcnow = UTCNow()
