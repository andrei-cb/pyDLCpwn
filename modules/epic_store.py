import aiohttp
import json
import os
import urllib.parse
from typing import List, Tuple

class Request:
    def __init__(self, namespace: str):
        self.query = """
        query searchOffers($namespace: String!) {
            Catalog {
                searchStore(category: "*", namespace: $namespace){
                    elements {
                        id
                        title
                        developer
                        items {
                            id
                        }
                        catalogNs {
                            mappings(pageType: "productHome") {
                                pageSlug
                            }
                        }
                    }
                }
            }
        }
        """
        self.variables = {"namespace": namespace}

class EpicStore:
    @staticmethod
    async def query_catalog(category_namespace: str) -> List[Tuple[str, str, str, str, str]]:
        dlc_ids = []
        cache_file = f"./app_info/{category_namespace}.json"
        cached_exists = os.path.exists(cache_file)

        response = None

        if not cached_exists:
            response = await EpicStore.query_graphql(category_namespace)
            try:
                with open(cache_file, 'w') as f:
                    json.dump(response, f, indent=4)
            except:
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

        search_store = response['data']['Catalog']['searchStore']['elements']
        for element in search_store:
            for item in element['items']:
                dlc_ids.append((item['id'], element['title']))

        return dlc_ids

    @staticmethod
    async def query_graphql(category_namespace: str):
        try:
            encoded = urllib.parse.quote(category_namespace)
            request = Request(encoded)
            payload = json.dumps({
                "query": request.query,
                "variables": request.variables
            })

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://graphql.epicgames.com/graphql",
                    data=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response.raise_for_status()
                    data = await response.text()
                    return json.loads(data)
        except:
            return None
