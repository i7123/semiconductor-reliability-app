import math
import numpy as np
from typing import Dict, Any, List
from .base import BaseCalculator, CalculatorInfo, InputField

class DuaneModelCalculator(BaseCalculator):
    """Duane Model Reliability Growth Calculator"""
    
    @property
    def info(self) -> CalculatorInfo:
        return CalculatorInfo(
            id="duane_model",
            name="Duane Model Reliability Growth Calculator",
            description="Calculate reliability growth parameters and predict MTBF using the Duane model",
            category="Reliability Growth",
            input_fields=[
                InputField(
                    name="failure_times",
                    label="Failure Times",
                    type="text",
                    unit="hours",
                    description="Comma-separated list of failure times in ascending order (e.g., 100, 250, 480, 750, 1200)",
                    required=True
                ),
                InputField(
                    name="target_time",
                    label="Target Time",
                    type="float",
                    unit="hours",
                    description="Time at which to predict MTBF (optional)",
                    required=False,
                    min_value=0.0
                ),
                InputField(
                    name="confidence_level",
                    label="Confidence Level",
                    type="select",
                    unit="%",
                    description="Statistical confidence level for predictions",
                    required=True,
                    options=["90", "95", "99"],
                    default_value="95"
                ),
                InputField(
                    name="total_test_time",
                    label="Total Test Time",
                    type="float",
                    unit="hours",
                    description="Total accumulated test time (optional, will use last failure time if not provided)",
                    required=False,
                    min_value=0.0
                )
            ]
        )
    
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        validated_inputs = self.validate_inputs(inputs)
        
        failure_times_str = validated_inputs["failure_times"]
        target_time = validated_inputs.get("target_time")
        confidence_level = int(validated_inputs["confidence_level"])
        total_test_time = validated_inputs.get("total_test_time")
        
        # Parse failure times
        try:
            failure_times = [float(x.strip()) for x in failure_times_str.split(',') if x.strip()]
            failure_times.sort()  # Ensure ascending order
        except ValueError:
            raise ValueError("Failure times must be numeric values separated by commas")
        
        if len(failure_times) < 2:
            raise ValueError("At least 2 failure times are required for Duane model analysis")
        
        # Validate that failure times are in ascending order
        for i in range(1, len(failure_times)):
            if failure_times[i] <= failure_times[i-1]:
                raise ValueError("Failure times must be in strictly ascending order")
        
        # Calculate Duane model parameters
        duane_results = self._calculate_duane_model(failure_times, total_test_time)
        
        # Base results
        results = {
            "input_data": {
                "failure_times": failure_times,
                "number_of_failures": len(failure_times),
                "test_duration": duane_results["test_duration"],
                "confidence_level": confidence_level
            },
            "duane_model_parameters": duane_results["parameters"],
            "cumulative_mtbf_data": duane_results["cumulative_data"],
            "model_fit_statistics": duane_results["fit_stats"]
        }
        
        # Predict MTBF at target time if provided
        if target_time is not None and target_time > 0:
            target_prediction = self._predict_mtbf_at_time(
                target_time, duane_results["parameters"], confidence_level
            )
            results["target_prediction"] = target_prediction
        
        # Predict MTBF at final test time
        final_time = duane_results["test_duration"]
        final_prediction = self._predict_mtbf_at_time(
            final_time, duane_results["parameters"], confidence_level
        )
        results["final_prediction"] = final_prediction
        
        # Calculate reliability growth rate and interpretation
        alpha = duane_results["parameters"]["alpha"]
        beta = duane_results["parameters"]["beta"]
        
        growth_rate = (1 - beta) * 100
        results["reliability_growth"] = {
            "growth_rate_percent": round(growth_rate, 2),
            "interpretation": self._interpret_growth_rate(beta),
            "time_to_double_mtbf": self._calculate_time_to_double_mtbf(beta, final_time)
        }
        
        return results
    
    def _calculate_duane_model(self, failure_times: List[float], total_test_time: float = None) -> Dict[str, Any]:
        """
        Calculate Duane model parameters using linear regression on log-log scale.
        
        Duane Model: MTBF_c(t) = α * t^β
        Where: 
        - MTBF_c(t) is cumulative MTBF at time t
        - α is the scale parameter
        - β is the growth parameter (0 < β < 1 for improvement)
        """
        
        n_failures = len(failure_times)
        
        # Create failure numbers array (1, 2, 3, ..., n)
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
        
        # Calculate standard errors
        mse = ss_res / (n - 2) if n > 2 else 0
        s_xx = sum((x - sum_x/n) ** 2 for x in ln_times)
        se_beta = math.sqrt(mse / s_xx) if s_xx > 0 else 0
        se_alpha = math.sqrt(mse * (1/n + (sum_x/n)**2 / s_xx)) if s_xx > 0 else 0
        
        return {
            "parameters": {
                "alpha": round(alpha, 6),
                "beta": round(beta, 6),
                "ln_alpha": round(ln_alpha, 6)
            },
            "cumulative_data": {
                "failure_times": failure_times,
                "failure_numbers": failure_numbers,
                "cumulative_mtbf": [round(mtbf, 2) for mtbf in cumulative_mtbf]
            },
            "fit_stats": {
                "r_squared": round(r_squared, 6),
                "standard_error_beta": round(se_beta, 6),
                "standard_error_alpha": round(se_alpha, 6),
                "degrees_of_freedom": n - 2
            },
            "test_duration": test_duration
        }
    
    def _predict_mtbf_at_time(self, time: float, parameters: Dict[str, float], 
                             confidence_level: int) -> Dict[str, Any]:
        """Predict MTBF at a specific time using the Duane model"""
        
        alpha = parameters["alpha"]
        beta = parameters["beta"]
        
        # Predicted cumulative MTBF
        mtbf_cumulative = alpha * (time ** beta)
        
        # Instantaneous MTBF (derivative of cumulative)
        # For Duane model: MTBF_i(t) = (α/β) * t^β
        if beta != 0:
            mtbf_instantaneous = (alpha / beta) * (time ** beta)
        else:
            mtbf_instantaneous = float('inf')
        
        # Simple confidence intervals (approximate)
        # Note: For rigorous confidence intervals, we would need the full covariance matrix
        confidence_factor = {90: 1.645, 95: 1.96, 99: 2.576}[confidence_level]
        
        # Approximate confidence bounds (assuming log-normal distribution)
        ln_mtbf = math.log(mtbf_cumulative)
        se_ln_mtbf = 0.1  # Simplified standard error
        
        lower_bound = math.exp(ln_mtbf - confidence_factor * se_ln_mtbf)
        upper_bound = math.exp(ln_mtbf + confidence_factor * se_ln_mtbf)
        
        return {
            "time": time,
            "mtbf_cumulative": round(mtbf_cumulative, 2),
            "mtbf_instantaneous": round(mtbf_instantaneous, 2),
            "confidence_interval": {
                "lower": round(lower_bound, 2),
                "upper": round(upper_bound, 2),
                "level": confidence_level
            }
        }
    
    def _interpret_growth_rate(self, beta: float) -> str:
        """Interpret the reliability growth based on beta parameter"""
        
        if beta > 1:
            return "Reliability is deteriorating (β > 1)"
        elif beta == 1:
            return "No reliability growth (β = 1, constant failure rate)"
        elif beta > 0.8:
            return "Slow reliability growth (β > 0.8)"
        elif beta > 0.5:
            return "Moderate reliability growth (0.5 < β ≤ 0.8)"
        elif beta > 0.2:
            return "Good reliability growth (0.2 < β ≤ 0.5)"
        else:
            return "Excellent reliability growth (β ≤ 0.2)"
    
    def _calculate_time_to_double_mtbf(self, beta: float, current_time: float) -> float:
        """Calculate time required to double the current MTBF"""
        
        if beta <= 0 or beta >= 1:
            return float('inf')
        
        # For Duane model: MTBF(t) = α * t^β
        # To double: 2 * MTBF(t1) = MTBF(t2)
        # So: 2 * α * t1^β = α * t2^β
        # Therefore: t2 = t1 * 2^(1/β)
        
        doubling_factor = 2 ** (1 / beta)
        time_to_double = current_time * (doubling_factor - 1)
        
        return round(time_to_double, 2)