from fastapi import FastAPI
from api import router 
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()

# Include the routes from the API module
app.include_router(router)

# Static files if needed
app.mount("/static", StaticFiles(directory="app/static"), name="static")


if __name__ == '__main__':
    # Start a uvicorn server
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)