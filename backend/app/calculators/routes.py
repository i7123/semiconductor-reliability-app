from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from pydantic import BaseModel

from . import get_calculator, list_calculators
from .base import CalculatorInfo

router = APIRouter()

class CalculationRequest(BaseModel):
    inputs: Dict[str, Any]

class CalculationResponse(BaseModel):
    calculator_id: str
    inputs: Dict[str, Any]
    results: Dict[str, Any]
    success: bool
    message: str = ""

@router.get("/", response_model=List[CalculatorInfo])
async def get_available_calculators():
    """Get list of all available calculators with their input field definitions"""
    return list_calculators()

@router.get("/{calculator_id}/info", response_model=CalculatorInfo)
async def get_calculator_info(calculator_id: str):
    """Get detailed information about a specific calculator"""
    try:
        calculator = get_calculator(calculator_id)
        return calculator.info
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/calculate/{calculator_id}", response_model=CalculationResponse)
async def calculate(calculator_id: str, request: CalculationRequest):
    """Perform calculation using the specified calculator"""
    try:
        calculator = get_calculator(calculator_id)
        results = calculator.calculate(request.inputs)
        
        return CalculationResponse(
            calculator_id=calculator_id,
            inputs=request.inputs,
            results=results,
            success=True,
            message="Calculation completed successfully"
        )
    
    except ValueError as e:
        # Input validation errors
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid input",
                "message": str(e),
                "calculator_id": calculator_id
            }
        )
    except Exception as e:
        # Other calculation errors
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Calculation failed",
                "message": "An error occurred during calculation",
                "calculator_id": calculator_id
            }
        )

@router.get("/calculate/{calculator_id}/example")
async def get_calculation_example(calculator_id: str):
    """Get example inputs and expected outputs for a calculator"""
    try:
        calculator = get_calculator(calculator_id)
        
        # Generate example inputs based on field definitions
        example_inputs = {}
        for field in calculator.info.input_fields:
            if field.default_value is not None:
                example_inputs[field.name] = field.default_value
            elif field.type == "float":
                if field.name == "failure_rate":
                    example_inputs[field.name] = 0.0001
                elif field.name == "activation_energy":
                    example_inputs[field.name] = 0.7
                elif field.name.endswith("temperature") or "temp" in field.name:
                    example_inputs[field.name] = 25.0 if "use" in field.name else 125.0
                elif "reliability" in field.name:
                    example_inputs[field.name] = 0.95
                elif "time" in field.name or "duration" in field.name:
                    example_inputs[field.name] = 8760.0
                elif field.name == "target_mtbf":
                    example_inputs[field.name] = 1000.0
                elif field.name == "test_duration":
                    example_inputs[field.name] = 100.0
                elif field.name == "target_time":
                    example_inputs[field.name] = 2000.0
                elif field.name == "total_test_time":
                    example_inputs[field.name] = 1500.0
                else:
                    example_inputs[field.name] = 1.0
            elif field.type == "int":
                if field.name == "max_failures":
                    example_inputs[field.name] = 0
                else:
                    example_inputs[field.name] = 10
            elif field.type == "select" and field.options:
                example_inputs[field.name] = field.options[0]
            elif field.type == "bool":
                example_inputs[field.name] = True
            elif field.type == "text":
                if field.name == "failure_times":
                    example_inputs[field.name] = "100, 250, 480, 750, 1200, 1800"
        
        # Calculate example results
        example_results = calculator.calculate(example_inputs)
        
        return {
            "calculator_id": calculator_id,
            "example_inputs": example_inputs,
            "example_results": example_results,
            "description": f"Example calculation for {calculator.info.name}"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate example for {calculator_id}"
        )