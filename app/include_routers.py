from app.routes.users import router as user_router
from app.routes.sensors import router as sensor_router
from app.routes.auth import router as auth_router
from app.routes.flowers import router as flower_router
from app.routes.chart import router as chart_router
from app.routes.notification import router as notification_router
from app.routes.image import router as image_router

def include_routers(app):
    app.include_router(user_router, prefix="/users", tags=["Users"])
    app.include_router(auth_router, prefix="/auth", tags=["Auth"])
    app.include_router(sensor_router, prefix="/sensors", tags=["Sensors"])
    app.include_router(flower_router, prefix="/flower", tags=["Flower prefab: not sensors!"])
    app.include_router(chart_router, prefix="/chart", tags=["Charts endpoints"])
    app.include_router(notification_router, prefix="/notification", tags=["Notification"])
    app.include_router(image_router, prefix="/image", tags=["Image"])

    return app