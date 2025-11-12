from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello, FastAPI!"}

@app.get("/home/{name}")
def s_hello(name: str):
    return {"message": f"Hello, {name}! Welcome to FastAPI."}

@app.get("/about")
def about():
    return {
        "project": "FastAPI Demo App",
        "version": "1.0",
        "developer": "Tanishq",
        "description": "A simple FastAPI project demonstrating basic routes."

    }