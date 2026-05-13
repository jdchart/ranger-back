import requests

class GBIF:
    def __init__(self, **kwargs):
        self.api_prefix = kwargs.get("api_prefix", "https://api.gbif-uat.org/v1/")

    def search(self, **kwargs):
        params = {
            "taxonKey" : self._taxon_strong_to_int(kwargs.get("taxon", "aves")),
            "limit" : kwargs.get("limit", 10),
            "geometry": "POLYGON((-5 47, -5 49, -1 49, -1 47, -5 47))"
        }

        response = requests.get(f"{self.api_prefix}occurrence/search", params = params)
        data = response.json()
        return data["results"]

    def _taxon_strong_to_int(self, as_string):
        if as_string == "aves" or as_string == "birds":
            return 212
        
class Aves:
    def __init__(self, **kwargs):
        self.key = kwargs.get("key", None)
        self.dataset_key = kwargs.get("dataset_key", None)

    def _parse_response(self, response):
        self.key = response.get("key")
        self.dataset_key = response.get("datasetKey")