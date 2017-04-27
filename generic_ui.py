from automated_sla_tool.src.GenericUi import GenericUi as Ui
from automated_sla_tool.src.SlaReport import SlaReport

from sys import argv
from datetime import datetime, timedelta


def when_to_when():
    print('Start')
    start = datetime.now().date().replace(year=int(input('Year?')), month=int(input('Month?')), day=int(input('Day?')))
    print('End')
    end = datetime.now().date().replace(year=int(input('Year?')), month=int(input('Month?')), day=int(input('Day?')))
    while start <= end:
        my_ui = Ui()
        my_obj = SlaReport(report_date=start)
        my_ui.object = my_obj
        my_ui.run()
        start += timedelta(days=1)


def manual_input():
    my_ui = Ui()
    my_obj = SlaReport()
    my_ui.object = my_obj
    my_ui.run()


def main(report_date=None):
    if report_date:
        my_ui = Ui()
        my_obj = SlaReport(report_date=report_date)
        my_ui.object = my_obj
        my_ui.run()
    else:
        when_to_when()
        # manual_input()


if __name__ == '__main__':
    # main(datetime.today().date().replace(year=int(input('Year?')), month=int(input('Month?')), day=int(input('Day?'))))
    main()
else:
    main(argv[1:])
    # main(datetime.date().replace(year=int(input('Year?')), month=int(input('Month?')), day=int(input('Day?'))))
