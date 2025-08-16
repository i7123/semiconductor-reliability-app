import math
from typing import Dict, Any
from .base import BaseCalculator, CalculatorInfo, InputField

class TestSampleSizeCalculator(BaseCalculator):
    """Test Sample Size Calculator for reliability demonstration testing"""
    
    @property
    def info(self) -> CalculatorInfo:
        return CalculatorInfo(
            id="test_sample_size",
            name="Test Sample Size Calculator",
            description="Calculate required sample size for reliability demonstration testing",
            category="Test Planning",
            input_fields=[
                InputField(
                    name="target_reliability",
                    label="Target Reliability",
                    type="float",
                    unit="",
                    description="Required reliability level (0-1, e.g., 0.95 for 95%)",
                    required=True,
                    min_value=0.1,
                    max_value=0.999
                ),
                InputField(
                    name="confidence_level",
                    label="Confidence Level",
                    type="select",
                    unit="%",
                    description="Statistical confidence level",
                    required=True,
                    options=["80", "90", "95", "99"],
                    default_value="90"
                ),
                InputField(
                    name="test_type",
                    label="Test Type",
                    type="select",
                    unit="",
                    description="Type of reliability test",
                    required=True,
                    options=["success_run", "time_terminated", "failure_terminated"],
                    default_value="success_run"
                ),
                InputField(
                    name="test_duration",
                    label="Test Duration",
                    type="float",
                    unit="hours",
                    description="Duration of each test (for time-terminated tests)",
                    required=False,
                    min_value=0.0
                ),
                InputField(
                    name="target_mtbf",
                    label="Target MTBF",
                    type="float",
                    unit="hours",
                    description="Target Mean Time Between Failures",
                    required=False,
                    min_value=0.0
                ),
                InputField(
                    name="max_failures",
                    label="Maximum Allowed Failures",
                    type="int",
                    unit="",
                    description="Maximum number of failures allowed in test",
                    required=False,
                    min_value=0,
                    max_value=100
                )
            ]
        )
    
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        validated_inputs = self.validate_inputs(inputs)
        
        target_reliability = validated_inputs["target_reliability"]
        confidence_level = int(validated_inputs["confidence_level"])
        test_type = validated_inputs["test_type"]
        test_duration = validated_inputs.get("test_duration")
        target_mtbf = validated_inputs.get("target_mtbf")
        max_failures = validated_inputs.get("max_failures", 0)
        
        # Chi-square critical values for different confidence levels
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
            # Success run testing (zero failures allowed)
            # n = ln(1-C) / ln(R) where C = confidence, R = reliability
            confidence_decimal = confidence_level / 100
            sample_size = math.log(1 - confidence_decimal) / math.log(target_reliability)
            sample_size = math.ceil(sample_size)
            
            results.update({
                "required_sample_size": sample_size,
                "test_method": "Success Run Test",
                "description": f"Test {sample_size} units with zero failures to demonstrate {target_reliability:.3f} reliability at {confidence_level}% confidence"
            })
            
        elif test_type == "time_terminated" and test_duration and target_mtbf:
            # Time-terminated test
            # Total test time = chi_square * MTBF / 2
            chi_square = chi_square_values[confidence_level][max_failures]
            total_test_time = chi_square * target_mtbf / 2
            sample_size = math.ceil(total_test_time / test_duration)
            
            results.update({
                "required_sample_size": sample_size,
                "total_test_time": round(total_test_time, 2),
                "test_duration_per_unit": test_duration,
                "test_method": "Time-Terminated Test",
                "chi_square_value": chi_square,
                "description": f"Test {sample_size} units for {test_duration} hours each (total {total_test_time:.0f} hours) with max {max_failures} failures"
            })
            
        elif test_type == "failure_terminated" and target_mtbf:
            # Failure-terminated test
            chi_square = chi_square_values[confidence_level][max_failures]
            total_test_time = chi_square * target_mtbf / 2
            
            # For failure-terminated, we need to estimate sample size based on expected failures
            if max_failures > 0:
                # Estimate sample size assuming uniform failure distribution
                estimated_sample_size = max_failures * 3  # Conservative estimate
            else:
                estimated_sample_size = 10  # Minimum for zero-failure test
            
            results.update({
                "estimated_sample_size": estimated_sample_size,
                "expected_total_test_time": round(total_test_time, 2),
                "test_method": "Failure-Terminated Test",
                "chi_square_value": chi_square,
                "description": f"Test until {max_failures} failures occur, expecting ~{total_test_time:.0f} total test hours"
            })
        
        # Calculate test efficiency metrics
        if "required_sample_size" in results:
            total_units = results["required_sample_size"]
            if test_duration:
                total_test_hours = total_units * test_duration
                results["total_test_hours"] = round(total_test_hours, 2)
                results["test_cost_factor"] = round(total_test_hours / 1000, 2)  # Relative cost factor
        
        # Add recommendations
        recommendations = []
        
        if target_reliability > 0.99:
            recommendations.append("High reliability target requires large sample sizes")
        
        if confidence_level >= 95:
            recommendations.append("High confidence level increases required sample size")
        
        if test_type == "success_run" and target_reliability > 0.95:
            recommendations.append("Consider time-terminated testing for cost efficiency")
        
        if recommendations:
            results["recommendations"] = recommendations
        
        # Calculate alternative scenarios
        alternatives = []
        
        if test_type == "success_run":
            # Show what happens with lower confidence
            for alt_conf in [80, 90]:
                if alt_conf != confidence_level:
                    alt_confidence_decimal = alt_conf / 100
                    alt_sample_size = math.ceil(math.log(1 - alt_confidence_decimal) / math.log(target_reliability))
                    alternatives.append({
                        "confidence_level": alt_conf,
                        "sample_size": alt_sample_size,
                        "reduction": results["required_sample_size"] - alt_sample_size
                    })
        
        if alternatives:
            results["alternative_scenarios"] = alternatives
        
        return results