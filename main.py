import yaml
import pandas as pd
import numpy as np
import time
import os
import copy # Needed for deep copying config dictionaries

# Import model classes (assuming they are in the 'models' directory)
from models.segmentation import SMESegmentationModel
from models.financing import SMEFinancingModel
from models.technology import TechnologyAdoptionModel
from models.market_access import MarketAccessModel
from models.human_capital import HumanCapitalModel
from models.regulatory import RegulatoryEnvironmentModel
from models.business_environment import BusinessEnvironmentModel
from models.innovation import InnovationModel
from models.sustainability import SustainabilityModel
from models.resilience import ResilienceModel
from models.internationalization import InternationalizationModel
from models.inclusion import InclusionModel
from data_handler import SMEDataHandler


def merge_configs(default, override):
    """Deeply merges override dict into default dict."""
    merged = copy.deepcopy(default)
    for key, value in override.items():
        if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value
    return merged

class BangladeshSMESimulation:
    """Main simulation environment integrating all components for Bangladesh SME sector."""
    def __init__(self, config_path='config.yaml'):
        """Initialize the simulation environment."""
        print("Initializing Bangladesh SME Simulation...")
        self.config_path = config_path
        self.raw_config = self._load_config()
        if not self.raw_config:
            raise ValueError("Failed to load configuration.")

        self.sim_params = self.raw_config.get('simulation_parameters', {})
        self.start_year = self.sim_params.get('start_year', 2025)
        self.end_year = self.sim_params.get('end_year', 2035)
        self.current_year = self.start_year
        self.results = {} # Stores results keyed by scenario_name, then year
        self.current_scenario_name = None
        self.config = None # Will hold the merged config for the current scenario
        self.smes_df = None

        # Initialize data handler (needed for population generation)
        self.data_handler = SMEDataHandler(config_path=self.config_path)
        self.data_handler.load_historical_data() # Load data needed for initialization

        # Models will be initialized per scenario in _reset_simulation_state
        self.business_segments = None
        self.financing = None
        self.technology = None
        self.market_access = None
        self.human_capital = None
        self.regulatory = None
        self.business_environment = None
        self.innovation = None
        self.sustainability = None
        self.resilience = None
        self.internationalization = None
        self.inclusion = None
        self.environment_state = {}
        self.labor_market_state = {}

        print("Simulation environment initialized.")

    def _load_config(self):
        """Loads the simulation configuration file."""
        print(f"Loading configuration from {self.config_path}...")
        try:
            with open(self.config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            print("Configuration loaded successfully.")
            return config_data
        except FileNotFoundError:
            print(f"ERROR: Configuration file not found at {self.config_path}")
            return None
        except yaml.YAMLError as e:
            print(f"ERROR: Error parsing configuration file: {e}")
            return None
        except Exception as e:
            print(f"ERROR: An unexpected error occurred while loading config: {e}")
            return None

    def _get_scenario_config(self, scenario_name):
        """Constructs the complete configuration for a given scenario."""
        if 'default_parameters' not in self.raw_config:
            print("ERROR: 'default_parameters' section missing in config.")
            return None
        
        # 1. Start with essential top-level sections (use deepcopy to avoid modifying raw_config)
        final_config = {
            'simulation_parameters': copy.deepcopy(self.raw_config.get('simulation_parameters', {})),
            'data_sources': copy.deepcopy(self.raw_config.get('data_sources', {}))
            # Add other essential top-level sections if they exist and are needed
        }

        # 2. Merge default model parameters with scenario overrides
        defaults = self.raw_config['default_parameters']
        scenarios = self.raw_config.get('scenarios', {})
        
        if scenario_name not in scenarios:
            print(f"Warning: Scenario '{scenario_name}' not found in config. Using defaults only.")
            scenario_overrides = {}
        else:
            scenario_overrides = scenarios[scenario_name] or {}
            scenario_overrides.pop('description', None) 

        merged_model_params = merge_configs(defaults, scenario_overrides)

        # 3. Add the merged model parameters into the final config
        #    These will be top-level keys like 'sme_segmentation', 'financing', etc.
        final_config.update(merged_model_params)

        return final_config

    def run_simulation(self, scenarios_to_run):
        """Execute the simulation over the defined time period for specified scenarios."""
        if not scenarios_to_run:
            print("No scenarios specified to run.")
            return {}
            
        print(f"\n----- Starting Simulation Runs for Scenarios: {', '.join(scenarios_to_run)} -----")
        self.results = {} # Clear previous results

        for scenario_name in scenarios_to_run:
            print(f"\n----- Running Simulation: Scenario '{scenario_name}' ----- ")
            self.current_scenario_name = scenario_name
            self.config = self._get_scenario_config(scenario_name)
            if self.config is None:
                print(f"ERROR: Could not load configuration for scenario '{scenario_name}'. Skipping.")
                continue

            self._reset_simulation_state() # Reset state using self.config
            if self.smes_df is None:
                 print(f"ERROR: Failed to initialize SME population for scenario '{scenario_name}'. Skipping.")
                 continue
                 
            scenario_run_results = {} # Store results for this specific scenario run
            for year in range(self.start_year, self.end_year + 1):
                start_time = time.time()
                print(f"\n--- Simulating Year {year} --- Scenario: {scenario_name} ---")
                self.current_year = year
                self.step() # Run one year step using self.config
                self._collect_results(year) # Collect results into self.results[scenario_name]
                end_time = time.time()
                print(f"--- Year {year} completed in {end_time - start_time:.2f} seconds ---")
            
            # Note: _collect_results now stores directly into self.results[scenario_name]
            print(f"----- Scenario '{scenario_name}' Finished ----- ")

        print("\nSimulation Run Completed for all specified scenarios.")
        self.current_scenario_name = None # Reset current scenario
        self.config = None
        return self.results

    def _reset_simulation_state(self):
        """Resets the simulation state using the current self.config."""
        print("Resetting simulation state...")
        if self.config is None:
            print("ERROR: Cannot reset state without a loaded scenario configuration.")
            return
            
        np.random.seed(self.config.get('simulation_parameters', {}).get('random_seed', 42)) # Reset seed for reproducibility

        # Initialize/Re-initialize models with the current scenario config
        print("  Initializing models for the current scenario...")
        self.business_segments = SMESegmentationModel(self.config) 
        self.financing = SMEFinancingModel(self.config)
        self.technology = TechnologyAdoptionModel(self.config)
        self.market_access = MarketAccessModel(self.config)
        self.human_capital = HumanCapitalModel(self.config)
        self.regulatory = RegulatoryEnvironmentModel(self.config)
        self.business_environment = BusinessEnvironmentModel(self.config)
        self.innovation = InnovationModel(self.config)
        self.sustainability = SustainabilityModel(self.config)
        self.resilience = ResilienceModel(self.config)
        self.internationalization = InternationalizationModel(self.config)
        self.inclusion = InclusionModel(self.config)
        print("  Models initialized.")

        # Initialize/Re-initialize the SME population using the current config
        print("  Initializing SME population...")
        # Pass config in case segmentation model uses scenario-specific params
        self.smes_df = self.business_segments.initialize_population(self.data_handler, self.config) 
        if self.smes_df is None:
             print("  ERROR: Failed to initialize SME population DataFrame.")
             # Handle error appropriately - maybe raise exception or return status
        else:
             print(f"  SME population initialized with {len(self.smes_df)} SMEs.")

        # Reset state variables
        self.environment_state = {}
        self.labor_market_state = {}
        self.current_year = self.start_year
        # Clear results for the current scenario if it exists (it shouldn't if reset is called before run)
        if self.current_scenario_name in self.results:
             self.results[self.current_scenario_name] = {}
        print("State reset complete.")


    def step(self):
        """Runs a single time step (one year) of the simulation using self.config."""
        if self.smes_df is None:
            print("ERROR: SME DataFrame not initialized. Cannot run step.")
            return
        if self.config is None:
            print("ERROR: Scenario configuration not loaded. Cannot run step.")
            return

        # --- Update environment state based on scenario config --- 
        # Example: Update infrastructure index based on scenario rate
        infra_rate = self.config.get('business_environment', {}).get('infrastructure_improvement_rate', 0)
        current_infra = self.environment_state.get('infrastructure_index', self.config.get('business_environment', {}).get('initial_infrastructure_index', 0.5))
        self.environment_state['infrastructure_index'] = min(1.0, current_infra + infra_rate)
        # Add other environment updates here (e.g., policy changes, market conditions)
        print(f"Simulating business environment dynamics for year {self.current_year} (Scenario: {self.current_scenario_name})...")
        self.environment_state = self.business_environment.simulate_environment_dynamics(self.current_year, self.config)

        # --- Simulate SME behaviors using models and current self.config --- 
        # Order matters: Some dynamics might depend on the state updated by others
        print(f"Simulating regulatory dynamics for year {self.current_year} (Scenario: {self.current_scenario_name})...")
        self.smes_df = self.regulatory.simulate_regulatory_dynamics(self.smes_df, self.current_year, self.environment_state, self.config)
        
        print(f"Simulating human capital dynamics for year {self.current_year}...")
        self.smes_df = self.human_capital.simulate_human_capital_dynamics(self.smes_df, self.current_year, self.labor_market_state)
        
        print(f"Simulating technology adoption for year {self.current_year}...")
        self.smes_df = self.technology.simulate_adoption_dynamics(self.smes_df, self.current_year)
        
        print(f"Simulating finance access for year {self.current_year}...")
        self.smes_df = self.financing.simulate_financing_dynamics(self.smes_df, self.current_year)
        
        print(f"Simulating innovation dynamics for year {self.current_year}...")
        self.smes_df = self.innovation.simulate_innovation_dynamics(self.smes_df, self.current_year, self.environment_state)
        
        print(f"Simulating sustainability dynamics for year {self.current_year} (Scenario: {self.current_scenario_name})...")        
        self.smes_df = self.sustainability.simulate_sustainability_dynamics(self.smes_df, self.current_year, self.environment_state, self.config)
        
        print(f"Simulating resilience dynamics for year {self.current_year} (Scenario: {self.current_scenario_name})...")
        self.smes_df = self.resilience.simulate_resilience_dynamics(self.smes_df, self.current_year, self.environment_state, self.config)
        
        print(f"Simulating market dynamics for year {self.current_year}...")
        self.smes_df = self.market_access.simulate_market_dynamics(self.smes_df, self.current_year)

        print(f"Simulating internationalization dynamics for year {self.current_year}...")
        self.smes_df = self.internationalization.simulate_internationalization_dynamics(self.smes_df, self.current_year, self.environment_state, {})

        print(f"Simulating inclusion dynamics for year {self.current_year} (Scenario: {self.current_scenario_name})...")
        self.smes_df = self.inclusion.simulate_inclusion_dynamics(self.smes_df, self.current_year, self.environment_state, self.config)

        # --- Update SME status/segmentation (entry/exit/growth) --- 
        print(f"Updating SME segmentation for year {self.current_year}...")
        self.smes_df = self.business_segments.update_segmentation(self.smes_df, self.current_year) # Pass config if needed

        # --- Cleanup / End-of-year updates --- 
        active_sme_count = len(self.smes_df[self.smes_df['status'] == 'active'])
        print(f"  Finished simulation step for year {self.current_year}. Active SMEs: {active_sme_count}")


    def _collect_results(self, year):
        """Collect results for the current year and store in self.results[current_scenario_name]."""
        if self.current_scenario_name is None:
             print("ERROR: Cannot collect results, current scenario name not set.")
             return
             
        print(f"  Collecting results for year {year}...")
        if self.smes_df is None:
            results_this_year = {'error': 'SME DataFrame is None'}
        else:    
            results_this_year = {}
            # Save a copy of the full SME DataFrame for this year
            results_this_year['smes_data'] = self.smes_df.copy()
            
            # Calculate and store summary metrics
            results_this_year['total_smes'] = len(self.smes_df)
            active_smes = self.smes_df[self.smes_df['status'] == 'active']
            results_this_year['active_smes'] = len(active_smes)
            
            # Add environment state (make a copy)
            results_this_year['environment_state'] = copy.deepcopy(self.environment_state)
        
        # Ensure the scenario key exists in results
        if self.current_scenario_name not in self.results:
            self.results[self.current_scenario_name] = {}
            
        # Store results for the current year under the current scenario
        self.results[self.current_scenario_name][year] = results_this_year
        print(f"  Results collected for year {year}.")

    def save_results(self, results_data, filename):
        """Save the provided simulation results dictionary to a file."""
        # Note: results_data is expected to be the dictionary for a SINGLE scenario {year: data}
        print(f"Saving results to {filename}...")
        if not results_data or not isinstance(results_data, dict):
            print(f"Warning: Invalid or empty results data provided for {filename}. Skipping save.")
            return
        try:
            # Using pickle for potentially complex data structures
            pd.to_pickle(results_data, filename)
            print(f"Results saved successfully to {filename}.")
        except Exception as e:
            print(f"Error saving results to {filename}: {e}")

# --- Main execution block --- 
if __name__ == "__main__":
    print("Starting Bangladesh SME Simulation Script")
    
    config_file = 'config.yaml'
    if not os.path.exists(config_file):
         print(f"ERROR: {config_file} not found in the current directory ({os.getcwd()}).")
         print("Please ensure the configuration file exists.")
    else:
        try:
            simulation = BangladeshSMESimulation(config_path=config_file)
            
            # Define which scenarios to run from the config file
            scenarios_to_run = ['baseline', 'pro_investment', 'digital_leap'] 
            # Future: Get this list from command line args or config itself
            
            # Run simulation for the specified scenarios
            all_simulation_results = simulation.run_simulation(scenarios_to_run=scenarios_to_run)
            
            # Save results for each completed scenario
            print("\n----- Saving Results -----")
            if all_simulation_results:
                output_dir = 'output' # Define output directory
                os.makedirs(output_dir, exist_ok=True) # Ensure output directory exists
                for scenario_name, scenario_data in all_simulation_results.items():
                    if scenario_data: # Check if scenario actually produced data
                        # Construct full path including the output directory
                        output_filename = os.path.join(output_dir, f"{scenario_name}_results.pkl") 
                        simulation.save_results(scenario_data, output_filename)
                    else:
                        print(f"No results data found for scenario '{scenario_name}', skipping save.")
            else:
                 print("No simulation results were generated.")

            # Basic print of final year results for baseline (if run)
            if 'baseline' in all_simulation_results and simulation.end_year in all_simulation_results['baseline']:
                print("\nBaseline Scenario - Final Year Results Summary:")
                final_results = all_simulation_results['baseline'][simulation.end_year]
                if 'error' in final_results:
                     print(f"  Error in final year data: {final_results['error']}")
                else:
                     print(f"  Total SMEs: {final_results.get('total_smes', 'N/A')}")
                     print(f"  Active SMEs: {final_results.get('active_smes', 'N/A')}")
                     # Add other key metrics if needed
            else:
                print("\nCould not retrieve final year baseline results summary.")

        except Exception as e:
             print(f"\n--- UNEXPECTED ERROR DURING SIMULATION RUN --- ")
             print(f"Error Type: {type(e).__name__}")
             print(f"Error Details: {e}")
             import traceback
             print("Traceback:")
             traceback.print_exc()

        print("\nScript Finished.")
