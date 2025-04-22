import numpy as np
import pandas as pd

class InternationalizationModel:
    """Model export capacity building and global market integration for Bangladeshi SMEs"""
    def __init__(self, config):
        """Initialize internationalization model parameters."""
        print("Initializing InternationalizationModel...")
        # Ensure self.config is a dictionary
        self.config = config.get('internationalization') or {}
        # Load parameters like export readiness thresholds, target market access factors, GVC linkage probabilities
        self.initial_export_propensity_index = self.config.get('initial_export_propensity_index', 0.1) # Example scale 0-1
        self.export_entry_prob_medium_large = self.config.get('export_entry_prob_medium_large', 0.05) # Base prob for M/L SMEs
        self.export_revenue_boost = self.config.get('export_revenue_boost', 0.15) # e.g. 15% boost if exporting
        # ... other parameters

    def simulate_internationalization_dynamics(self, smes_df, year, environment_state, market_access_state):
        """Simulate SME internationalization activities (exporting, GVCs)."""
        print(f"Simulating internationalization dynamics for year {year}...")
        if smes_df is None or smes_df.empty:
            print("SME data not available for internationalization simulation.")
            return smes_df # Return the input df (None or empty)
        
        # Example: Medium/Large SMEs have a chance to become exporters
        if 'is_exporter' in smes_df.columns and 'size' in smes_df.columns and 'revenue' in smes_df.columns:
            # Identify non-exporting Medium or Large SMEs
            eligible_smes = (smes_df['is_exporter'] == False) & (smes_df['size'].isin(['Medium', 'Large'])) & (smes_df['status'] == 'active')
            
            if eligible_smes.any():
                # Determine which eligible SMEs become exporters based on probability
                becomes_exporter = np.random.rand(eligible_smes.sum()) < self.export_entry_prob_medium_large
                
                # Get the indices of SMEs that will start exporting
                exporting_indices = smes_df.loc[eligible_smes].index[becomes_exporter]
                
                if len(exporting_indices) > 0:
                    smes_df.loc[exporting_indices, 'is_exporter'] = True
                    # Optional: Give an initial revenue boost for becoming an exporter
                    revenue_boost_amount = smes_df.loc[exporting_indices, 'revenue'] * self.export_revenue_boost
                    smes_df.loc[exporting_indices, 'revenue'] += revenue_boost_amount
                    print(f"  {len(exporting_indices)} SMEs started exporting this year.")
        else:
            print("  Skipping internationalization dynamics logic: 'is_exporter', 'size', or 'revenue' column missing.")

        # Placeholder for other internationalization factors:
        # - Impact of export promotion policies
        # - Dynamics of existing exporters (increasing/decreasing exports, exiting markets)
        # - Integration into Global Value Chains (GVCs)
        # - Role of trade agreements or infrastructure (from environment_state)
        pass

        return smes_df # Ensure the modified DataFrame is returned

    # --- Potential sub-methods --- 
    # def model_export_readiness(self, smes_df, year):
    #     pass
    # def model_target_market_selection(self, smes_df, year, global_market_data):
    #     pass
    # def model_gvc_integration(self, smes_df, year, environment_state):
    #     pass
    # def model_export_performance(self, smes_df, year):
    #     pass
