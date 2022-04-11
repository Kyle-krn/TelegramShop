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
                                      children: bool = False,
                                      children_count: bool = False,
                                      products: bool = False,
                                      products_count: bool = False):
        params = {
            "name": 1 if name else 0,
            "slug": 1 if slug else 0,
            "filters": 1 if filters else 0,
            "parent_id": 1 if parent_id else 0,
            "children": 1 if children else 0,
            "children_count": 1 if children_count else 0,
            "products": 1 if products else 0,
            "products_count": 1 if products_count else 0,
        }
        resp = await self.get_request(path=f'category/light/{category_id}', params=params)
        return resp

    async def get_distinct_string_value(self, category_id: int, attr_name: str):
        params = {'attr_name': attr_name}
        resp = await self.get_request(path=f'category/get_list_string_attr_value/{category_id}', params=params)
        return resp

    async def get_min_max_for_category(self, category_id: int):
        resp = await self.get_request(path=f'category/min_max/{category_id}')
        return resp

    async def get_min_max_digit_attr(self, category_id: int, attr_name: str):
        params = {'attr_name': attr_name}
        resp = await self.get_request(path=f'category/get_min_max_digit_attr_value/{category_id}', params=params)
        return resp

    async def get_products_queryset(self, category_id: int, body: dict, offset: int, limit: int):
        params = {'offset': offset, 'limit': limit}
        resp = await self.post_request(path=f'product/query_by_category/{category_id}', data=body, params=params)
        return resp
        
    async def get_request(self, path: str, params: dict = {}, return_json: bool = True):
        header = {}
        # if token:
        header['Authorization'] = self.token
        request_url = f'{self.url}/{path}'
        async with aiohttp.request('GET', request_url, headers=header, params=params) as response:
            return await response.json() if return_json else response

    async def post_request(self, path: str, data: dict = None, params: dict = {}, token: str = None, return_json: bool = True):
        header = {}
        # if token:
        header['Authorization'] = self.token
        request_url = f'{self.url}/{path}'
        async with aiohttp.request('POST', request_url, headers=header, params=params, json=data) as response:
            return await response.json() if return_json else response


api = ShopApi()