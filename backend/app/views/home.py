from .router import router

@router.get("/")
async def read_root():
    return {"Hello": "World"}
