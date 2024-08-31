from setuptools import setup, find_packages

setup(
    name='blushy',  # Name of your package
    version='0.1.12',
    packages=find_packages(exclude=['build', 'build.*',"blushy.egg*"]),  # Exclude 'build' folder and its subpackages
    install_requires=[
       "pymysql",
       "sqlalchemy",
       "requests",
       "torch",
       "transformers",
       "pillow",
       "lxml"
    ],
    include_package_data=True,
    description='A utility package for common functionalities',
    author='Tolga Gunduz',
    author_email='tolga@blushy.app',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',  # Specify Python version compatibility
)