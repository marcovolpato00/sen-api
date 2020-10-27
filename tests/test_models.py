from sen_api import IntervalReading


def test_interval_reading():
    reading = IntervalReading('01/10/2020', '04/10/2020', 55)
    assert reading.interval_days == 4
    assert reading.avg_consumption == 14

    reading = IntervalReading('01/03/2020', '31/03/2020', 341)
    assert reading.interval_days == 31
    assert reading.avg_consumption == 11

    assert IntervalReading('01/03/2020', '31/03/2020', 341) == reading
