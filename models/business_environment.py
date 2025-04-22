import numpy as np

class BusinessEnvironmentModel:
    """Model broader infrastructural and ecosystem factors affecting Bangladeshi SMEs"""
    def __init__(self, config):
        """Initialize business environment parameters."""
        print("Initializing BusinessEnvironmentModel...")
        # Ensure self.config is a dictionary
        self.config = config.get('business_environment') or {}
        # Load parameters like infrastructure quality, corruption levels, market competition dynamics
        self.initial_infra_index = self.config.get('initial_infra_index', 0.5) # Example scale 0-1
        self.annual_infra_improvement_rate = self.config.get('annual_infra_improvement_rate', 0.01) # 1% improvement per year
        # Store the current state internally
        self.current_infra_index = self.initial_infra_index
        self.current_environment_state = {}
        # ... other parameters

    def simulate_environment_dynamics(self, year, policy_scenario='baseline'):
        """Simulate changes in the macro business environment (infrastructure, competition etc.)."""
        print(f"Simulating business environment dynamics for year {year} (Scenario: {policy_scenario})...")
        
        # Example: Simulate gradual infrastructure improvement
        # Start from the initial value in the first simulation year (e.g., 2025)
        # This assumes __init__ is called once per simulation run/scenario
        # More robust: Calculate based on start_year and current year
        start_year = self.config.get('start_year', 2025) # Need access to sim start year
        years_passed = max(0, year - start_year)
        self.current_infra_index = self.initial_infra_index * (1 + self.annual_infra_improvement_rate)**years_passed
        # Cap the index (e.g., at 1.0)
        self.current_infra_index = min(self.current_infra_index, 1.0) 
        
        print(f"  Calculated Infrastructure Index: {self.current_infra_index:.3f}")

        # Placeholder for other factors (competition, corruption index, etc.)
        # These could also change based on year and policy_scenario

        # Return the current state as a dictionary for other models to use
        self.current_environment_state = {
            'infrastructure_index': self.current_infra_index,
            'competition_level': self.config.get('initial_competition_level', 0.6), # Static example
            'policy_scenario': policy_scenario
            # Add other state variables here
        }
        return self.current_environment_state

    # --- Potential sub-methods --- 
    # def model_infrastructure_development(self, year, policy_scenario):
    #     pass
    # def model_market_competition(self, year):
    #     pass
    # def model_corruption_perception(self, year, policy_scenario):
    #     pass
    # def model_political_stability(self, year):
    #     pass
