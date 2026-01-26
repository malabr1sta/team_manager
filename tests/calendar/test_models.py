from datetime import datetime


class TestCalendar:

    def test_events_for_day_returns_only_not_cancelled(self, calendar):
        date = datetime(2026, 1, 10)

        result = calendar.events_for_day(date)

        assert len(result) == 1
        assert result[0]._title == "Event 1"

    def test_events_for_day_empty_if_no_events(self, calendar):
        date = datetime(2026, 1, 20)

        result = calendar.events_for_day(date)

        assert result == []

    def test_events_for_month_returns_only_month_events(self, calendar):
        result = calendar.events_for_month(2026, 1)

        assert len(result) == 2
        titles = {e._title for e in result}
        assert titles == {"Event 1", "Event 3"}

    def test_events_for_month_excludes_cancelled(self, calendar):
        result = calendar.events_for_month(2026, 1)

        assert all(not e._cancelled for e in result)
