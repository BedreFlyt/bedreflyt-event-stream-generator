# Synthetic Event Stream Generator
- [Synthetic Event Stream Generator](#synthetic-event-stream-generator)
- [About This Project](#about-this-project)
- [Prerequisites](#prerequisites)
- [➡️ How To Get Started ⬅️](#️-how-to-get-started-️)
  - [System Setup](#system-setup)
- [Project Structure](#project-structure)
- [Repository Maintenance](#repository-maintenance)


# About This Project
Welcome to the *Synthetic Event Stream Generator* project! The objective of this project is to build and maintain a general purpose synthetic event / synthetic data generator for digital twins. This project is a fork of (https://github.com/BusterSalomon/UIO-DT-Synthetic-Event-Stream-Generator). Use that for the latest version and to adapt that to your need.

# Prerequisites
It is recommended that you are familiar with:
- Python
- Probability Distributions

# ➡️ How To Get Started ⬅️
All learning resources are located in the documentations folder [docs](/docs).
- If you are interested in knowing about the internal workings of the generator, go through the documents in [design_and_architecture](docs/design_and_architecture)
- To learn about how to use the tool, go through the examples in the [examples](/docs/examples), from top to bottom. To run the examples, make sure to have setup your system in accordance with the system setup instructions below.
## System Setup
- You are advised to run the code in a virtual environment like conda or venv
- To enable imports across the project and install the required dependencies open a terminal in root and run `pip install -e.`
# Project Structure
```
📦UIO-DT-Synthetic-Data-Generator
 ┣ 📂docs
 ┃ ┣ 📂design_and_architecture
 ┃ ┗ 📂examples
 ┣ 📂src
 ┃ ┣ 📂old_prototypes
 ┃ ┣ 🐍analytics.py
 ┃ ┣ 🐍EventStreamGenerator.py 
 ┃ ┗ 🐍utils.py
 ┗ 📜README.md
```

# Repository Maintenance
Use the VSCode extension [Markdown All in One](https://marketplace.visualstudio.com/items/?itemName=yzhang.markdown-all-in-one) to update the table of contents. 
