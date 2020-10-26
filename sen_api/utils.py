from datetime import datetime


def str_to_datetime(str_date) -> datetime:
    return datetime.strptime(str_date, '%d/%m/%Y')

########################################################################################################################

