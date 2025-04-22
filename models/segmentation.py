import pandas as pd
import numpy as np

class SMESegmentationModel:
    """Model diverse SME types and business models in Bangladesh"""
    def __init__(self, config):
        """Initialize SME segmentation parameters using config and potentially data."""
        print("Initializing SMESegmentationModel...")
        self.config = config.get('sme_segmentation', {})
        self.data_config = config.get('data_sources', {})
        self.use_synthetic_data = self.data_config.get('use_synthetic_data', False)
        
        # Store generation params if using synthetic
        if self.use_synthetic_data:
             self.num_smes = self.config.get('num_synthetic_smes', 1000)
             self.sector_dist = self.config.get('sector_distribution', {})
             self.size_dist = self.config.get('size_distribution', {})
             self.formality_dist = self.config.get('formality_distribution', {})
             self.location_dist = self.config.get('location_distribution', {})
             self.avg_age = self.config.get('avg_business_age', 5)
             self.rev_range = self.config.get('initial_revenue_range', [10000, 1000000])
             # Ensure keys in distributions are strings
             self.sector_dist = {str(k): v for k, v in self.sector_dist.items()}
             self.size_dist = {str(k): v for k, v in self.size_dist.items()}
             self.formality_dist = {str(k): v for k, v in self.formality_dist.items()}
             self.location_dist = {str(k): v for k, v in self.location_dist.items()}
        else:
             self.initial_population = self.config.get('initial_population', 10000)

        # Placeholder for SME population DataFrame
        self.smes = None

    def initialize_population(self, data_handler, config):
        """Create the initial set of SME agents, either synthetic or from loaded data."""
        if self.use_synthetic_data:
            print(f"Generating synthetic SME population of size {self.num_smes}...")
            ids = np.arange(self.num_smes)
            
            # Generate categorical features based on distributions
            sectors = np.random.choice(list(self.sector_dist.keys()), size=self.num_smes, p=list(self.sector_dist.values()))
            sizes = np.random.choice(list(self.size_dist.keys()), size=self.num_smes, p=list(self.size_dist.values()))
            formalities = np.random.choice(list(self.formality_dist.keys()), size=self.num_smes, p=list(self.formality_dist.values()))
            locations = np.random.choice(list(self.location_dist.keys()), size=self.num_smes, p=list(self.location_dist.values()))
            
            # Generate numerical features
            # Age: simple normal distribution around mean (ensure non-negative)
            ages = np.maximum(0, np.random.normal(loc=self.avg_age, scale=self.avg_age/2, size=self.num_smes)).astype(int)
            # Revenue: simple uniform distribution within range (consider log-uniform for more realism later)
            revenues = np.random.uniform(low=self.rev_range[0], high=self.rev_range[1], size=self.num_smes)
            # Employment: correlate roughly with size category (simple approach)
            employment = np.zeros(self.num_smes, dtype=int)
            employment[sizes == 'Micro (<10 employees)'] = np.random.randint(1, 10, size=np.sum(sizes == 'Micro (<10 employees)'))
            employment[sizes == 'Small (10-49 employees)'] = np.random.randint(10, 50, size=np.sum(sizes == 'Small (10-49 employees)'))
            employment[sizes == 'Medium (50-249 employees)'] = np.random.randint(50, 250, size=np.sum(sizes == 'Medium (50-249 employees)'))
            # Handle potential empty categories if num_smes is small
            if np.sum(employment == 0) > 0:
                 print(f"Warning: {np.sum(employment == 0)} SMEs have 0 employment due to sampling. Setting to 1.")
                 employment[employment == 0] = 1 # Assign minimum employment

            # Create DataFrame
            self.smes = pd.DataFrame({
                'id': ids,
                'sector': sectors,
                'size_category': sizes, # Full description
                'formality': formalities,
                'location': locations,
                'age': ages,
                'revenue': revenues,
                'employment': employment,
                'status': 'active', # Initial status
                # --- Columns needed by specific models ---
                # Financing
                'creditworthiness': np.random.uniform(0.3, 0.8, size=self.num_smes), # Example score 0-1
                'debt': np.random.uniform(0, 50000, size=self.num_smes) * (revenues / revenues.mean()), # Debt scaled roughly by revenue
                # Technology
                'has_adopted_tech': np.random.choice([False, True], size=self.num_smes, p=[0.8, 0.2]), # Initial adoption rate
                'digital_literacy': np.random.uniform(0.1, 0.6, size=self.num_smes), # Example score 0-1
                # Human Capital
                'skill_level': np.random.uniform(0.1, 0.5, size=self.num_smes), # Example initial skill index
                # Productivity (base, influenced by others later)
                'productivity': np.random.normal(loc=1.0, scale=0.2, size=self.num_smes), # Example productivity index
                # Regulatory
                'compliance_cost': 0.0, # Initial cost, updated by model
                # Innovation
                'is_innovator': False,
                # Sustainability
                'resource_efficiency': np.random.uniform(0.1, 0.4, size=self.num_smes), # Example index
                # Resilience
                'resilience_score': np.random.uniform(0.1, 0.3, size=self.num_smes), # Example index
                # Internationalization & Market Access
                'is_exporter': False,
                'uses_ecommerce': np.random.choice([False, True], size=self.num_smes, p=[0.7, 0.3]), # Example usage
                # Inclusion
                'inclusion_score': np.random.uniform(0.2, 0.5, size=self.num_smes), # Example score 0-1
                'owner_gender': np.random.choice(['male', 'female'], size=self.num_smes, p=[1-self.config.get('initial_women_ownership_rate', 0.15), self.config.get('initial_women_ownership_rate', 0.15)]),
                'is_youth_led': np.random.choice([False, True], size=self.num_smes, p=[0.8, 0.2]) # Example youth rate
            })
            # Create 'size' column from 'size_category' for simpler model logic
            size_map = {
                'Micro (<10 employees)': 'Micro',
                'Small (10-49 employees)': 'Small',
                'Medium (50-249 employees)': 'Medium'
                # Add 'Large' if it exists in your config
            }
            self.smes['size'] = self.smes['size_category'].map(size_map).fillna('Unknown') # Add simple size column

            self.smes.set_index('id', inplace=True)
            print("Synthetic SME population generated.")

        else:
            print("Attempting to load SME population data via DataHandler...")
            # --- Placeholder for loading real data --- 
            # This is where you would load the primary SME dataset
            # Example: primary_sme_data_key = 'bbs_census' # Or another key from config
            # self.smes = data_handler.get_data(primary_sme_data_key)
            # if self.smes is None:
            #     print(f"Error: Could not load primary SME data using key '{primary_sme_data_key}'. Simulation cannot proceed without initial population.")
            #     return None
            # else:
            #     print(f"Loaded initial SME population from {primary_sme_data_key}.")
            #     # --- Data Preprocessing/Column Mapping --- 
            #     # Rename columns to match simulation expectations
            #     # Ensure required columns exist (id, sector, size_category, formality, location, age, status etc.)
            #     # Add missing placeholder columns with default values if needed
            #     # Set index to SME ID
            #     # self.smes.set_index('your_sme_id_column', inplace=True)
            #     # ... preprocessing steps ...
            print("Warning: Real data loading not implemented yet. No SME population initialized.")
            self.smes = None # Ensure it's None if loading fails or isn't implemented
            
        # Final check and return
        return self.smes

    def update_segmentation(self, smes_df, year):
        """Update SME segments based on transitions (growth, decline, formalization, exit)."""
        print(f"Updating SME segmentation for year {year}...")
        if smes_df is None:
            print("SME population data frame is None.")
            return None # Return None if input is None
        
        # Implement logic for:
        # - SME growth/shrinkage (changing size category)
        # - Formalization transitions
        # - Sector changes (less common, but possible)
        # - Business exit/failure
        # - New business entry
        # NOTE: This currently does nothing to the dataframe
        pass 

        return smes_df # Return the (potentially modified) DataFrame

    def update_business_model(self, year):
        """Update SME business models based on strategic shifts."""
        pass

    # --- Potentially add methods for specific segment dynamics --- 
    # def model_manufacturing_dynamics(self, year):
    #     pass
    # def model_service_dynamics(self, year):
    #     pass
    # def model_agribusiness_dynamics(self, year):
    #     pass
    # def model_informal_transition(self, year):
    #     pass
