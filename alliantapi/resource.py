from .client import Client, get_system_layers, get_application_layers
from.parameters import ResourceParameters, CollectionParameters
from .alliant_api_response import AlliantApiResponse, Contract
import logging


class AlliantApi(Client):

    def __init__(self, base_url: str, user_id: str = None, password: str = None, system_layer_key: str = None,
                 application_layer: str = None,
                 number_of_retries: int = 3,
                 retry_delay: int = 3,
                 retry_backoff: int = 2,
                 database_server: str = None,
                 database_username: str = None,
                 database_password: str = None
                 ):

        super().__init__(base_url, user_id, password, system_layer_key, application_layer, number_of_retries,
                         retry_delay, retry_backoff)

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
        Resource method to provide a fast route to getting a GUID for a transaction characteristic based on an Id
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

    def complete_and_approve_contract(self, guid: str, approve_message: str) -> Contract:
        """
        Takes a contract through the complete and approval stages of contract lifecycle

        :param guid: the guid for the resource you are referencing
        :type guid: str
        :param approve_message: The approval message to be used
        :type approve_message: str
        :return: AlliantApiResponse
        :rtype: AlliantApiResponse
        """

        response = self.lookup_contract(guid)
        contract_id = response.result['id']
        logging.info(f"{contract_id} initial contract status is {response.contract_status}")

        if response.contract_status in ('In Revision', 'In Setup'):
            self.contract_action(guid, 'complete')
            response = self.lookup_contract(guid)

        if response.contract_status  == 'Complete':
            response = self.contract_action(guid, 'approve', approve_message)
            if response:
                response = self.lookup_contract(guid)

        logging.info(f"{contract_id} final contract status is {response.contract_status}")
        return response

    def complete_approve_post_adjustment(self, guid: str, approve_message: str) -> AlliantApiResponse:
        """
        Takes an adjustment through the complete, approval, and posting stages of contract lifecycle

        :param guid: the guid for the resource you are referencing
        :type guid: str
        :param approve_message: The approval message to be used
        :type approve_message: str
        :return: AlliantApiResponse
        :rtype: AlliantApiResponse
        """

        response = self.lookup_adjustment(guid)
        adjustment_descr = response.result['description']
        logging.info(f"{adjustment_descr} initial adjustment status is {response.adjustment_status}")

        if response.adjustment_status in ('In Setup'):
            self.adjustment_action(guid, 'complete')
            response = self.lookup_adjustment(guid)

        if response.adjustment_status  == 'Complete':
            response = self.adjustment_action(guid, 'approve', approve_message)
            if response:
                response = self.lookup_adjustment(guid)

        if response.adjustment_status  == 'Approved':
            response = self.adjustment_action(guid, 'post', approve_message)
            if response:
                response = self.lookup_adjustment(guid)

        logging.info(f"{adjustment_descr} final adjustment status is {response.adjustment_status}")
        return response