from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, constr, conint, Field
from typing import List

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Список пользователей
users: List['User'] = []  # Используем строковую аннотацию для отложенной ссылки на класс User

# Модель пользователя
class User(BaseModel):
    id: int
    username: constr(min_length=1) = Field(..., title="Имя пользователя", description="Имя пользователя не должно быть пустым")
    age: conint(ge=18, le=120) = Field(..., title="Возраст", description="Возраст от 18 до 120 лет")

# Получение списка всех пользователей и отображение их в шаблоне
@app.get("/", response_class=HTMLResponse)
async def read_users(request: Request):
    return templates.TemplateResponse("users.html", {"request": request, "users": users})

# Получение информации о конкретном пользователе по ID
@app.get("/user/{user_id}", response_class=HTMLResponse)
async def get_user(request: Request, user_id: int):
    for user in users:
        if user.id == user_id:
            return templates.TemplateResponse("user.html", {"request": request, "user": user})
    raise HTTPException(status_code=404, detail="User was not found")

# Создание нового пользователя
@app.post("/user/", response_model=User, response_description="Пользователь зарегистрирован")
async def create_user(username: str, age: int):
    user_id = len(users) + 1  # Генерация id
    new_user = User(id=user_id, username=username, age=age)
    users.append(new_user)
    return new_user

# Обновление существующего пользователя
@app.put("/user/{user_id}", response_model=User, response_description="Пользователь обновлен")
async def update_user(user_id: int, username: str, age: int):
    for user in users:
        if user.id == user_id:
            user.username = username
            user.age = age
            return user
    raise HTTPException(status_code=404, detail="User was not found")

# Удаление пользователя
@app.delete("/user/{user_id}", response_description="Пользователь удален")
async def delete_user(user_id: int):
    for index, user in enumerate(users):
        if user.id == user_id:
            deleted_user = users.pop(index)
            return deleted_user
    raise HTTPException(status_code=404, detail="User was not found")

# Создание нескольких пользователей для тестирования
@app.on_event("startup")
async def startup_event():
    await create_user("UrbanUser", 24)
    await create_user("UrbanTest", 22)
    await create_user("Capybara", 60)
