from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Dash_tooltip",
    use_scm_version=True,  # Use the version from SCM (e.g., git)
    setup_requires=["setuptools_scm"],
    author="kb-",
    description="A tooltip functionality for Dash.",  # A brief description
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kb-/Dash_tooltip",  # Your project's repository URL
    packages=find_packages(),  # Automatically discover and include all packages
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Minimum python version required
    install_requires=[
        # List your dependencies here, for instance:
        # "dash>=1.0.0",
    ],
)
