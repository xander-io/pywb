import setuptools

from pyww import VERSION

with open("requirements.txt", "r") as reqs_file:
    reqs = [i.strip() for i in reqs_file]

setuptools.setup(
    name="pyww",
    version=VERSION,
    author="xander-io",
    description="Python Web Watcher",
    packages=setuptools.find_packages(),
    install_requires=reqs,
    python_requires=">=3.9.0",
    entry_points={"console_scripts": ["pyww = pyww.app:run"]}
)
