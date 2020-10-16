import setuptools
from pyww import VERSION

setuptools.setup(
    name="pyww",
    version=VERSION,
    author="xander-io",
    author_email="zackanderson026@gmail.com",
    description="Web watcher for python",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    entry_points={ "console_scripts": ["pyww = pyww.app:run"] }
)