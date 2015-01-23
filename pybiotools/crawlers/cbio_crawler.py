from httplib import HTTPConnection, HTTPException, OK
from urllib import urlencode

class CBioCrawler(object):
    URL = "http://www.cbioportal.org/"

    def __init__(self):
        self.__connection = None
        self.__params = dict()
        pass

    def _conn(self):
        if self.__connection is None or self.__connection.sock is None:
            self.__connection = HTTPConnection(self.__class__.URL, 80)
        return self.__connection

    def set_param(self, key, value):
        self.__params[key] = value

    def set_param_collection(self, key, arr):
        self.set_param(key, ','.join(arr))

    def set_genes(self, genes):
        self.set_param_collection('gene_list', genes)

    def set_cases(self, cases):
        self.set_param_collection('case_set_id', cases)

    def set_profiles(self, profiles):
        self.set_param_collection('genetic_profile_id', profiles)

    def get_profile_data(self):
        self._conn().request('GET', 'webservice.do',
            urlencode({'cmd': 'getProfileData'}.merge(self.__params)))
        response = self._conn().getresponse()
        if response.reason != OK:
            raise HTTPException(str(response.status) + str(response.reason))
        return response.read()