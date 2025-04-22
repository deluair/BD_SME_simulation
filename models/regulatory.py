import numpy as np
import pandas as pd

class RegulatoryEnvironmentModel:
    """Model regulatory frameworks, compliance costs, and policy impacts on Bangladeshi SMEs"""
    def __init__(self, config):
        """Initialize regulatory environment parameters from the 'regulatory' section of the config."""
        print("Initializing RegulatoryEnvironmentModel...")
        # Ensure self.config accesses the 'regulatory' sub-dictionary
        self.config = config.get('regulatory') if isinstance(config, dict) and 'regulatory' in config else {}
        if not self.config:
             print("Warning: 'regulatory' section not found or empty in config.")

        # Load parameters with defaults
        self.compliance_cost_factor = self.config.get('base_compliance_cost_factor', 0.01)
        self.formalization_prob_factor = self.config.get('formalization_prob_factor', 0.01)
        self.tax_rate_revenue = self.config.get('tax_rate_revenue', 0.10)
        # Add other parameters as needed

    # Update signature to match call from main.py
    def simulate_regulatory_dynamics(self, smes_df, year, environment_state, config):
        """Simulate the impact of regulations and policies on SMEs based on scenario config."""
        # Use self.config for parameters specific to this model's section
        # Use the passed 'config' for potential cross-model parameters if needed
        print(f"Simulating regulatory dynamics for year {year}...")
        if smes_df is None or smes_df.empty:
            print("  SME data not available for regulatory simulation.")
            return smes_df # Return original df
            
        required_cols = ['status', 'formality', 'revenue']
        if not all(col in smes_df.columns for col in required_cols):
             print(f"  Skipping regulatory cost dynamics: One or more required columns missing ({required_cols}).")
             # Ensure compliance_cost column exists even if skipping
             if 'compliance_cost' not in smes_df.columns:
                 smes_df['compliance_cost'] = 0.0
             # Still attempt formalization logic if possible
        else:
            # --- 1. Compliance Cost Calculation --- 
            print(f"  Applying compliance cost factor: {self.compliance_cost_factor}")
            formal_smes_mask = (smes_df['status'] == 'active') & (smes_df['formality'] == 'Formal')
            # Ensure revenue is numeric
            smes_df['revenue'] = pd.to_numeric(smes_df['revenue'], errors='coerce').fillna(0)
            
            # Calculate cost as factor * revenue for formal SMEs
            smes_df.loc[formal_smes_mask, 'compliance_cost'] = smes_df.loc[formal_smes_mask, 'revenue'] * self.compliance_cost_factor
            # Set cost to 0 for informal or inactive SMEs
            smes_df.loc[~formal_smes_mask, 'compliance_cost'] = 0.0
            
            avg_cost = smes_df.loc[formal_smes_mask, 'compliance_cost'].mean() if formal_smes_mask.any() else 0
            print(f"  Applied compliance costs to {formal_smes_mask.sum()} formal SMEs (Average: {avg_cost:.2f}).")

        # --- 2. Formalization Decision (Placeholder) --- 
        # A more complex model would simulate the decision to formalize based on costs/benefits
        if 'formality' in smes_df.columns:
            informal_active_mask = (smes_df['status'] == 'active') & (smes_df['formality'] == 'Informal')
            if informal_active_mask.any():
                prob_formalize = self.formalization_prob_factor # Simplified base probability
                # Could be influenced by environment_state (e.g., enforcement), perceived benefits etc.
                becomes_formal = np.random.rand(informal_active_mask.sum()) < prob_formalize
                formalizing_indices = smes_df.loc[informal_active_mask].index[becomes_formal]
                if len(formalizing_indices) > 0:
                     smes_df.loc[formalizing_indices, 'formality'] = 'Formal'
                     # Potentially reset compliance cost to 0 for the first year of being formal?
                     smes_df.loc[formalizing_indices, 'compliance_cost'] = 0.0 
                     print(f"  {len(formalizing_indices)} SMEs transitioned to Formal status.")

        # --- 3. Tax Calculation (Placeholder) --- 
        # Need profit calculation first (Revenue - Costs - Compliance Cost etc.)
        # if 'profit' in smes_df.columns:
        #     smes_df['tax_payable'] = np.maximum(0, smes_df['profit'] * self.tax_rate_revenue)
            
        return smes_df

    # --- Potential sub-methods --- 
    # def model_compliance_burden(self, smes_df, year, policy_scenario):
    #     pass
    # def model_policy_impact_analysis(self, smes_df, year, policy_details):
    #     pass
    # def model_enforcement_effects(self, smes_df, year):
    #     pass
    # def model_formalization_incentives(self, smes_df, year):
    #     pass
