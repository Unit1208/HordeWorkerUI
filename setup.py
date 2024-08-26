from setuptools import setup, find_packages

setup(
    name='aihorde-worker-manager',
    version='0.1.0',
    description='A GUI application to manage AI Horde workers',
    author='Unit1208',
    author_email='unit1208@national.shitposting.agency',
    url='https://github.com/Unit1208/HordeWorkerUI',  # Update with your actual URL if available
    packages=find_packages(),
    install_requires=[
        'PyQt5>=5.15.11',  # Specify the minimum version for PyQt5
        'keyring>=23.3.0',
        'requests>=2.32.3',
    ],
    entry_points={
        'console_scripts': [
            'aihorde-worker-manager=pyqt:main',  # Adjust according to the actual script entry point
        ],
    },
    python_requires='>=3.6',  # Adjust based on the Python version compatibility
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
