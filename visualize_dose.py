import SimpleITK as sitk
import numpy as np
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(11, 9))

for row, phase in enumerate(['inhale', 'exhale']):
    img = sitk.ReadImage(f'data/dosimetry_{phase}_dose.mhd')
    arr = sitk.GetArrayFromImage(img)  # (z, y, x)

    mid_z = arr.shape[0] // 2
    axial = arr[mid_z]
    coronal_mip = arr.max(axis=0)

    im0 = axes[row, 0].imshow(axial, cmap='hot')
    axes[row, 0].set_title(f'{phase.capitalize()} — axial slice (z={mid_z})')
    axes[row, 0].axis('off')
    plt.colorbar(im0, ax=axes[row, 0], label='Dose (Gy)', fraction=0.046)

    im1 = axes[row, 1].imshow(coronal_mip, cmap='hot')
    axes[row, 1].set_title(f'{phase.capitalize()} — coronal MIP')
    axes[row, 1].axis('off')
    plt.colorbar(im1, ax=axes[row, 1], label='Dose (Gy)', fraction=0.046)

plt.tight_layout()
plt.savefig('dose_visualization.png', dpi=150)
print("Saved: dose_visualization.png")

