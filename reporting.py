import pandas as pd
import matplotlib.pyplot as plt
import pickle
import os
import glob

# --- Configuration ---
OUTPUT_DIR = 'output'
PLOTS_DIR = os.path.join(OUTPUT_DIR, 'plots')
REPORT_FILE = os.path.join(OUTPUT_DIR, 'simulation_report.html')

# --- Helper Functions ---
def load_results(filepath):
    """Loads simulation results from a pickle file."""
    if not os.path.exists(filepath):
        print(f"Error: Results file not found at {filepath}")
        return None
    try:
        with open(filepath, 'rb') as f:
            results = pickle.load(f)
        print(f"Results loaded successfully from {filepath}")
        return results
    except Exception as e:
        print(f"Error loading results file: {e}")
        return None

def create_directories():
    """Creates the output and plots directories if they don't exist."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(PLOTS_DIR, exist_ok=True)
    print(f"Ensured output directories exist: {OUTPUT_DIR}, {PLOTS_DIR}")

def generate_plots(all_scenario_results, plots_dir):
    """Generates and saves comparative plots based on results from multiple scenarios."""
    if not all_scenario_results:
        print("No scenario results data to plot.")
        return {}

    plot_paths = {}
    # Define metrics to plot and their y-axis labels
    metrics_to_plot = {
        # metric_key: (Y-Axis Label, Required Column(s), Output Filename)
        'active_smes_count': ('Number of Active SMEs', ['status'], 'comparison_active_smes.png'),
        'avg_revenue': ('Average Revenue', ['status', 'revenue'], 'comparison_average_revenue.png'),
        'tech_adoption_rate': ('Tech Adoption Rate (%)', ['status', 'has_adopted_tech'], 'comparison_tech_adoption_rate.png'),
        'exporter_count': ('Number of Exporters', ['status', 'is_exporter'], 'comparison_exporter_count.png'),
        'avg_skill': ('Average Skill Level (Index)', ['status', 'skill_level'], 'comparison_average_skill.png'),
        'avg_resilience': ('Average Resilience Score (Index)', ['status', 'resilience_score'], 'comparison_average_resilience.png')
    }

    plt.style.use('ggplot') # Try ggplot style

    # Generate a plot for each metric comparing scenarios
    for metric, (ylabel, required_cols, filename) in metrics_to_plot.items():
        plt.figure(figsize=(10, 6))
        plot_title = f"Comparison: {ylabel.split('(')[0].strip()} Over Time"
        plt.title(plot_title)
        plt.xlabel('Year')
        plt.ylabel(ylabel)

        # Track if any data was plotted for this metric
        plotted_something = False

        # Iterate through each scenario's results
        for scenario_name, results_dict in all_scenario_results.items():
            if not results_dict or not isinstance(results_dict, dict):
                print(f"[Plotting - {metric}] Skipping scenario '{scenario_name}': Invalid or empty results dictionary.")
                continue

            years = sorted(results_dict.keys())
            if not years:
                print(f"[Plotting - {metric}] Skipping scenario '{scenario_name}': No years found in results.")
                continue
            
            scenario_data = []
            min_year, max_year = min(years), max(years)
            all_years_range = range(min_year, max_year + 1)
            
            # Ensure data points for all years in the range, handling missing years
            for year in all_years_range:
                year_data = results_dict.get(year, {}) # Get data for the year or empty dict
                df = year_data.get('smes_data', pd.DataFrame()) # Get DataFrame or empty

                # Check for required columns
                if not df.empty:
                    missing_cols = [col for col in required_cols if col not in df.columns]
                    if missing_cols:
                        print(f"[Plotting - {metric}] Warning: Missing required column(s) {missing_cols} for year {year} in scenario '{scenario_name}'. Using default value.")
                        df = pd.DataFrame() # Treat as empty if required columns are missing

                if df.empty:
                    # If no DataFrame or required columns missing, append default value (0)
                    scenario_data.append({'year': year, metric: 0})
                    # Optionally print a warning if it's an expected year with data
                    # if year in results_dict:
                    #     print(f"[Plotting - {metric}] Warning: Empty DataFrame or missing required columns for year {year} in scenario '{scenario_name}'. Using default value.")
                    continue # Move to next year

                active_smes = df[df['status'] == 'active']
                if active_smes.empty:
                    # If no active SMEs, append default value (0)
                    scenario_data.append({'year': year, metric: 0})
                    # print(f"[Plotting - {metric}] Info: No active SMEs for year {year} in scenario '{scenario_name}'. Using default value.")
                    continue # Move to next year

                # Calculate metric value for this year
                value = 0 # Default
                try:
                    if metric == 'active_smes_count':
                        value = len(active_smes)
                    elif metric == 'avg_revenue':
                        value = active_smes['revenue'].mean()
                    elif metric == 'avg_skill':
                        value = active_smes['skill_level'].mean()
                    elif metric == 'tech_adoption_rate':
                        value = active_smes['has_adopted_tech'].mean() * 100
                    elif metric == 'exporter_count':
                        value = active_smes['is_exporter'].sum()
                    elif metric == 'avg_resilience':
                        value = active_smes['resilience_score'].mean()
                except KeyError as e:
                    print(f"[Plotting - {metric}] Error calculating metric for year {year}, scenario '{scenario_name}': Missing column {e}. Using 0.")
                    value = 0 # Should be caught by column check earlier, but belts and suspenders
                    
                # Handle potential NaN from calculations (e.g., mean of empty series)
                value = value if pd.notna(value) else 0 
                    
                scenario_data.append({'year': year, metric: value})
            
            if not scenario_data:
                print(f"[Plotting - {metric}] No data aggregated for scenario '{scenario_name}'. Skipping plot line.")
                continue
                
            # Create DataFrame from the list of dicts for this scenario
            agg_df = pd.DataFrame(scenario_data)
            agg_df.set_index('year', inplace=True)
            
            if not agg_df.empty and metric in agg_df.columns:
                 # Ensure markers are visible
                 plt.plot(agg_df.index, agg_df[metric], marker='o', linestyle='-', label=scenario_name, markersize=5)
                 plotted_something = True
            else:
                 # This case should be less likely now with the improved aggregation logic
                 print(f"[Plotting - {metric}] Failed to plot line for scenario '{scenario_name}' (Dataframe empty or metric column missing after aggregation).")

        # Finalize plot after iterating through all scenarios
        if plotted_something:
            if metric == 'tech_adoption_rate':
                plt.ylim(0, 100) # Keep ylim for adoption rate
            plt.legend()
            plt.tight_layout()
            plot_path = os.path.join(plots_dir, filename)
            plt.savefig(plot_path)
            plt.close()
            # Store relative path using the base metric name as key
            plot_paths[ylabel.split('(')[0].strip()] = os.path.relpath(plot_path, OUTPUT_DIR)
            print(f"Saved comparative plot: {plot_path}")
        else:
             print(f"Skipping save for empty plot: {plot_title}")
             plt.close() # Close the empty figure

    return plot_paths # Return dict of plot titles to relative paths

def generate_html_report(report_file, plot_paths, all_scenario_results):
    """Generates an HTML report embedding the saved plots and a summary table."""
    
    # --- Calculate Summary Statistics ---    
    summary_data = {}
    final_year = 0
    if all_scenario_results:
        # Find the latest year across all scenarios
        all_years = set()
        for results_dict in all_scenario_results.values():
            if results_dict: all_years.update(results_dict.keys())
        final_year = max(all_years) if all_years else 0

        if final_year > 0:
            for scenario_name, results_dict in all_scenario_results.items():
                if not results_dict or final_year not in results_dict:
                    summary_data[scenario_name] = {metric: 'N/A' for metric, _ in plot_paths.items()} # Handle missing final year data
                    continue
                
                year_data = results_dict[final_year]
                df = year_data.get('smes_data', pd.DataFrame())
                scenario_summary = {}
                
                if df.empty:
                     scenario_summary = {metric: 'N/A (No Data)' for metric, _ in plot_paths.items()} 
                else:
                    active_smes = df[df['status'] == 'active']
                    if active_smes.empty:
                        scenario_summary = {metric: '0 (No Active)' for metric, _ in plot_paths.items()}
                    else:
                        # Use plot_paths keys (which are titles like 'Number of Active SMEs') to map back to metric calculations
                        # This is a bit fragile, ideally we'd reuse the metric keys directly
                        metric_map = {
                            'Number of Active SMEs': lambda d: len(d),
                            'Average Revenue': lambda d: d['revenue'].mean() if 'revenue' in d else 'N/A',
                            'Tech Adoption Rate': lambda d: d['has_adopted_tech'].mean() * 100 if 'has_adopted_tech' in d else 'N/A',
                            'Number of Exporters': lambda d: d['is_exporter'].sum() if 'is_exporter' in d else 'N/A',
                            'Average Skill Level': lambda d: d['skill_level'].mean() if 'skill_level' in d else 'N/A',
                            'Average Resilience Score': lambda d: d['resilience_score'].mean() if 'resilience_score' in d else 'N/A'
                        }
                        
                        for title in plot_paths.keys():
                             if title in metric_map:
                                 calc_func = metric_map[title]
                                 try:
                                     value = calc_func(active_smes)
                                     # Format numbers nicely
                                     if isinstance(value, (int, float)):
                                         if 'Rate' in title or 'Score' in title or 'Level' in title:
                                             scenario_summary[title] = f"{value:.2f}"
                                         elif 'Revenue' in title:
                                              scenario_summary[title] = f"{value:,.0f}"
                                         else:
                                              scenario_summary[title] = f"{value:,}"
                                     else: 
                                         scenario_summary[title] = value # Keep 'N/A' as is
                                 except Exception as e:
                                     print(f"Error calculating summary for {title}, scenario {scenario_name}: {e}")
                                     scenario_summary[title] = 'Error'
                             else:
                                 scenario_summary[title] = 'N/A (Calc Missing)' 
                                 
                summary_data[scenario_name] = scenario_summary

    # --- Generate HTML Content ---    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SME Simulation Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }}
        h1 {{ text-align: center; color: #005a9c; }}
        h2 {{ color: #005a9c; border-bottom: 2px solid #005a9c; padding-bottom: 5px; margin-top: 40px;}}
        .intro, .summary-container {{ background-color: #fff; padding: 20px; margin-bottom: 30px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .plot-container {{ text-align: center; margin-bottom: 30px; padding: 15px; border: 1px solid #ddd; border-radius: 8px; background-color: #fff; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        img {{ max-width: 95%; height: auto; border-radius: 4px; margin-top: 10px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background-color: #e2e2e2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
    </style>
</head>
<body>
    <h1>Bangladesh SME Simulation Results (Scenario Comparison)</h1>
    
    <div class="intro">
        <p>This report summarizes the results of an agent-based simulation modeling the dynamics of Small and Medium Enterprises (SMEs) in Bangladesh under different policy scenarios. 
        The simulation tracks various metrics over time to compare the potential impacts of these scenarios.</p>
    </div>

    <h2>Final Year ({final_year if final_year > 0 else 'N/A'}) Summary Statistics</h2>
    <div class="summary-container">
"""
    if not summary_data:
        html_content += "<p>Summary statistics could not be generated.</p>"
    else:
        html_content += "<table>\n<thead>\n<tr><th>Metric</th>"
        scenarios = list(summary_data.keys())
        for scenario in scenarios:
            html_content += f"<th>{scenario}</th>"
        html_content += "</tr>\n</thead>\n<tbody>\n"
        
        # Assuming all scenarios have the same metrics keys from plot_paths
        if scenarios:
            metrics = list(summary_data[scenarios[0]].keys())
            for metric in metrics:
                html_content += f"<tr><td>{metric}</td>"
                for scenario in scenarios:
                    value = summary_data[scenario].get(metric, 'N/A')
                    html_content += f"<td>{value}</td>"
                html_content += "</tr>\n"
        
        html_content += "</tbody>\n</table>\n"
        
    html_content += "</div>\n"

    html_content += "<h2>Comparative Plots Over Time</h2>\n"

    if not plot_paths:
        html_content += "<p>No plots were generated.</p>"
    else:
        for title, path in plot_paths.items():
            # Ensure forward slashes for HTML paths, even on Windows
            html_path = path.replace('\\', '/') 
            html_content += f"""    <div class="plot-container">
        <h2>{title}</h2>
        <img src="{html_path}" alt="{title} Plot">
    </div>
"""

    html_content += """</body>
</html>
"""

    try:
        with open(report_file, 'w') as f:
            f.write(html_content)
        print(f"HTML report generated successfully at {report_file}")
    except Exception as e:
        print(f"Error writing HTML report: {e}")

# --- Main Execution ---
def main():
    print("Starting simulation reporting process...")
    create_directories()

    # Find all scenario result files
    result_files = glob.glob(os.path.join(OUTPUT_DIR, '*_results.pkl'))
    if not result_files:
        print(f"Error: No '*_results.pkl' files found in {OUTPUT_DIR}")
        return

    # Load results for all scenarios
    all_results = {}
    for filepath in result_files:
        scenario_name = os.path.basename(filepath).replace('_results.pkl', '')
        results_data = load_results(filepath)
        if results_data:
            all_results[scenario_name] = results_data
        else:
            print(f"Skipping scenario {scenario_name} due to loading error.")

    if not all_results:
        print("No results could be loaded. Exiting reporting.")
        return

    # Generate comparative plots
    plot_paths = generate_plots(all_results, PLOTS_DIR)

    # Generate HTML report including plots and summary
    generate_html_report(REPORT_FILE, plot_paths, all_results)

    print("Reporting process finished.")

if __name__ == "__main__":
    main()
