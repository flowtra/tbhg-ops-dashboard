import asyncio

from fastapi import FastAPI
from datetime import datetime
import apiFuncs
from apiFuncs import *
from googleLib import googleFuncs
import threading

app = FastAPI()

restNames = {'afterwit': 'aw',
             'elanew': 'ela',
             'thegreatmischief': 'tgm',
             'tipoosteria': 'to',
             'tipopastabar': 'tpb',
             'tipopizzeriaetrattoria': 'tpz',
             'tipostradakeongsaik': 'tsks',
             'tipostrada': 'tsn',
             'workingtitlelasalle': 'wtls',
             'workingtitleriverside': 'wtrs'}

venueIDs = {
        'ahNzfnNldmVucmREDACTED': 'Afterwit',
        'ahNzfnNldmVucmREDACTED': 'Ela Jalan Sultan',
        'ahNzfnNldmVucmREDACTED': 'The Great Mischief',
        'ahNzfnNldmVucmREDACTED': 'Tipo Osteria',
        'ahNzfnNldmVucmREDACTED': 'Tipo Pasta Bar',
        'ahNzfnNldmVucmREDACTED': 'Tipo Pizzeria',
        'ahNzfnNldmVucmREDACTED': 'Tipo Strada KS',
        'ahNzfnNldmVucmREDACTED': 'Tipo Strada Novena',
        'ahNzfnNldmVucmREDACTED': 'WT Lasalle',
        'ahNzfnNldmVucmREDACTED': 'WT Riverside',
        }


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

@app.get("/getNewLogin")
async def getNewLogin(oldSessionID: str):
    loginDict = getNewCookies(rf"{oldSessionID}")

    if loginDict["success"] == "true":
        with open("authCookies.ini", "w") as outFile:
            outFile.write(str(loginDict))
        return "True"
    elif loginDict["success"] == "false":
        return "False"


@app.get("/getLiveSeated")
async def getLiveSeated():
    dateNow = str(datetime.now().strftime("%d%m%Y"))
    allSeated = getAllRestaurantLiveSeated(restNames, dateNow)

    return allSeated

@app.get("/getAllProjectedSeated")
async def getAllProjSeated(date: str):
    allRestShiftsDict = getAllProjectedSeated(restNames, date)

    return allRestShiftsDict


@app.get("/checkResvAvailability")
async def getAllProjSeated(restName, pax: int, date: str, resvTime):
    restID = restNames[restName]
    print(restName, restID, pax, date, resvTime)
    canBook = checkResvAvailability(restName, restID, pax, date, resvTime)

    return {"available": canBook}


@app.get("/getAllSevenroomsReviews")
async def getAllProjSeated(start_date, end_date): #YYYY-MM-DD
    reviews = getAllSevenroomsReviews_clean(venueIDs, start_date, end_date)

    return reviews


@app.get("/getAllReviews")
async def getAllReviews(start_date, end_date): #YYYY-MM-DD
    sevenroomReviews = getAllSevenroomsReviews_clean(venueIDs, start_date, end_date)
    googleReviews = googleFuncs.getBatchReviews()
    allReviews = {key: sevenroomReviews.get(key, []) + googleReviews.get(key, []) for key in set(list(sevenroomReviews.keys()) + list(googleReviews.keys()))}

    allReviews["reviews"].sort(key=lambda x: x['created'], reverse=True)

    return allReviews
