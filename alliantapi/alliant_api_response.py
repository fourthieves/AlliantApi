import logging
from requests import Response
from json import JSONDecodeError

#################################################################################################
#
#   Classes for formatting responses
#
#################################################################################################


class AlliantApiResponse(Response):
    """
    A class to structure the responses from API calls
    """
    def __init__(self, response: Response):
        """

        :param response: This response object is a requests.response object.
        :type response: Complete documentation for this object can be found at
            https://docs.python-requests.org/en/master/api/#requests.Response
        """

        # This gets the state from the Response object that has been passed in, and then applies it to our
        # new AlliantApiResponse object

        super().__init__()  # This is redundant but it makes the linter happy

        self.__setstate__(response.__getstate__())

        try:
            self.errors: list = self.json().get('errors')
            self.has_errors: bool = self.json().get('hasErrors')
            self.result = self.json().get('result')
            self.warnings: list = self.json().get('warnings')
            self.has_warnings: bool = self.json().get('hasWarnings')

        except JSONDecodeError:
            logging.error(
                f'{self.request.method = }\n'
                f'  {self.status_code = }\n'
                f'  {self.request.url = }\n'
                f'  {self.request.headers = }\n'
                f'  {self.request.body = }\n'
            )

            self.errors: list = []
            self.has_errors: bool = True
            self.result = None
            self.warnings: list = []
            self.has_warnings: bool = False

        if self.has_errors:
            logging.error(
                f'{self.request.method = }\n'
                f'  {self.status_code = }\n'
                f'  {self.request.url = }\n'
                f'  {self.request.headers = }\n'
                f'  {self.request.body = }\n'
                f'  {self.errors = }'
            )

        if self.has_warnings:
            logging.warning(
                f'{self.request.method = }\n'
                f'  {self.status_code = }\n'
                f'  {self.request.url = }\n'
                f'  {self.request.headers = }\n'
                f'  {self.request.body = }\n'
                f'  {self.warnings = }'
            )

        return


class Collection(AlliantApiResponse):

    def __init__(self, response: Response):
        super().__init__(response)

        self.next_page_url: str = self.result.get('previousPageUrl')
        self.previous_page_url: str = self.result.get('nextPageUrl')
        self.items: list = self.result.get('items')
        self.item_count: int = self.result.get('itemCount')
        self.total_item_count: int = self.result.get('totalItemCount')
        self.guids: list = [item.get('guid') for item in self.items]


class Adjustment(AlliantApiResponse):
    """
    A subclass of Response.  This offers additional methods to return data specific to the adjustment header object.
    It can only work with a resource and not with a collection
    """
    def __init__(self, response: Response):
        super().__init__(response)

        try:
            self.adjustment_status: str = self.result.get('statusReference').get('displayName')
        except AttributeError:
            self.adjustment_status = None


class Contract(AlliantApiResponse):
    """
    A subclass of Response.  This offers additional methods to return data specific to the adjustment header object.
    It can only work with a resource and not with a collection
    """

    def __init__(self, response: Response):
        super().__init__(response)

        try:
            self.contract_status: str = self.result.get('statusReference').get('displayName')
        except AttributeError:
            self.contract_status = None

