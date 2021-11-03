from typing import List

__all__ = [
    'ListDefinition',
]


class ListDefinition:
    """
    This class constructs list definitions for making list related API calls.
    Available properties are:

    included_items_references
    excluded_items_references
    included_xrefs_references
    excluded_xrefs_references

    """

    def __init__(self, included_items_references: List[dict] = None, excluded_items_references: List[dict] = None,
                 included_xrefs_references: List[dict] = None, excluded_xrefs_references: List[dict] = None):

        self.included_items_references = included_items_references
        self.excluded_items_references = excluded_items_references
        self.included_xrefs_references = included_xrefs_references
        self.excluded_xrefs_references = excluded_xrefs_references

    @property
    def included_items_references(self):
        return self._included_items_references

    @included_items_references.setter
    def included_items_references(self, value):

        self._check_format_of_references(value)
        self._included_items_references = value

    @property
    def excluded_items_references(self):
        return self._excluded_items_references

    @excluded_items_references.setter
    def excluded_items_references(self, value):

        self._check_format_of_references(value)
        self._excluded_items_references = value

    @property
    def included_xrefs_references(self):
        return self._included_xrefs_references

    @included_xrefs_references.setter
    def included_xrefs_references(self, value):

        self._check_format_of_references(value)
        self._included_xrefs_references = value

    @property
    def excluded_xrefs_references(self):
        return self._excluded_xrefs_references

    @excluded_xrefs_references.setter
    def excluded_xrefs_references(self, value):

        self._check_format_of_references(value)
        self._excluded_xrefs_references = value

    @staticmethod
    def _check_format_of_references(value):
        """
        The format supplied should match the format to be supplied to the Alliant API for setting a reference field.
        This means it should be a list of dictionaries, with a key that appropriately maps to the reference

        """

        allowed_types = (list, tuple)
        allowed_dict_keys = ('guid', 'id', 'description')

        if value:

            if not isinstance(value, allowed_types):
                raise TypeError(f"Allowed types include - {allowed_types}.  Supplied type is {type(value)}")

            for item in value:
                assert isinstance(item, dict), f"The list should contain only dicts.  This list contained {item}"
                assert len(item.keys()) == 1, f"Dictionaries expected to contain a single key.  Found {item}"
                assert list(item.keys())[0].lower() in allowed_dict_keys, f"Allowed dict keys include - " \
                                                                          f"{allowed_dict_keys}. Found {item}"

    def list_details(self, action: str):

        list_details = []

        for item_reference in self.included_items_references:

            list_object = {
                '_action': action,
                'excludeFlag': False,
                'itemReference': item_reference
            }

            list_details.append(list_object)

        for item_reference in self.excluded_items_references:
            list_object = {
                '_action': action,
                'excludeFlag': True,
                'itemReference': item_reference
            }

            list_details.append(list_object)

        return list_details

    def list_xrefs(self, action: str):

        list_xrefs = []

        for item_reference in self.included_xrefs_references:
            list_object = {
                '_action': action,
                'excludeFlag': False,
                'itemReference': item_reference
            }

            list_xrefs.append(list_object)

        for item_reference in self.excluded_xrefs_references:
            list_object = {
                '_action': action,
                'excludeFlag': True,
                'itemReference': item_reference
            }

            list_xrefs.append(list_object)

        return list_xrefs

    def list_body(self,
                  action: str,
                  list_description: str,
                  list_detail_key: str,
                  list_xrefs_key: str,
                  include_only_common_items: bool = False,
                  definition_text: str = None,):

        body = dict([
            (list_detail_key, self.list_details(action)),
            (list_xrefs_key, self.list_xrefs(action)),
            ('description', list_description)
        ])

        if include_only_common_items:
            body['includeOnlyCommonItemsFlag'] = include_only_common_items

        if definition_text:
            body['definitionText'] = definition_text

        return body
