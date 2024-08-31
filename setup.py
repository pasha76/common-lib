from setuptools import setup, find_packages

setup(
    name='common',  # Name of your package
    version='0.1.0',
    packages=find_packages(include=['common', 'common.*']),
    install_requires=[
       "pymysql",
       "sqlalchemy",
       "requests",
       "torch",
       "transformers",
       "Pillow",
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