# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator


class BasicAuthenticator(HttpAuthenticator):
    def __init__(self, app_id: str, secret: str):
        self.app_id = app_id
        self.secret = secret

    def get_auth_header(self) -> Mapping[str, Any]:
        auth_str = requests.auth._basic_auth_str(self.app_id, self.secret)
        auth_header = {
            "Authorization": auth_str
        }
        return auth_header


class PlanningCenterStream(HttpStream, ABC):
    """ Base class for Planning Center Online API. """

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        try:
            offset = {
                "offset": response.json().get("meta").get("next").get("offset")
            }
            return offset

        except AttributeError:
            return None

        except KeyError:
            return None

    def request_params(self,
                       stream_state: Mapping[str, Any],
                       stream_slice: Mapping[str, Any] = None,
                       next_page_token: Mapping[str, Any] = None,
                       ) -> MutableMapping[str, Any]:
        """
        Usually contains common params e.g. pagination size etc.
        """
        params = {
            "per_page": 100
        }
        if next_page_token:
            params["offset"] = next_page_token.get("offset")

        return params

    def parse_response(self,
                       response: requests.Response,
                       stream_state: Mapping[str, Any],
                       stream_slice: Mapping[str, Any] = None,
                       next_page_token: Mapping[str, Any] = None,
                       ) -> Iterable[Mapping]:
        """
        The data is found in the 'data' key of the response dict.
        """
        return response.json().get("data")


class PlanningCenterPeopleStream(PlanningCenterStream, ABC):
    """ 
    Base class for Planning Center Online People v2 API. 
    """

    url_base = "https://api.planningcenteronline.com/people/v2/"

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        """ 
        Provide the API version. 
        """
        return {"X-PCO-API-Version": "2020-07-22"}


class PeopleAddress(PlanningCenterPeopleStream):
    """
    Each record represents an address in the People API.
    """
    primary_key = "id"

    def path(self,
             stream_state: Mapping[str, Any] = None,
             stream_slice: Mapping[str, Any] = None,
             next_page_token: Mapping[str, Any] = None
             ) -> str:
        return "addresses"


class PeopleCampus(PlanningCenterPeopleStream):
    """
    Each record represents a campus in the People API.
    """
    primary_key = "id"

    def path(self,
             stream_state: Mapping[str, Any] = None,
             stream_slice: Mapping[str, Any] = None,
             next_page_token: Mapping[str, Any] = None
             ) -> str:
        return "campuses"


class PeopleEmail(PlanningCenterPeopleStream):
    """
    Each record represents an email address in the People API.
    """
    primary_key = "id"

    def path(self,
             stream_state: Mapping[str, Any] = None,
             stream_slice: Mapping[str, Any] = None,
             next_page_token: Mapping[str, Any] = None
             ) -> str:
        return "emails"


class PeopleHousehold(PlanningCenterPeopleStream):
    """
    Each record represents a household in the People API.
    """
    primary_key = "id"

    def path(self,
             stream_state: Mapping[str, Any] = None,
             stream_slice: Mapping[str, Any] = None,
             next_page_token: Mapping[str, Any] = None
             ) -> str:
        return "households"


class PeoplePerson(PlanningCenterPeopleStream):
    """
    Each record represents a person in the People API.
    """
    primary_key = "id"

    def path(self,
             stream_state: Mapping[str, Any] = None,
             stream_slice: Mapping[str, Any] = None,
             next_page_token: Mapping[str, Any] = None
             ) -> str:
        return "people"


class SourcePlanningCenter(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        TODO add checks for the connector.
        
        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        app_id = config["app_id"]
        secret = config["secret"]
        auth = BasicAuthenticator(app_id=app_id, secret=secret)
        return [
            PeoplePerson(authenticator=auth),
            PeopleAddress(authenticator=auth),
            PeopleEmail(authenticator=auth),
            PeopleHousehold(authenticator=auth),
            PeopleCampus(authenticator=auth)
        ]
