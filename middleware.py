from werkzeug.wrappers import Request, Response
import shelve
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
load_dotenv()

class middleware():

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = Request(environ)

        if self.ratelimiter(request):

            res = Response('Rate limit excedeed. Try slowing down!',
                           mimetype='text/plain', status=429)
            return res(environ, start_response)

        return self.app(environ, start_response)

    def ratelimiter(self, request: Request) -> bool:
        limit = int(os.getenv('LIMIT', ''))
        period = int(os.getenv('PERIOD', ''))
        real_ip = os.getenv('REAL_IP', False)

        # Real IP can be used if there is proxy upstream which can be
        # trusted to include the real ip in the header
        # default is False
        if real_ip == "True":
            ip = request.headers.getlist("X-Forwarded-For")[0]
        else:
            ip = request.remote_addr

        timestamp = datetime.now().replace(microsecond = 0)
        valid_time = timestamp - timedelta(seconds=int(period))
        file = f'hash_data/route{request.path.replace("/", "_")}'

        with shelve.open(file , writeback=True) as hash_storage:

            if ip in hash_storage:
                # Request list for this IP
                reqs_ip = hash_storage[ip]

                # Remove invalid timestamps
                for req_list in reqs_ip[:]:          
                    if req_list[0] < valid_time:
                        reqs_ip.remove(req_list)
                    else:
                        break
                
                # Check number of requests and compare to the limit
                counter = sum([req_list[1] for req_list in reqs_ip])
                if counter >= limit:
                    return True

                # Populate the hash file with the current request
                if not reqs_ip:
                    reqs_ip.append([timestamp, 1])
                elif reqs_ip[-1][0] == timestamp:
                    reqs_ip[-1] = [reqs_ip[-1][0], reqs_ip[-1][1] + 1]
                else:
                    reqs_ip.append([timestamp, 1])
            else:
                hash_storage[ip] = [[timestamp, 1]]
                
            return False