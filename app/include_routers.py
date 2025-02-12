from app.routes.users import router as user_router
from app.routes.sensors import router as sensor_router
from app.routes.auth import router as auth_router

def include_routers(app):
    app.include_router(user_router, prefix="/users", tags=["Users"])
    app.include_router(auth_router, prefix="/auth", tags=["Auth"])
    app.include_router(sensor_router, prefix="/sensors", tags=["Sensors"])

    return app