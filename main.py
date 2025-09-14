from fastapi import FastAPI
from routes import register_routes
import uvicorn


app=FastAPI()
register_routes(app)
@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":

    uvicorn.run('main:app', host="0.0.0.0", port=18000,reload=True)