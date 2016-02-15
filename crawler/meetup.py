
import functools
try:
    import urlparse
except:
    import urllib.parse as urlparse

import ratelim
import requests
import toolz


RATELIM_LIMIT = 30
RATELIM_PERIOD = 10

#class MeetupIterator(object):
#    """This object iterates over API results, providing transparent iteration."""
#    def __init__(self, api):
#        self._api = api
#
#    def __getattr__(self, name, **kwargs):
#        if not name.startswith('_'):
#            return self._api.__getattr(name, **kwargs)
#        api_method = object.__getattribute__(self, name)
#        def new_api_method():
#            api_method(name, **kwargs)
#
#
#    def __next__(self):
#        api

def unpaginate_results(pages):
    return toolz.concat((page['results'] for page in pages))


class MeetupApi(object):
    _base = 'https://api.meetup.com'

    _endpoints = ('cities', 'groups', 'members', 'events', 'categories', )
    _error_keys = set(['details', 'problem', 'code', 'errors', ])

    def __init__(self, api_key):
        self._key = api_key

    def __getattr__(self, name, **kwargs):
        if name in MeetupApi._endpoints:
            return functools.partial(self._get, name, **kwargs)
        else:
            attr = object.__getattribute__(self, name)

    def _normalise_url(self, url):
        urlsplitted = urlparse.urlsplit(url)
        query = urlsplitted.query
        endpoint = urlsplitted.path
        params = urlparse.parse_qs(query)
        url = urlparse.urljoin(self._base, endpoint)
        return url, params

    @ratelim.patient(RATELIM_LIMIT, RATELIM_PERIOD)
    def _get(self, endpoint, **params):
        """
        More info at: http://www.meetup.com/meetup_api/#limits
        """
        default_params = {
            'key': self._key,
            'format': 'json',
        }
        default_params.update(params)
        params = default_params

        url, url_params = self._normalise_url(endpoint)
        params.update(url_params)
        try:
            response = requests.get(url, params=params)
            if response.status_code != 200:
                raise AttributeError
            out = response.json()
            out['rate'] = {}
            out['rate']['limit'] = response.headers['X-RateLimit-Limit']
            out['rate']['limit_remaining'] = response.headers['X-RateLimit-Remaining']
            out['rate']['reset'] = response.headers['X-RateLimit-Reset']
            if int(out['rate']['limit_remaining']) == 0:
                sleep(int(out['rate']['reset'])+1)
            if self._error_keys.intersection(out.keys()):
                raise AttributeError
        except AttributeError as ex:
            print(url)
            print(response)
            print(response.json())
            raise(ex)
        return out

