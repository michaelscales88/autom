from automated_sla_tool.bin.generic_ui import main
from automated_sla_tool.src.utilities import valid_dt


if __name__ == "__main__":
    from sys import argv
    main(report_date=valid_dt(argv[1]) if len(argv) > 1 else None)
else:
    print('entered else')
