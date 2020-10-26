import math

from .utils import str_to_datetime


__all__ = [
    'IntervalReading',
    'Bill'
]


class IntervalReading(object):
    def __init__(self, interval_start: str, interval_end: str, total_consumption: int):
        self.total_consumption = total_consumption
        self.interval_start = str_to_datetime(interval_start)
        self.interval_end = str_to_datetime(interval_end)
        self.interval_days = (self.interval_end - self.interval_start).days + 1   # count the last day too
        self.avg_consumption = 0 if self.interval_days == 0 else math.ceil(self.total_consumption / self.interval_days)

    def to_dict(self) -> dict:
        return {
            'interval_start': str(self.interval_start.date()),
            'interval_end': str(self.interval_end.date()),
            'interval_days': self.interval_days,
            'total_consumption': self.total_consumption,
            'mean_consumption': self.avg_consumption
        }

    def __eq__(self, other: 'IntervalReading'):
        return (
            self.interval_start == other.interval_start,
            self.interval_end == other.interval_end,
            self.total_consumption == other.total_consumption
        )

    def __str__(self):
        return f'<IntervalReading ' \
               f'start={str(self.interval_start.date())},' \
               f'end={self.interval_end.date()},' \
               f'consumption={self.total_consumption}>'

    def __repr__(self):
        return self.__str__()

########################################################################################################################


class Bill(object):
    def __init__(self, number: int, due_date: str, amount: float, is_payed: bool, params: dict):
        self.number = number
        self.due_date = str_to_datetime(due_date)
        self.amount = amount
        self.is_payed = is_payed
        self.params = params

    @property
    def document_name(self) -> str:
        return f'bill_{str(self.due_date.date())}.pdf'

    def to_dict(self) -> dict:
        return {
            'number': self.number,
            'due_date': str(self.due_date.date()),
            'amount': self.amount,
            'is_payed': self.is_payed
        }

    def __str__(self):
        return f'<Bill ' \
               f'number={str(self.number)},' \
               f'due_date={str(self.due_date.date())},' \
               f'amount={str(self.amount)},' \
               f'is_payed={str(self.is_payed)}>'

    def __repr__(self):
        return self.__str__()
