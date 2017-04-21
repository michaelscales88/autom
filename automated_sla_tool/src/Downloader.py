from re import search, M, I, DOTALL


from automated_sla_tool.src.ImapConnection import ImapConnection
from automated_sla_tool.src.utilities import valid_dt, valid_phone_number


class Downloader(ImapConnection):
    @staticmethod
    def lexer(full_string, pivot):  # create settings option which creates an OrdDict that executes instructions
        if full_string:
            search_object = search('\(([^()]+)\)', full_string, M | I | DOTALL)
            try:
                val1, val2 = search_object.groups()[0].split(pivot)
            except AttributeError:
                val1 = val2 = False
            return val1, val2

    def get_f_list(self, on, f_list):
        matched_f_list = {}
        ids = super().get_ids(on, 'FROM "Chronicall Reports"')
        for f in f_list:
            matched_f_list[f] = ids.get(f, None)
        return matched_f_list

    def get_vm(self, on):
        payload = {}
        ids = super().get_ids(on, 'FROM "vmpro@mindwireless.com"')
        for k, v in ids.items():
            phone_number, client_name = self.lexer(v.pop('subject', None), pivot=' > ')
            if client_name:
                client_data = payload.get(client_name, [])
                a_vm = {
                    'phone_number': valid_phone_number(phone_number),
                    'time': valid_dt(v['dt'])
                }
                client_data.append(a_vm)
                payload[client_name] = client_data
        return payload
