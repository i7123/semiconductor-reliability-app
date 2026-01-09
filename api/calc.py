from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
import math

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path
        
        # Handle /calculators/ endpoint
        if path == "/calculators/" or path == "/calculators":
            self.send_calculator_list()
        # Handle /calculators/{id}/info endpoint
        elif path.startswith("/calculators/") and path.endswith("/info"):
            calc_id = path.split("/")[2]
            self.send_calculator_info(calc_id)
        # Handle /health endpoint
        elif path == "/health":
            self.send_health()
        else:
            self.send_404()
    
    def do_POST(self):
        path = self.path
        
        # Handle /calculators/calculate/{id} endpoint
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
            self.send_404()
    
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
            }
        ]
        
        for calc in calculators:
            if calc["id"] == calc_id:
                self.send_json_response(200, calc)
                return
        
        self.send_json_response(404, {"error": "Calculator not found"})
    
    def send_health(self):
        self.send_json_response(200, {"status": "healthy"})
    
    def send_404(self):
        self.send_json_response(404, {"error": "Not found"})
    
    def calculate(self, calc_id, inputs):
        if calc_id == "mtbf":
            return self.calculate_mtbf(inputs)
        elif calc_id == "duane_model":
            return self.calculate_duane_model(inputs)
        else:
            return {"calculator_id": calc_id, "success": False, "error": "Calculator not implemented"}
    
    def calculate_mtbf(self, inputs):
        try:
            failure_rate = float(inputs.get("failure_rate", 0.0001))
            confidence_level = int(inputs.get("confidence_level", 95))
            operating_hours = float(inputs.get("operating_hours", 8760))
            
            # Basic MTBF calculation
            mtbf_hours = 1 / failure_rate if failure_rate > 0 else float('inf')
            
            # Calculate reliability
            reliability = math.exp(-operating_hours / mtbf_hours) if mtbf_hours > 0 else 0
            
            return {
                "calculator_id": "mtbf",
                "success": True,
                "results": {
                    "mtbf_hours": mtbf_hours,
                    "mtbf_years": mtbf_hours / 8760,
                    "reliability": reliability * 100,
                    "failure_rate": failure_rate,
                    "operating_hours": operating_hours,
                    "confidence_level": confidence_level
                }
            }
        except Exception as e:
            return {"calculator_id": "mtbf", "success": False, "error": str(e)}
    
    def calculate_duane_model(self, inputs):
        try:
            failure_times_str = inputs.get("failure_times", "")
            confidence_level = int(inputs.get("confidence_level", 95))
            
            # Parse failure times
            failure_times = [float(x.strip()) for x in failure_times_str.split(',') if x.strip()]
            failure_times.sort()
            
            if len(failure_times) < 2:
                raise ValueError("At least 2 failure times are required")
            
            # Calculate Duane model parameters
            n_failures = len(failure_times)
            failure_numbers = list(range(1, n_failures + 1))
            cumulative_mtbf = [failure_times[i] / failure_numbers[i] for i in range(n_failures)]
            
            # Linear regression on log-log scale
            ln_times = [math.log(t) for t in failure_times]
            ln_mtbf = [math.log(mtbf) for mtbf in cumulative_mtbf]
            
            n = len(ln_times)
            sum_x = sum(ln_times)
            sum_y = sum(ln_mtbf)
            sum_xx = sum(x * x for x in ln_times)
            sum_xy = sum(ln_times[i] * ln_mtbf[i] for i in range(n))
            
            # Calculate beta and alpha
            beta = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)
            ln_alpha = (sum_y - beta * sum_x) / n
            alpha = math.exp(ln_alpha)
            
            # Growth rate
            growth_rate = (1 - beta) * 100
            
            final_time = failure_times[-1]
            mtbf_cumulative = alpha * (final_time ** beta)
            
            return {
                "calculator_id": "duane_model",
                "success": True,
                "results": {
                    "duane_model_parameters": {
                        "alpha": round(alpha, 6),
                        "beta": round(beta, 6)
                    },
                    "reliability_growth": {
                        "growth_rate_percent": round(growth_rate, 2)
                    },
                    "final_prediction": {
                        "mtbf_cumulative": round(mtbf_cumulative, 2)
                    },
                    "input_data": {
                        "failure_times": failure_times,
                        "number_of_failures": len(failure_times)
                    }
                }
            }
        except Exception as e:
            return {"calculator_id": "duane_model", "success": False, "error": str(e)}