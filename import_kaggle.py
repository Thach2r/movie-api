import csv
from database import SessionLocal, engine, Base
from models import BoxOfficeMovie

Base.metadata.create_all(bind=engine)

def import_movies():
    db = SessionLocal()
    count = 0
    skipped = 0

    with open("movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                year = int(row["year"]) if row["year"] else None
                gross = float(row["gross"]) if row["gross"] else None
                budget = float(row["budget"]) if row["budget"] else None
                score = float(row["score"]) if row["score"] else None
                votes = float(row["votes"]) if row["votes"] else None
                runtime = float(row["runtime"]) if row["runtime"] else None

                # Skip rows missing key fields
                if not year or not gross or gross <= 0:
                    skipped += 1
                    continue

                movie = BoxOfficeMovie(
                    name=row["name"],
                    genre=row["genre"],
                    year=year,
                    score=score,
                    votes=votes,
                    director=row["director"],
                    star=row["star"],
                    country=row["country"],
                    budget=budget,
                    gross=gross,
                    company=row["company"],
                    runtime=runtime
                )
                db.add(movie)
                count += 1

            except Exception as e:
                skipped += 1
                continue

        db.commit()

    print(f"Successfully imported: {count} movies")
    print(f"Skipped (missing data): {skipped} movies")
    db.close()

if __name__ == "__main__":
    import_movies()