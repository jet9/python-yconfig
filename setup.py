from setuptools import setup, find_packages

setup(
    name="yconfig",
    version=__import__("yconfig").__version__,
    description="Yet Another YAML configuration files manager for python",
    long_description="Yet Another YAML configuration files manager for python",
    author="Dmitry Kurbatov",
    author_email="dk@dimcha.ru",
    license="BSD",
    url="https://github.com/jet9/python-yconfig",
    py_modules=['yconfig'],
    requires=['ndict', 'PyYAML'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python"
    ]
)
