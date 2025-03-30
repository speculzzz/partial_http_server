from setuptools import setup, find_packages


setup(
    name="partial_http_server",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "httpd=server:start_server",
        ],
    },
    python_requires='>=3.11',
)
