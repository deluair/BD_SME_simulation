import pandas as pd
import yaml
import os

class SMEDataHandler:
    """Handles loading, preprocessing, and providing access to SME-related data."""
    def __init__(self, config_path='config.yaml'):
        """Initialize the data handler by loading configuration."""
        print("Initializing SMEDataHandler...")
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            self.data_sources = self.config.get('data_sources', {})
            self.project_root = os.path.dirname(os.path.abspath(config_path))
        except FileNotFoundError:
            print(f"Error: Configuration file not found at {config_path}")
            self.config = {}
            self.data_sources = {}
            self.project_root = os.getcwd()
        except yaml.YAMLError as e:
            print(f"Error parsing configuration file: {e}")
            self.config = {}
            self.data_sources = {}
            self.project_root = os.getcwd()
            
        self.loaded_data = {} # Dictionary to store loaded dataframes

    def _get_full_path(self, data_path):
        """Constructs an absolute path relative to the project root."""
        if os.path.isabs(data_path):
            return data_path
        return os.path.join(self.project_root, data_path)

    def load_historical_data(self):
        """Load historical SME data from sources defined in the config, if configured to do so."""
        print("Checking data loading configuration...")
        use_synthetic = self.data_sources.get('use_synthetic_data', False)

        if use_synthetic:
            print("Configured to use synthetic data. Skipping file loading.")
            # Data generation will be handled by the relevant model (e.g., SMESegmentationModel)
            return

        print("Configured to load data from files. Loading historical data...")
        for key, source_info in self.data_sources.items():
            if key == 'use_synthetic_data': # Skip this config key
                continue
            
            if isinstance(source_info, str): # Simple path definition
                path = self._get_full_path(source_info)
                try:
                    if path.endswith('.csv'):
                        self.loaded_data[key] = pd.read_csv(path)
                        print(f"  Loaded {key} from {path}")
                    elif path.endswith(('.xlsx', '.xls')):
                         # Might need specific sheet name
                        self.loaded_data[key] = pd.read_excel(path) 
                        print(f"  Loaded {key} from {path}")
                    # Add more file types as needed (json, etc.)
                    else:
                        print(f"  Warning: Unsupported file type for {key}: {path}")
                except FileNotFoundError:
                    print(f"  Warning: Data file not found for {key} at {path}")
                except Exception as e:
                    print(f"  Error loading {key} from {path}: {e}")
            elif isinstance(source_info, dict): # More complex definition (e.g., API)
                 print(f"  Data source '{key}' requires custom loading logic (e.g., API). Implement if needed.")
                 # Add logic here to handle API calls or database connections if required
        
        print("Finished loading historical data.")
        # Perform initial preprocessing if necessary
        self.preprocess_data()

    def preprocess_data(self):
        """Perform basic preprocessing on loaded dataframes."""
        print("Preprocessing data...")
        # Example: Standardize column names, handle missing values, convert types
        # for key, df in self.loaded_data.items():
        #     # df.columns = [col.lower().replace(' ', '_') for col in df.columns]
        #     # df.fillna(value=pd.NA, inplace=True) # Or specific imputation
        #     pass
        print("Finished preprocessing data.")

    def get_data(self, key):
        """Retrieve a loaded dataframe by its key."""
        return self.loaded_data.get(key, None)

    def integrate_realtime_data(self, api_connections):
        """Set up connections to real-time data sources (Placeholder)."""
        print("Setting up real-time data integration (Placeholder)...")
        # This would involve establishing connections to APIs or streams
        # and potentially updating internal data stores periodically.
        pass

    def get_config_parameter(self, param_path, default=None):
        """Helper to get nested parameters from the config."""
        keys = param_path.split('.')
        val = self.config
        try:
            for key in keys:
                val = val[key]
            return val
        except (KeyError, TypeError):
            return default

# Example usage (if run directly)
if __name__ == '__main__':
    # Assumes config.yaml is in the parent directory
    config_file_path = os.path.join(os.path.dirname(__file__), '..', 'config.yaml') 
    data_handler = SMEDataHandler(config_path=config_file_path)
    data_handler.load_historical_data()
    
    bbs_data = data_handler.get_data('bbs_census')
    if bbs_data is not None:
        print("\nBBS Census Data Info:")
        bbs_data.info()
    else:
        print("\nBBS Census data not loaded.")
        
    start_year = data_handler.get_config_parameter('simulation_parameters.start_year')
    print(f"\nSimulation Start Year from config: {start_year}")
