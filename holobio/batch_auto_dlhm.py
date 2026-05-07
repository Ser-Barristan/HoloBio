import os
import numpy as np
import pandas as pd
import imageio.v2 as imageio

from holobio.parallel_rc import dlhm_rec
from holobio.utilities import imageRead
from holobio.unwrap_methods import apply_unwrap


# ----------------------------
# Load grayscale image
# ----------------------------
def load_gray(path):
    return np.array(imageRead(path), dtype=np.float64)


# ----------------------------
# Normalize and save TIFF
# ----------------------------
def save_phase_tiff(phase_map, save_path):
    phase_map = np.nan_to_num(phase_map)

    norm = (phase_map - np.min(phase_map)) / (
        np.max(phase_map) - np.min(phase_map) + 1e-12
    )

    out = (norm * 65535).astype(np.uint16)

    imageio.imwrite(save_path, out)


# ----------------------------
# Main reconstruction
# ----------------------------
def reconstruct_single(holo, wavelength_um, L_mm, Z_mm, pixel_pitch_um):
    wavelength = wavelength_um * 1e-6
    L = L_mm * 1e-3
    Z = Z_mm * 1e-3
    dx = pixel_pitch_um * 1e-6

    W_c = dx * holo.shape[1]

    amp, phase = dlhm_rec(
        hologram=holo,
        L=L,
        z=Z,
        W_c=W_c,
        dx_out=dx,
        wavelength=wavelength
    )

    complex_field = amp * np.exp(1j * phase)

    return complex_field


# ----------------------------
# Batch Processor
# ----------------------------
def run_batch(parent_dir, csv_path, pixel_pitch_um=1.12):

    df = pd.read_csv(csv_path)

    for idx, row in df.iterrows():

        try:
            # ----------------------------
            # Path
            # ----------------------------
            rel_path = row["clear_path"]
            img_path = os.path.join(parent_dir, rel_path)

            folder = os.path.dirname(img_path)

            # ----------------------------
            # Reference
            # ----------------------------
            ref_candidates = [
                f for f in os.listdir(folder)
                if os.path.splitext(f)[0].lower() == "ref"
            ]

            if not ref_candidates:
                print(f"[NO REF] {folder}")
                continue

            ref_path = os.path.join(folder, ref_candidates[0])

            # ----------------------------
            # Parameters
            # ----------------------------
            wavelength_um = float(row["wavelength_um"])
            L_mm = float(row["L_mm"])
            Z_mm = float(row["Z_mm"])

            # ----------------------------
            # Load
            # ----------------------------
            holo = load_gray(img_path)
            ref = load_gray(ref_path)

            # ----------------------------
            # Reconstruct
            # ----------------------------
            obj_field = reconstruct_single(
                holo,
                wavelength_um,
                L_mm,
                Z_mm,
                pixel_pitch_um
            )

            ref_field = reconstruct_single(
                ref,
                wavelength_um,
                L_mm,
                Z_mm,
                pixel_pitch_um
            )

            # ----------------------------
            # Reference subtraction
            # ----------------------------
            corrected = obj_field / (ref_field + 1e-12)

            # ----------------------------
            # Raw phase
            # ----------------------------
            raw_phase = np.angle(corrected)

            # ----------------------------
            # Unwrap
            # ----------------------------
            final_phase = apply_unwrap(raw_phase, "Skimage Unwrap")

            # ----------------------------
            # Save
            # ----------------------------
            base = os.path.splitext(os.path.basename(img_path))[0]

            save_path = os.path.join(folder, f"{base}p.tiff")

            save_phase_tiff(final_phase, save_path)

            print(f"[DONE] {save_path}")

        except Exception as e:
            print(f"[ERROR] Row {idx}: {e}")
