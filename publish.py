#!/usr/bin/env python3
"""
Package Publishing Helper

This script helps with publishing the auto-doc-generator package.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd, check=True):
    """Run a shell command."""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, shell=isinstance(cmd, str), check=check)
    return result.returncode == 0


def clean_build():
    """Clean previous build artifacts."""
    print("🧹 Cleaning build artifacts...")
    
    dirs_to_clean = ['build', 'dist', '*.egg-info']
    for pattern in dirs_to_clean:
        if '*' in pattern:
            import glob
            for path in glob.glob(pattern):
                if os.path.isdir(path):
                    import shutil
                    shutil.rmtree(path)
        else:
            path = Path(pattern)
            if path.exists():
                import shutil
                shutil.rmtree(path)


def build_package():
    """Build the package."""
    print("📦 Building package...")
    return run_command([sys.executable, '-m', 'build'])


def check_package():
    """Check the built package."""
    print("🔍 Checking package...")
    return run_command([sys.executable, '-m', 'twine', 'check', 'dist/*'])


def test_install():
    """Test installation of the built package."""
    print("🧪 Testing package installation...")
    
    # Create a temporary virtual environment
    import tempfile
    import venv
    
    with tempfile.TemporaryDirectory() as temp_dir:
        venv_dir = Path(temp_dir) / "test_env"
        venv.create(venv_dir, with_pip=True)
        
        # Get the python executable in the venv
        if os.name == 'nt':
            python_exe = venv_dir / "Scripts" / "python.exe"
            pip_exe = venv_dir / "Scripts" / "pip.exe"
        else:
            python_exe = venv_dir / "bin" / "python"
            pip_exe = venv_dir / "bin" / "pip"
        
        # Install the package
        dist_files = list(Path("dist").glob("*.whl"))
        if not dist_files:
            dist_files = list(Path("dist").glob("*.tar.gz"))
        
        if not dist_files:
            print("❌ No distribution files found!")
            return False
        
        install_cmd = [str(pip_exe), 'install', str(dist_files[0])]
        if not run_command(install_cmd, check=False):
            print("❌ Package installation failed!")
            return False
        
        # Test the CLI
        test_cmd = [str(python_exe), '-c', 'import sys; sys.argv=["autodoc", "--help"]; from auto_doc_generator import main; main()']
        if not run_command(test_cmd, check=False):
            print("❌ CLI test failed!")
            return False
        
        print("✅ Package installation test passed!")
        return True


def upload_to_test_pypi():
    """Upload to Test PyPI."""
    print("🚀 Uploading to Test PyPI...")
    cmd = [
        sys.executable, '-m', 'twine', 'upload',
        '--repository', 'testpypi',
        'dist/*'
    ]
    return run_command(cmd)


def upload_to_pypi():
    """Upload to PyPI."""
    print("🚀 Uploading to PyPI...")
    cmd = [sys.executable, '-m', 'twine', 'upload', 'dist/*']
    return run_command(cmd)


def create_github_release(version, description=""):
    """Create GitHub release."""
    print(f"🏷️ Creating GitHub release for version {version}...")
    
    # Create git tag
    run_command(['git', 'tag', f'v{version}'])
    run_command(['git', 'push', 'origin', f'v{version}'])
    
    print(f"✅ Created tag v{version}. GitHub Actions will handle the release.")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Package publishing helper")
    parser.add_argument('--clean', action='store_true', help='Clean build artifacts')
    parser.add_argument('--build', action='store_true', help='Build package')
    parser.add_argument('--check', action='store_true', help='Check package')
    parser.add_argument('--test', action='store_true', help='Test package installation')
    parser.add_argument('--test-upload', action='store_true', help='Upload to Test PyPI')
    parser.add_argument('--upload', action='store_true', help='Upload to PyPI')
    parser.add_argument('--release', help='Create GitHub release with version')
    parser.add_argument('--all', action='store_true', help='Run full workflow (clean, build, check, test)')
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        args.all = True  # Default to running all steps
    
    success = True
    
    if args.clean or args.all:
        clean_build()
    
    if args.build or args.all:
        success &= build_package()
    
    if args.check or args.all:
        success &= check_package()
    
    if args.test or args.all:
        success &= test_install()
    
    if args.test_upload and success:
        success &= upload_to_test_pypi()
    
    if args.upload and success:
        success &= upload_to_pypi()
    
    if args.release and success:
        create_github_release(args.release)
    
    if success:
        print("🎉 All operations completed successfully!")
        
        if args.all:
            print("\n📋 Next steps:")
            print("1. Test install from Test PyPI: pip install -i https://test.pypi.org/simple/ auto-doc-generator")
            print("2. If everything works, upload to PyPI: python publish.py --upload")
            print("3. Create GitHub release: python publish.py --release 1.0.0")
    else:
        print("❌ Some operations failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
