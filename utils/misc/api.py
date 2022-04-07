from data.config import API_TOKEN, API_URL
import aiohttp

class ShopApi:
    
    def __init__(self):
        self.url = API_URL
        self.token = API_TOKEN

    async def get_main_category_info(self):
        resp = await self.get_request(path=f"category/main")
        return resp

    async def get_product_info(self, product_id: id):
        resp = await self.get_request(path=f'product/{product_id}', params={'active': 1})
        return resp

    async def get_category_info(self, category_id: id):
        resp = await self.get_request(path=f'category/{category_id}', params={'active': 1})
        return resp

    async def get_category_light_info(self, 
                                      category_id: int,
                                      name: bool = False,
                                      slug: bool = False,
                                      filters: bool = False,
                                      parent_id: bool = False,
                                      childrens: bool = False,
                                      products: bool = False):
        params = {
            "name": 1 if name else 0,
            "slug": 1 if slug else 0,
            "filters": 1 if filters else 0,
            "parent_id": 1 if parent_id else 0,
            "childrens": 1 if childrens else 0,
            "products": 1 if products else 0,
        }
        resp = await self.get_request(path=f'category/light/{category_id}', params=params)
        return resp

    async def get_request(self, path: str, params: dict = {}, return_json: bool = True):
        header = {}
        # if token:
        header['Authorization'] = self.token
        request_url = f'{self.url}/{path}'
        async with aiohttp.request('GET', request_url, headers=header, params=params) as response:
            return await response.json() if return_json else response

    async def post_request(self, path: str, data: dict = None, token: str = None, return_json: bool = True):
        header = {}
        if token:
            header['Authorization'] = token
        request_url = f'{self.url}/{path}'
        async with aiohttp.request('POST', request_url, headers=header, json=data) as response:
            return await response.json() if return_json else response


api = ShopApi()