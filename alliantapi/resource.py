from .client import Client, get_system_layers, get_application_layers
import logging


class AlliantApi(Client):

    def __init__(self, base_url, user_id=None, password=None, system_layer_key=None, application_layer=None,
                 database_server=None, database_username=None, database_password=None):

        super().__init__(base_url, user_id, password, system_layer_key, application_layer)

        self.database_server = database_server
        self.database_username = database_username
        self.database_password = database_password

    def __enter__(self):
        super().login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().logout()
        return

    def process_contract_deletion(self, guid):

        response = super().lookup_contract(guid)
        print(guid, response.contract_status)
        if response.contract_status == 'Active':
            super().contract_action(guid, 'revise')
            response = super().lookup_contract(guid)
            logging.info(response.contract_status)

        if response.contract_status in ('In Revision', 'In Setup', 'Prior Revision'):
            response = super().delete_contract(guid)
            print(response.status_code, response.result)
            if response.status_code == 200:
                return f"{guid} - Successfully deleted"
            else:
                return f"{guid} - Error - {response.errors}"

        return f"{guid} - {response.contract_status} not deleted"
