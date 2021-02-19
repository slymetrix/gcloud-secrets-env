import os
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gcloud-secrets-env",
    version="1.0.0",
    author="Domenico Cirasino",
    author_email="domenico.cirasino@slymetrix.com",
    description="A utility to replace environ variables with Google Secrets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/slymetrix/gcloud-secrets-env",
    packages=setuptools.find_packages(),
    namespaces=['gcloud_secrets_env'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'google-api-core[grpc]==1.19.0',
        'google-cloud-secret-manager==1.0.0',
        'six>=1.12.0',
    ],
    package_root = os.path.abspath(os.path.dirname(__file__)),
)
