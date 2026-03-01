from fastapi import FastAPI
from database import Base, engine
from routers import movies, reviews, tags, analytics

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CineMetrics API",
    description="A movie analytics and review API powered by TMDB",
    version="1.0.0"
)

app.include_router(movies.router)
app.include_router(reviews.router)
app.include_router(tags.router)
app.include_router(analytics.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to CineMetrics API",
        "docs": "/docs",
        "version": "1.0.0"
    }