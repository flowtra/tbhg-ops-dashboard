import grequests
import requests
import time
import json
import configparser
import asyncio

DEBUG = False


def getNewCookies(old_session_userid):
    csrf = "REDACTED"
    url = "https://www.sevenrooms.com/login?rurl=%2Fmanager%2Felanew%2Freservations%2Fday%2F03-13-2024"

    payload = f'csrftoken={csrf}&rurl=%2Fmanager%2Felanew%2Freservations%2Fday%2F03-13-2024&email=REDACTED&password=REDACTED&lsubmit=Login'
    headers = {
        'authority': 'www.sevenrooms.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'cookie': f'csrftoken={csrf}; session_userid={str(old_session_userid)}',
        'origin': 'https://www.sevenrooms.com',
        'referer': 'https://www.sevenrooms.com/login?rurl=%2Fmanager%2Felanew%2Freservations%2Fday%2F03-13-2024',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    response = requests.post(url, headers=headers, data=payload, allow_redirects=True)
    newCookies = response.cookies.get_dict()

    newSessionUserID = newCookies["session_userid"]
    newSessionID = newCookies["sessionid"]
    if newSessionUserID and newSessionID:
        config = configparser.ConfigParser()
        config['authCookies'] = {"success": "true",
                                 "session_userid": newSessionUserID,
                                 "sessionid": newSessionID}
        with open('authCookies.ini', 'w') as outFile:
            config.write(outFile)
        return {"success": "true"}
    else:
        return {"success": "false", "error": f"{str(response.status_code)} - {response.text} {str(response.cookies.get_dict())}"}

def getCookieFromFile():
    config = configparser.ConfigParser()
    config.read('authCookies.ini')

    if config["authCookies"]["success"] == "true":
        return config["authCookies"]["sessionid"], config["authCookies"]["session_userid"]
    else:
        return False, False

def getAllRestaurantResvData(date: str, restNames: dict): #Returns array of responses
    sessionID, sessionUserID = getCookieFromFile()
    if sessionID == False: #not using if not because pycharm is dumb
        return False

    dateStr = f"{date[2:4]}-{date[:2]}-{date[4:8]}"
    authHeaders = {
        'authority': 'www.sevenrooms.com',
        'accept': '*/*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/json',
        'cookie': f'csrftoken=REDACTED; sessionid_keepalive="<(*^*)>"; sessionid={sessionID}; session_userid={sessionUserID}',
        'referer': 'https://www.sevenrooms.com/manager/tipopastabar/reservations/day/03-11-2024',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    urls = []
    for restName in restNames.keys():
        urls.append(f"https://www.sevenrooms.com/api-yoa/actuals/day?date={dateStr}&venue={restName}")

    if DEBUG:
        start = time.time()

    rs = (grequests.get(u, headers=authHeaders) for u in urls)
    responses = grequests.map(rs)
    if DEBUG:
        end = time.time()
        elapsed = end - start
        for response in responses:
            print(f"Time for {str(response.url).split('venue=')[1]}: {response.elapsed}")
        print(f'Time taken: {elapsed:.6f} seconds')

    #TIMEOUT CHECK
    resp1 = responses[0]
    if str(resp1.status_code) == "401":
        print("Session Cookie Expired | Retrieving new one.")
        status = getNewCookies(old_session_userid=sessionUserID)
        if status["success"] == "true":
            responses = getAllRestaurantResvData(date, restNames)
            return responses
        else:
            return False
    else:
        return responses


def getAllRestaurantLiveSeated(restNames: dict, date: str):
    responses = getAllRestaurantResvData(date, restNames)
    reply = {
        "aw": 0,
        "ela": 0, # Ela Jalan Sultan
        "tgm": 0,
        "to": 0,
        "tpb": 0,
        "tpz": 0,
        "tsks": 0,
        "tsn": 0,
        "wtls": 0,
        "wtrs": 0,
    }
    for response in responses:
        if response.status_code == 200:
            restFullName = str(response.url).split("&venue=")[1]
            restData = response.json()

            liveSeated = 0
            for x in restData["data"]["actuals"]:
                if x["status"] in ["ARRIVED", "ARRIVED_PARTIAL"]:  # ACCOUNTING FOR PARTIAL ARRIVALS
                    liveSeated += x["max_guests"]
                    reply[restNames[restFullName]] = liveSeated

    return reply


def getRestaurantResvData(restName: str, date: str):
    sessionID, sessionUserID = getCookieFromFile()
    if sessionID == False:  # not using if not because pycharm is dumb
        return False

    print("WARNING | FUNCTION OUT OF DATE MUST UPDATE COOKIES !!!")
    dateStr = f"{date[2:4]}-{date[:2]}-{date[4:8]}"
    authHeaders = {
        'authority': 'www.sevenrooms.com',
        'accept': '*/*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/json',
        'cookie': f'csrftoken=REDACTED; sessionid_keepalive="<(*^*)>"; sessionid={sessionID}; session_userid={sessionUserID};',
        'referer': 'https://www.sevenrooms.com/manager/tipopastabar/reservations/day/03-11-2024',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    url = f"https://www.sevenrooms.com/api-yoa/actuals/day?date={dateStr}&venue={restName}"
    r = requests.get(url, headers=authHeaders)

    if r.status_code == 200:
        return r.json()
    elif r.status_code == 401:
        print("Session Cookie Expired | Retrieving new one.")
        status = getNewCookies(old_session_userid=sessionUserID)
        if status["success"] == "true":
            r = getRestaurantResvData(restName, date)
            return r
        else:
            return False #catch this error


def countLiveSeated(restData):
    liveSeated = 0
    for x in restData["data"]["actuals"]:
        if x["status"] in ["ARRIVED", "ARRIVED_PARTIAL"]: # ACCOUNTING FOR PARTIAL ARRIVALS
            # print(f'{x["arrival_time"]} | {x["status"]} | {x["client_display_name"]} - {x["max_guests"]}')

            liveSeated += x["max_guests"]  # use a better identifier for seated guests in case of partial

    return liveSeated


def getShiftsUsed(arrTime, shifts):  # for improvement: JUST USE A LIST
    timeDict = {'0900': 0, '0930': 0, '1000':0, '1030': 0, '1100': 0, '1130': 0, '1200': 0, '1230': 0, '1300': 0, '1330': 0, '1400': 0, '1430': 0, '1500': 0,
                '1530': 0, '1600': 0, '1630': 0, '1700': 0, '1730': 0, '1800': 0, '1830': 0, '1900': 0, '1930': 0,
                '2000': 0, '2030': 0, '2100': 0, '2130': 0, '2200': 0, '2230': 0, '2300': 0, '2330': 0}
    shiftsUsed = []

    ki = dict()
    ik = dict()
    for i, k in enumerate(timeDict):
        ki[k] = i  # dictionary index_of_key
        ik[i] = k  # dictionary key_of_index

    for i in range(shifts):
        # Get next key in Dictionary
        index_of_test_key = ki[arrTime]
        index_of_next_key = index_of_test_key + i
        res = ik[index_of_next_key] if index_of_next_key in ik else None
        shiftsUsed.append(res)
        # printing result
    return shiftsUsed

def getAllProjectedSeated(restNames: dict, dateStr: str): #Date in format ddmmyyyy for consistency. Always pass ddmmyyyy into functions.
    allRestData = getAllRestaurantResvData(dateStr, restNames)
    print("DATA RETRIEVED")

    allRestShiftsDict = {}

    for restResponse in allRestData:
        restData = restResponse.json() #add exception catch? status code check?

        restFullName = str(restResponse.url).split("&venue=")[1]
        restID = restNames[restFullName]

        shiftsDict = {'1000':0, '1030': 0, '1100': 0, '1130': 0, '1200': 0, '1230': 0, '1300': 0, '1330': 0, '1400': 0, '1430': 0, '1500': 0,
                      '1530': 0, '1600': 0, '1630': 0, '1700': 0, '1730': 0, '1800': 0, '1830': 0, '1900': 0, '1930': 0,
                      '2000': 0, '2030': 0, '2100': 0, '2130': 0, '2200': 0, '2230': 0, '2300': 0, '2330': 0}

        for x in restData["data"]["actuals"]:
            # input(
            #     f'{x["arrival_time"]} | {x["status"]} | {x["client_display_name"]} - {x["max_guests"]} | {int(x["duration"] / 30)}')
            arrivalTime = x["arrival_time"].replace(":", "")[0:4]
            shifts = int(x["duration"] / 30)
            shiftsUsed = getShiftsUsed(arrivalTime, shifts)
            try:
                for shiftUsed in shiftsUsed:
                    shiftsDict[shiftUsed] += x["max_guests"]  # ERROR ACCOUNT FOR SHIFtS BEYOND CLOSING TIME
            except:
                print(
                    f'[{restFullName}] EXCEPTION | LIKELY SHIFT EXCEEDED for {x["arrival_time"]} | {x["status"]} | {x["client_display_name"]} - {x["max_guests"]} | {int(x["duration"] / 30)}')
                pass

        allRestShiftsDict[restID] = shiftsDict

    return allRestShiftsDict


def getSingleProjectedSeated(restData): #Date in format ddmmyyyy for consistency. Always pass ddmmyyyy into functions.

    shiftsDict = {'1000':0, '1030': 0, '1100': 0, '1130': 0, '1200': 0, '1230': 0, '1300': 0, '1330': 0, '1400': 0, '1430': 0, '1500': 0,
                  '1530': 0, '1600': 0, '1630': 0, '1700': 0, '1730': 0, '1800': 0, '1830': 0, '1900': 0, '1930': 0,
                  '2000': 0, '2030': 0, '2100': 0, '2130': 0, '2200': 0, '2230': 0, '2300': 0, '2330': 0}

    for x in restData["data"]["actuals"]:
        # input(
        #     f'{x["arrival_time"]} | {x["status"]} | {x["client_display_name"]} - {x["max_guests"]} | {int(x["duration"] / 30)}')
        arrivalTime = x["arrival_time"].replace(":", "")[0:4]
        shifts = int(x["duration"] / 30)
        shiftsUsed = getShiftsUsed(arrivalTime, shifts)
        try:
            for shiftUsed in shiftsUsed:
                shiftsDict[shiftUsed] += x["max_guests"]  # ERROR ACCOUNT FOR SHIFtS BEYOND CLOSING TIME
        except:
            print(
                f'[SINGLE REST] EXCEPTION | LIKELY SHIFT EXCEEDED for {x["arrival_time"]} | {x["status"]} | {x["client_display_name"]} - {x["max_guests"]} | {int(x["duration"] / 30)}')
            pass

    return shiftsDict


def checkResvAvailability(restName, restID, pax: int, date: str, resvTime):
    restData = getRestaurantResvData(restName, date) #date passed in should be ddmmyyyy
    shiftsDict = getSingleProjectedSeated(restData)
    from Dashboard import getCapacity

    maxCapacity = int(getCapacity(restID))
    paxBooked = int(shiftsDict[str(resvTime)])
    availCapacity = maxCapacity - paxBooked
    if pax <= availCapacity: #CAN ADD BUFFER HERE
        return True
    else:
        return False


def getAllSevenroomsReviewsResponses(venueIDs, start_date: str, end_date: str):
    sessionID, sessionUserID = getCookieFromFile()
    if sessionID == False: #not using if not because pycharm is dumb
        return False


    authHeaders = {
        'authority': 'www.sevenrooms.com',
        'accept': '*/*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/json',
        'cookie': f'csrftoken=REDACTED; sessionid_keepalive="<(*^*)>"; sessionid={sessionID}; session_userid={sessionUserID}',
        'referer': 'https://www.sevenrooms.com/manager2/tipopastabar/marketing/reviews/',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    urls = []
    for venueID in venueIDs.keys():
        urls.append(f"https://www.sevenrooms.com/api-yoa/reviews?venue={venueID}&sites=sevenrooms&start_date={start_date}&end_date={end_date}&offset=0&limit=5000&sort=-date")

    if DEBUG:
        start = time.time()

    rs = (grequests.get(u, headers=authHeaders) for u in urls)
    responses = grequests.map(rs)
    if DEBUG:
        end = time.time()
        elapsed = end - start
        for response in responses:
            print(f"Time for {str(response.url).split('venue=')[1]}: {response.elapsed}")
        print(f'Time taken: {elapsed:.6f} seconds')

    #TIMEOUT CHECK
    resp1 = responses[0]
    if str(resp1.status_code) == "401":
        print("Session Cookie Expired | Retrieving new one.")
        status = getNewCookies(old_session_userid=sessionUserID)
        if status["success"] == "true":
            responses = getAllSevenroomsReviewsResponses(venueIDs, start_date, end_date)
            return responses
        else:
            return False
    else:
        return responses


def getAllSevenroomsReviews_clean(venueIDs, start_date: str, end_date: str):
    responses = getAllSevenroomsReviewsResponses(venueIDs, start_date, end_date)
    allReviews = {"reviews": []}
    for response in responses:
        reviewsJson = response.json()

        for review in reviewsJson['data']['results']:
            allReviews["reviews"].append({
                "source": "sevenrooms", #FROM SEVENROOMS. IMPORTANT
                "concept": venueIDs[review['venue_id']],
                "resvID": review['actual_id'],
                "actual_name": review['actual_name'],
                "created": review['created'],
                "notes": review['notes'],
                "stars": review['rating'],
                "reviewDate": review['date']
            })

    allReviews["reviews"].sort(key = lambda x:x['created'], reverse=True) #sort by datetime, most recent to oldest

    return allReviews

#todo is to add sentiment analysis, use graded reviews and output best positive, worst, and neutral

# Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     for restName in restNames.values():
#         restData = getRestaurantResvData(restName, "12032024")
#         liveSeated = countLiveSeated(restData)
#         print(f"{restName}: {liveSeated}")
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
