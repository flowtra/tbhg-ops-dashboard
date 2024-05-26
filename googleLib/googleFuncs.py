import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def initCreds():
    CLIENT_FILE = 'googleLib/tbhg-acc1.json'
    SCOPES = ['https://www.googleapis.com/auth/business.manage']

    creds = None

    if os.path.exists('googleLib/token.json'):
        creds = Credentials.from_authorized_user_file('googleLib/token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def getBatchReviews():
    creds = initCreds()

    googleLocNames = {
            'locations/REDACTED': 'Afterwit',
            'locations/REDACTED': 'Ela Jalan Sultan',
            'locations/REDACTED': 'The Great Mischief',
            'locations/REDACTED': 'Tipo Osteria',
            'locations/REDACTED': 'Tipo Pasta Bar',
            'locations/REDACTED': 'Tipo Pizzeria',
            'locations/REDACTED': 'Tipo Strada KS',
            'locations/REDACTED': 'Tipo Strada Novena',
            'locations/REDACTED': 'WT Lasalle',
            'locations/REDACTED': 'WT Riverside',
            }
    googleLocNamesArr = ['accounts/REDACTED/locations/REDACTED', 'accounts/REDACTED/locations/REDACTED', 'accounts/REDACTED/locations/REDACTED', 'accounts/REDACTED/locations/REDACTED', 'accounts/REDACTED/locations/REDACTED', 'accounts/REDACTED/locations/REDACTED', 'accounts/REDACTED/locations/REDACTED', 'accounts/REDACTED/locations/REDACTED', 'accounts/REDACTED/locations/REDACTED', 'accounts/REDACTED/locations/REDACTED']
    reviewsDict = {"reviews": []}

    numberDict = {
        'ONE': 1,
        'TWO': 2,
        'THREE': 3,
        'FOUR': 4,
        'FIVE': 5
    }

    API_SERVICE_NAME = 'mybusiness'
    API_VERSION = 'v4'
    service = build(API_SERVICE_NAME, API_VERSION, credentials=creds, discoveryServiceUrl='https://developers.google.com/static/my-business/samples/mybusiness_google_rest_v4p9.json')

    body = {
      "locationNames": googleLocNamesArr,
      "pageSize": 50,
      "ignoreRatingOnlyReviews": False
    }
    reviewsJson = service.accounts().locations().batchGetReviews(name="accounts/REDACTED", body=body).execute()
    reviews = reviewsJson['locationReviews']
    for review in reviews:
        concept = googleLocNames["locations/" + review["name"].split('locations/')[1]]
        try:
            reviewsDict["reviews"].append({"source": "google",
                                           "concept": concept,
                                           "resvID": "NA",
                                           "actual_name": review["review"]["reviewer"]["displayName"],
                                           "created": review["review"]["createTime"],
                                           "notes": review["review"]["comment"],
                                           "stars": numberDict[review["review"]["starRating"]],
                                           "reviewDate": review["review"]["createTime"].split('T')[0]}
                                          )
            # print(f'{concept} | {review["review"]["starRating"]} | {review["review"]["reviewer"]["displayName"]} | {review["review"]["comment"]}')
        except:
            reviewsDict["reviews"].append({"source": "google",
                                           "concept": concept,
                                           "resvID": "NA",
                                           "actual_name": review["review"]["reviewer"]["displayName"],
                                           "created": review["review"]["createTime"],
                                           "notes": None,
                                           "stars": numberDict[review["review"]["starRating"]],
                                           "reviewDate": review["review"]["createTime"].split('T')[0]}
                                          )
            # print(f'{concept} | {review["review"]["starRating"]} | {review["review"]["reviewer"]["displayName"]} | NA')

    return reviewsDict