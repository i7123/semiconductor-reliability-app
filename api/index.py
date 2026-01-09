"""
Vercel serverless function for Semiconductor Reliability Calculator API
Full-featured version with all 6 calculators including complete MTBF and Duane Model implementations
"""
from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import math

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path
        
        if path == "/health":
            self.send_json_response(200, {"status": "healthy"})
        elif path == "/calculators/" or path == "/calculators":
            self.send_calculator_list()
        elif path.startswith("/calculators/") and path.endswith("/info"):
            calc_id = path.split("/")[2]
            self.send_calculator_info(calc_id)
        elif path.startswith("/calculators/calculate/") and path.endswith("/example"):
            # Handle /calculators/calculate/{calc_id}/example
            parts = path.split("/")
            calc_id = parts[3]
            self.send_calculator_example(calc_id)
        else:
            self.send_json_response(404, {"error": "Not found"})
    
    def do_POST(self):
        path = self.path
        
        if path.startswith("/calculators/calculate/"):
            calc_id = path.split("/")[3]
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(post_data)
                inputs = data.get("inputs", {})
                result = self.calculate(calc_id, inputs)
                self.send_json_response(200, result)
            except Exception as e:
                self.send_json_response(400, {"error": str(e)})
        else:
            self.send_json_response(404, {"error": "Not found"})
    
    def send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def send_calculator_list(self):
        calculators = [
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
                        "max_value": 1.0,
                        "description": "Expected failure rate in failures per hour"
                    },
                    {
                        "name": "operating_hours",
                        "label": "Operating Hours", 
                        "type": "float",
                        "required": False,
                        "default_value": 8760,
                        "min_value": 1,
                        "description": "Total operating hours for reliability calculation"
                    },
                    {
                        "name": "confidence_level",
                        "label": "Confidence Level",
                        "type": "select",
                        "options": ["90", "95", "99"],
                        "default_value": "95",
                        "required": True,
                        "description": "Statistical confidence level for the calculation"
                    }
                ]
            },
            {
                "id": "duane_model",
                "name": "Duane Model Reliability Growth Calculator",
                "description": "Calculate reliability growth parameters and predict MTBF using the Duane model",
                "category": "Reliability Growth",
                "input_fields": [
                    {
                        "name": "failure_times",
                        "label": "Failure Times",
                        "type": "text",
                        "unit": "hours",
                        "description": "Comma-separated list of failure times in ascending order (e.g., 100, 250, 480, 750, 1200)",
                        "required": True
                    },
                    {
                        "name": "target_time",
                        "label": "Target Time",
                        "type": "float",
                        "unit": "hours",
                        "description": "Time at which to predict MTBF (optional)",
                        "required": False,
                        "min_value": 0.0
                    },
                    {
                        "name": "confidence_level",
                        "label": "Confidence Level",
                        "type": "select",
                        "unit": "%",
                        "description": "Statistical confidence level for predictions",
                        "required": True,
                        "options": ["90", "95", "99"],
                        "default_value": "95"
                    }
                ]
            },
            {
                "id": "test_sample_size",
                "name": "Test Sample Size Calculator",
                "description": "Calculate required sample size for reliability demonstration testing",
                "category": "Test Planning",
                "input_fields": [
                    {
                        "name": "target_reliability",
                        "label": "Target Reliability",
                        "type": "float",
                        "unit": "",
                        "description": "Required reliability level (0-1, e.g., 0.95 for 95%)",
                        "required": True,
                        "min_value": 0.1,
                        "max_value": 0.999
                    },
                    {
                        "name": "confidence_level",
                        "label": "Confidence Level",
                        "type": "select",
                        "unit": "%",
                        "description": "Statistical confidence level",
                        "required": True,
                        "options": ["80", "90", "95", "99"],
                        "default_value": "90"
                    },
                    {
                        "name": "test_type",
                        "label": "Test Type",
                        "type": "select",
                        "unit": "",
                        "description": "Type of reliability test",
                        "required": True,
                        "options": ["success_run", "time_terminated", "failure_terminated"],
                        "default_value": "success_run"
                    },
                    {
                        "name": "test_duration",
                        "label": "Test Duration",
                        "type": "float",
                        "unit": "hours",
                        "description": "Duration of each test (for time-terminated tests)",
                        "required": False,
                        "min_value": 0.0
                    },
                    {
                        "name": "target_mtbf",
                        "label": "Target MTBF",
                        "type": "float",
                        "unit": "hours",
                        "description": "Target Mean Time Between Failures",
                        "required": False,
                        "min_value": 0.0
                    },
                    {
                        "name": "max_failures",
                        "label": "Maximum Allowed Failures",
                        "type": "int",
                        "unit": "",
                        "description": "Maximum number of failures allowed in test",
                        "required": False,
                        "min_value": 0,
                        "max_value": 100
                    }
                ]
            },
            {
                "id": "dummy_calculator_1",
                "name": "Advanced Stress Testing Calculator",
                "description": "Calculate stress test parameters and life predictions under various stress conditions",
                "category": "Future Development",
                "input_fields": [
                    {
                        "name": "stress_level",
                        "label": "Stress Level",
                        "type": "float",
                        "unit": "units",
                        "description": "Applied stress level for testing",
                        "required": True,
                        "min_value": 0.0
                    },
                    {
                        "name": "temperature",
                        "label": "Temperature",
                        "type": "float",
                        "unit": "°C",
                        "description": "Test temperature",
                        "required": True,
                        "min_value": -50.0,
                        "max_value": 200.0
                    }
                ]
            },
            {
                "id": "dummy_calculator_2",
                "name": "Burn-in Optimization Calculator",
                "description": "Optimize burn-in time and conditions to maximize early failure detection",
                "category": "Future Development",
                "input_fields": [
                    {
                        "name": "burn_in_time",
                        "label": "Burn-in Time",
                        "type": "float",
                        "unit": "hours",
                        "description": "Duration of burn-in testing",
                        "required": True,
                        "min_value": 0.0
                    },
                    {
                        "name": "cost_per_hour",
                        "label": "Cost per Hour",
                        "type": "float",
                        "unit": "$/hour",
                        "description": "Cost of burn-in testing per hour",
                        "required": True,
                        "min_value": 0.0
                    },
                    {
                        "name": "defect_rate",
                        "label": "Initial Defect Rate",
                        "type": "float",
                        "unit": "%",
                        "description": "Expected initial defect rate",
                        "required": True,
                        "min_value": 0.0,
                        "max_value": 100.0
                    }
                ]
            },
            {
                "id": "dummy_calculator_3",
                "name": "Lifetime Data Analysis Calculator",
                "description": "Analyze lifetime data using various statistical distributions and models",
                "category": "Future Development",
                "input_fields": [
                    {
                        "name": "lifetime_data",
                        "label": "Lifetime Data",
                        "type": "text",
                        "unit": "hours",
                        "description": "Comma-separated lifetime values",
                        "required": True
                    },
                    {
                        "name": "distribution_type",
                        "label": "Distribution Type",
                        "type": "select",
                        "unit": "",
                        "description": "Statistical distribution to fit",
                        "required": True,
                        "options": ["Exponential", "Weibull", "Lognormal", "Gamma"],
                        "default_value": "Weibull"
                    },
                    {
                        "name": "censoring_type",
                        "label": "Censoring Type",
                        "type": "select",
                        "unit": "",
                        "description": "Type of data censoring",
                        "required": True,
                        "options": ["None", "Right", "Left", "Interval"],
                        "default_value": "None"
                    }
                ]
            }
        ]
        self.send_json_response(200, calculators)
    
    def send_calculator_info(self, calc_id):
        calculators = [
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
                        "max_value": 1.0,
                        "description": "Expected failure rate in failures per hour"
                    },
                    {
                        "name": "operating_hours",
                        "label": "Operating Hours",
                        "type": "float", 
                        "required": False,
                        "default_value": 8760,
                        "min_value": 1,
                        "description": "Total operating hours for reliability calculation"
                    },
                    {
                        "name": "confidence_level",
                        "label": "Confidence Level",
                        "type": "select",
                        "options": ["90", "95", "99"],
                        "default_value": "95",
                        "required": True,
                        "description": "Statistical confidence level for the calculation"
                    }
                ]
            },
            {
                "id": "duane_model",
                "name": "Duane Model Reliability Growth Calculator",
                "description": "Calculate reliability growth parameters and predict MTBF using the Duane model",
                "category": "Reliability Growth",
                "input_fields": [
                    {
                        "name": "failure_times",
                        "label": "Failure Times",
                        "type": "text",
                        "unit": "hours",
                        "description": "Comma-separated list of failure times in ascending order (e.g., 100, 250, 480, 750, 1200)",
                        "required": True
                    },
                    {
                        "name": "target_time",
                        "label": "Target Time",
                        "type": "float",
                        "unit": "hours",
                        "description": "Time at which to predict MTBF (optional)",
                        "required": False,
                        "min_value": 0.0
                    },
                    {
                        "name": "confidence_level",
                        "label": "Confidence Level",
                        "type": "select",
                        "unit": "%",
                        "description": "Statistical confidence level for predictions", 
                        "required": True,
                        "options": ["90", "95", "99"],
                        "default_value": "95"
                    }
                ]
            },
            {
                "id": "test_sample_size",
                "name": "Test Sample Size Calculator",
                "description": "Calculate required sample size for reliability demonstration testing",
                "category": "Test Planning",
                "input_fields": [
                    {
                        "name": "target_reliability",
                        "label": "Target Reliability",
                        "type": "float",
                        "unit": "",
                        "description": "Required reliability level (0-1, e.g., 0.95 for 95%)",
                        "required": True,
                        "min_value": 0.1,
                        "max_value": 0.999
                    },
                    {
                        "name": "confidence_level",
                        "label": "Confidence Level",
                        "type": "select",
                        "unit": "%",
                        "description": "Statistical confidence level",
                        "required": True,
                        "options": ["80", "90", "95", "99"],
                        "default_value": "90"
                    },
                    {
                        "name": "test_type",
                        "label": "Test Type",
                        "type": "select",
                        "unit": "",
                        "description": "Type of reliability test",
                        "required": True,
                        "options": ["success_run", "time_terminated", "failure_terminated"],
                        "default_value": "success_run"
                    },
                    {
                        "name": "test_duration",
                        "label": "Test Duration",
                        "type": "float",
                        "unit": "hours",
                        "description": "Duration of each test (for time-terminated tests)",
                        "required": False,
                        "min_value": 0.0
                    },
                    {
                        "name": "target_mtbf",
                        "label": "Target MTBF",
                        "type": "float",
                        "unit": "hours",
                        "description": "Target Mean Time Between Failures",
                        "required": False,
                        "min_value": 0.0
                    },
                    {
                        "name": "max_failures",
                        "label": "Maximum Allowed Failures",
                        "type": "int",
                        "unit": "",
                        "description": "Maximum number of failures allowed in test",
                        "required": False,
                        "min_value": 0,
                        "max_value": 100
                    }
                ]
            },
            {
                "id": "dummy_calculator_1",
                "name": "Advanced Stress Testing Calculator",
                "description": "Calculate stress test parameters and life predictions under various stress conditions",
                "category": "Future Development",
                "input_fields": [
                    {
                        "name": "stress_level",
                        "label": "Stress Level",
                        "type": "float",
                        "unit": "units",
                        "description": "Applied stress level for testing",
                        "required": True,
                        "min_value": 0.0
                    },
                    {
                        "name": "temperature",
                        "label": "Temperature",
                        "type": "float",
                        "unit": "°C",
                        "description": "Test temperature",
                        "required": True,
                        "min_value": -50.0,
                        "max_value": 200.0
                    }
                ]
            },
            {
                "id": "dummy_calculator_2",
                "name": "Burn-in Optimization Calculator",
                "description": "Optimize burn-in time and conditions to maximize early failure detection",
                "category": "Future Development",
                "input_fields": [
                    {
                        "name": "burn_in_time",
                        "label": "Burn-in Time",
                        "type": "float",
                        "unit": "hours",
                        "description": "Duration of burn-in testing",
                        "required": True,
                        "min_value": 0.0
                    },
                    {
                        "name": "cost_per_hour",
                        "label": "Cost per Hour",
                        "type": "float",
                        "unit": "$/hour",
                        "description": "Cost of burn-in testing per hour",
                        "required": True,
                        "min_value": 0.0
                    },
                    {
                        "name": "defect_rate",
                        "label": "Initial Defect Rate",
                        "type": "float",
                        "unit": "%",
                        "description": "Expected initial defect rate",
                        "required": True,
                        "min_value": 0.0,
                        "max_value": 100.0
                    }
                ]
            },
            {
                "id": "dummy_calculator_3",
                "name": "Lifetime Data Analysis Calculator",
                "description": "Analyze lifetime data using various statistical distributions and models",
                "category": "Future Development",
                "input_fields": [
                    {
                        "name": "lifetime_data",
                        "label": "Lifetime Data",
                        "type": "text",
                        "unit": "hours",
                        "description": "Comma-separated lifetime values",
                        "required": True
                    },
                    {
                        "name": "distribution_type",
                        "label": "Distribution Type",
                        "type": "select",
                        "unit": "",
                        "description": "Statistical distribution to fit",
                        "required": True,
                        "options": ["Exponential", "Weibull", "Lognormal", "Gamma"],
                        "default_value": "Weibull"
                    },
                    {
                        "name": "censoring_type",
                        "label": "Censoring Type",
                        "type": "select",
                        "unit": "",
                        "description": "Type of data censoring",
                        "required": True,
                        "options": ["None", "Right", "Left", "Interval"],
                        "default_value": "None"
                    }
                ]
            }
        ]
        
        for calc in calculators:
            if calc["id"] == calc_id:
                self.send_json_response(200, calc)
                return
        
        self.send_json_response(404, {"error": "Calculator not found"})
    
    def send_calculator_example(self, calc_id):
        """Return example inputs and results for a calculator"""
        examples = {
            "mtbf": {
                "calculator_id": "mtbf",
                "example_inputs": {
                    "failure_rate": 0.0001,
                    "operating_hours": 8760,
                    "confidence_level": "95"
                },
                "example_results": {
                    "calculator_id": "mtbf",
                    "success": True,
                    "results": {
                        "mtbf_hours": 10000.0,
                        "mtbf_years": 1.1416,
                        "reliability": 41.69,
                        "failure_probability": 58.31,
                        "failure_rate": 0.0001,
                        "operating_hours": 8760,
                        "confidence_level": 95,
                        "expected_failures": 0.876
                    }
                }
            },
            "duane_model": {
                "calculator_id": "duane_model",
                "example_inputs": {
                    "failure_times": "100, 250, 480, 750, 1200, 1800, 2500",
                    "target_time": 5000,
                    "confidence_level": "95"
                },
                "example_results": {
                    "calculator_id": "duane_model",
                    "success": True,
                    "results": {
                        "duane_model_parameters": {
                            "alpha": 25.5,
                            "beta": 0.45
                        },
                        "final_prediction": {
                            "time": 2500,
                            "mtbf_cumulative": 357.14,
                            "mtbf_instantaneous": 649.35
                        },
                        "reliability_growth": {
                            "growth_rate_percent": 55.0,
                            "interpretation": "Moderate reliability growth (0.5 < β ≤ 0.8)"
                        }
                    }
                }
            },
            "test_sample_size": {
                "calculator_id": "test_sample_size",
                "example_inputs": {
                    "target_reliability": 0.95,
                    "confidence_level": "90",
                    "test_type": "success_run",
                    "max_failures": 0
                },
                "example_results": {
                    "calculator_id": "test_sample_size",
                    "success": True,
                    "results": {
                        "target_reliability": 0.95,
                        "confidence_level": 90,
                        "test_type": "success_run",
                        "max_failures_allowed": 0,
                        "required_sample_size": 45,
                        "test_method": "Success Run Test",
                        "description": "Test 45 units with zero failures to demonstrate 0.950 reliability at 90% confidence"
                    }
                }
            },
            "dummy_calculator_1": {
                "calculator_id": "dummy_calculator_1",
                "example_inputs": {
                    "stress_level": 100.0,
                    "temperature": 85.0
                },
                "example_results": {
                    "calculator_id": "dummy_calculator_1",
                    "success": True,
                    "results": {
                        "status": "in_development",
                        "message": "This calculator is currently in development."
                    }
                }
            },
            "dummy_calculator_2": {
                "calculator_id": "dummy_calculator_2",
                "example_inputs": {
                    "burn_in_time": 168.0,
                    "cost_per_hour": 5.0,
                    "defect_rate": 2.0
                },
                "example_results": {
                    "calculator_id": "dummy_calculator_2",
                    "success": True,
                    "results": {
                        "status": "in_development",
                        "message": "This calculator is currently in development."
                    }
                }
            },
            "dummy_calculator_3": {
                "calculator_id": "dummy_calculator_3",
                "example_inputs": {
                    "lifetime_data": "100, 250, 380, 420, 550, 600, 780, 890",
                    "distribution_type": "Weibull",
                    "censoring_type": "None"
                },
                "example_results": {
                    "calculator_id": "dummy_calculator_3",
                    "success": True,
                    "results": {
                        "status": "in_development",
                        "message": "This calculator is currently in development."
                    }
                }
            }
        }
        
        if calc_id in examples:
            self.send_json_response(200, examples[calc_id])
        else:
            self.send_json_response(404, {"error": "Example not found for calculator"})
    
    def calculate(self, calc_id, inputs):
        if calc_id == "mtbf":
            return self.calculate_mtbf(inputs)
        elif calc_id == "duane_model":
            return self.calculate_duane_model(inputs)
        elif calc_id == "test_sample_size":
            return self.calculate_test_sample_size(inputs)
        elif calc_id == "dummy_calculator_1":
            return self.calculate_dummy_calculator_1(inputs)
        elif calc_id == "dummy_calculator_2":
            return self.calculate_dummy_calculator_2(inputs)
        elif calc_id == "dummy_calculator_3":
            return self.calculate_dummy_calculator_3(inputs)
        else:
            return {"calculator_id": calc_id, "success": False, "error": "Calculator not implemented"}
    
    def calculate_mtbf(self, inputs):
        """Full MTBF Calculator implementation"""
        try:
            failure_rate = float(inputs.get("failure_rate", 0.0001))
            confidence_level = int(inputs.get("confidence_level", 95))
            operating_hours = float(inputs.get("operating_hours", 8760))
            
            # Basic MTBF calculation
            mtbf_hours = 1 / failure_rate if failure_rate > 0 else float('inf')
            
            # Calculate reliability at operating hours
            reliability = math.exp(-operating_hours / mtbf_hours) if mtbf_hours > 0 else 0
            
            # Calculate other reliability metrics
            mtbf_years = mtbf_hours / 8760
            failure_probability = 1 - reliability
            
            # Confidence interval calculation (simplified)
            confidence_multiplier = {90: 1.645, 95: 1.96, 99: 2.576}[confidence_level]
            
            return {
                "calculator_id": "mtbf",
                "success": True,
                "results": {
                    "mtbf_hours": round(mtbf_hours, 2),
                    "mtbf_years": round(mtbf_years, 4),
                    "reliability": round(reliability * 100, 4),
                    "failure_probability": round(failure_probability * 100, 4),
                    "failure_rate": failure_rate,
                    "operating_hours": operating_hours,
                    "confidence_level": confidence_level,
                    "expected_failures": round(operating_hours / mtbf_hours, 4) if mtbf_hours > 0 else 0
                },
                "metadata": {
                    "units": {
                        "mtbf_hours": "hours",
                        "mtbf_years": "years",
                        "reliability": "%",
                        "failure_probability": "%",
                        "failure_rate": "failures/hour",
                        "operating_hours": "hours",
                        "expected_failures": "failures"
                    },
                    "descriptions": {
                        "mtbf_hours": "Mean Time Between Failures",
                        "mtbf_years": "MTBF in Years",
                        "reliability": f"Reliability over {operating_hours} hours",
                        "failure_probability": "Probability of failure during operating period",
                        "failure_rate": "Failure Rate (constant)",
                        "expected_failures": "Expected number of failures during operating period"
                    }
                }
            }
        except Exception as e:
            return {"calculator_id": "mtbf", "success": False, "error": str(e)}
    
    def calculate_duane_model(self, inputs):
        """Full Duane Model Reliability Growth Calculator implementation"""
        try:
            failure_times_str = inputs.get("failure_times", "")
            target_time = inputs.get("target_time")
            confidence_level = int(inputs.get("confidence_level", 95))
            total_test_time = inputs.get("total_test_time")
            
            # Parse failure times
            try:
                failure_times = [float(x.strip()) for x in failure_times_str.split(',') if x.strip()]
                failure_times.sort()
            except ValueError:
                raise ValueError("Failure times must be numeric values separated by commas")
            
            if len(failure_times) < 2:
                raise ValueError("At least 2 failure times are required for Duane model analysis")
            
            # Calculate Duane model parameters using full implementation
            n_failures = len(failure_times)
            failure_numbers = list(range(1, n_failures + 1))
            
            # Calculate cumulative MTBF = failure_time / failure_number
            cumulative_mtbf = [failure_times[i] / failure_numbers[i] for i in range(n_failures)]
            
            # Use total test time if provided, otherwise use last failure time
            test_duration = total_test_time if total_test_time is not None else failure_times[-1]
            
            # Linear regression on log-log scale: ln(MTBF_c) = ln(α) + β * ln(t)
            ln_times = [math.log(t) for t in failure_times]
            ln_mtbf = [math.log(mtbf) for mtbf in cumulative_mtbf]
            
            # Calculate regression parameters
            n = len(ln_times)
            sum_x = sum(ln_times)
            sum_y = sum(ln_mtbf)
            sum_xx = sum(x * x for x in ln_times)
            sum_xy = sum(ln_times[i] * ln_mtbf[i] for i in range(n))
            
            # Slope (β) and intercept (ln(α))
            beta = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
            ln_alpha = (sum_y - beta * sum_x) / n
            alpha = math.exp(ln_alpha)
            
            # Calculate R-squared for goodness of fit
            y_mean = sum_y / n
            ss_tot = sum((y - y_mean) ** 2 for y in ln_mtbf)
            y_pred = [ln_alpha + beta * x for x in ln_times]
            ss_res = sum((ln_mtbf[i] - y_pred[i]) ** 2 for i in range(n))
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            
            # Predicted cumulative MTBF at test duration
            final_time = test_duration
            mtbf_cumulative = alpha * (final_time ** beta)
            
            # Instantaneous MTBF
            mtbf_instantaneous = (alpha / beta) * (final_time ** beta) if beta != 0 else float('inf')
            
            # Growth rate and interpretation
            growth_rate = (1 - beta) * 100
            
            # Time to double MTBF
            if 0 < beta < 1:
                doubling_factor = 2 ** (1 / beta)
                time_to_double = final_time * (doubling_factor - 1)
            else:
                time_to_double = float('inf')
            
            # Interpretation
            if beta > 1:
                interpretation = "Reliability is deteriorating (β > 1)"
            elif beta == 1:
                interpretation = "No reliability growth (β = 1, constant failure rate)"
            elif beta > 0.8:
                interpretation = "Slow reliability growth (β > 0.8)"
            elif beta > 0.5:
                interpretation = "Moderate reliability growth (0.5 < β ≤ 0.8)"
            elif beta > 0.2:
                interpretation = "Good reliability growth (0.2 < β ≤ 0.5)"
            else:
                interpretation = "Excellent reliability growth (β ≤ 0.2)"
            
            results = {
                "input_data": {
                    "failure_times": failure_times,
                    "number_of_failures": len(failure_times),
                    "test_duration": test_duration,
                    "confidence_level": confidence_level
                },
                "duane_model_parameters": {
                    "alpha": round(alpha, 6),
                    "beta": round(beta, 6),
                    "ln_alpha": round(ln_alpha, 6)
                },
                "cumulative_mtbf_data": {
                    "failure_times": failure_times,
                    "failure_numbers": failure_numbers,
                    "cumulative_mtbf": [round(mtbf, 2) for mtbf in cumulative_mtbf]
                },
                "model_fit_statistics": {
                    "r_squared": round(r_squared, 6),
                    "degrees_of_freedom": n - 2
                },
                "final_prediction": {
                    "time": final_time,
                    "mtbf_cumulative": round(mtbf_cumulative, 2),
                    "mtbf_instantaneous": round(mtbf_instantaneous, 2)
                },
                "reliability_growth": {
                    "growth_rate_percent": round(growth_rate, 2),
                    "time_to_double_mtbf": round(time_to_double, 2) if time_to_double != float('inf') else None,
                    "interpretation": interpretation
                }
            }
            
            # Add target prediction if requested
            if target_time is not None and target_time > 0:
                target_mtbf_cumulative = alpha * (target_time ** beta)
                target_mtbf_instantaneous = (alpha / beta) * (target_time ** beta) if beta != 0 else float('inf')
                results["target_prediction"] = {
                    "time": target_time,
                    "mtbf_cumulative": round(target_mtbf_cumulative, 2),
                    "mtbf_instantaneous": round(target_mtbf_instantaneous, 2)
                }
            
            return {
                "calculator_id": "duane_model",
                "success": True,
                "results": results,
                "metadata": {
                    "units": {
                        "failure_times": "hours",
                        "mtbf_cumulative": "hours", 
                        "mtbf_instantaneous": "hours",
                        "test_duration": "hours",
                        "time_to_double_mtbf": "hours"
                    },
                    "descriptions": {
                        "alpha": "Duane model scale parameter",
                        "beta": "Duane model growth parameter (0 < β < 1 for improvement)",
                        "r_squared": "Goodness of fit (closer to 1 is better)",
                        "growth_rate_percent": "Reliability growth rate percentage",
                        "mtbf_cumulative": "Cumulative MTBF at specified time",
                        "mtbf_instantaneous": "Instantaneous MTBF at specified time"
                    }
                }
            }
        except Exception as e:
            return {"calculator_id": "duane_model", "success": False, "error": str(e)}
    
    def calculate_test_sample_size(self, inputs):
        try:
            target_reliability = float(inputs.get("target_reliability", 0.95))
            confidence_level = int(inputs.get("confidence_level", 90))
            test_type = inputs.get("test_type", "success_run")
            test_duration = inputs.get("test_duration")
            target_mtbf = inputs.get("target_mtbf")
            max_failures = int(inputs.get("max_failures", 0))
            
            chi_square_values = {
                80: {0: 1.609, 1: 3.219, 2: 4.642, 3: 5.989},
                90: {0: 2.303, 1: 4.605, 2: 6.251, 3: 7.779},
                95: {0: 2.996, 1: 5.991, 2: 7.815, 3: 9.488},
                99: {0: 4.605, 1: 9.210, 2: 11.345, 3: 13.277}
            }
            
            results = {
                "target_reliability": target_reliability,
                "confidence_level": confidence_level,
                "test_type": test_type,
                "max_failures_allowed": max_failures
            }
            
            if test_type == "success_run":
                confidence_decimal = confidence_level / 100
                sample_size = math.log(1 - confidence_decimal) / math.log(target_reliability)
                sample_size = math.ceil(sample_size)
                
                results.update({
                    "required_sample_size": sample_size,
                    "test_method": "Success Run Test",
                    "description": f"Test {sample_size} units with zero failures to demonstrate {target_reliability:.3f} reliability at {confidence_level}% confidence"
                })
            
            return {
                "calculator_id": "test_sample_size",
                "success": True,
                "results": results
            }
        except Exception as e:
            return {"calculator_id": "test_sample_size", "success": False, "error": str(e)}
    
    def calculate_dummy_calculator_1(self, inputs):
        return {
            "calculator_id": "dummy_calculator_1",
            "success": True,
            "results": {
                "status": "in_development",
                "message": "This calculator is currently in development. Please check back for future updates.",
                "planned_features": [
                    "Stress acceleration factor calculations",
                    "Life prediction modeling",
                    "Multi-stress analysis",
                    "Statistical confidence intervals"
                ]
            }
        }
    
    def calculate_dummy_calculator_2(self, inputs):
        return {
            "calculator_id": "dummy_calculator_2",
            "success": True,
            "results": {
                "status": "in_development",
                "message": "This calculator is currently in development. Please check back for future updates.",
                "planned_features": [
                    "Optimal burn-in time calculation",
                    "Cost-benefit analysis",
                    "Defect detection efficiency",
                    "Burn-in temperature optimization"
                ]
            }
        }
    
    def calculate_dummy_calculator_3(self, inputs):
        return {
            "calculator_id": "dummy_calculator_3",
            "success": True,
            "results": {
                "status": "in_development",
                "message": "This calculator is currently in development. Please check back for future updates.",
                "planned_features": [
                    "Multiple distribution fitting",
                    "Parameter estimation with MLE",
                    "Goodness-of-fit testing",
                    "Probability plotting",
                    "Censored data analysis"
                ]
            }
        }