import setuptools

from pywb import VERSION

with open("requirements.txt", "r") as reqs_file:
    reqs = [i.strip() for i in reqs_file]

setuptools.setup(
    name="pywb",
    version=VERSION,
    author="xander-io",
    description="Python Web Bot",
    packages=setuptools.find_packages(),
    install_requires=reqs,
    include_package_data=True,
    python_requires=">=3.9.0",
    entry_points={"console_scripts": ["pywb = pywb.app:run"]}
)
