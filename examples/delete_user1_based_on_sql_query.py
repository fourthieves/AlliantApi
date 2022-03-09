import alliantapi
import pyodbc  # This example utilises pyodbc to fetch list data utilising SQL
import logging
import concurrent.futures


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')


# As we are making calls to an API, this is set up with multi-threading to help with performance
number_of_threads_to_run = 10

base_url = 'http://alliantwebserver/'
server = 'ALLIANT_SQL_SERVER_ADDRESS'
database = 'alt_test'

system_layer = 'default'
application_layer = 'alt_test'

username = 'username'
password = 'password'

connection_string = 'DRIVER={SQL Server};SERVER=' + server \
                    + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password

# The SQL below selects the user 1 to be deleted

sql = f"""
SELECT [unique_identity]  , udkey_1_id
  FROM [uv_udkey_1] u1
  where NOT EXISTS (SELECT * FROM [dbo].[uv_posted_history] ph WHERE u1.udkey_1_sid = ph.udkey_1_sid)
  AND udkey_1_id NOT IN('Untitled', 'Unspecified')
"""

print(sql)

cnxn = pyodbc.connect(connection_string)
cursor = cnxn.cursor()
cursor.execute(sql)

columns = [column[0] for column in cursor.description]
items = [dict(zip(columns, row)) for row in cursor.fetchall()]

cursor.close()
cnxn.close()

with alliantapi.AlliantApi(base_url,
                           user_id=username,
                           password=password,
                           system_layer_key=system_layer,
                           application_layer=application_layer,
                           ) as aa:

    # This produces 409 errors for contracts that can't be completed and retries won't help
    aa.error_codes_to_retry.remove(409)

    kwargs_list = [{'tc_number': '1', 'guid': item['unique_identity']} for item in items]

    print(len(kwargs_list))

    with concurrent.futures.ThreadPoolExecutor(number_of_threads_to_run) as executor:

        futures = {executor.submit(aa.delete_user_x, **kwargs): kwargs for
                   kwargs in kwargs_list}

        for future in concurrent.futures.as_completed(futures):
            response = future.result()

            logging.info(f"{response.status_code} - {response.url}")
