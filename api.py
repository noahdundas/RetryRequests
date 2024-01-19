from . import util
import requests, json, time

# Requirements: sudo pip install requests

# Gets a company api gateway key, redacted for security
def getApiGatewayKey():
    return "[REDACTED]"

# Gets a company platform key, redacted for security
def getPlatformKey():
    return "[REDACTED]"

# Gets a copy of the default headers that requests should use
def getHeaders():
    headers = requests.utils.default_headers()
    headers.update(
        {
            'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
        }
    )
    return headers

# Sample function that sends fetchGet to company api gateway
def installationStats(logPath, installationId):
    apigateway = "https://" + installationId + ".company.com"
    authKey = getApiGatewayKey()
    getUrl = apigateway + "/gw/installationStats?authKey=" + authKey + "&installationId=" + installationId

    resp = fetchGet(getUrl, logPath, omitTags=[], expecting = "installationStats")
    if resp == False:
        return False
    try:
        resp_data = resp.json()
    except:
        util.log(logPath, "Error: could not parse JSON result!")
        return False
    return resp_data

# Sample function that sends fetchPost to company api gateway
def setInstallationStats(platformUrl, installationId, logicTriggersCount, tableCount, pageCount, userCount, engLogPath):
    platformKey = getPlatformKey()
    data = {
        'platformKey':platformKey,
        'installationId':installationId,
        'logicTriggersCount':logicTriggersCount,
        'tableCount':tableCount,
        'pageCount':pageCount,
        'userCount':userCount
    }

    url = platformUrl + "/api/setInstallationStats"

    resp = fetchPostDefault(url, data, engLogPath)
    return resp.status_code

# Sample function that sends a slack message
def slackPost(TEXT, logPath):
    data = {
        'text':TEXT
    }

    url = "https://hooks.slack.com/services/[REDACTED]"

    resp = fetchPostDefault(url, data, logPath)
    return resp

# Runs a get request to the provided url and logs the output to the specified path
#@param getUrl The url to make the request to
#@param logPath The filepath to log results
#@return The response object returned by the request or False if the request failed
def fetchGet(getUrl, logPath, omitTags = None, expecting = "", retries = None):
    params=""
    headers=getHeaders()
    timeout=60

    try:
        #-Initialize omission tags-
        if omitTags is None:
            omitTags = []
            
        #-Initialize retry array-
        if retries is None:
            retries = [1,2,3,5,10,30,60,120,240,600]

        #-Send Request-
        util.log(logPath, "Fetching " + getUrl)
        resp = requests.get(getUrl, params=params, headers=headers, timeout=timeout)

        #-Process Response Output-
        textResponse = str(resp.text)
        # If the calling method wants to omit tags from the response, filter them out
        if(len(omitTags) > 0):
            textResponse = omitJsonTags(textResponse, omitTags, logPath)
        util.log(logPath, "Recieved response code " + str(resp.status_code) + " and text: " + textResponse)


        #-Check Response-
        if checkNonRetry(resp):
            return resp
        # Check the status code of the response
        resp.raise_for_status()
        # If the calling method expects something in the response, check for it
        if(expecting != ""):
            if not verifyResponse(resp, expecting):
                raise Exception("Response failed verfication!")
        
        # If all checks pass - success!
        util.log(logPath, "Fetched from " + getUrl + " successfully")
        return resp
    except:
        curRetry = 1

        #-Retry Loop-
        while(curRetry <= len(retries)):
            util.log(logPath, "Fetch Failed, attempting retry #" + str(curRetry) + " in " + str(retries[curRetry-1]) + " seconds")
            time.sleep(retries[curRetry-1])
            util.log(logPath, "Retrying...")
            try:
                #-Send Request-
                resp = requests.get(getUrl, params=params, headers=headers, timeout=timeout)
                
                #-Process Response-
                textResponse = str(resp.text)
                # If the calling method wants to omit tags from the response, filter them out
                if(len(omitTags) > 0):
                    textResponse = omitJsonTags(textResponse, omitTags, logPath)
                util.log(logPath, "Recieved response code " + str(resp.status_code) + " and text: " + textResponse)
                
                #-Check Response-
                resp.raise_for_status()
                # If the calling method expects something in the response, check for it
                if(expecting != ""):
                    if not verifyResponse(resp, expecting):
                        raise Exception("Response failed verfication!")

                # If all checks pass - success!
                util.log(logPath, "Fetched " + getUrl + " successfully")
                return resp
            except:
                # If the fetch failed, retry
                curRetry = curRetry + 1

        # After all retries fail, return false
        util.log(logPath, "Get FAILED for " + getUrl + " " + str(len(retries)) + " times, returning false.")
        return False

# Runs a post request to the given url using default parameters by calling fetchPost, and logs the output to the specified path
#@param fetchUrl The url to make the request to
#@param reqInfo The information to extract data from that will be sent to the url
#@param logPath The filepath to log results
def fetchPostDefault(fetchUrl, reqInfo, logPath, omitTags = [], expecting = ""):
    data=json.dumps(reqInfo)
    headers = getHeaders()
    headers.update({'Content-type': 'application/json', 'Accept': 'text/plain'})
    timeout = 240
    return fetchPost(fetchUrl, data, headers, timeout, logPath, omitTags, expecting)

# Runs a post request to the given url using provided parameters, and logs the output to the specified path
#@param fetchUrl The url to make the request to
#@param fetchData The data posted to the given url
#@param fetchHeaders The headers used by the post request
#@param fetchTimeout The timeout of the request in seconds
#@param logPath The filepath to log results
#@return The response object returned by the request, or a response with error code 504 if the request failed
def fetchPost(fetchUrl, fetchData, fetchHeaders, fetchTimeout, logPath, omitTags = None, expecting = "", retries = None):
    try:
        #-Initialize omission tags-
        if omitTags is None:
            omitTags = []

        #-Initialize retry array-
        if retries is None:
            retries = [1,2,3,5,10,30,60,120,240,600]

        # If the calling method wants to omit tags from the logging, filter them out from the request logging
        textData = str(fetchData)
        if(len(omitTags) > 0):
            textData = omitJsonTags(textData, omitTags, logPath)

        #-Send Request-
        util.log(logPath, "Posting to " + fetchUrl + " with data: " + textData)
        resp = requests.post(fetchUrl, data=fetchData, headers=fetchHeaders, timeout=fetchTimeout)

        #-Process Response Output-
        textResponse = str(resp.text)
        #If the calling method wants to omit tags from the logging, filter them out from the response logging
        if(len(omitTags) > 0):
            textResponse = omitJsonTags(textResponse, omitTags, logPath)
        util.log(logPath, "Recieved response code " + str(resp.status_code) + " and text: " + textResponse)

        #-Check Response-
        if checkNonRetry(resp):
            return resp
        # Check the status code of the response
        resp.raise_for_status()
        # If the calling method expects something in the response, check for it
        if(expecting != ""):
            if not verifyResponse(resp, expecting):
                raise Exception("Response failed verfication!")

        # If all checks pass - success!
        util.log(logPath, "Posted to " + fetchUrl + " successfully")
        return resp
    except:
        curRetry = 1

        #-Retry Loop-
        resp = requests.Response()
        while(curRetry <= len(retries)):
            util.log(logPath, "Post failed, attempting retry #" + str(curRetry) + " in " + str(retries[curRetry-1]) + " seconds")
            time.sleep(retries[curRetry-1])
            util.log(logPath, "Retrying...")
            try:
                #-Send Request-
                resp = requests.post(fetchUrl, data=fetchData, headers=fetchHeaders, timeout=fetchTimeout)
                
                #-Process Response Output-
                textResponse = str(resp.text)
                #If the calling method wants to omit tags from the response, filter them out
                if(len(omitTags) > 0):
                    textResponse = omitJsonTags(textResponse, omitTags, logPath)
                util.log(logPath, "Recieved response code " + str(resp.status_code) + " and text: " + textResponse)

                #-Check Response-
                resp.raise_for_status()
                # If the calling method expects something in the response, check for it
                if(expecting != ""):
                    if not verifyResponse(resp, expecting):
                        raise Exception("Response failed verfication!")

                # If all checks pass - success!
                util.log(logPath, "Posted to " + fetchUrl + " successfully")
                return resp
            except:
                curRetry = curRetry + 1
        util.log(logPath, "Post FAILED for " + fetchUrl + " " + str(len(retries)) + " times, returning false.")
        return resp

# Checks a string for json tags and removes them
#@param text The original text to strip tags from
#@param omitTags An array of tags to omit from the given text
#@return The text with any alterations
def omitJsonTags(text, omitTags, logPath):
    try:
        textJson = json.loads(text)
        for tag in omitTags:
            textJson.pop(tag, None)
        return json.dumps(textJson)
    except:
        util.log(logPath, "Attempted to omit tags " + str(omitTags) + " from text " + text + " and failed")
        return text

# Runs the response through a tag-specific check to verify that its internal data qualifies to pass retries
#@param resp The response returned from fetch
#@param expecting A text string indicating what check to run against the response
#@return A boolean value indicating whether or not the response passed the check
def verifyResponse(resp, expecting):
    try:
        respString = str(resp)
        respJson = resp.json()

        if expecting == "responseCode":
            if("responseCode" in respJson):
                if(respJson["responseCode"] == 200):
                    return True
            return False 
        elif expecting == "error":
            if("error" not in respJson):
                return True
            return False
        elif expecting == "installationStats":
            if("response" in respJson):
                if("result" in respJson["response"]):
                    countJson = respJson["response"]["result"]
                    if(("logicTriggersCount" in countJson) and ("tableCount" in countJson) and ("pageCount" in countJson)):
                        return True
            return False
        elif expecting == "true":
            if "True" in str(respJson):
                return True
            return False
        elif expecting == "200":
            if "200" in respString:
                return True
            return False
        else:
            print("ERROR: Unexpected fetchGet/fetchPost return check value")
            return True

    except Exception as e:
        print("Error thrown: " + str(e))
        return True

# Checks the response and its internals (if any) for a 400 code, in which case we do not want to retry
#@param resp The response returned from fetch
#@return A boolean value indicating whether or not a 400 code was found
def checkNonRetry(resp):
    respCode = resp.status_code
    if(respCode >= 400 and respCode < 500):
        return True

    try:
        respJson = resp.json()
        if("responseCode" in respJson):
            if(respJson["responseCode"] >= 400 and respJson["responseCode"] < 500):
                return True
    except:
        return False

    return False
