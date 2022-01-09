Work Sample for Product Aspect, Python Variant
---

API Rate Limiter Using the Sliding Log Algorithm.
To reduce memory usage, requests sent at the same second are saved in one array represented by [ timestamp, number ] where number is the number of requests for this timestamp.

## Development

Created a middleware class that is executed for every request.
If the rate limit is not yet reached the middleware forwards the request, otherwise the request is dropped and a response indicating that limit is reached is forwarded.

The ratelimiter function itself takes on the request and returns a boolen value.
For each endpoint a dictionary-like object file is created where IPs and requests are stored as key-value pairs.
As a request is received, the file for this endpoint is opened and is checked whether this request's IP is in file as a key.
If it is not, then a new key is created with this IP and value of this time stamp.
If this key exists then all the requests between now and now minus the period are summed and if the sum is greater or equal to the limit then this request is dropped. If the sum is lower than the limit, the request is forwarded and appended to the requests for this ip.
