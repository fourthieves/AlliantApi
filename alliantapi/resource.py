from .client import Client, get_system_layers, get_application_layers
from.parameters import ResourceParameters, CollectionParameters
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

    def lookup_user_x_guid_with_filter(self, tc_number: str, filter_field: str, filter_value: str) -> str:
        """
        Resource method to provide a fast route to getting a GUID for a tracnsaction characteristic based on an Id
        or description

        :param tc_number: the number relating to the TC being referenced. 1-20
        :type tc_number: str
        :param filter_field: field to filter on
        :type filter_field: str
        :param filter_value: value of the filter
        :type filter_value: str
        :return: GUID
        :rtype: str
        """

        collection_parameters = CollectionParameters(
            verbosity='minimal',
            filter_field=filter_field,
            filter_value=filter_value,
            filter_operator='eq'
        )

        response = self.lookup_user_x_collection(tc_number, collection_parameters=collection_parameters)

        return response.guids[0]

    def lookup_adjustment_guid_with_filter(self, filter_field: str, filter_value: str) -> str:
        """

        :param filter_field: field to filter on
        :type filter_field: str
        :param filter_value: value of the filter
        :type filter_value: str
        :return: GUID
        :rtype: str
        """

        collection_parameters = CollectionParameters(
            verbosity='minimal',
            filter_field=filter_field,
            filter_value=filter_value,
            filter_operator='eq'
        )

        response = self.lookup_adjustment_collection(collection_parameters=collection_parameters)

        return response.guids[0]

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
