from fastapi import FastAPI, Depends
from Database import Base, engine
from user.Route import router as user_router
from message.Route import Route as Message_route
from fastapi.middleware.cors import CORSMiddleware
Origins = ["https://www.google.com"]



app = FastAPI(title="FastAPI Telegram", version="0.0.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=Origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
Base.metadata.create_all(bind=engine)
app.include_router(user_router)
app.include_router(Message_route)

# git init for starting git
# git add --all(or name of specefic file
# git commit -m "comment for commited files
# git branch -M main(branch name)
# git remote add origin(remotename)
# git edited
# git for your main reason
# git in this mainsd
#adnamdsoasndoasdn
# adsnkasdasdjlnalsdxqdsads;
