import math
from typing import Dict, Any
from .base import BaseCalculator, CalculatorInfo, InputField
from scipy import stats

class MTBFCalculator(BaseCalculator):
    """Mean Time Between Failures (MTBF) Calculator for semiconductor devices"""
    
    @property
    def info(self) -> CalculatorInfo:
        return CalculatorInfo(
            id="mtbf",
            name="MTBF Calculator",
            description="Calculate Mean Time Between Failures for semiconductor devices",
            category="Reliability",
            input_fields=[
                InputField(
                    name="failure_rate",
                    label="Failure Rate (λ)",
                    type="float",
                    unit="failures/hour",
                    description="Device failure rate in failures per hour",
                    required=True,
                    min_value=0.0
                ),
                InputField(
                    name="operating_hours",
                    label="Operating Hours",
                    type="float",
                    unit="hours",
                    description="Total operating hours (optional, for reliability calculation)",
                    required=False,
                    min_value=0.0
                ),
                InputField(
                    name="confidence_level",
                    label="Confidence Level",
                    type="select",
                    unit="%",
                    description="Statistical confidence level",
                    required=True,
                    options=["90", "95", "99"],
                    default_value="95"
                ),
                InputField(
                    name="num_failures",
                    label="Number of Failures",
                    type="int",
                    unit="",
                    description="Number of observed failures (for precise confidence intervals)",
                    required=False,
                    min_value=0,
                    max_value=1000
                ),
                InputField(
                    name="test_time",
                    label="Total Test Time",
                    type="float",
                    unit="hours",
                    description="Total test time (for precise confidence intervals)",
                    required=False,
                    min_value=0.0
                )
            ]
        )
    
    def calculate(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        validated_inputs = self.validate_inputs(inputs)
        
        failure_rate = validated_inputs["failure_rate"]
        operating_hours = validated_inputs.get("operating_hours")
        confidence_level = int(validated_inputs["confidence_level"])
        num_failures = validated_inputs.get("num_failures")
        test_time = validated_inputs.get("test_time")
        
        # Basic MTBF calculation
        mtbf_hours = 1 / failure_rate if failure_rate > 0 else float('inf')
        mtbf_years = mtbf_hours / (365.25 * 24)
        
        results = {
            "mtbf_hours": round(mtbf_hours, 2),
            "mtbf_years": round(mtbf_years, 4),
            "failure_rate": failure_rate,
            "confidence_level": confidence_level
        }
        
        # Calculate reliability if operating hours provided
        if operating_hours is not None:
            reliability = math.exp(-failure_rate * operating_hours)
            unreliability = 1 - reliability
            
            results.update({
                "reliability": round(reliability, 6),
                "unreliability": round(unreliability, 6),
                "reliability_percent": round(reliability * 100, 4),
                "operating_hours": operating_hours
            })
        
        # Precise confidence interval calculations using chi-square distribution
        confidence_intervals = self._calculate_precise_confidence_intervals(
            failure_rate, confidence_level, num_failures, test_time
        )
        
        if confidence_intervals:
            results.update(confidence_intervals)
        
        return results
    
    def _calculate_precise_confidence_intervals(self, failure_rate: float, confidence_level: int, 
                                              num_failures: int = None, test_time: float = None) -> Dict[str, Any]:
        """
        Calculate precise confidence intervals using chi-square distribution.
        
        For exponential distribution (constant failure rate):
        - MTBF = Total Test Time / Number of Failures
        - 2*T*λ follows chi-square distribution with 2*r degrees of freedom
        """
        
        # If we have test data (failures and test time), use precise method
        if num_failures is not None and test_time is not None and test_time > 0:
            return self._precise_confidence_interval_from_test_data(
                num_failures, test_time, confidence_level
            )
        
        # If we only have failure rate, use method assuming this is from test data
        elif failure_rate > 0:
            return self._confidence_interval_from_failure_rate(
                failure_rate, confidence_level
            )
        
        return {}
    
    def _precise_confidence_interval_from_test_data(self, num_failures: int, test_time: float, 
                                                   confidence_level: int) -> Dict[str, Any]:
        """Calculate precise confidence intervals from actual test data"""
        
        alpha = (100 - confidence_level) / 100
        
        # For zero failures case
        if num_failures == 0:
            # Use chi-square with 2 degrees of freedom for upper bound
            chi2_upper = stats.chi2.ppf(1 - alpha/2, 2)
            mtbf_lower = float(2 * test_time / chi2_upper)
            mtbf_upper = float('inf')  # Infinite upper bound for zero failures
            
            failure_rate_lower = 0.0
            failure_rate_upper = float(chi2_upper / (2 * test_time))
            
        else:
            # For r failures, use chi-square with 2r degrees of freedom
            df = 2 * num_failures
            
            # Chi-square critical values
            chi2_lower = stats.chi2.ppf(alpha/2, df)
            chi2_upper = stats.chi2.ppf(1 - alpha/2, df)
            
            # MTBF confidence limits
            mtbf_lower = float(2 * test_time / chi2_upper)
            mtbf_upper = float(2 * test_time / chi2_lower)
            
            # Failure rate confidence limits (inverse of MTBF)
            failure_rate_lower = float(chi2_lower / (2 * test_time))
            failure_rate_upper = float(chi2_upper / (2 * test_time))
        
        # Observed MTBF from test data
        if num_failures > 0:
            observed_mtbf = test_time / num_failures
            observed_failure_rate = num_failures / test_time
        else:
            observed_mtbf = float('inf')
            observed_failure_rate = 0.0
        
        return {
            "precise_analysis": {
                "test_data": {
                    "failures": num_failures,
                    "test_time": test_time,
                    "observed_mtbf": round(observed_mtbf, 2) if observed_mtbf != float('inf') else "∞",
                    "observed_failure_rate": round(observed_failure_rate, 8)
                },
                "mtbf_confidence_interval": {
                    "lower": round(mtbf_lower, 2),
                    "upper": round(mtbf_upper, 2) if mtbf_upper != float('inf') else "∞",
                    "method": "Chi-square exact"
                },
                "failure_rate_confidence_interval": {
                    "lower": round(failure_rate_lower, 8),
                    "upper": round(failure_rate_upper, 8),
                    "method": "Chi-square exact"
                }
            }
        }
    
    def _confidence_interval_from_failure_rate(self, failure_rate: float, confidence_level: int) -> Dict[str, Any]:
        """
        Calculate confidence intervals when only failure rate is known.
        Assumes this comes from sufficient test data for normal approximation.
        """
        
        mtbf = 1 / failure_rate
        alpha = (100 - confidence_level) / 100
        
        # For large sample approximation (when we don't know the exact test conditions)
        # Use the fact that MTBF estimates are approximately log-normal distributed
        
        # Approximate standard error for MTBF (assuming Poisson process)
        # This is a reasonable approximation when we don't have the original test data
        z_values = {90: 1.645, 95: 1.96, 99: 2.576}
        z = z_values[confidence_level]
        
        # For exponential distribution, coefficient of variation = 1
        # Standard error of MTBF ≈ MTBF (for single observation)
        # For better approximation, assume this comes from reasonable sample size
        assumed_failures = 10  # Conservative assumption for approximation
        
        # Using chi-square approximation
        df = 2 * assumed_failures
        chi2_lower = stats.chi2.ppf(alpha/2, df)
        chi2_upper = stats.chi2.ppf(1 - alpha/2, df)
        
        # Approximate confidence bounds
        mtbf_lower = float(mtbf * df / chi2_upper)
        mtbf_upper = float(mtbf * df / chi2_lower)
        
        failure_rate_lower = float(1 / mtbf_upper)
        failure_rate_upper = float(1 / mtbf_lower)
        
        return {
            "approximate_analysis": {
                "note": f"Approximate confidence intervals (assuming ~{assumed_failures} failures observed)",
                "mtbf_confidence_interval": {
                    "lower": round(mtbf_lower, 2),
                    "upper": round(mtbf_upper, 2),
                    "method": "Chi-square approximation"
                },
                "failure_rate_confidence_interval": {
                    "lower": round(failure_rate_lower, 8),
                    "upper": round(failure_rate_upper, 8),
                    "method": "Chi-square approximation"
                }
            }
        }