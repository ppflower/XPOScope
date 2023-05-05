import asyncio
from mitmproxy import http
from mitmproxy import options
from mitmproxy.tools.dump import DumpMaster
import config
import traffic_utils
import traffic_transfer_client



def get_resp_body(flow: http.HTTPFlow):
    res = flow.response.get_text()
    return res


def is_image_flow(http_url: str):
    lower_http_url = http_url.lower()
    if lower_http_url.endswith(".bmp") or lower_http_url.endswith(".jpg") or lower_http_url.endswith(
            ".jpeg") or lower_http_url.endswith(".png") or lower_http_url.endswith(".gif"):
        return True
    return False


def tuple_list_to_json(tuple_list: list):
    res = {}
    for tup in tuple_list:
        res[tup[0]] = tup[1]
    return res


async def start(client, m):
    my_addon = TrafficMonitor(client)
    m.addons.add(my_addon)
    await m.run()
    return m


class TrafficMonitor:
    url_list = None
    count = None
    client = None

    def __init__(self, client):
        self.url_list = []
        self.count = 0
        self.client = client
        pass

    def request(self, flow: http.HTTPFlow):
        pass

    def response(self, flow: http.HTTPFlow):
        # connect = {'opt_type': -1}
        # self.client.s.send(json.dumps(connect).encode())
        if is_image_flow(flow.request.url):
            return
        if not (flow.request.method == "GET" or flow.request.method == "POST"):
            return
        if flow.response.status_code != 200 and flow.response.status_code != 200:
            return

        if "content-type" in dict(flow.response.headers) or "Content-Type" in dict(flow.response.headers):
            if not flow.request.url.endswith(".js"):
                try:
                    content = get_resp_body(flow)
                except Exception:
                    return
                if not content:
                    return
                resp_json = traffic_utils.to_dict(content)
                if not resp_json or not isinstance(resp_json, dict):
                    return
                if 'data' in resp_json:
                    data_json = resp_json['data']
                    if data_json and isinstance(data_json, dict) and len(data_json) > 0:
                        self.client.data_transfer(flow.request.url, data_json)


# async def send_message():
#     global message_queue
#     start_time = time.time()
#     while True:
#         if len(message_queue) > 0:
#             flow_tuple = message_queue.remove(0)
#             if isinstance(flow_tuple, tuple):
#                 flow_url = flow_tuple[0]
#                 data_json = flow_tuple[1]
#                 client.data_transfer(flow_url, data_json)
#         end_time = time.time()
#         if len(message_queue) == 0 and end_time - start_time >= config.MINI_APP_TEST_TIME:
#             break

async def main(client):
    ip = config.get_ip()
    print(ip)
    opts = options.Options(
        listen_host=ip,
        listen_port=8080
    )
    m = DumpMaster(opts)
    task = asyncio.create_task(start(client, m))
    await asyncio.sleep(config.MINI_APP_TEST_TIME)
    client.close()
    m.shutdown()
    task.cancel()
    await task


if __name__ == "__main__":
    client = traffic_transfer_client.Client(config.TCP_PORT)
    try:
        asyncio.run(main(client))
    except asyncio.exceptions.CancelledError:
        print("Cancel mitmproxy")
    except RuntimeError:
        print("Cancel mitmproxy")
    print("traffic monitor end")
