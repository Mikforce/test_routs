# docker build -t your-image-name .
# docker run -p 8000:8000 your-image-name
# http://127.0.0.1:8000/
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from database import Base, Location, SessionLocal, Location_id
from fastapi_caching import FastAPICache
import uvicorn

app = FastAPI()


@app.get('/')
def index():
    return {"message": "Привет, мир! Это тестовое задание"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload_route", tags=["routes"]) # метод для загрузки данных о расположениях из CSV файла в базу данных.
async def upload_route(csv_file: UploadFile = File(...), db: Base = Depends(get_db)):
    data = await csv_file.read()

    try:
        decoded_data = data.decode('utf-8')
        lines = decoded_data.split("\n")
        print(len(lines))
        for line in lines[1:]:
            columns = line.split(",")
            if len(columns) >= 16:  # Добавляем проверку на минимальную длину списка
                # Добавляем проверку на пустую строку перед преобразованием
                population = int(columns[8]) if columns[8].strip() else 0
                density = float(columns[9]) if columns[9].strip() else 0.0

                location_data = {
                    "zip": columns[0],
                    "lat": float(columns[1]),
                    "lng": float(columns[2]),
                    "city": columns[3],
                    "state_id": columns[4],
                    "state_name": columns[5],
                    "zcta": True if columns[6].lower() == 'true' else False,
                    "parent_zcta": columns[7],
                    "population": population,
                    "density": density,
                    "county_fips": columns[10],
                    "county_name": columns[11],
                    "county_weights": columns[12],
                    "county_names_all": columns[13],
                    "county_fips_all": columns[14],
                    "imprecise": True if columns[15].lower() == 'true' else False
                }
                location = Location(**location_data)
                db.add(location)

        db.commit()
        return {"message": "Route points uploaded and saved to the database successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not process CSV file: {str(e)}")


@app.get("/locations", tags=["routes"]) # метод для получения всех расположений из базы данных.
def get_locations(db: SessionLocal = Depends(get_db)):
    locations = db.query(Location).all()
    return locations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

@app.get("/sorted_locations", tags=["routes"]) # метод для сортировки расположений по state_id и сохранения их в другую таблицу Location_id
def sort_locations(db: Session = Depends(get_db)):
    locations = db.query(Location).order_by(Location.state_id).all()

    sorted_routes = []
    current_state_id = None
    current_points = []

    for location in locations:
        if location.state_id != current_state_id:
            if current_state_id:
                # Сортируем точки в порядке возрастания широты
                current_points.sort(key=lambda x: x["lat"])
                sorted_routes.append({"id": current_state_id, "points": current_points})

                current_points = []  # Сбрасываем текущие точки

            current_state_id = location.state_id

        current_points.append({"lat": location.lat, "lng": location.lng})

    if current_state_id:
        # Сортируем точки в порядке возрастания широты для последнего state_id
        current_points.sort(key=lambda x: x["lat"])
        sorted_routes.append({"id": current_state_id, "points": current_points})

    try:
        for idx, route in enumerate(sorted_routes, start=1):
            location_id = Location_id(id=idx, point=str(route["points"]))
            db.add(location_id)

        db.commit()  # Сохраняем все точки одновременно

    except IntegrityError as e:
        db.rollback()
        return {"error": "IntegrityError occurred. Rollback transaction."}

    return sorted_routes


@app.get("/locations_id", tags=["routes"])
def get_locations(db: SessionLocal = Depends(get_db)):
    locations = db.query(Location_id).all()
    return locations


cache = FastAPICache()
@app.get("/api/routes/{id}", tags=["routes"])
@cache.cache()
def get_optimal_route_by_id(id: int, db: Session = Depends(get_db)):
    location_id = db.query(Location_id).filter(Location_id.id == id).first()

    if not location_id:
        raise HTTPException(status_code=404, detail="Route not found")

    return {"id": location_id.id, "points": eval(location_id.point)}

@app.delete("/api/routes/{id}", tags=["routes"])
def delete_route_by_id(id: int, db: Session = Depends(get_db)):  # метод для удаления маршрута по ID.
    location_id = db.query(Location_id).filter(Location_id.id == id).first()

    if not location_id:
        raise HTTPException(status_code=404, detail="Route not found")

    db.delete(location_id)
    db.commit()

    return {"message": f"Route with ID {id} has been deleted"}

@app.delete("/api/routes/delete_all", tags=["routes"])
def delete_all_routes(db: Session = Depends(get_db)): # метод для удаления всех маршрутов в таблице Location_id.
    db.query(Location_id).delete()
    db.commit()

    return {"message": "All routes have been deleted"}
if __name__ == '__main__':
    uvicorn.run(app, host="localhost", port=8000)