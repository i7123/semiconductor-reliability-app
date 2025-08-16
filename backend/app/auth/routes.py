from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from ..database.database import get_db
from ..database.models import User, UsageLog
from . import schemas, utils

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=schemas.Token)
async def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    user = utils.create_user(db, user_data.email, user_data.password)
    
    # Create access token
    access_token = utils.create_access_token(data={"user_id": user.id})
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=schemas.Token)
async def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = utils.authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = utils.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.User)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    user = utils.get_user_from_token(db, credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

@router.get("/usage", response_model=schemas.UsageStatus)
async def get_usage_status(
    request: Request,
    db: Session = Depends(get_db)
):
    user = None
    ip_address = request.client.host if request.client else "unknown"
    
    # Try to get user from auth token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            user = utils.get_user_from_token(db, token)
        except:
            # Ignore auth errors for anonymous usage
            pass
    
    # Get usage in last 24 hours
    since = datetime.utcnow() - timedelta(days=1)
    
    if user:
        usage_count = db.query(UsageLog).filter(
            UsageLog.user_id == user.id,
            UsageLog.timestamp >= since,
            UsageLog.success == True
        ).count()
    else:
        usage_count = db.query(UsageLog).filter(
            UsageLog.ip_address == ip_address,
            UsageLog.user_id.is_(None),
            UsageLog.timestamp >= since,
            UsageLog.success == True
        ).count()
    
    daily_limit = 10  # Same as middleware
    if user and user.is_premium:
        daily_limit = 1000  # High limit for premium users
    
    # Prepare the response data
    response_data = {
        'daily_usage': usage_count,
        'daily_limit': daily_limit,
        'is_premium': False,
        'usage_remaining': max(0, daily_limit - usage_count),
        'reset_time': datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    }
    
    # Update is_premium if user is authenticated
    if user:
        response_data['is_premium'] = user.is_premium
    
    return schemas.UsageStatus(**response_data)

@router.post("/upgrade")
async def upgrade_to_premium(
    request: Request,
    db: Session = Depends(get_db)
):
    # Get user from auth token
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization token required")
    
    token = auth_header.split(" ")[1]
    user = utils.get_user_from_token(db, token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # In a real app, you'd integrate with a payment processor here
    # For demo purposes, we'll just upgrade the user
    user.is_premium = True
    db.commit()
    db.refresh(user)  # Refresh to get updated data
    
    premium_token = utils.generate_premium_token(db, user.id)
    
    return {
        "message": "Successfully upgraded to premium",
        "premium_token": premium_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "is_premium": user.is_premium,
            "created_at": user.created_at
        }
    }