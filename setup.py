from setuptools import setup, find_packages

setup(
    name='tonibox',  # Replace with your package name
    version='0.1',
    package_dir={'': 'src'},  # This tells setuptools to look in src for packages
    packages=find_packages(where='src'),
    install_requires=[
        # Add any dependencies here, e.g., 'numpy', 'requests'
    ],
)
