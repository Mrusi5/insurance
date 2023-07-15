from datetime import date, datetime

import json
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from src.models import InsuranceEntry
from src.schemas import InsuranceRequestSchema
from src.database import init_db, close_db
from src.schemas import InsuranceRequestSchema


app = FastAPI()
templates = Jinja2Templates(directory="src/templates")


main_file = "src/tariffs.json"


def load_tariffs():
    with open(main_file, 'r') as f:
        return json.load(f)
    
# Создание списка тарифов из данных в формате JSON
tariffs = load_tariffs()

# Инициализация базы данных
@app.on_event("startup")
async def startup_event():
    await init_db()

# Закрытие базы данных
@app.on_event("shutdown")
async def shutdown_event():
    await close_db()
 



@app.post("/upload_tariffs")
async def upload_tariffs(date: date, file: UploadFile = File(...)):
    try:
        contents = await file.read()
        tariffs[date.isoformat()] = json.loads(contents.decode('utf-8'))

        with open(main_file, 'w') as f:
            json.dump(tariffs, f, indent=4)

        return {'message': 'Tariffs uploaded successfully'}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload tariffs: {str(e)}")

    
@app.get("/tariffs.json")
def get_tariffs_json():
    try:
        with open("src/tariffs.json", "r") as json_file:
            data = json.load(json_file)
        
        return JSONResponse(content=data)
    except FileNotFoundError:
        return JSONResponse(content={"error": "File not found"}, status_code=404)


@app.post("/home")
async def calculate_insurance_cost(cargo: InsuranceRequestSchema):
    cargo_type = cargo.cargo_type
    declared_value = cargo.declared_value
    date = cargo.date

    date_ranges = list(tariffs.keys())
    date_ranges.sort()
    date_range = None
    if date >= datetime.strptime(date_ranges[-1], "%Y-%m-%d").date():
        date_range = date_ranges[-1]
    else:
        for i in range(len(date_ranges) - 1):
            start_date = datetime.strptime(date_ranges[i], "%Y-%m-%d").date()
            end_date = datetime.strptime(date_ranges[i+1], "%Y-%m-%d").date()
            if start_date <= date < end_date:
                date_range = date_ranges[i]
                break

    if date_range is None:
        return {"error": "Invalid date"}

    tariffs_for_date = tariffs[date_range]
    
    if cargo_type not in [t["cargo_type"] for t in tariffs_for_date]:
        return {"error": "Invalid cargo type"}

    for tariff in tariffs_for_date:
        if tariff["cargo_type"] == cargo_type:
            insurance_cost = declared_value * tariff["rate"]

            # Создание экземпляра модели InsuranceEntry
            insurance_entry = InsuranceEntry(
            cargo_type=cargo_type,
            declared_value=declared_value,
            insurance_date=date,
            insurance_amount=insurance_cost
            )    

            # Сохранение записи в базе данных
            await insurance_entry.save()

            
            return {"insurance_cost": insurance_cost}

    return {"error": "An error occurred while calculating the insurance cost"}

    

@app.get("/home")
def home(request: Request, insurance_cost: float = 0):
    return templates.TemplateResponse("home.html", {"request": request, "insurance_cost": insurance_cost})