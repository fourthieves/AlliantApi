import alliantapi
import pyodbc  # This example utilises pyodbc to fetch list data utilising SQL
import logging
import concurrent.futures


logging.basicConfig(
    level=logging.INFO,
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


# You can use multiple lists and bring all of the values back to a single python list of dicts
# or just use a single list item
contract_list_descrs = ['Contract List 1']
adjustment_types_to_include = []


sql = f"""
  SELECT distinct c.contract_id
  ,ah.unique_identity as adj_guid
  ,ah.adjustment_sid
  ,ah.descr as adjustment_description
  ,status_id
  FROM [dbo].[x_adjustment_hdr] ah
  INNER JOIN [dbo].[c_context_element] ce on ah.context_element_sid = ce.context_element_sid
  INNER JOIN [dbo].[x_contract] c on ah.item_sid = c.contract_sid
  INNER JOIN [dbo].[c_adjustment_type_hdr] ath on ah.adjustment_type_sid = ath.adjustment_type_sid
  INNER JOIN [dbo].[x_contract_list_resolved] clr on clr.contract_sid = c.contract_sid
  INNER JOIN [dbo].[x_contract_list_hdr] clh on clh.contract_list_sid = clr.contract_list_sid
  INNER JOIN [dbo].[c_status] s on ah.status_sid = s.status_sid
  WHERE ce.context_column_name = 'contract_sid'
  AND ath.adjustment_type_id IN('{"', '".join(adjustment_types_to_include)}')
  AND clh.descr IN('{"', '".join(contract_list_descrs)}')
  AND status_id NOT IN('POSTED')
"""

print(sql)

cnxn = pyodbc.connect(connection_string)
cursor = cnxn.cursor()
cursor.execute(sql)

columns = [column[0] for column in cursor.description]
adjustments = [dict(zip(columns, row)) for row in cursor.fetchall()]

cursor.close()
cnxn.close()

with alliantapi.AlliantApi(base_url,
                           user_id=username,
                           password=password,
                           system_layer_key=system_layer,
                           application_layer=application_layer,
                           ) as aa:

    # This produces 409 errors for contracts that can't be completed and retries won't help
    # aa.error_codes_to_retry.remove(409)

    kwargs_list = [{'guid': adjustment['adj_guid'], 'approve_message': approve_message} for adjustment in adjustments]

    print(len(kwargs_list))

    with concurrent.futures.ThreadPoolExecutor(number_of_threads_to_run) as executor:

        futures = {executor.submit(aa.complete_approve_post_adjustment, **kwargs): kwargs for
                   kwargs in kwargs_list}

        for future in concurrent.futures.as_completed(futures):
            future.result()
