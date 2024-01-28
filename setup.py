from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="fastipy",
    version="1.5.0",
    description="Fastipy is a fast and easy-to-use open source Python library for developing RESTful APIs. Inspired by the FastAPI and Fastify syntax and powered by uvicorn ASGI web server.",
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Bielgomes/Fastipy",
    author="Bielgomes",
    author_email="bielgomesdasilva@hotmail.com",
    license="GNU Affero General Public License v3",
    project_urls={
        "Bug Tracker": "https://github.com/Bielgomes/Fastipy/issues"
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Framework :: FastAPI"
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    install_requires=["uvicorn[standard]", "nest-asyncio"],
    python_requires=">=3.10",
)