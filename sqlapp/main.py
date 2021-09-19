from typing import List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()

"""
------------------- User model endpoints -------------------
"""

@app.post('/users/', response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
	db_user = crud.get_user_by_email(db, email=user.email)
	if db_user:
		raise HTTPException(status_code=400, detail='Email already registered!')
	return crud.create_user(db=db, user=user)


@app.get('/users/', response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
	users = crud.get_users(db, skip=skip, limit=limit)
	return users


@app.get('/users/{user_id}/', response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
	db_user = crud.get_user(db, user_id=user_id)
	if db_user is None:
		raise HTTPException(status_code=404, detail='User not found')
	return db_user


"""
------------------- Item model endpoints -------------------
"""

@app.post('/users/{user_id}/items/', response_model=schemas.Item)
def create_item_for_user(
		user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)):
	return crud.create_user_item(db=db, item=item, user_id=user_id)
	

@app.get('/items/', response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
	items = crud.get_items(db, skip=skip, limit=limit)
	return items


@app.get('/items/{item_id}/', response_model=schemas.Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
	db_item = crud.get_item(db, item_id=item_id)
	if db_item is None:
		raise HTTPException(status_code=404, detail='Item not found')
	return db_item


@app.delete('/items/{item_id}/', status_code=200)
def delete_item(item_id: int, db: Session = Depends(get_db)):
	db_item = crud.get_item(db, item_id=item_id)
	
	if db_item is None:
		raise HTTPException(status_code=404, detail='Item not found')
	
	db.delete(db_item)
	db.commit()
	return []