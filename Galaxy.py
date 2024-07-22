# Extragalatic
import os
import pytest
import numpy as np
from astropy.io.fits import HDUList
from matplotlib import pyplot as plt
from matplotlib.colors import LogNorm
import scopesim
import synphot
from scopesim import Source
from astropy.io import fits
from scopesim_templates.extragalactic import galaxy
from scopesim import rc
from scopesim.source.source_templates import star_field
import scopesim_templates as sim_tp
from scopesim.optics.fov_manager import FOVManager

PLOTS = True

if rc.__config__["!SIM.tests.run_integration_tests"] is False:
    pytestmark = pytest.mark.skip("Ignoring DREAMS integration tests")

# Set TOP_PATH to the directory containing the DREAMS package
TOP_PATH = "/Users/anjali/Desktop"
rc.__config__["!SIM.file.local_packages_path"] = TOP_PATH

# Adjust the PKGS dictionary to reflect the correct path
PKGS = {"DREAMS": os.path.join(TOP_PATH, "DREAMS")}

# Verify the path to the DREAMS package
if not os.path.exists(PKGS["DREAMS"]):
    raise FileNotFoundError(f"DREAMS package not found at {PKGS['DREAMS']}")
else:
    print("DREAMS package found at:", PKGS["DREAMS"])

cmds = scopesim.UserCommands(use_instrument="DREAMS")
cmds["!OBS.dit"] = 1000
cmds["!OBS.ndit"] = 1000
cmds["!DET.bin_size"] = 1
cmds["!OBS.sky.bg_mag"] = 14.9
cmds["!OBS.sky.filter_name"] = "J"
cmds["SIM.sub_pixel.flag"] = True
dreams = scopesim.OpticalTrain(cmds)
dreams["detector_linearity"].include = False
dreams.fov_manager = FOVManager(dreams.optics_manager.fov_setup_effects, cmds=dreams.cmds, preload_fovs=False)
# Then make the initial field of view 10 times larges than normal.
dreams.fov_manager.volumes_list[0]["x_min"] = -18000  # arcsec
dreams.fov_manager.volumes_list[0]["x_max"] = 18000
dreams.fov_manager.volumes_list[0]["y_min"] = -18000
dreams.fov_manager.volumes_list[0]["y_max"] = 18000
# Finally, shrink the field of view to the detector size.
dreams.fov_manager._fovs_list = list(dreams.fov_manager.generate_fovs_list())

print("scopesim package loaded successfully.")
#src = sim_tp.stellar.clusters.cluster(mass=10000,  distance=50000, core_radius=70, seed=9002)
src= sim_tp.extragalactic.galaxy("kc96/s0", z=2.48, amplitude= 14.5, filter_curve="J", pixel_scale= 2.48, r_eff=2.5, n=4, ellip=0.5, theta=45, extend=3) # pixel_scale is in arcsec/pixel
dreams.observe(src, update=False)
print("yessss anjali")
hdus = dreams.readout()
#dreams.readout(filename="Han.fits")
plt.subplot(121)
wave = np.arange(3000, 11000)
plt.plot(wave, dreams.optics_manager.surfaces_table.throughput(wave))
plt.subplot(122)
im = hdus[0][1].data
detector_order = [1, 2, 3, 4, 5, 6]
plt.figure(figsize=(20, 20))
for plot_number, hdu_number in enumerate(detector_order, 1):
    plt.subplot(3, 2, plot_number)
    plt.imshow(np.log10(src.fields[0].data), origin="lower")
    plt.colorbar()
    
plt.show()
