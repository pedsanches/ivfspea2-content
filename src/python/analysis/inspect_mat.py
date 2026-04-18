import scipy.io
import os


def inspect_mat(filepath):
    try:
        mat = scipy.io.loadmat(filepath)
        print(f"Keys in {os.path.basename(filepath)}:")
        for key in mat:
            if not key.startswith("__"):
                print(
                    f"  - {key}: {type(mat[key])}, shape={mat[key].shape if hasattr(mat[key], 'shape') else 'N/A'}"
                )
                # If metric is a scalar, print it
                if hasattr(mat[key], "shape") and mat[key].shape == (1, 1):
                    print(f"    Value: {mat[key][0][0]}")
    except Exception as e:
        print(f"Error reading {filepath}: {e}")


path1 = "/home/pedro/desenvolvimento/ivfspea2/data/raw/Experimentos_Platemo/IVFSPEA2_R0.100_C16_DTLZ1/IVFSPEA2_DTLZ1_M3_D7_1.mat"
path2 = "/home/pedro/desenvolvimento/ivfspea2/data/raw/Experimentos_Platemo/IVFSPEA2_2OBJ_R0.10_C0.10/IVFSPEA2_DTLZ1_M2_D6_1.mat"

print("--- File 1 (Likely 3-Obj) ---")
inspect_mat(path1)
print("\n--- File 2 (Likely 2-Obj) ---")
inspect_mat(path2)
