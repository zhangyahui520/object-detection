from setuptools import setup, find_packages

setup(
    name="object_detection",
    version="0.0.0",
    description="TODO",
    author="Xinyuan Yao",
    author_email="yao.ntno@google.com",
    license="TODO",
    packages=find_packages(),
    package_data={"object_detection": ["py.typed"],},
    install_requires=[
        "matplotlib",
        "torch",
        "torchvision",
        "efficientnet_pytorch",
        "scipy",
        "typing_extensions",
        "tqdm",
    ],
    extras_require={
        "dev": [
            "mypy",
            "pytest",
            "black",
            "pytest-mock",
            "pytest-cov",
            "opencv-python",
        ]
    },
)
