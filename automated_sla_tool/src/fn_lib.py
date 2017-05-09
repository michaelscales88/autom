from datetime import timedelta


class FnLib(object):
    def __getitem__(self, item):
        try:
            return getattr(FnLib, item)
        except AttributeError:
            print('No item found FnLib')

    # These are fn

    @staticmethod
    def get_min(sheet, column=None):
        return min(sheet.column[column])

    @staticmethod
    def get_max(sheet, column=None):
        return max(sheet.column[column])

    @staticmethod
    def get(sheet, row=None, column=None):
        try:
            return sheet[row, column]
        except ValueError:
            return sheet[int(row), column]

    @staticmethod
    def get_sum(sheet, column=None):
        return sum([item for item in sheet.column[column] if isinstance(item, timedelta)],
                   timedelta(0))

    @staticmethod
    def item_in(sheet, item=None, column=None, rtn_val=True):
        return rtn_val if item in sheet.column[column] else False

    @staticmethod
    def corr_sum(sheet, key_col=None, match_col=None, key_val=None):
        return sum(
            [matched_item[1] for matched_item in zip(sheet.column[key_col], sheet.column[match_col])
             if matched_item[0] == key_val],
            timedelta(0)
        )

    # These are behaviors

    @staticmethod
    def phone_number(mixed_string):
        only_digits = [ch for ch in str(mixed_string) if ch.isdigit()]
        try:
            return int(
                str(
                    ''.join(
                        only_digits[1:]
                        if len(only_digits) > 7 and only_digits[0] == 1
                        else only_digits
                    )
                )
            )
        except ValueError:
            return None

    @staticmethod
    def custom_voicemail():
        pass
