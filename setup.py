from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="fastipy",
    version="1.5.1",
    description="Fastipy is a fast and easy-to-use open source Python library for developing RESTful APIs. Inspired by the FastAPI and Fastify syntax and powered by uvicorn ASGI web server.",
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Bielgomes/Fastipy",
    author="Bielgomes",
    author_email="bielgomesdasilva@hotmail.com",
    license="GNU Affero General Public License v3",
    project_urls={"Bug Tracker": "https://github.com/Bielgomes/Fastipy/issues"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        "uvicorn[standard]",
        "starlette",
        "nest-asyncio",
        "Jinja2",
    ],
    python_requires=">=3.10",
)
