import argparse
import pydicom
import numpy as np
import glob
import os
from scipy.ndimage import zoom
import SimpleITK as sitk

TARGET_XY = 128
SLICE_STEP = 1

materials = [
    (0, "Air"), (1, "Lung"), (2, "Adipose"), (3, "Water"),
    (4, "Muscle"), (5, "B100Bone"), (6, "BoneCompact"),
    (7, "BoneCortical"), (8, "Fe"),
]

hu_thresholds = [-800, -145, -60, 0, 60, 1150, 1500, 2100, 66000]


def hu_to_material_index(hu_array):
    idx = np.searchsorted(hu_thresholds, hu_array, side="left")
    return np.clip(idx, 0, len(hu_thresholds) - 1).astype(np.int32)


def convert(dicom_dir, out_prefix):
    files = glob.glob(os.path.join(dicom_dir, "*.dcm"))
    if not files:
        raise FileNotFoundError(f"No .dcm files found in {dicom_dir}")

    slices = [pydicom.dcmread(f) for f in files]
    slices.sort(key=lambda s: float(s.ImagePositionPatient[2]))
    slices = slices[::SLICE_STEP]

    rows, cols = slices[0].Rows, slices[0].Columns
    n_slices = len(slices)
    px_spacing = slices[0].PixelSpacing
    slice_thickness = float(slices[0].SliceThickness) * SLICE_STEP

    print(f"Loaded {n_slices} slices, {rows}x{cols} each")
    print(f"Resampling to {TARGET_XY}x{TARGET_XY}x{n_slices}")

    volume = np.zeros((n_slices, TARGET_XY, TARGET_XY), dtype=np.uint8)
    for i, s in enumerate(slices):
        hu = s.pixel_array.astype(np.int32) * int(s.RescaleSlope) + int(s.RescaleIntercept)
        hu_small = zoom(hu, TARGET_XY / hu.shape[0], order=1)
        volume[i] = hu_to_material_index(hu_small)

    scale = cols / TARGET_XY
    voxel_xy_mm = float(px_spacing[1]) * scale
    voxel_z_mm = slice_thickness

    img = sitk.GetImageFromArray(volume)
    img.SetSpacing((voxel_xy_mm, voxel_xy_mm, voxel_z_mm))
    img.SetOrigin((0.0, 0.0, 0.0))

    mhd_path = f"{out_prefix}.mhd"
    sitk.WriteImage(img, mhd_path)
    print(f"Written: {mhd_path} (+ .raw / .zraw)")

    range_path = f"{out_prefix}_range.txt"
    with open(range_path, "w") as f:
        for idx, name in materials:
            f.write(f"{idx} {idx} {name}\n")
    print(f"Written: {range_path}")

    print(f"Dimensions: {TARGET_XY} x {TARGET_XY} x {n_slices}")
    print(f"Voxel size: {voxel_xy_mm:.4f} x {voxel_xy_mm:.4f} x {voxel_z_mm:.4f} mm")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True, choices=["inhale", "exhale"])
    args = parser.parse_args()

    if args.phase == "inhale":
        dicom_dir = "/home/cwr/dicom_src_copy/build/inhale_sorted"
        out_prefix = "/home/cwr/ggems_lung/data/phantom_inhale"
    else:
        dicom_dir = "/home/cwr/dicom_src_copy/build/exhale_sorted"
        out_prefix = "/home/cwr/ggems_lung/data/phantom_exhale"

    os.makedirs(os.path.dirname(out_prefix), exist_ok=True)
    convert(dicom_dir, out_prefix)
