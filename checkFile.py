"""
FHE demo with TenSEAL (CKKS): encrypt numeric columns from an Excel, multiply, and decrypt.

Usage:
python fhe_demo_tenseal.py --excel /path/to/your.xlsx --scale 2**40 --poly-degree 8192

Requirements:
pip install tenseal pandas openpyxl

Notes:
- CKKS is approximate FHE; expect tiny numerical differences after decryption.
- This script multiplies the first two numeric columns element-wise.
If only one numeric column exists, it squares that column.
"""

import argparse
import pandas as pd
import tenseal as ts
import os

def load_numeric_columns(csv_path: str) -> pd.DataFrame:
    """Load Excel and return DataFrame containing only numeric columns."""
    df = pd.read_csv(csv_path)
    num_df = df.select_dtypes(include=["number"]).copy()
    print(num_df)
    if num_df.empty:
        raise ValueError("No numeric columns found in the CSV file.")
    return num_df

def build_ckks_context(poly_degree: int = 8192,coeff_mod_bit_sizes=None,global_scale: float = 2**40) -> ts.Context:
        """Create and return a TenSEAL CKKS context with relin & galois keys."""
        # Typical chain for small-depth operations (adjust if you need deeper circuits)
        coeff_mod_bit_sizes = [60, 40, 40, 60]
        ctx = ts.context(ts.SCHEME_TYPE.CKKS,
                         poly_modulus_degree=poly_degree,
                         coeff_mod_bit_sizes=coeff_mod_bit_sizes)
        if coeff_mod_bit_sizes is None:
            ctx.generate_galois_keys()
            ctx.generate_relin_keys()
            ctx.global_scale = global_scale
        return ctx

def encrypt_columns(ctx: ts.Context, df: pd.DataFrame) -> dict:
        """Encrypt each numeric column as a CKKS vector and return dict of ciphertexts."""
        enc_cols = {}
        for col in df.columns:
            #ensure floats for CKKS
            vec = df[col].astype(float).tolist()
            print(vec)
            enc_cols[col] = ts.ckks_vector(ctx, vec)
            print(enc_cols[col])
        return enc_cols

def multiply_and_decrypt(enc_cols: dict, df: pd.DataFrame) -> pd.Series:
    """Perform ciphertext-ciphertext multiplication on first two columns (or square first),
    then decrypt and return a Pandas Series with results."""
    cols = list(df.columns)
    if len(cols) >= 2:
        c1 = enc_cols[cols[0]]
        c2 = enc_cols[cols[1]]
        prod_enc = c1 * c2 # ciphertext * ciphertext
        prod_dec = prod_enc.decrypt() # decrypt to python list (approximate)
        return pd.Series(prod_dec, name=f"{cols[0]}_times_{cols[1]}")
    else:
        c1 = enc_cols[cols[0]]
        prod_enc = c1 * c1
        prod_dec = prod_enc.decrypt()
        return pd.Series(prod_dec, name=f"{cols[0]}_squared")

def main():
    parser = argparse.ArgumentParser(description="FHE multiply numeric columns in Excel using TenSEAL CKKS")
    parser.add_argument("--excel", required=True, help="Path to the Excel file (.xlsx)")
    parser.add_argument("--poly-degree", type=int, default=8192, help="CKKS poly_modulus_degree (e.g., 8192)")
    parser.add_argument("--scale", type=float, default=2**40, help="CKKS global scale (e.g., 2**40)")
    parser.add_argument("--coeff-mod", nargs="+", type=int, default=[60, 40, 40, 60], help="CKKS coeff_mod_bit_sizes")
    args = parser.parse_args()

    excel_path = "C:/Users/vidyamudaliar/PycharmProjects/FHEProject/demand_stat.csv"
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Excel file not found: {excel_path}")

    # 1) Load numeric columns
    num_df = load_numeric_columns(excel_path)
    print(f"Numeric columns found: {list(num_df.columns)}")
    print("First few rows (plaintext):")
    print(num_df.head().to_string(index=False))

    # 2) Build CKKS context
    ctx = build_ckks_context(poly_degree=args.poly_degree,
    coeff_mod_bit_sizes=args.coeff_mod,
    global_scale=args.scale)

    # 3) Encrypt numeric columns
    enc_cols = encrypt_columns(ctx, num_df)
    print("Encryption complete (CKKS vectors created).")

    # 4) Multiply under encryption and decrypt the result
    decrypted_product = multiply_and_decrypt(enc_cols, num_df)
    decrypted_product = decrypted_product.astype(float).reset_index(drop=True)

    # 5) Plaintext product for comparison
    if num_df.shape[1] >= 2:
        plaintext_product = (num_df.iloc[:, 0] * num_df.iloc[:, 1]).astype(float).reset_index(drop=True)
    else:
        plaintext_product = (num_df.iloc[:, 0] * num_df.iloc[:, 0]).astype(float).reset_index(drop=True)

    # 6) Compile results and show
    out_df = pd.DataFrame({
    "plaintext_product": plaintext_product,
    "decrypted_product": decrypted_product
    })
    out_df["abs_error"] = (out_df["plaintext_product"] - out_df["decrypted_product"]).abs()

    print("\nComparison (first 10 rows):")
    print(out_df.head(10).to_string(index=False))

    # 7) Save results
    out_path = os.path.splitext(excel_path)[0] + "_fhe_result.csv"
    out_df.to_csv(out_path, index=False)
    print(f"\nSaved results to: {out_path}")

    if __name__ == "__main__":
        main()


