import alliantapi
import pyodbc  # This example utilises pyodbc to fetch list data utilising SQL
import logging
import concurrent.futures
import time
import datetime
from pathlib import Path

logging.basicConfig(
    filename=f"{Path(__file__).stem}.log",
    filemode='a',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


# As we are making calls to an API, this is set up with multi-threading to help with performance
number_of_threads_to_run = 5

# Message for approving the contracts with
approve_message = 'Approved by API script'

base_url = 'http://alliantwebserver/'
server = 'ALLIANT_SQL_SERVER_ADDRESS'
database = 'alt_test'

system_layer = 'default'
application_layer = 'alt_test'


username = 'username'
password = 'username'

connection_string = 'DRIVER={SQL Server};SERVER=' + server \
                    + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password

with open("failed_contracts.txt") as myfile:
    lines = myfile.readlines()
    failed_contracts = [line.rstrip() for line in lines]

print(f"{len(failed_contracts)} errored contracts in the list")

# You can use multiple lists and bring all of the values back to a single python list of dicts
# or just use a single list item
contract_list_descrs = ['Contract List 1']

sql = f"""
SELECT 
c.[unique_identity] as [guid]
,c.[contract_id]
,c.[descr]
,s.[status_id]
FROM [dbo].[x_contract_list_hdr] clh 
INNER JOIN [dbo].[x_contract_list_resolved] clr on clh.contract_list_sid = clr.contract_list_sid
INNER JOIN [dbo].[x_contract] c on clr.contract_sid=c.contract_sid
INNER JOIN [dbo].[c_status] s on c.status_sid = s.status_sid
WHERE s.status_id NOT IN ('APPROVED', 'ACTIVE')
AND clh.descr IN('{"', '".join(contract_list_descrs)}')
"""

print(sql)

cnxn = pyodbc.connect(connection_string)
cursor = cnxn.cursor()
cursor.execute(sql)

columns = [column[0] for column in cursor.description]
contracts = [dict(zip(columns, row)) for row in cursor.fetchall()]

cursor.close()
cnxn.close()

print(f"Full list of contracts is {len(contracts)}")
contracts = [d for d in contracts if d.get('contract_id') not in failed_contracts]
print(f"List of contracts with errors removed is {len(contracts)}")

t_start = time.perf_counter()

work_list_lenth = len(contracts)
remaining_work = work_list_lenth


with alliantapi.AlliantApi(base_url,
                           user_id=username,
                           password=password,
                           system_layer_key=system_layer,
                           application_layer=application_layer,
                           number_of_retries=0
                           ) as aa:

    aa.reset_metadata()

    kwargs_list = [{'guid': contract['guid'], 'approve_message': 'Approved by API script'} for contract in contracts]

    with concurrent.futures.ThreadPoolExecutor(5) as executor:

        futures = {executor.submit(aa.complete_and_approve_contract, **kwargs): kwargs for
                   kwargs in kwargs_list}

        for future in concurrent.futures.as_completed(futures):
            result = future.result()

            remaining_work -= 1
            if remaining_work % 100 == 0:
                pct_complete = round(remaining_work / work_list_lenth * 100, 1)
                completed_work = work_list_lenth - remaining_work
                t_current = time.perf_counter()

                elapsed_time = round(t_current - t_start, 0)
                remaining_time = round(elapsed_time / completed_work * remaining_work, 0)

                print('****************************************************************')
                print(f"{remaining_work} ({pct_complete}%) - contracts remaining")
                print(f"{str(datetime.timedelta(seconds=elapsed_time))} time elapsed")
                print(f"{str(datetime.timedelta(seconds=remaining_time))} estimated time remaining")
                print('****************************************************************')

            if result.contract_status == 'In Setup':
                with open("failed_contracts.txt", "a") as myfile:
                    myfile.write(result.result['id'] + "\n")
                    print(result.result['id'], 'Error File updated')
            else:
                print(result.result['id'], result.contract_status)
