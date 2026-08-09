import pandas as pd
import matplotlib.pyplot as plt
import pygmo as pg
import numpy as np

# --- Configuration ---
file_spea2 = 'generation_objectives_MaF2_3Obj_SPEA2.csv'
file_ivf = 'generation_objectives_MaF2_3OBJ_IVFSPEA2.csv' # Corrected filename case if necessary
output_plot_file = 'convergence_comparison_MaF2_3Obj.png'

# Reference point for Hypervolume calculation
# Adjust this point based on the actual range of your objectives
# It should be slightly worse than the worst possible objective values.
ref_point = [1.1, 1.1, 1.1]

# --- Load Data ---
try:
    df_spea2 = pd.read_csv(file_spea2)
    df_ivf = pd.read_csv(file_ivf)
    print(f"Successfully loaded {file_spea2}")
    print(f"Successfully loaded {file_ivf}")
except FileNotFoundError as e:
    print(f"Error loading file: {e}")
    print("Please ensure the file paths are correct and the files are in the PlatEMO directory.")
    exit()
except Exception as e:
    print(f"An error occurred while reading the CSV files: {e}")
    exit()


# --- Hypervolume Calculation Function ---
def calculate_hypervolume(group, ref_point):
    """Calculates the hypervolume for a group of points."""
    # Extract objective values
    objectives = group[['Objective1', 'Objective2', 'Objective3']].values
    if objectives.shape[0] == 0:
        return 0.0
    try:
        # Calculate hypervolume using pygmo
        hv = pg.hypervolume(objectives)
        return hv.compute(ref_point)
    except Exception as e:
        print(f"Error calculating hypervolume for generation {group.name}: {e}")
        # Handle cases where hypervolume calculation might fail (e.g., all points dominated by ref_point)
        # Check if points dominate the reference point
        if np.any(np.all(objectives <= ref_point, axis=1)):
             # If at least one point dominates or is equal to the ref point in all objectives,
             # try calculating dominated hypervolume.
             # This assumes minimization. For maximization, adjust accordingly.
             try:
                 # Attempt calculation again, pygmo might handle some cases internally
                 # Or consider alternative ways if pygmo fails consistently for valid fronts
                 print(f"Attempting hypervolume calculation again for generation {group.name}")
                 hv = pg.hypervolume(objectives)
                 return hv.compute(ref_point)
             except Exception as e_retry:
                 print(f"Retry failed for generation {group.name}: {e_retry}. Returning 0.")
                 return 0.0 # Or np.nan
        else:
             # All points are worse than the reference point
             print(f"All points dominated by reference point in generation {group.name}. Returning 0.")
             return 0.0


# --- Calculate HV per Generation ---
print("Calculating Hypervolume for SPEA2...")
hv_spea2 = df_spea2.groupby('Generation').apply(calculate_hypervolume, ref_point=ref_point)

print("Calculating Hypervolume for IVF-SPEA2...")
hv_ivf = df_ivf.groupby('Generation').apply(calculate_hypervolume, ref_point=ref_point)

# --- Plotting ---
print("Generating plot...")
plt.figure(figsize=(12, 7))

plt.plot(hv_spea2.index, hv_spea2.values, label='SPEA2', marker='o', linestyle='-', markersize=4)
plt.plot(hv_ivf.index, hv_ivf.values, label='IVF-SPEA2', marker='x', linestyle='--', markersize=4)

# Add details to the plot
plt.title('Hypervolume Convergence Comparison (MaF2 - 3 Objectives)')
plt.xlabel('Generation')
plt.ylabel('Hypervolume Indicator (HV)')
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.tight_layout()

# Save the plot
try:
    plt.savefig(output_plot_file)
    print(f"Plot saved successfully as {output_plot_file}")
except Exception as e:
    print(f"Error saving plot: {e}")

# Show the plot (optional)
# plt.show()

print("Script finished.")