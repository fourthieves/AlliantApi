
__all__ = [
    'ResourceParameters',
    'CollectionParameters',
]


class ResourceParameters:

    def __init__(self,
                 verbosity: str = None,
                 include: list[str] = None,
                 exclude: list[str] = None):
        """
        This class houses details of parameters that can be passed when the expected response is a resource

        :param verbosity: [optional] defines the verbosity of the response 'minimal|default|verbose'
        :type verbosity: str
        :param include: [optional] list of fields to additionally include in a minimal or default response
        :type include: list[str]
        :param exclude: [optional] list of fields to specifically exclude from the response
        :type exclude: list[str]

        """
        self.verbosity = verbosity
        self.include = include
        self.exclude = exclude

    @staticmethod
    def form_param_string(param_list) -> str:

        if param_list:
            param_string = f"${'&'.join(param_list)}"
        else:
            param_string = None

        return param_string

    def parameter_string(self) -> str:
        """

        :return: a url parameter string
        :rtype: str
        """

        param_list = []

        if self.verbosity:
            param_list.append(self.verbosity)

        if self.include:
            include_string = f"include={','.join(self.include)}"
            param_list.append(include_string)

        if self.exclude:
            exclude_string = f"exclude={','.join(self.exclude)}"
            param_list.append(exclude_string)

        return self.form_param_string(param_list)


class CollectionParameters(ResourceParameters):

    def __init__(self,
                 verbosity: str = None,
                 include: list[str] = None,
                 exclude: list[str] = None,
                 top: int = None,
                 skip: int = None,
                 order_by_field: str = None,
                 order_by_order: str = None,
                 filter_field: str = None,
                 filter_value: str = None,
                 filter_operator: str = None,
                 filter_string: str = None):
        """
        This class houses details of parameters that can be passed when the expected response is a collection

        :param verbosity: [optional] defines the verbosity of the response 'minimal|default|verbose'
        :type verbosity: str
        :param include: [optional] list of fields to additionally include in a minimal or default response
        :type include: list[str]
        :param exclude: [optional] list of fields to specifically exclude from the response
        :type exclude: list[str]
        :param top: [optional] number of records returned in the page, default is 20
        :type top: int
        :param skip: [optional] number of records to skip when paging your response
        :type skip: int
        :param order_by_field: [optional] field to sort on
        :type order_by_field: str
        :param order_by_order: [optional] asc|desc - if not provided, will default to asc
        :type order_by_order: str
        :param filter_field: [optional] name of the field you would like to filter on
        :type filter_field: str
        :param filter_value: [optional] filter value
        :type filter_value: str
        :param filter_operator: [optional] operator to use with the filter
        'contains|endswith|startswith|eq|ne|le|lt|ge|gt'
        :type filter_operator: str
        :param filter_string: [optional] if you want to utilise a complex filter string with multiple filters then you
        can provide the entire string here. A complex string may look like "(id eq '123' or description eq 'my item')
        and statusReference.id ne 'active'". Do not provide the "$filter=" portion of the string.  If this parameter is
        populated, it will override anything in  filter_field, filter_value and filter_operator
        :type filter_string: str
        """

        super().__init__(verbosity, include, exclude)
        self.top = top
        self.skip = skip
        self.order_by_field = order_by_field
        self.order_by_order = order_by_order
        self.filter_field = filter_field
        self.filter_value = filter_value
        self.filter_operator = filter_operator
        self.filter_string = filter_string

    @staticmethod
    def _preprocess_filter(string):
        """
        Reformats a string that will be used as a filter parameter
        :param string: The string to be reformatted
        :type string: str
        :return:
        :rtype: STR
        """

        return string.replace("'", r"\'").replace(' ', '+')

    def parameter_string(self) -> str:
        """

        :return: a url parameter string
        :rtype: str
        """

        param_list = []

        if self.verbosity:
            param_list.append(self.verbosity)

        if self.include:
            include_string = f"include={','.join(self.include)}"
            param_list.append(include_string)

        if self.exclude:
            exclude_string = f"exclude={','.join(self.exclude)}"
            param_list.append(exclude_string)

        if self.top:
            top_string = f"$top={self.top}"
            param_list.append(top_string)

        if self.skip:
            skip_string = f"$skip={self.skip}"
            param_list.append(skip_string)

        if self.order_by_field:

            if self.order_by_order:
                order = self.order_by_order
            else:
                order = 'asc'

            order_by_string = f"$orderby={self.order_by_field} {order}"
            param_list.append(order_by_string)

        if self.filter_string:
            filter_string = self._preprocess_filter(f"$filter={self.filter_string}'")
            param_list.append(filter_string)
        else:
            if self.filter_field:
                filter_string = self._preprocess_filter(
                    f"$filter={self.filter_field} {self.filter_operator} '{self.filter_value}'"
                )
                param_list.append(filter_string)

        return self.form_param_string(param_list)
