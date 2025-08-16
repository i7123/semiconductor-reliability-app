from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel

class CalculatorInput(BaseModel):
    pass

class CalculatorOutput(BaseModel):
    pass

class InputField(BaseModel):
    name: str
    label: str
    type: str  # "float", "int", "select", "bool"
    unit: str = ""
    description: str = ""
    required: bool = True
    min_value: float = None
    max_value: float = None
    options: List[str] = []  # For select type
    default_value: Any = None

class CalculatorInfo(BaseModel):
    id: str
    name: str
    description: str
    category: str
    input_fields: List[InputField]

class BaseCalculator(ABC):
    """Base class for all semiconductor reliability calculators"""
    
    @property
    @abstractmethod
    def info(self) -> CalculatorInfo:
        """Return calculator information including input fields"""
        pass
    
    @abstractmethod
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Perform the calculation and return results"""
        pass
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input values against field definitions"""
        validated = {}
        errors = []
        
        for field in self.info.input_fields:
            value = inputs.get(field.name)
            
            # Check required fields
            if field.required and (value is None or value == ""):
                errors.append(f"{field.label} is required")
                continue
            
            # Skip validation for optional empty fields
            if not field.required and (value is None or value == ""):
                continue
                
            # Type validation and conversion
            try:
                if field.type == "float":
                    value = float(value)
                elif field.type == "int":
                    value = int(value)
                elif field.type == "bool":
                    value = bool(value)
                elif field.type == "select":
                    if value not in field.options:
                        errors.append(f"{field.label} must be one of: {', '.join(field.options)}")
                        continue
            except (ValueError, TypeError):
                errors.append(f"{field.label} must be a valid {field.type}")
                continue
            
            # Range validation
            if field.type in ["float", "int"]:
                if field.min_value is not None and value < field.min_value:
                    errors.append(f"{field.label} must be >= {field.min_value}")
                    continue
                if field.max_value is not None and value > field.max_value:
                    errors.append(f"{field.label} must be <= {field.max_value}")
                    continue
            
            validated[field.name] = value
        
        if errors:
            raise ValueError("; ".join(errors))
        
        return validated