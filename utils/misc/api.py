from data.config import API_TOKEN, API_URL
import aiohttp

class ShopApi:
    
    def __init__(self):
        self.url = API_URL
        self.token = API_TOKEN

    async def get_main_category_info(self):
        resp = await self.get_request(path=f"category/main")
        return resp

    async def get_category_info(self, category_id: id):
        resp = await self.get_request(path=f'category/{category_id}')
        return resp

    async def get_request(self, path: str, return_json: bool = True):
        header = {}
        # if token:
        header['Authorization'] = self.token
        request_url = f'{self.url}/{path}'
        async with aiohttp.request('GET', request_url, headers=header) as response:
            return await response.json() if return_json else response

    async def post_request(self, path: str, data: dict = None, token: str = None, return_json: bool = True):
        header = {}
        if token:
            header['Authorization'] = token
        request_url = f'{self.url}/{path}'
        async with aiohttp.request('POST', request_url, headers=header, json=data) as response:
            return await response.json() if return_json else response


api = ShopApi()