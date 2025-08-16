from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

from ..database.database import SessionLocal
from ..database.models import UsageLog, User
from ..auth.utils import get_user_from_token

class UsageTrackerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, daily_limit: int = 10):
        super().__init__(app)
        self.daily_limit = daily_limit
        
    async def dispatch(self, request: Request, call_next):
        # Only track calculator endpoints, but skip example endpoints
        if (not request.url.path.startswith("/api/calculators/calculate") or 
            request.url.path.endswith("/example")):
            return await call_next(request)
            
        db = SessionLocal()
        try:
            # Get user info
            user = None
            ip_address = request.client.host if request.client else "unknown"
            
            # Try to get user from auth token (skip errors to allow anonymous usage)
            try:
                auth_header = request.headers.get("Authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    token = auth_header.split(" ")[1]
                    user = get_user_from_token(db, token)
            except:
                # Ignore auth errors for anonymous usage
                pass
            
            # Check usage limits (with better error handling)
            try:
                usage_limit_ok = self._check_usage_limit(db, user, ip_address)
                if not usage_limit_ok:
                    raise HTTPException(
                        status_code=429,
                        detail={
                            "error": "Usage limit exceeded",
                            "message": f"Daily limit of {self.daily_limit} calculations reached",
                            "requires_auth": user is None,
                            "upgrade_needed": user is not None and not user.is_premium
                        }
                    )
            except HTTPException:
                raise
            except Exception as e:
                # If usage checking fails, allow the request but log the error
                print(f"Usage limit check failed: {e}")
                pass
            
            # Process the request
            response = await call_next(request)
            
            # Log successful calculation (skip errors to not break functionality)
            try:
                calculator_type = request.url.path.split('/')[-1]
                self._log_usage(db, user, ip_address, calculator_type, True)
            except:
                # Ignore logging errors
                pass
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            # For any other errors, just pass through without logging to avoid breaking functionality
            db.close()
            return await call_next(request)
        finally:
            try:
                db.close()
            except:
                pass
    
    def _check_usage_limit(self, db: Session, user: User, ip_address: str) -> bool:
        try:
            # Premium users have unlimited access
            if user and user.is_premium:
                return True
                
            # Check usage in last 24 hours
            since = datetime.utcnow() - timedelta(days=1)
            
            if user:
                # Registered user - check by user_id
                usage_count = db.query(UsageLog).filter(
                    UsageLog.user_id == user.id,
                    UsageLog.timestamp >= since,
                    UsageLog.success == True
                ).count()
            else:
                # Anonymous user - check by IP
                usage_count = db.query(UsageLog).filter(
                    UsageLog.ip_address == ip_address,
                    UsageLog.user_id.is_(None),
                    UsageLog.timestamp >= since,
                    UsageLog.success == True
                ).count()
            
            return usage_count < self.daily_limit
        except Exception as e:
            # If anything goes wrong with usage checking, allow the request
            print(f"Usage limit check error: {e}")
            return True
    
    def _log_usage(self, db: Session, user: User, ip_address: str, calculator_type: str, success: bool):
        usage_log = UsageLog(
            user_id=user.id if user else None,
            ip_address=ip_address,
            calculator_type=calculator_type,
            success=success
        )
        db.add(usage_log)
        db.commit()