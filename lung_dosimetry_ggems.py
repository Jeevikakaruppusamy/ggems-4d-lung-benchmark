import argparse
from ggems import *

parser = argparse.ArgumentParser(
  prog='lung_dosimetry_ggems.py',
  description='GGEMS photon dosimetry on the real 4D-Lung voxelized phantom',
)

parser.add_argument('-d', '--device', required=False, type=str, default='0', help="OpenCL device")
parser.add_argument('-p', '--phase', required=True, type=str, choices=['inhale', 'exhale'], help="Breathing phase to simulate")
parser.add_argument('-n', '--nparticles', required=False, type=int, default=1000000, help="Number of particles")
parser.add_argument('-s', '--seed', required=False, type=int, default=777, help="Seed of pseudo generator number")
parser.add_argument('-v', '--verbose', required=False, type=int, default=0, help="Set level of verbosity")

args = parser.parse_args()

device = args.device
verbosity_level = args.verbose
number_of_particles = args.nparticles
seed = args.seed
phase = args.phase

GGEMSVerbosity(verbosity_level)

opencl_manager = GGEMSOpenCLManager()
materials_database_manager = GGEMSMaterialsDatabaseManager()
processes_manager = GGEMSProcessesManager()
range_cuts_manager = GGEMSRangeCutsManager()

# OpenGL setup BEFORE device activation (matches GGEMS example order)
opengl_manager = GGEMSOpenGLManager()
opengl_manager.set_window_dimensions(800, 800)
opengl_manager.set_msaa(4)
opengl_manager.set_background_color('black')
opengl_manager.set_draw_axis(True)
opengl_manager.set_world_size(1.5, 1.5, 1.5, 'm')
opengl_manager.set_image_output(f'data/opengl_view_{phase}')
opengl_manager.set_displayed_particles(min(number_of_particles, 256))
opengl_manager.set_particle_color('gamma', 152, 251, 152)
opengl_manager.initialize()

opencl_manager.set_device_to_activate(device)

materials_database_manager.set_materials('materials.txt')

mhd_file = f'data/phantom_{phase}.mhd'
range_file = f'data/phantom_{phase}_range.txt'

phantom = GGEMSVoxelizedPhantom('lung_phantom')
phantom.set_phantom(mhd_file, range_file)
phantom.set_rotation(0.0, 0.0, 0.0, 'deg')
phantom.set_position(0.0, 0.0, 0.0, 'mm')
phantom.set_visible(True)

dosimetry = GGEMSDosimetryCalculator()
dosimetry.attach_to_navigator('lung_phantom')
dosimetry.set_output_basename(f'data/dosimetry_{phase}')
dosimetry.set_dosel_size(3.5156, 3.5156, 3.0, 'mm')
dosimetry.water_reference(False)
dosimetry.minimum_density(0.01, 'g/cm3')

dosimetry.uncertainty(True)
dosimetry.photon_tracking(False)
dosimetry.edep(True)
dosimetry.hit(True)
dosimetry.edep_squared(True)

processes_manager.add_process('Compton', 'gamma', 'all')
processes_manager.add_process('Photoelectric', 'gamma', 'all')
processes_manager.add_process('Rayleigh', 'gamma', 'all')

range_cuts_manager.set_cut('gamma', 0.1, 'mm', 'all')

point_source = GGEMSXRaySource('point_source')
point_source.set_source_particle_type('gamma')
point_source.set_number_of_particles(number_of_particles)
point_source.set_position(-400.0, 0.0, 0.0, 'mm')
point_source.set_rotation(0.0, 0.0, 0.0, 'deg')
point_source.set_beam_aperture(10.0, 'deg')
point_source.set_focal_spot_size(0.0, 0.0, 0.0, 'mm')
point_source.set_monoenergy(1.0, 'MeV')

ggems = GGEMS()
ggems.opencl_verbose(True)
ggems.material_database_verbose(False)
ggems.navigator_verbose(False)
ggems.source_verbose(True)
ggems.memory_verbose(True)
ggems.process_verbose(True)
ggems.range_cuts_verbose(True)
ggems.random_verbose(True)
ggems.profiling_verbose(True)
ggems.tracking_verbose(False, 0)

ggems.initialize(seed)
ggems.run()

dosimetry.delete()
ggems.delete()
exit()
