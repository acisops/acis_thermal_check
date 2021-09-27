#!/usr/bin/env python
from setuptools import setup
import glob

try:
    from testr.setup_helper import cmdclass
except ImportError:
    cmdclass = {}

templates = glob.glob("templates/*")
data = glob.glob("data/*")

entry_points = {
    'console_scripts': [
        'dea_check = acis_thermal_check.scripts.dea_check:main',
        'dpa_check = acis_thermal_check.scripts.dpa_check:main',
        'psmc_check = acis_thermal_check.scripts.psmc_check:main',
        'acisfp_check = acis_thermal_check.scripts.acisfp_check:main',
        'fep1_mong_check = acis_thermal_check.scripts.fep1_mong_check:main',
        'fep1_actel_check = acis_thermal_check.scripts.fep1_actel_check:main',
        'bep_pcb_check = acis_thermal_check.scripts.bep_pcb_check:main'
    ]
}

setup(name='acis_thermal_check',
      packages=["acis_thermal_check"],
      use_scm_version=True,
      setup_requires=['setuptools_scm', 'setuptools_scm_git_archive'],
      description='ACIS Thermal Model Library',
      author='John ZuHone',
      author_email='john.zuhone@cfa.harvard.edu',
      url='https://github.com/acisops/acis_thermal_check',
      data_files=[('templates', templates), ('data', data)],
      include_package_data=True,
      entry_points=entry_points,
      zip_safe=False,
      tests_require=["pytest"],
      cmdclass=cmdclass,
      )
