from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def index(): return {"name: “First Data"}





def main():
    print("Hello World!")

if __name__ == "__main__":
    main()