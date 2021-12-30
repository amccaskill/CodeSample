import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="example-pkg-amccaskill",
    version="1.0.0",
    author="Adrian McCaskill",
    author_email="mccaskill.adrian@gmail.com",
    description="A simple API and Router Class",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amccaskill/CodeSample/Python/AppDev",
    project_urls={
        "Bug Tracker": "https://github.com/amccaskill/CodeSample/Python/AppDev",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=['flask'],
    python_requires=">=3.6",
)
