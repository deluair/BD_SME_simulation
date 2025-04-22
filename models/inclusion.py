import numpy as np
import pandas as pd

class InclusionModel:
    """Model inclusive business models and diversity within Bangladeshi SMEs"""
    def __init__(self, config):
        """Initialize inclusion model parameters."""
        print("Initializing InclusionModel...")
        # Ensure self.config is a dictionary
        self.config = config.get('inclusion') or {}
        # Load parameters like female entrepreneurship rates, disability inclusion metrics, base-of-pyramid market focus
        self.initial_inclusion_score = self.config.get('initial_inclusion_score', 0.2) # Example scale 0-1
        self.inclusion_improvement_prob = self.config.get('inclusion_improvement_prob', 0.02) # Chance per year
        self.inclusion_improvement_amount = self.config.get('inclusion_improvement_amount', 0.01) # How much score improves
        # ... other parameters

    def simulate_inclusion_dynamics(self, smes_df, year, environment_state, policy_scenario):
        """Simulate the evolution of inclusive practices in SMEs."""
        print(f"Simulating inclusion dynamics for year {year} (Scenario: {policy_scenario})...")
        if smes_df is None or smes_df.empty:
            print("SME data not available for inclusion simulation.")
            return
            
        # Example: SMEs have a small chance to improve their 'inclusion_score'
        if 'inclusion_score' in smes_df.columns:
            # Identify SMEs that could potentially improve (e.g., active ones)
            eligible_smes = smes_df['status'] == 'active'
            if eligible_smes.any():
                # Determine which SMEs improve based on probability
                improves_inclusion = np.random.rand(eligible_smes.sum()) < self.inclusion_improvement_prob
                
                # Get the indices of SMEs that will improve
                improving_indices = smes_df.loc[eligible_smes].index[improves_inclusion]
                
                if len(improving_indices) > 0:
                    # Apply the improvement, ensuring it doesn't exceed a max (e.g., 1.0)
                    current_score = smes_df.loc[improving_indices, 'inclusion_score']
                    new_score = np.minimum(1.0, current_score + self.inclusion_improvement_amount)
                    smes_df.loc[improving_indices, 'inclusion_score'] = new_score
                    print(f"  {len(improving_indices)} SMEs improved their inclusion score.")
        else:
            print("  Skipping inclusion dynamics logic: 'inclusion_score' column missing.")
            
        # Placeholder for other inclusion factors:
        # - Tracking female/disabled employment/ownership rates
        # - Adoption of specific inclusive business models (e.g., targeting BoP markets)
        # - Impact of policies promoting inclusion
        # - Link between inclusion and other outcomes (resilience, market access)
        pass
        
        return smes_df # Ensure the modified DataFrame is returned

    # --- Potential sub-methods --- 
    # def model_gender_diversity(self, smes_df, year):
    #     pass
    # def model_disability_inclusion(self, smes_df, year):
    #     pass
    # def model_bop_market_strategies(self, smes_df, year):
    #     pass
    # def model_inclusive_value_chains(self, smes_df, year):
    #     pass
    # def calculate_inclusion_adoption_prob(self, sme_data, practice_type, year, policy_scenario):
    #     # Based on awareness, cost/benefit, incentives, social norms etc.
    #     return 0.0 # Placeholder
