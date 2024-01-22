## Retry Requests
This project was to create a unified way of sending GET and POST REST API calls to the company's internal api gateway and external third-party endpoints. In addition to making and returning the call, the functions fetchGet and fetchPost (_api.py_) implement a configurable retry system, the ability to omit extraneous json tags from the results of the call, and a system of checking internal return results for commonly expected values. 

For example, in several instances when this program was initially used, a call would be made to an API that returns the results of another API call, or which would return a failure message with a successful status code. In these circumstances, the fetchGet and fetchPost methods are able to check the internals of the response for an expected value, and determine whether or not a retry should be attempted.

For company security, all identifying information has been redacted and all but a select few examples of the internal functions in _api.py_ that use fetchGet and fetchPost have been removed.
