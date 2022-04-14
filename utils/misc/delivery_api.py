import aiohttp


class DeliveryApi:
    
    def __init__(self):
        self.url = 'http://127.0.0.1:5000'
        # self.token = API_TOKEN

    async def pochta_rf(self, postcode: int, weight: int = 1):
        data = {
            'postcode': postcode,
            'weight': weight,
        }
        return await self.post_request(path='pochta-rf/delivery_price', data=data)

    async def get_request(self, path: str, params: dict = {}, return_json: bool = True):
        header = {}
        # if token:
        # header['Authorization'] = self.token
        request_url = f'{self.url}/{path}'
        async with aiohttp.request('GET', request_url, headers=header, params=params) as response:
            return await response.json() if return_json else response

    async def post_request(self, path: str, data: dict = None, params: dict = {}, token: str = None, return_json: bool = True):
        header = {}
        # if token:
        # header['Authorization'] = self.token
        request_url = f'{self.url}/{path}'
        async with aiohttp.request('POST', request_url, headers=header, params=params, json=data) as response:
            return await response.json() if return_json else response

delivery_api = DeliveryApi()