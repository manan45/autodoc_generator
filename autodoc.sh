#!/bin/bash
# AutoDoc Wrapper Script
# This script ensures the Python bin directory is in PATH and runs autodoc

# Add Python bin directory to PATH
export PATH="/Users/manan/Library/Python/3.9/bin:$PATH"

# Change to the autodoc directory
cd /Users/manan/auto_doc_generator

# Run autodoc with all passed arguments
/Users/manan/Library/Python/3.9/bin/autodoc "$@"
