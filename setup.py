from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in appointedd_integration/__init__.py
from appointedd_integration import __version__ as version

setup(
	name="appointedd_integration",
	version=version,
	description="App to Integrate Appointedd with ERPNext",
	author="Hardik Gadesha",
	author_email="hardikgadesha@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
