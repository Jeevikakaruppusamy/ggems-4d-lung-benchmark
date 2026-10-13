# GGEMS 4D-Lung Benchmark

GPU-accelerated photon dosimetry on breathing-phase (4D-Lung) CT voxel phantoms using GGEMS (OpenCL).

## Aim

To establish a reproducible workflow that converts breathing-phase lung CT data into GGEMS voxelized phantoms and computes photon dose distributions on a GPU, as a basis for benchmarking against Geant4 (CPU).

## Contents

| File | Purpose |
|---|---|
| `convert_to_ggems.py` | Converts CT series (inhale and exhale phases) into GGEMS phantom files (.mhd/.raw and range file) using HU-to-material mapping |
| `materials.txt` | Material definitions used by the phantoms (based on the GGEMS example file, extended with additional materials) |
| `lung_dosimetry_ggems.py` | GGEMS dosimetry simulation: 1 MeV mono-energetic external photon source on the voxelized phantom |
| `visualize_dose.py` | Dose visualization (axial slice and coronal maximum-intensity projection) |

## Workflow

1. Obtain a breathing-phase CT dataset (TCIA 4D-Lung collection; not included in this repository).
2. Run `convert_to_ggems.py` to generate the inhale and exhale phantoms.
3. Run `lung_dosimetry_ggems.py` for each phase.
4. Run `visualize_dose.py` to produce dose maps.

File paths inside the scripts correspond to the original working directory and should be adapted to the local setup.

## Requirements

- GGEMS (https://github.com/GGEMS/GGEMS) with Python bindings
- OpenCL-capable device
- Python packages: SimpleITK, NumPy, Matplotlib

## Phantom and simulation settings

- Phantom grid: 128 x 128 x 50 voxels (voxel size 3.5156 x 3.5156 x 3.0 mm), resampled from 512 x 512 x 50 CT slices
- Source: 1 MeV mono-energetic external photon source
- Particles: 100,000 per run
- Hardware: integrated Intel UHD Graphics 770 (OpenCL)

## Results obtained (confirmed)

| Phase | Total dose (sum over voxels) | Simulation time |
|---|---|---|
| Inhale | 2.615760e-04 Gy | 109 ms |
| Exhale | 2.665771e-04 Gy | 111 ms |

## Limitations

- GGEMS supports photon and electron transport only. These results are therefore not directly comparable with the neutron-source Geant4 results of the related lung dosimetry work.
- Results are from a single run per phase; statistical uncertainty across independent seeds has not been evaluated.
- The Intel integrated GPU does not support double precision, so the GGEMS build was configured for single precision and local source modifications were required. These modifications are not part of this repository.
- CT data and generated phantoms are not distributed here.

## Status

Work in progress. Planned work includes a quantitative comparison with Geant4 on the same phantoms.
