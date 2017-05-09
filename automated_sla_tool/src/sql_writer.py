import pypyodbc as ps
from automated_sla_tool.src.query_writer import QueryWriter
from datetime import timedelta


class SqlWriter(QueryWriter):

    def get_conn(self):
        return ps.connect(self.conn_string)

    def replicate_to(self, dest_conn=None, sql_commands=()):
        if dest_conn:
            for sql_command in sql_commands:
                columns, data = self.get_data(sql_command.cmd)
                data.name = sql_command.name
                dest_conn.copy_tables(columns, data)
        else:
            print('No connection to transfer to.')

    def get_db_info(self):
        cursor1 = self._conn.cursor()
        cursor2 = self._conn.cursor()

        for i, rows in enumerate(cursor1.tables()):
            if rows['table_type'] == "TABLE":
                print('{i}: {row}'.format(i=i, row=rows['table_name']))
                for fld in cursor2.columns(rows['table_name']):
                    print(fld['table_name'], fld['column_name'])

    def dict_command(self):
        for call_id, call_details in super().group('call_id').items():
            print(call_id)
            duration = timedelta(0)
            for call_detail in call_details:
                print(call_detail)
                diff = call_detail['end_time'] - call_detail['start_time']
                print(diff)
                duration += diff
            print(duration)

    def simple_query(self):
        # TODO Fix error: malformed results. Sample that breaks below
        # Issue seems to be with joining tables with matching field names
        '''
        Select Distinct c_call.call_id, c_event.event_id, *
        From c_event
        Inner Join c_call on c_event.call_id = c_call.call_id
        where to_char(c_call.start_time, 'YYYY-MM-DD') = '2017-03-06' and
        c_call.call_direction = 1
        Order by c_event.event_id
        '''
        rtn = super().simple_query()
        print(rtn.number_of_columns())
        print(rtn.colnames)
        print(rtn)
