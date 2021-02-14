from enum import Enum
from pymongo import MongoClient
from fastapi import FastAPI
from typing import Optional, List
from pydantic import BaseModel, HttpUrl
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from os import environ

load_dotenv()

class Category(str, Enum):
    solo = 'solo'
    assisted = 'assisted'


class Style(str, Enum):
    streaks = 'streaks'
    no_moving = 'no_moving'
    speedrun = 'speedrun'


class Name(str, Enum):
    nm = 'nm'
    nmpz = 'nmpz'
    ncnc = 'ncnc'


class Map(BaseModel):
    name: str
    link: HttpUrl


class Record(BaseModel):
    category: Category
    style: Style
    name: Name
    map_name: Map
    video: str
    time: Optional[str]
    score: Optional[str]
    streak: Optional[int]
    _id: Optional[str]


class Query(BaseModel):
    parameters: dict
    results: list


class Response(BaseModel):
    status_code: int = 200
    success: bool = True
    message: str
    data: dict
    data: Query 


client = MongoClient(environ["MONGO_URI"])
db = client.geoguessr_wr_api
collection = db["records"]

print(client)

app = FastAPI()


@app.get("/records", responses={200: {'model': Response}})
async def get_records_list(category: Optional[Category] = None, style: Optional[Style] = None, name: Optional[Name] = None, map_name: Optional[str] = None):
    print(category, style, name, map_name)

    query = {
        "category": category, 
        "style": style, 
        "name": name, 
        "map.name": map_name
    }

    filtered_query = {k:v for k,v in query.items() if v is not None}
    record_query_results = collection.find(filtered_query)

    record_query_results = list(record_query_results)
    for record in record_query_results:
        record['_id'] = str(record['_id'])

    return Response(
                status_code=200,
                message="Records for query",
                data=Query(parameters=query,results=record_query_results)
            )

@app.post("/add")
async def add_new_record(body: Record):
    print('Recieved: ' + body.json())
    returnBody = body.dict()

    id = collection.insert_one(body.dict()).inserted_id
    returnBody['_id'] = str(id)

    return Response(
                status_code=200,
                message="New record successfully added.",
                data=returnBody
            )


"""
    /records 

    queries:
    |-->  category (solo | assisted)
    |-->  style (streaks | no-moving | speedruns)
    |-->  name (nm | nmpz | ncnc)
    |-->  map (a-diverse-world-3 | a-balanced-world | an-improved-world)

    |-->  player (string)

    /records?category=solo&style=no-moving&name=nm&map=a-diverse-world-3

"""