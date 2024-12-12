import setuptools

setuptools.setup(
    name="cdk",
    version="0.0.1",
    description="A CDK Python app",
    long_description="Streamlit app designed to learn Japanese kana",
    long_description_content_type="text/markdown",
    author="Darya Petrashka",
    package_dir={"": "cdk"},
    packages=setuptools.find_packages(where="cdk"),
    install_requires=[
        "aws-cdk-lib>=2.0.0",
        "constructs>=10.0.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Code Generators",
        "Typing :: Typed",
    ],
)
