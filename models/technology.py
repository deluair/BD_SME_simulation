import numpy as np
import pandas as pd

class TechnologyAdoptionModel:
    """Model technology diffusion and digital transformation in Bangladeshi SMEs"""
    def __init__(self, config):
        """Initialize technology adoption parameters from the 'technology_adoption' section of the config."""
        print("Initializing TechnologyAdoptionModel...")
        # Ensure self.config accesses the 'technology_adoption' sub-dictionary
        self.config = config.get('technology_adoption') if isinstance(config, dict) and 'technology_adoption' in config else {}
        if not self.config:
             print("Warning: 'technology_adoption' section not found or empty in config.")

        # Load parameters with defaults
        self.initial_digital_adoption_rate = self.config.get('initial_digital_adoption_rate', 0.15)
        self.base_adoption_prob = self.config.get('base_adoption_prob', 0.05)
        self.literacy_influence_on_adoption = self.config.get('literacy_influence_on_adoption', 0.1)
        self.tech_productivity_boost = self.config.get('tech_productivity_boost', 0.03) # Renamed from config
        self.literacy_improvement_rate = self.config.get('digital_literacy_improvement_rate', 0.02) # Added from config
        # Add other parameters like tech_cost_factor_revenue if needed for more complex logic

    def simulate_adoption_dynamics(self, smes_df, year):
        """Simulate SME decisions to adopt new technologies and update digital literacy."""
        print(f"Simulating technology adoption dynamics for year {year}...")
        if smes_df is None or smes_df.empty:
            print("  SME data not available for technology adoption simulation.")
            return smes_df # Return original df
            
        required_cols = ['status', 'has_adopted_tech', 'digital_literacy', 'productivity']
        if not all(col in smes_df.columns for col in required_cols):
             print(f"  Skipping tech adoption logic: One or more required columns missing ({required_cols}).")
             # Ensure columns exist even if skipping
             for col in required_cols:
                 if col not in smes_df.columns:
                     if col == 'has_adopted_tech':
                         smes_df[col] = False # Default
                     elif col == 'digital_literacy':
                         smes_df[col] = 0.1 # Default low literacy
                     elif col == 'productivity':
                          smes_df[col] = 1.0 # Default base productivity
                     # 'status' should exist from segmentation
             # Fall through to literacy improvement
             # return smes_df # Option to fully skip

        active_smes_mask = smes_df['status'] == 'active'
        
        # --- 1. Technology Adoption Decision --- 
        # Identify non-adopters who are active
        eligible_smes_mask = active_smes_mask & (smes_df['has_adopted_tech'] == False)
        
        num_eligible = eligible_smes_mask.sum()
        if num_eligible > 0:
            # Calculate individual probability based on literacy
            prob_adopt = self.base_adoption_prob + (smes_df.loc[eligible_smes_mask, 'digital_literacy'] * self.literacy_influence_on_adoption)
            prob_adopt = np.clip(prob_adopt, 0.001, 0.95) # Keep probability reasonable

            # Determine which eligible SMEs adopt
            adopts_tech = np.random.rand(num_eligible) < prob_adopt
            
            # Get the indices of SMEs that adopt
            adopter_indices = smes_df.loc[eligible_smes_mask].index[adopts_tech]
            num_adopters = len(adopter_indices)
            
            if num_adopters > 0:
                smes_df.loc[adopter_indices, 'has_adopted_tech'] = True
                # Optional: Boost productivity for new adopters
                # Ensure productivity is numeric
                smes_df['productivity'] = pd.to_numeric(smes_df['productivity'], errors='coerce').fillna(1.0)
                productivity_boost_amount = smes_df.loc[adopter_indices, 'productivity'] * self.tech_productivity_boost
                smes_df.loc[adopter_indices, 'productivity'] += productivity_boost_amount
                print(f"  {num_adopters} SMEs adopted new technology this year.")
            else:
                 print("  No new SMEs adopted technology this year.")
        else:
            print("  No eligible SMEs (active non-adopters) found.")

        # --- 2. Digital Literacy Improvement --- 
        if 'digital_literacy' in smes_df.columns:
            # Improve literacy for all active SMEs (simplified) - Max capped at 1.0
            smes_df['digital_literacy'] = pd.to_numeric(smes_df['digital_literacy'], errors='coerce').fillna(0.1)
            literacy_increase = self.literacy_improvement_rate 
            # Can make increase stochastic or dependent on other factors later
            smes_df.loc[active_smes_mask, 'digital_literacy'] = np.clip(smes_df.loc[active_smes_mask, 'digital_literacy'] + literacy_increase, 0, 1.0)
            avg_literacy = smes_df.loc[active_smes_mask, 'digital_literacy'].mean()
            print(f"  Average digital literacy among active SMEs increased to: {avg_literacy:.3f}")
        else:
             print("  'digital_literacy' column not found, skipping improvement.")
             
        return smes_df

    # --- Potential sub-methods --- 
    # def model_digital_readiness(self, smes_df, year):
    #     pass
    # def model_technology_diffusion(self, year, environment_state):
    #     # Model overall availability and cost trends of technologies
    #     pass
    # def model_adoption_decision(self, sme_data, year, environment_state):
    #     # More complex decision logic based on ROI, skills, competition
    #     pass
    # def model_impact_on_productivity(self, smes_df, year):
    #     # Relate tech level to productivity changes
    #     pass
