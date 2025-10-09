# Gemini Project Analysis: OMR Grading System

## Project Overview

This project is an Optical Mark Recognition (OMR) grading system designed to automatically grade answer sheets. It leverages computer vision techniques, primarily using Python with the OpenCV library. The project is structured as an 8-week academic endeavor, with a clear, progressive implementation plan. The system is designed to be robust, employing multiple detection methods (contour, Hough transform, and template matching) and a fusion mechanism to improve accuracy.

The core of the project lies in the `src` directory, which is organized into `preprocessing` and `template_detector` modules. The `template_detector` module contains the main pipeline for processing OMR sheets, including grid detection, segmentation, and bubble (answer) detection. The project is well-configured, with a central `config.py` file for managing all processing parameters.

## Building and Running

The project uses a Python environment managed with `uv`.

### Prerequisites

*   Python 3.9+
*   `uv` package installer

### Setup and Execution

1.  **Create and activate the virtual environment:**
    ```bash
    uv venv omr_env
    .\omr_env\Scripts\Activate.ps1
    ```

2.  **Install dependencies:**
    ```bash
    uv pip install opencv-python==4.8.1.78 numpy==1.24.3 matplotlib pandas
    ```

3.  **Run the main processing pipeline:**
    While there isn't a single "main" script evident from the file structure, the `OMRPipeline` class in `src/template_detector/pipeline.py` is the entry point for processing. To run the pipeline, you would need to create a script that imports and uses this class.

    **TODO:** Create a main script (`main.py` or similar) to provide a clear entry point for running the OMR processing on an image or a directory of images.

## Development Conventions

*   **Configuration Management:** The project uses a centralized configuration system (`src/template_detector/config.py`) with dataclasses to manage all parameters for the different processing modules. This is a good practice that makes the system easy to configure and tune.
*   **Modular Architecture:** The code is well-organized into modules with specific responsibilities (e.g., `core`, `segmentation`, `utils`). This makes the codebase easier to understand, maintain, and extend.
*   **Structured Timeline:** The project follows a structured 8-week timeline with clear goals for each week. This indicates a well-planned and organized development process.
*   **Documentation:** The project includes a `README.md` file with good setup instructions and a high-level overview. There are also `README.md` files within some of the subdirectories.
*   **Testing:** A `tests` directory exists, but it is not clear how comprehensive the tests are. The `src/template_detector/tests` directory contains a `test_pipeline.py`, which is a good sign.
