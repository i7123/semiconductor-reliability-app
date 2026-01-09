"""
Calculator implementations for the Semiconductor Reliability API
"""
import math

def calculate_stress_analysis(inputs: dict) -> dict:
    """Advanced Stress Analysis Calculator"""
    temperature = float(inputs.get("temperature", 25.0))
    voltage = float(inputs.get("voltage", 3.3))
    current = float(inputs.get("current", 0.1))
    duration = float(inputs.get("duration", 1000))
    
    # Calculate power and thermal stress
    power = voltage * current
    thermal_stress = max(0, temperature - 25) * 0.1
    
    # Calculate failure rate (simplified model)
    base_failure_rate = 1e-6
    temp_factor = math.exp((temperature - 25) / 10)
    voltage_factor = (voltage / 3.3) ** 2
    failure_rate = base_failure_rate * temp_factor * voltage_factor
    
    return {
        "calculator_id": "stress_analysis",
        "success": True,
        "results": {
            "power_dissipation": power,
            "thermal_stress": thermal_stress,
            "failure_rate": failure_rate,
            "reliability": math.exp(-failure_rate * duration) * 100,
            "temperature": temperature,
            "voltage": voltage,
            "current": current,
            "duration": duration
        },
        "metadata": {
            "units": {
                "power_dissipation": "W",
                "thermal_stress": "arbitrary units",
                "failure_rate": "failures/hour",
                "reliability": "%",
                "temperature": "°C",
                "voltage": "V",
                "current": "A",
                "duration": "hours"
            },
            "descriptions": {
                "power_dissipation": "Power dissipation in the device",
                "thermal_stress": "Relative thermal stress level",
                "failure_rate": "Estimated failure rate",
                "reliability": f"Reliability over {duration} hours",
                "temperature": "Operating temperature",
                "voltage": "Operating voltage",
                "current": "Operating current",
                "duration": "Test duration"
            }
        }
    }

def calculate_burn_in(inputs: dict) -> dict:
    """Burn-in Optimization Calculator"""
    batch_size = int(inputs.get("batch_size", 1000))
    defect_density = float(inputs.get("defect_density", 100.0))
    temp_high = float(inputs.get("temp_high", 125.0))
    temp_low = float(inputs.get("temp_low", -40.0))
    
    # Calculate expected defects and yield
    expected_defects = (defect_density / 1e6) * batch_size
    yield_percentage = (1 - (expected_defects / batch_size)) * 100
    
    # Calculate temperature cycling effectiveness
    temp_range = temp_high - temp_low
    effectiveness = min(100, (temp_range / 100) * 10)
    
    return {
        "calculator_id": "burn_in",
        "success": True,
        "results": {
            "expected_defects": expected_defects,
            "yield_percentage": yield_percentage,
            "temp_range": temp_range,
            "effectiveness": effectiveness,
            "batch_size": batch_size,
            "defect_density": defect_density,
            "temp_high": temp_high,
            "temp_low": temp_low
        },
        "metadata": {
            "units": {
                "expected_defects": "units",
                "yield_percentage": "%",
                "temp_range": "°C",
                "effectiveness": "%",
                "batch_size": "units",
                "defect_density": "DPM",
                "temp_high": "°C",
                "temp_low": "°C"
            },
            "descriptions": {
                "expected_defects": "Expected number of defective units",
                "yield_percentage": "Expected yield percentage",
                "temp_range": "Temperature range for burn-in",
                "effectiveness": "Estimated effectiveness of burn-in",
                "batch_size": "Number of units in batch",
                "defect_density": "Defect density in defects per million",
                "temp_high": "High temperature for burn-in",
                "temp_low": "Low temperature for burn-in"
            }
        }
    }

def calculate_lifetime_analysis(inputs: dict) -> dict:
    """Lifetime Data Analysis Calculator"""
    distribution_type = inputs.get("distribution_type", "Weibull")
    sample_data = [float(x.strip()) for x in inputs.get("sample_data", "1000,1200,1500,1800,2000").split(",") if x.strip()]
    confidence_level = int(inputs.get("confidence_level", 95))
    censoring = inputs.get("censoring", "Right")
    
    if not sample_data:
        raise ValueError("Sample data cannot be empty")
    
    # Basic statistics
    n = len(sample_data)
    mean_life = sum(sample_data) / n
    sorted_data = sorted(sample_data)
    median_life = sorted_data[n//2] if n % 2 == 1 else (sorted_data[n//2-1] + sorted_data[n//2])/2
    
    # Calculate failure rate (assuming exponential distribution for simplicity)
    total_hours = sum(sample_data)
    failure_rate = n / total_hours if total_hours > 0 else 0
    
    # Calculate confidence bounds (simplified)
    z_scores = {90: 1.645, 95: 1.96, 99: 2.576}
    z = z_scores.get(confidence_level, 1.96)
    std_dev = (sum((x - mean_life) ** 2 for x in sample_data) / (n - 1)) ** 0.5 if n > 1 else 0
    margin_of_error = z * (std_dev / (n ** 0.5)) if n > 0 else 0
    
    return {
        "calculator_id": "lifetime_analysis",
        "success": True,
        "results": {
            "distribution_type": distribution_type,
            "sample_size": n,
            "mean_life": mean_life,
            "median_life": median_life,
            "failure_rate": failure_rate,
            "reliability": math.exp(-failure_rate * mean_life) * 100 if failure_rate > 0 else 100,
            "standard_deviation": std_dev,
            "margin_of_error": margin_of_error,
            "confidence_interval_lower": max(0, mean_life - margin_of_error),
            "confidence_interval_upper": mean_life + margin_of_error,
            "confidence_level": confidence_level,
            "censoring_type": censoring
        },
        "metadata": {
            "units": {
                "mean_life": "hours",
                "median_life": "hours",
                "failure_rate": "failures/hour",
                "reliability": "%",
                "standard_deviation": "hours",
                "margin_of_error": "hours",
                "confidence_interval_lower": "hours",
                "confidence_interval_upper": "hours"
            },
            "descriptions": {
                "distribution_type": "Statistical distribution used for analysis",
                "sample_size": "Number of data points in the sample",
                "mean_life": "Mean time to failure (MTTF)",
                "median_life": "Median time to failure",
                "failure_rate": "Estimated failure rate",
                "reliability": f"Reliability at mean life ({mean_life:.1f} hours)",
                "standard_deviation": "Standard deviation of failure times",
                "margin_of_error": f"Margin of error at {confidence_level}% confidence",
                "confidence_interval_lower": f"Lower bound of {confidence_level}% confidence interval",
                "confidence_interval_upper": f"Upper bound of {confidence_level}% confidence interval",
                "censoring_type": f"Type of data censoring: {censoring}"
            }
        }
    }

def calculate_acceleration_factor(inputs: dict) -> dict:
    """Acceleration Factor Calculator"""
    model_type = inputs.get("model_type", "Arrhenius")
    temp_use = float(inputs.get("temp_use", 25.0)) + 273.15  # Convert to Kelvin
    temp_stress = float(inputs.get("temp_stress", 85.0)) + 273.15  # Convert to Kelvin
    activation_energy = float(inputs.get("activation_energy", 0.7))  # in eV
    
    # Boltzmann constant in eV/K
    k = 8.617333262145e-5
    
    # Calculate acceleration factor based on model type
    if model_type == "Arrhenius":
        af = math.exp((activation_energy / k) * ((1/temp_use) - (1/temp_stress)))
    elif model_type == "Eyring":
        af = (temp_stress / temp_use) * math.exp((activation_energy / k) * ((1/temp_use) - (1/temp_stress)))
    elif model_type == "Peck":
        # Peck's model (simplified for temperature and humidity)
        rh_use = float(inputs.get("rh_use", 50.0))  # Relative humidity in %
        rh_stress = float(inputs.get("rh_stress", 85.0))  # Relative humidity in %
        af = math.exp((activation_energy / k) * ((1/temp_use) - (1/temp_stress))) * ((rh_stress / rh_use) ** 2.7)
    else:
        af = 1.0
    
    return {
        "calculator_id": "acceleration_factor",
        "success": True,
        "results": {
            "acceleration_factor": af,
            "model_type": model_type,
            "temp_use": temp_use - 273.15,  # Convert back to Celsius
            "temp_stress": temp_stress - 273.15,  # Convert back to Celsius
            "activation_energy": activation_energy,
            "test_time_reduction": (1 - (1/af)) * 100 if af > 1 else 0
        },
        "metadata": {
            "units": {
                "acceleration_factor": "x",
                "temp_use": "°C",
                "temp_stress": "°C",
                "activation_energy": "eV",
                "test_time_reduction": "%"
            },
            "descriptions": {
                "acceleration_factor": f"Acceleration factor using {model_type} model",
                "model_type": "Acceleration model used for calculation",
                "temp_use": "Normal use temperature",
                "temp_stress": "Accelerated stress temperature",
                "activation_energy": "Activation energy for the failure mechanism",
                "test_time_reduction": "Reduction in test time compared to use conditions"
            }
        }
    }

def calculate_sample_size(inputs: dict) -> dict:
    """Sample Size Calculator for Reliability Testing"""
    reliability_goal = float(inputs.get("reliability_goal", 95.0)) / 100.0  # Convert to decimal
    confidence_level = int(inputs.get("confidence_level", 95))
    expected_failures = int(inputs.get("expected_failures", 0))
    
    # Calculate required sample size using binomial distribution approximation
    if expected_failures == 0:
        # Zero-failure test
        n = math.ceil(math.log(1 - (confidence_level / 100.0)) / math.log(reliability_goal))
        actual_confidence = 1 - (reliability_goal ** n)
    else:
        # Allow for expected failures (simplified calculation)
        n = math.ceil((expected_failures + 1) / (1 - reliability_goal))
        actual_confidence = 1 - sum(
            math.comb(n, k) * ((1 - reliability_goal) ** k) * (reliability_goal ** (n - k))
            for k in range(expected_failures + 1)
        )
    
    # Calculate test time if provided
    test_duration = float(inputs.get("test_duration", 0))
    if test_duration > 0:
        test_time = n * test_duration
    else:
        test_time = None
    
    return {
        "calculator_id": "sample_size",
        "success": True,
        "results": {
            "sample_size": n,
            "reliability_goal": reliability_goal * 100,  # Convert back to percentage
            "confidence_level": confidence_level,
            "expected_failures": expected_failures,
            "actual_confidence": actual_confidence * 100,  # Convert to percentage
            "test_duration": test_duration if test_duration > 0 else None,
            "total_test_time": test_time
        },
        "metadata": {
            "units": {
                "sample_size": "units",
                "reliability_goal": "%",
                "confidence_level": "%",
                "actual_confidence": "%",
                "test_duration": "hours",
                "total_test_time": "unit-hours"
            },
            "descriptions": {
                "sample_size": "Required number of test units",
                "reliability_goal": "Target reliability level",
                "confidence_level": "Desired confidence level",
                "expected_failures": "Number of failures to allow in the test",
                "actual_confidence": "Achieved confidence level with this sample size",
                "test_duration": "Duration of the test per unit (if applicable)",
                "total_test_time": "Total test time across all units (if duration specified)"
            }
        }
    }
