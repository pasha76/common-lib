from setuptools import setup, find_packages

setup(
    name='blushy',  # Name of your package
    version='0.2.12',
    packages=find_packages(exclude=['build', 'build.*',"blushy.egg*"]),  # Exclude 'build' folder and its subpackages
    install_requires=[
       "pymysql",
       "sqlalchemy",
       "requests",
       "torch",
       "transformers",
       "pillow",
       "lxml",
       "grpcio-tools",
       "protobuf",
       "qdrant-client",
       "scikit-learn",
       "SentencePiece",
       "numpy",
       "sentence-transformers",
       "google-cloud",
       "google-cloud-storage",
       "imagehash",
       "openai",
       "funcy"
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