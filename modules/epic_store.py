import cloudscraper
import json
import os
import asyncio
from typing import List, Tuple

class EpicStore:
    def __init__(self, locale="en-US", country="US"):
        self._graphql_url = "https://store.epicgames.com/graphql"
        self.locale = locale
        self.country = country
        self.scraper = cloudscraper.create_scraper()

    @staticmethod
    def _clean_1004_errors(raw):
        if 'errors' in raw:
            for error in raw['errors'].copy():
                service_response = error.get('serviceResponse')
                if service_response:
                    try:
                        if isinstance(service_response, str):
                            service_response = json.loads(service_response)
                        
                        if isinstance(service_response, dict) and service_response.get('numericErrorCode') == 1004:
                            raw['errors'].remove(error)
                    except:
                        pass
            if not raw['errors']:
                raw.pop('errors')
        return raw

    async def _make_graphql_query(self, query_string, **variables):
        variables.update({'locale': self.locale, 'country': self.country})
        
        def make_request():
            return self.scraper.post(
                self._graphql_url,
                json={'query': query_string, 'variables': variables},
            )

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, make_request)
        
        response.raise_for_status()
        data = response.json()
        return EpicStore._clean_1004_errors(data)
    
    async def query_addons(self, namespace: str):
        query = """
        query getAddonsByNamespace($categories: String!, $count: Int!, $country: String!, $locale: String!, $namespace: String!, $sortBy: String!, $sortDir: String!) {
            Catalog {
                catalogOffers(namespace: $namespace, locale: $locale, params: {category: $categories, count: $count, country: $country, sortBy: $sortBy, sortDir: $sortDir}) {
                    elements {
                        id
                        title
                        items {
                            id
                        }
                    }
                }
            }
        }
        """
        return await self._make_graphql_query(
            query,
            namespace=namespace,
            categories='addons|digitalextras',
            count=250,
            sortBy='releaseDate',
            sortDir='DESC'
        )

    @staticmethod
    async def query_catalog(category_namespace: str) -> List[Tuple[str, str]]:
        dlc_ids = []
        cache_file = f"./app_info/{category_namespace}.json"
        cached_exists = os.path.exists(cache_file)

        response = None
        store = EpicStore()

        if not cached_exists:
            try:
                response = await store.query_addons(category_namespace)
                
                # Debug dumping
                with open("./app_info/test.log", 'a') as f:
                     f.write(json.dumps(response, indent=4))

                try:
                    with open(cache_file, 'w') as f:
                        json.dump(response, f, indent=4)
                except:
                    pass
            except Exception as e:
                print(f"Error querying catalog: {e}")
                pass
        else:
            try:
                with open(cache_file, 'r') as f:
                    response = json.loads(f.read())
            except:
                if os.path.exists(cache_file):
                    os.remove(cache_file)

        if response is None:
            return dlc_ids

        try:
            if 'data' in response and 'Catalog' in response['data'] and 'catalogOffers' in response['data']['Catalog']:
                elements = response['data']['Catalog']['catalogOffers']['elements']
                for element in elements:
                    if 'items' in element:
                        for item in element['items']:
                            dlc_ids.append((item['id'], element['title']))
        except Exception as e:
            print(f"Error parsing DLCs: {e}")

        return dlc_ids
