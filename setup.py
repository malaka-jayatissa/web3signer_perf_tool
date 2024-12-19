from setuptools import setup, find_packages

setup(
    name="web3signer_perf_tool",
    version="0.0.1",
    description="Staking engine perf tool",
    author="Malaka Jayatissa",
    author_email="malaka@zerobeta.xyz",
    packages=find_packages(),
    install_requires=[
        # List your dependencies here
        "requests>=2.20.0",
        "numpy>=1.18.0",
        "boto3==1.34.113",
        "pyjwt==2.8.0",
        "cryptography==42.0.8",
        "pandas==2.2.3",
        "matplotlib==3.9.2",
        "httpx==0.27.2",
        "typer==0.12.3"
    ],
    classifiers=[
        # See https://pypi.org/classifiers/ for a list of valid classifiers
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',  # Specify the minimum Python version required
)