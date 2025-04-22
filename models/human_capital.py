import numpy as np
import pandas as pd

class HumanCapitalModel:
    """Model skills development, training, and labor market dynamics for Bangladeshi SMEs"""
    def __init__(self, config):
        """Initialize human capital model parameters."""
        print("Initializing HumanCapitalModel...")
        # Ensure self.config is a dictionary, even if 'human_capital' is missing or None in main config
        self.config = config.get('human_capital') or {}
        # Load parameters like skill gap sizes, training effectiveness, labor mobility rates
        self.initial_skill_level_index = self.config.get('initial_skill_level_index', 0.4) # Example scale 0-1
        self.skill_improvement_prob = self.config.get('skill_improvement_prob', 0.04) # Chance per year
        self.skill_improvement_amount = self.config.get('skill_improvement_amount', 0.015) # How much skill improves
        self.skill_productivity_boost = self.config.get('skill_productivity_boost', 0.02) # e.g. 2% productivity boost per skill point increase
        # ... other parameters

    def simulate_human_capital_dynamics(self, smes_df, year, labor_market_state):
        """Simulate changes in SME workforce skills and labor dynamics."""
        print(f"Simulating human capital dynamics for year {year}...")
        if smes_df is None or smes_df.empty:
            print("SME data not available for human capital simulation.")
            return smes_df # Return the input df (None or empty) instead of implicit None
            
        # Example: SMEs have a small chance to improve their average skill level
        if 'skill_level' in smes_df.columns and 'productivity' in smes_df.columns:
            # Identify SMEs that could potentially improve (e.g., active ones)
            eligible_smes = smes_df['status'] == 'active'
            if eligible_smes.any():
                # Determine which SMEs improve skills based on probability
                improves_skill = np.random.rand(eligible_smes.sum()) < self.skill_improvement_prob
                
                # Get the indices of SMEs that will improve
                improving_indices = smes_df.loc[eligible_smes].index[improves_skill]
                
                if len(improving_indices) > 0:
                    # Apply the skill improvement, ensuring it doesn't exceed a max (e.g., 1.0)
                    current_skill = smes_df.loc[improving_indices, 'skill_level']
                    new_skill = np.minimum(1.0, current_skill + self.skill_improvement_amount)
                    smes_df.loc[improving_indices, 'skill_level'] = new_skill
                    
                    # Optional: Improve productivity based on skill increase
                    productivity_boost = (new_skill - current_skill) * self.skill_productivity_boost * smes_df.loc[improving_indices, 'productivity']
                    smes_df.loc[improving_indices, 'productivity'] += productivity_boost
                    
                    print(f"  {len(improving_indices)} SMEs improved their skill level.")
        else:
            print("  Skipping human capital dynamics logic: 'skill_level' or 'productivity' column missing.")

        # Placeholder for other human capital factors:
        # - Hiring/firing decisions based on growth/decline
        # - Impact of training programs (cost vs. benefit)
        # - Labor mobility between firms/sectors
        # - Wage dynamics
        # - Specific skill types (technical, managerial, digital)
        pass

        return smes_df # Ensure the modified DataFrame is returned

    # --- Potential sub-methods --- 
    # def model_skills_gap_analysis(self, smes_df, year):
    #     pass
    # def model_training_investment(self, smes_df, year):
    #     pass
    # def model_labor_market_matching(self, year, labor_market_state):
    #     # Simulate supply/demand for skills at macro level
    #     pass
    # def model_workforce_demographics(self, smes_df, year):
    #     pass
