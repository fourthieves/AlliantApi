import logging
from requests import Response
from json import JSONDecodeError
from dataclasses import dataclass

#################################################################################################
#
#   Data Classes and sub classes for formatting responses
#
#################################################################################################


class AlliantApiResponse(Response):
    """
    A class to structure the responses from API calls
    """
    def __init__(self, response: Response):
        """

        :param response: This response object is a requests.response object.
        :type response: Complete documentation for this object can be found at https://docs.python-requests.org/en/master/api/#requests.Response
        """

        # This gets the state from the Response object that has been passed in, and then applies it to our
        # new AlliantApiResponse object
        self.__setstate__(response.__getstate__())

        try:
            self.errors = self.json().get('errors')
            self.has_errors = self.json().get('hasErrors')
            self.result = self.json().get('result')
            self.warnings = self.json().get('warnings')
            self.has_warnings = self.json().get('hasWarnings')

        except JSONDecodeError:
            logging.error(
                f'{self.request.method = }\n'
                f'  {self.status_code = }\n'
                f'  {self.request.url = }\n'
                f'  {self.request.headers = }\n'
                f'  {self.request.body = }\n'
            )

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


@dataclass
class RequestFormat:
    method: str
    url: str
    body: str
    headers: str


class Collection(AlliantApiResponse):

    @property
    def next_page_url(self) -> str:
        return self.result.get('previousPageUrl')

    @property
    def previous_page_url(self) -> str:
        return self.result.get('nextPageUrl')

    @property
    def items(self) -> list:
        return self.result.get('items')

    @property
    def item_count(self) -> int:
        return self.result.get('itemCount')

    @property
    def total_item_count(self) -> int:
        return self.result.get('totalItemCount')

    @property
    def guids(self) -> list:
        return [item.get('guid') for item in self.items]


class Adjustment(AlliantApiResponse):
    """
    A subclass of Response.  This offers additional methods to return data specific to the adjustment header object.
    It can only works with a resource and not with a collection
    """

    @property
    def adjustment_status(self):

        try:
            status = self.result.get('statusReference').get('displayName')
        except AttributeError:
            status = None

        return status


class Contract(AlliantApiResponse):
    """
    A subclass of Response.  This offers additional methods to return data specific to the adjustment header object.
    It can only works with a resource and not with a collection
    """

    @property
    def contract_status(self):

        try:
            status = self.result.get('statusReference').get('displayName')
        except AttributeError:
            status = None

        return status
