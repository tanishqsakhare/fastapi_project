from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello, fastapi"}

@app.get("/name")
def home():
    return {"message": "My name is Tanishq"}