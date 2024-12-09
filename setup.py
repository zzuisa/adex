from setuptools import setup, find_packages

# 读取 README.md 作为长描述
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Adex",  
    version="0.1.0",  
    author="Ao Sun",  
    author_email="zzuisa.cn@gmail.com",  
    description="A simple tool for managing and launching resources based on commands.",  # 简短描述
    long_description=long_description,  
    long_description_content_type="text/markdown",  
    url="https://github.com/your-repo/Adex",  
    packages=find_packages(where="src"),  
    package_dir={"": "src"},  
    classifiers=[  
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  
    install_requires=[  
        "keyboard",
        "tkinter"
    ],
    entry_points={  
        'console_scripts': [
            'adex=src.gui.gui_main:main', 
        ],
    },
    include_package_data=True, 
    data_files=[  
        ('Adex/resources', ['resources/resources.json']),
    ]
)