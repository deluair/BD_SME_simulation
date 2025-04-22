import numpy as np
import pandas as pd

class InnovationModel:
    """Model innovation capacity and new product/process development in Bangladeshi SMEs"""
    def __init__(self, config):
        """Initialize innovation model parameters."""
        print("Initializing InnovationModel...")
        # Ensure self.config is a dictionary
        self.config = config.get('innovation') or {}
        # Load parameters like R&D investment levels, collaboration rates, IP generation
        self.base_innovation_prob = self.config.get('base_innovation_prob', 0.01) # Base probability per year
        self.skill_influence_on_innovation = self.config.get('skill_influence_on_innovation', 0.05) # How much skill level boosts prob
        # ... other parameters

    def simulate_innovation_dynamics(self, smes_df, year, environment_state):
        """Simulate innovation activities and their outcomes for SMEs."""
        print(f"Simulating innovation dynamics for year {year}...")
        if smes_df is None or smes_df.empty:
            print("SME data not available for innovation simulation.")
            return smes_df # Return the input df (None or empty)
            
        # Example: SMEs have a chance to become 'innovators'
        # Probability influenced by base rate and skill level
        if 'is_innovator' in smes_df.columns and 'skill_level' in smes_df.columns:
            not_innovators = smes_df['is_innovator'] == False
            if not_innovators.any():
                # Calculate individual probability based on skill
                # Ensure skill_level doesn't make probability > 1 or < 0
                prob_innovate = self.base_innovation_prob + (smes_df.loc[not_innovators, 'skill_level'] * self.skill_influence_on_innovation)
                prob_innovate = np.clip(prob_innovate, 0.001, 0.99) # Keep probability reasonable
                
                # Random draw for each non-innovator SME
                becomes_innovator = np.random.rand(len(prob_innovate)) < prob_innovate
                
                # Update the DataFrame for those who become innovators
                innovator_indices = smes_df.loc[not_innovators].index[becomes_innovator]
                if len(innovator_indices) > 0:
                    smes_df.loc[innovator_indices, 'is_innovator'] = True
                    print(f"  {len(innovator_indices)} SMEs became innovators this year.")
        else:
            print("  Skipping innovation dynamics logic: 'is_innovator' or 'skill_level' column missing.")
            
        # Placeholder for other innovation factors:
        # - Impact of R&D investment (if tracked)
        # - Effect of collaborations
        # - Link between innovation and productivity/revenue growth
        pass

        return smes_df # Ensure the modified DataFrame is returned

    # --- Potential sub-methods --- 
    # def model_rnd_investment(self, smes_df, year):
    #     pass
    # def model_product_process_innovation(self, smes_df, year):
    #     pass
    # def model_collaboration_networks(self, smes_df, year):
    #     pass
    # def model_ip_generation(self, smes_df, year):
    #     pass
