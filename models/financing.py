import numpy as np
import pandas as pd

class SMEFinancingModel:
    """Model SME access to finance, credit risk, and investment behavior in Bangladesh"""
    def __init__(self, config):
        """Initialize financing model parameters from the 'financing' section of the config."""
        print("Initializing SMEFinancingModel...")
        # Ensure self.config accesses the 'financing' sub-dictionary
        self.config = config.get('financing') if isinstance(config, dict) and 'financing' in config else {}
        if not self.config:
             print("Warning: 'financing' section not found or empty in config.")

        # Load parameters with defaults
        self.base_loan_seek_prob = self.config.get('base_loan_seek_prob', 0.15)
        self.base_approval_factor = self.config.get('base_loan_approval_prob_factor', 0.5)
        self.avg_loan_size_factor = self.config.get('avg_loan_size_factor', 0.2) # Loan size as fraction of revenue
        self.max_debt_ratio = self.config.get('max_debt_ratio_threshold', 0.7)
        self.credit_guarantee_effect = self.config.get('credit_guarantee_effectiveness', 0.1)
        self.interest_rate_mean = self.config.get('interest_rate_mean', 0.09)
        self.interest_rate_stddev = self.config.get('interest_rate_stddev', 0.02)
        # Add other parameters as needed

    def simulate_financing_dynamics(self, smes_df, year):
        """Simulate SMEs seeking and potentially receiving financing based on scenario parameters."""
        print(f"Simulating financing dynamics for year {year}...")
        if smes_df is None or smes_df.empty:
            print("  SME data not available for financing simulation.")
            return smes_df # Return the original df if empty
            
        if not all(col in smes_df.columns for col in ['status', 'creditworthiness', 'debt', 'revenue', 'assets']):
             print("  Skipping financing dynamics: Required columns ('status', 'creditworthiness', 'debt', 'revenue', 'assets') missing.")
             # Ensure 'debt' column exists even if skipping
             if 'debt' not in smes_df.columns:
                  smes_df['debt'] = 0.0
             return smes_df

        # --- 1. SMEs Seeking Loans --- 
        active_smes_mask = smes_df['status'] == 'active'
        # Probability of seeking a loan can depend on factors, here simplified
        seeks_loan_prob = self.base_loan_seek_prob # Could add factors like growth plans, cash flow need etc.
        smes_seeking_loan = active_smes_mask & (np.random.rand(len(smes_df)) < seeks_loan_prob)
        
        num_seeking = smes_seeking_loan.sum()
        if num_seeking == 0:
            print("  No SMEs seeking loans this year.")
            # Simulate loan repayment even if no new loans
            smes_df = self._simulate_loan_repayment(smes_df, year)
            return smes_df
            
        print(f"  {num_seeking} SMEs are seeking loans.")

        # --- 2. Loan Approval Probability Calculation --- 
        approval_probs = pd.Series(0.0, index=smes_df.index)
        seeking_indices = smes_df[smes_seeking_loan].index

        # Calculate debt ratio (Debt / Assets) - handle potential division by zero
        # Ensure assets is numeric and non-zero before division
        smes_df['assets'] = pd.to_numeric(smes_df['assets'], errors='coerce').fillna(0)
        debt_ratio = smes_df.loc[seeking_indices, 'debt'] / smes_df.loc[seeking_indices, 'assets'].replace(0, np.inf)
        
        # Base approval probability adjusted by factors
        prob = self.base_approval_factor
        prob *= smes_df.loc[seeking_indices, 'creditworthiness'] # Higher creditworthiness increases chance
        prob *= (1 - np.clip(debt_ratio / self.max_debt_ratio, 0, 1)) # Lower prob if debt ratio high
        # Add effect of credit guarantee (simplified assumption: all seekers potentially eligible)
        prob += self.credit_guarantee_effect 
        
        # Clip probability between 0 and 1
        approval_probs.loc[seeking_indices] = np.clip(prob, 0, 1)

        # --- 3. Determine Loan Recipients --- 
        gets_loan_mask = (np.random.rand(len(smes_df)) < approval_probs) & smes_seeking_loan
        loan_recipient_indices = smes_df[gets_loan_mask].index
        num_recipients = len(loan_recipient_indices)
        
        if num_recipients > 0:
            print(f"  {num_recipients} SMEs received loans this year.")
            # --- 4. Calculate Loan Amount & Update Debt --- 
            # Ensure revenue is numeric
            smes_df['revenue'] = pd.to_numeric(smes_df['revenue'], errors='coerce').fillna(0)
            # Calculate loan amount (e.g., fraction of revenue)
            loan_amount = smes_df.loc[loan_recipient_indices, 'revenue'] * self.avg_loan_size_factor
            # Add loan amount to existing debt (ensure debt is numeric)
            smes_df['debt'] = pd.to_numeric(smes_df['debt'], errors='coerce').fillna(0)
            smes_df.loc[loan_recipient_indices, 'debt'] += loan_amount
            # Optional: Log or use loan for investment (update another column)
            # smes_df.loc[loan_recipient_indices, 'investment_this_year'] = loan_amount 
        else:
             print("  No SMEs received loans this year after assessment.")
             
        # --- 5. Simulate Loan Repayment --- 
        smes_df = self._simulate_loan_repayment(smes_df, year)

        return smes_df
        
    def _simulate_loan_repayment(self, smes_df, year):
        """Placeholder for simulating loan repayment, reducing debt over time."""
        if 'debt' in smes_df.columns and 'revenue' in smes_df.columns:
             # Very simple repayment model: repay a fraction of outstanding debt based on revenue
             # Needs a proper amortization schedule in a real model
             repayment_capacity_factor = 0.05 # e.g., 5% of revenue available for debt service
             max_repayment = smes_df['revenue'] * repayment_capacity_factor
             # Assume a fixed fraction of debt is *due* (e.g. 10% of principal per year simple)
             # This is highly simplified! 
             repayment_due_fraction = 0.10 
             repayment_amount = np.minimum(smes_df['debt'] * repayment_due_fraction, max_repayment)
             repayment_amount = np.maximum(repayment_amount, 0) # Ensure non-negative repayment
             
             smes_df['debt'] = np.maximum(0, smes_df['debt'] - repayment_amount) # Decrease debt, floor at 0
        return smes_df

    # --- Potential sub-methods from previous version (kept for reference) --- 
    # def model_credit_demand(self, smes_df, year):
    #     pass
    # def model_credit_supply(self, year, environment_state, policy_scenario):
    #     pass
    # def model_credit_risk_assessment(self, smes_df, year):
    #     pass
    # def model_investment_decisions(self, smes_df, year):
    #     pass
    # def calculate_loan_probability(self, sme_data, year, environment_state):
    #     return 0.0 # Placeholder
