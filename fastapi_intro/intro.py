from time import sleep
from datetime import datetime

from fastapi import FastAPI
from fastapi import Query, Path, Body, HTTPException, BackgroundTasks

from pydantic import BaseModel, Field

from starlette.responses import Response
from starlette.status import HTTP_201_CREATED

from typing import Optional, List


app = FastAPI()

@app.get('/') # methodとendpointの指定
async def hello():
    return {"text": "hello world!"}

@app.get('/get/{path}')
async def path_and_query_params(
    path: str,
    query: int,
    default_none: Optional[str] = None):
    return {"text": f"hellw, {path}, {query} and {default_none}"}

@app.get('/validtation/{path}')
async def vatlidation(
    string: str = Query(None, min_length=2, max_length=5, regex=r'[a-c]+.'),
    integer: int = Query(..., gt=1, le=3), # required
    alias_query: str = Query('default', alias='alias-query'),
    path: int = Path(10)):

    return {"string": string, "integer": integer, "alias-query": alias_query, "path": path}

class Data(BaseModel):
    """request data用の型ヒントがされたクラス"""
    string: str
    default_none: Optional[int] = None
    lists: List[int]

@app.post('/post')
async def declare_request_body(data: Data):
    return {"text": f"hello, {data.string}, {data.default_none}, {data.lists}"}

@app.post('/post/embed')
async def declare_embedded_request_body(data: Data=Body(..., embed=True)):
    return {"text": f"hello, {data.string}, {data.default_none}, {data.lists}"}

class subDict(BaseModel):
    strings: str
    integer: int

class NestedData(BaseModel):
    subData: subDict
    subDataList: List[subDict]

@app.post('/post/nested')
async def declare_nested_request_body(data: NestedData):
    return {"text": f"hello, {data.subData}, {data.subDataList}"}

class ValidationSubData(BaseModel):
    strings: str = Field(None, min_length=2, max_length=5, regex=r'[a-b]+.')
    integer: int = Field(..., gt=1, le=3) # required

class ValidatedNestedData(BaseModel):
    subData: ValidationSubData = Field(..., example={"strings": "aaa", "integer": 2})
    subDataList: List[ValidationSubData] = Field(...)

@app.post('/validation')
async def validation(data: ValidatedNestedData):
    return {'text': f"hello, {data.subData}, {data.subDataList}"}

class ItemOut(BaseModel):
    strings: str
    aux: int = 1
    text: str

@app.get('/', response_model=ItemOut)
async def response(strings: str, integer: int):
    return {"text": "hello world!", "strings": strings, "integer": integer}

# 辞書に存在しない場合にresponse_modelのattributesのデフォルト値を"入れない"
@app.get('/unset', response_model=ItemOut, response_model_exclude_unset=True)
async def response_exclued_unset(strings: str, integer: int):
    return {"text": "hello world!", "strings": strings, "integer": integer}

# response_modelの"strings", "aux"を無視 → "text"のみ返す
@app.get('/exclude', response_model=ItemOut, response_model_exclude={"strings", "aux"})
async def reponse_exclude(strings: str, integer: int):
    return {"text": "hello world!", "strings": strings, "integer": integer}

# response_modelの"text"のみ考慮する → "text"のみ返す
@app.get('/include', response_model=ItemOut, response_model_include={"text"})
async def reponse_include(strings: str, integer: int):
    return {"text": "hello world!", "strings": strings, "integer": integer}

@app.get('/status', status_code=200)
async def response_status_code(integer: int, response: Response):
    if integer > 5:
        # error handling
        raise HTTPException(status_code=404, detail="this is error messages")
    elif integer == 1:
        # set manually
        response.status_code = HTTP_201_CREATED
        return {"text": "hello world, created!"}
    else:
        # default status code
        return {"text": "hello world!"}

def time_bomb(count: int):
    sleep(count)
    print(f"bomb! {datetime.utcnow()}")

@app.get('/{count}')
async def back(count: int, background_tasks: BackgroundTasks):
    background_tasks.add_task(time_bomb, count)
    return {"text": "finish"}