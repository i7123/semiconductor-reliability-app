"""
Simplified FastAPI application for Vercel deployment
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import math
import os

app = FastAPI(
    title="Semiconductor Reliability Calculator API",
    description="API for reliability calculations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Semiconductor Reliability Calculator API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/health")
async def api_health_check():
    return {"status": "healthy"}

@app.post("/api/calculators/calculate/mtbf")
async def calculate_mtbf(data: dict):
    """MTBF Calculator"""
    try:
        inputs = data.get("inputs", {})
        failure_rate = float(inputs.get("failure_rate", 0.0001))
        confidence_level = int(inputs.get("confidence_level", 95))
        operating_hours = float(inputs.get("operating_hours", 8760))
        
        # Basic MTBF calculation
        mtbf_hours = 1 / failure_rate if failure_rate > 0 else float('inf')
        mtbf_years = mtbf_hours / (365.25 * 24)
        
        # Reliability calculation
        reliability = math.exp(-failure_rate * operating_hours)
        unreliability = 1 - reliability
        
        results = {
            "mtbf_hours": mtbf_hours,
            "mtbf_years": round(mtbf_years, 4),
            "failure_rate": failure_rate,
            "confidence_level": confidence_level,
            "reliability": round(reliability, 6),
            "unreliability": round(unreliability, 6),
            "reliability_percent": round(reliability * 100, 2),
            "operating_hours": operating_hours
        }
        
        return {
            "calculator_id": "mtbf",
            "inputs": inputs,
            "results": results,
            "success": True,
            "message": "Calculation completed successfully"
        }
        
    except Exception as e:
        return {
            "calculator_id": "mtbf",
            "success": False,
            "error": str(e)
        }

@app.get("/api/calculators/")
async def list_calculators():
    """List available calculators"""
    return [
        {
            "id": "mtbf",
            "name": "MTBF Calculator",
            "description": "Calculate Mean Time Between Failures with reliability analysis",
            "category": "Reliability",
            "input_fields": [
                {
                    "name": "failure_rate",
                    "label": "Failure Rate (failures per hour)",
                    "type": "float",
                    "required": True,
                    "default_value": 0.0001,
                    "min_value": 0.000001,
                    "max_value": 1.0
                },
                {
                    "name": "operating_hours",
                    "label": "Operating Hours",
                    "type": "float",
                    "required": False,
                    "default_value": 8760,
                    "min_value": 1
                },
                {
                    "name": "confidence_level",
                    "label": "Confidence Level (%)",
                    "type": "select",
                    "options": ["90", "95", "99"],
                    "default_value": "95",
                    "required": True
                }
            ]
        },
        {
            "id": "dummy_calculator_1",
            "name": "Advanced Stress Analysis",
            "description": "Comprehensive stress testing analysis for semiconductor components",
            "category": "Future Development",
            "input_fields": []
        },
        {
            "id": "dummy_calculator_2", 
            "name": "Burn-in Optimization",
            "description": "Optimize burn-in parameters for maximum defect detection",
            "category": "Future Development",
            "input_fields": []
        },
        {
            "id": "dummy_calculator_3",
            "name": "Lifetime Data Analysis",
            "description": "Statistical analysis of component lifetime data with multiple distributions",
            "category": "Future Development", 
            "input_fields": []
        }
    ]

@app.get("/api/calculators/{calculator_id}/info")
async def get_calculator_info(calculator_id: str):
    """Get calculator information"""
    calculators = await list_calculators()
    for calc in calculators:
        if calc["id"] == calculator_id:
            return calc
    return {"error": "Calculator not found"}, 404

# For Vercel
handler = app