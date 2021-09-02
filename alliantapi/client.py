import logging
import time
import requests
from .exceptions import *
from .alliant_api_response import *
from .parameters import CollectionParameters, ResourceParameters

#################################################################################################
#
#   Global functions to support the module
#
#################################################################################################


def _format_base_url(base_url: str) -> str:
    """
    Takes a base url and applies formatting to ensure it is in the expected format

    :param base_url: base_url to format
    :type base_url: str
    :return: a string containing the formatted/normalized base_url
    :rtype: str
    """

    if base_url.endswith('/'):
        base_url = base_url[:-1]

    if not base_url.endswith('api'):
        base_url = base_url + '/api'

    return base_url


def get_system_layers(base_url: str) -> AlliantApiResponse:
    """
    Fetches system layers that are found at the URL.

    :param base_url: base url for the API implementation
    :type base_url: str
    :return: AlliantApiResponse
    :rtype: AlliantApiResponse
    """

    url = _format_base_url(base_url) + '/security/systemLayers'
    response = requests.get(url)

    return AlliantApiResponse(response)


def get_application_layers(base_url: str, system_layer: str) -> AlliantApiResponse:
    """
    Fetches application layers that are found on the system layer at the URL.

    :param base_url: base url for the API implementation
    :type base_url: str
    :param system_layer: The system layer to get application layer from.  System layers can be found with
    get_system_layers()
    :type system_layer: str
    :return: AlliantApiResponse
    :rtype: AlliantApiResponse
    """

    url = _format_base_url(base_url) + f'/security/systemLayers/{system_layer}/applicationLayers'
    response = requests.get(url)

    return AlliantApiResponse(response)


#################################################################################################
#
#   Main API wrapper
#
#################################################################################################


class Client:

    def __init__(self, base_url: str, user_id: str = None, password: str = None, system_layer_key: str = None,
                 application_layer: str = None,
                 number_of_retries: int = 3,
                 retry_delay: int = 3,
                 retry_backoff: int = 2
                 ):
        """

        :param base_url: Base URL for the API
        :type base_url: str
        :param user_id: User Id for login
        :type user_id: str
        :param password: Password for login
        :type password: str
        :param system_layer_key: Value is typically 'default'  This can be found with the helper function
            get_system_layers()
        :type system_layer_key: str
        :param application_layer: This can be found with the helper function get_application_layers()
        :type application_layer: str
        :param number_of_retries: Defaulted to 3. For specified errors, this is the number of times they will be retried
        :type number_of_retries: int
        :param retry_delay: Delay between retries in seconds. Defaulted to 3
        :type retry_delay: int
        :param retry_backoff: Backoff multiplier between retries.  Defaulted to 2
        :type retry_backoff: int
        """

        self.number_of_retries = number_of_retries
        self.retry_delay = retry_delay
        self.retry_backoff = retry_backoff
        self.error_codes_to_retry = [500, 403]

        self.base_url = _format_base_url(base_url)

        self.user_id = user_id
        self.password = password
        self.system_layer_key = system_layer_key
        self.application_layer = application_layer

        self.token = None
        self.token_expires = None
        self.headers = {}
        self.session = requests.Session()

        # URLs
        self.user_x_url_base = self.base_url + f'/data/user'
        self.adjustment_headers_url = self.base_url + '/data/adjustmentHeaders'
        self.contacts_url = self.base_url + '/data/contacts'
        self.contracts_url = self.base_url + '/data/contracts'
        self.metadata_reset = self.base_url + '/metadata/reset'

    def login(self) -> AlliantApiResponse:
        """
        This method logs into Alliant and sets the token value in the class.  It is recommended that you use this class
        with a context manager to ensure sessions are logged out in the event of an error

        :return: AlliantApiResponse
        :rtype: AlliantApiResponse
        """

        login_url = self.base_url + '/security/login'
        response = requests.post(
            login_url,
            params={
                'userId': self.user_id,
                'password': self.password,
                'systemLayer': self.system_layer_key,
                'applicationLayer': self.application_layer
            }
        )

        try:
            self.token = response.json()['result']['token']
            self.token_expires = response.json()['result']['expires']
        except KeyError:
            return AlliantApiResponse(response)

        self.headers['X-AlliantSession'] = self.token

        self.session.headers.update(self.headers)

        logging.info(f"Logged in.  Token = {self.token}")

        return AlliantApiResponse(response)

    def logout(self) -> AlliantApiResponse:
        """
        Logs out of the API session

        :return: AlliantApiResponse
        :rtype: AlliantApiResponse
        """

        logout_url = self.base_url + '/security/logout'

        response = requests.post(
            logout_url,
            headers=self.headers
        )

        logging.info("Logged out")
        return AlliantApiResponse(response)

    def _send_request(self, req) -> requests.Response:
        """
        Handles the sending and retry logic for API calls
        :param req: The request object from Requests
        :type req: requests.Request
        :return: The requests response
        :rtype: requests.Response
        """

        retried_count = 0
        retry_time = self.retry_delay
        prepped = self.session.prepare_request(req)

        response = self.session.send(prepped)

        while response.status_code in self.error_codes_to_retry:
            retried_count += 1
            logging.warning(
                f"Retrying API Call - Attempt {retried_count}\n"
                f"  {response.status_code = }\n"
                f"  {response.request.method = }\n"
                f"  {response.request.url = }\n"
                f"  {response.request.body = }\n"
                f"  {response.text = }\n"
                f"  failed header - {response.request.headers = }\n"
            )

            time.sleep(retry_time)
            self.login()
            time.sleep(1)

            prepped = self.session.prepare_request(req)
            response = self.session.send(prepped)

            if retried_count == self.number_of_retries:
                if response.status_code in self.error_codes_to_retry:
                    logging.error("Finished retrying - call not made successfully\n"
                                  f"  {response.status_code = }\n"
                                  f"  {response.request.method = }\n"
                                  f"  {response.request.url = }\n"
                                  f"  {response.request.body = }\n"
                                  f"  {response.text = }\n"
                                  f"  failed header - {response.request.headers = }\n"
                                  )
                break

            retry_time = retry_time * self.retry_backoff

        return response

    #################################################################################################
    #
    #   TC Methods
    #
    #################################################################################################

    def lookup_user_x_collection(self, tc_number: str,
                                 collection_parameters: CollectionParameters = None) -> Collection:
        """
        Lookup a collection for a Transaction Characteristic.  Supply the number of the TC you would like to interact
        with and and collection parameters you would like applied to the response.

        :param tc_number: the number relating to the TC being referenced. 1-20
        :type tc_number: str
        :param collection_parameters: an instance of the CollectionParameters class that contains the parameters to be
        passed
        :type collection_parameters: CollectionParameters
        :return: Collection
        :rtype: Collection
        """

        user_x_url = self.user_x_url_base + str(tc_number)

        params = collection_parameters.parameter_string()

        req = requests.Request('GET', user_x_url, params=params)

        response = self._send_request(req)

        return Collection(response)

    def lookup_user_x_with_filter(self, tc_number, filter_field, filter_value, verbosity='default') -> Collection:
        # todo: remove this method
        """
        This method is deprecated.  You should now use lookup_user_x_collection and provide it with a
        CollectionParameters object to lookup a user_x value with a filter.

        :param tc_number:
        :type tc_number:
        :param filter_field:
        :type filter_field:
        :param filter_value:
        :type filter_value:
        :param verbosity:
        :type verbosity:
        :return:
        :rtype:
        """
        from warnings import warn
        warn("This method is deprecated.  You should now use lookup_user_x_collection and provide it with a "
             "CollectionParameters object to lookup a user_x value with a filter.")

        user_x_url = self.user_x_url_base + str(tc_number)

        str_id = ResourceParameters._preprocess_filter(str(filter_value))

        params = f"{verbosity}&$filter={filter_field} eq+'{str_id}'"

        req = requests.Request('GET', user_x_url, params=params)

        response = self._send_request(req)

        return Collection(response)

    def lookup_user_x_guid_with_filter(self, tc_number, filter_field, filter_value) -> str:

        response = self.lookup_user_x_with_filter(tc_number, filter_field, filter_value, verbosity='minimal')

        return response.guids[0]

    def lookup_user_x(self, tc_number, guid, verbosity='default') -> AlliantApiResponse:

        user_x_url = self.user_x_url_base + str(tc_number)

        params = verbosity

        req = requests.Request('GET', user_x_url + '/' + guid, params=params)

        response = self._send_request(req)

        return AlliantApiResponse(response)

    def patch_user_x(self, tc_number, guid, body, verbosity='default') -> AlliantApiResponse:

        user_x_url = self.user_x_url_base + str(tc_number) + '/' + guid

        params = verbosity

        req = requests.Request('PUT', user_x_url, json=body, params=params)

        response = self._send_request(req)

        return AlliantApiResponse(response)

    def create_user_x(self, tc_number: str, body: dict, verbosity='default') -> AlliantApiResponse:

        user_x_url = self.user_x_url_base + str(tc_number)

        params = verbosity

        req = requests.Request('POST', user_x_url, json=body, params=params)

        response = self._send_request(req)

        return AlliantApiResponse(response)

    #################################################################################################
    #
    #   Adjustment Methods
    #
    #################################################################################################

    def lookup_adjustment_with_filter(self, filter_field, filter_value, verbosity='default') -> Collection:

        str_id = ResourceParameters._preprocess_filter(str(filter_value))

        params = f"{verbosity}&$filter={filter_field} eq+'{str_id}'"

        req = requests.Request('GET',
                               self.adjustment_headers_url,
                               params=params
                               )

        response = self._send_request(req)

        return Collection(response)

    def lookup_adjustment_guid_with_filter(self, filter_field, filter_value) -> str:

        response = self.lookup_adjustment_with_filter(filter_field, filter_value, verbosity='minimal')

        return response.guids[0]

    def lookup_adjustment(self, guid, verbosity='default') -> Adjustment:

        params = verbosity

        req = requests.Request('GET',
                               self.adjustment_headers_url + '/' + guid,
                               params=params
                               )

        response = self._send_request(req)

        return Adjustment(response)

    def delete_adjustment(self, guid):

        req = requests.Request('DELETE',
                               self.adjustment_headers_url + '/' + guid,
                               )

        response = self._send_request(req)

        return AlliantApiResponse(response)

    def adjustment_action(self, guid: str, action: str, comment: str = None) -> AlliantApiResponse:
        """

        :param guid: This is the guid of the resource
        :param action: The action to be performed.  available actions are: approve, clear, clearRequest, copy,
            insetup, post
        :param comment: some of the actions require a comment, if required, this should be entered here.
        :return:
        """

        available_actions = ['approve', 'clear', 'clearRequest', 'copy', 'insetup', 'post', 'complete']
        actions_requiring_comment = ['approve', 'clearRequest']

        if action not in available_actions:
            raise ActionNotImplemented(
                f"The action '{action}' is not implemented.  Available actions are {available_actions}"
            )

        if action in actions_requiring_comment and comment is None:
            raise CommentRequired(f"Actions of type {actions_requiring_comment} require a comment")

        action_url = self.adjustment_headers_url + f'/{action}/{guid}'

        if action in actions_requiring_comment:
            req = requests.Request('PUT',
                                   action_url,
                                   json={'comment': comment}
                                   )
        else:
            req = requests.Request('PUT',
                                   action_url,
                                   )

        response = self._send_request(req)

        return AlliantApiResponse(response)

    #################################################################################################
    #
    #   Contract Methods
    #
    #################################################################################################

    def lookup_contract_with_filter(self, filter_field, filter_value, verbosity='default') -> Collection:

        str_id = ResourceParameters._preprocess_filter(str(filter_value))

        params = f"{verbosity}&$filter={filter_field} eq+'{str_id}'"

        req = requests.Request('GET',
                               self.contracts_url,
                               params=params
                               )

        response = self._send_request(req)

        return Collection(response)

    def lookup_contract_guid_with_filter(self, filter_field: str, filter_value: str) -> str:

        response = self.lookup_contract_with_filter(filter_field, filter_value, verbosity='minimal')

        return response.guids[0]

    def lookup_contract(self, guid, verbosity='default'):

        params = verbosity

        req = requests.Request('GET',
                               self.contracts_url + '/' + guid,
                               params=params
                               )

        response = self._send_request(req)

        return Contract(response)

    def delete_contract(self, guid: str) -> AlliantApiResponse:
        """
        This will delete a contract provided it is in revision or in setup

        :param guid: The guid of the contract to be deleted
        :type guid: str
        :return: AlliantApiResponse
        :rtype: AlliantApiResponse
        """

        req = requests.Request('DELETE',
                               self.contracts_url + '/' + guid,
                               )

        response = self._send_request(req)

        return AlliantApiResponse(response)

    def contract_action(self, guid: str, action: str, comment: str = None) -> AlliantApiResponse:
        """


        :param guid: This is the guid of the resource
        :param action: The action to be performed.  available actions are: 'approve', 'complete', 'copy', 'insetup',
                        model', 'resolve', 'revise'
        :param comment: The action 'approve' requires a comment.  If the action is not 'approve, then this is optional
        :type comment: str
        :return: AlliantApiResponse
        :rtype: AlliantApiResponse
        """

        available_actions = ['approve', 'complete', 'copy', 'insetup', 'model', 'resolve', 'revise']
        actions_requiring_comment = ['approve']

        if action not in available_actions:
            raise ActionNotImplemented(
                f"The action '{action}' is not implemented.  Available actions are {available_actions}"
            )

        if action in actions_requiring_comment and comment is None:
            raise CommentRequired(f"Actions of type {actions_requiring_comment} require a comment")

        action_url = self.contracts_url + f'/{action}/{guid}'

        if action in actions_requiring_comment:
            req = requests.Request('PUT',
                                   action_url,
                                   json={'comment': comment}
                                   )
        else:
            req = requests.Request('PUT',
                                   action_url,
                                   )

        response = self._send_request(req)

        return AlliantApiResponse(response)

    #################################################################################################
    #
    #   Contact Methods
    #
    #################################################################################################

    def lookup_contact_with_filter(self, filter_field, filter_value, verbosity='default') -> Collection:

        str_id = ResourceParameters._preprocess_filter(str(filter_value))

        params = f"{verbosity}&$filter={filter_field} eq+'{str_id}'"

        req = requests.Request('GET',
                               self.contacts_url,
                               params=params
                               )

        response = self._send_request(req)

        return Collection(response)

    def lookup_contact_guid_with_filter(self, filter_field: str, filter_value: str) -> str:

        response = self.lookup_contact_with_filter(filter_field, filter_value, verbosity='minimal')

        return response.guids[0]

    def lookup_contact(self, guid, verbosity='default') -> AlliantApiResponse:

        params = verbosity

        req = requests.Request('GET',
                               self.contacts_url + '/' + guid,
                               params=params
                               )

        response = self._send_request(req)

        return AlliantApiResponse(response)

    def lookup_contact_collection(self, verbosity='default') -> Collection:

        params = verbosity

        req = requests.Request('GET',
                               self.contacts_url,
                               params=params
                               )

        response = self._send_request(req)

        return Collection(response)

    def delete_contact(self, guid: str) -> AlliantApiResponse:

        req = requests.Request('DELETE',
                               self.contacts_url + '/' + guid,
                               )

        response = self._send_request(req)

        return AlliantApiResponse(response)

    def reset_metadata(self):

        req = requests.Request('POST', self.metadata_reset)

        response = self._send_request(req)

        return Contract(response)
