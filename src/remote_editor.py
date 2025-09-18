#!/usr/bin/env python3
"""
Remote Repository Editor

Provides functionality to edit and commit to repositories remotely.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
from git import Repo, GitCommandError
import yaml

from .main import main as generate_docs


class RemoteEditor:
    """Handles remote repository editing and documentation generation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize RemoteEditor with configuration."""
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
    def clone_repository(self, repo_url: str, branch: str = "main") -> Path:
        """Clone a repository to temporary directory."""
        temp_dir = Path(tempfile.mkdtemp())
        
        try:
            self.logger.info(f"Cloning repository {repo_url} to {temp_dir}")
            repo = Repo.clone_from(repo_url, temp_dir, branch=branch)
            return temp_dir
        except GitCommandError as e:
            self.logger.error(f"Failed to clone repository: {e}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise
    
    def generate_docs_for_repo(self, repo_path: Path, config_override: Optional[Dict[str, Any]] = None) -> Path:
        """Generate documentation for a cloned repository."""
        docs_dir = repo_path / "auto_generated_docs"
        docs_dir.mkdir(exist_ok=True)
        
        # Save current working directory
        original_cwd = os.getcwd()
        
        try:
            # Change to repository directory
            os.chdir(repo_path)
            
            # Override sys.argv to simulate command line args
            original_argv = sys.argv.copy()
            sys.argv = [
                'autodoc',
                '--repo', str(repo_path),
                '--output', str(docs_dir),
                '--analyze',
                '--generate',
                '--build'
            ]
            
            # Add config override if provided
            if config_override:
                config_path = repo_path / "temp_documentor.yaml"
                with open(config_path, 'w') as f:
                    yaml.dump(config_override, f)
                sys.argv.extend(['--config', str(config_path)])
            
            # Generate documentation
            generate_docs()
            
            return docs_dir
            
        except Exception as e:
            self.logger.error(f"Failed to generate documentation: {e}")
            raise
        finally:
            # Restore original state
            sys.argv = original_argv
            os.chdir(original_cwd)
    
    def commit_and_push(self, repo_path: Path, files_to_add: List[str], 
                       commit_message: str, branch: str = "docs-auto-update",
                       create_pr: bool = True) -> Dict[str, Any]:
        """Commit changes and optionally create pull request."""
        repo = Repo(repo_path)
        
        # Create and checkout new branch
        try:
            repo.git.checkout('-b', branch)
        except GitCommandError:
            # Branch might already exist
            repo.git.checkout(branch)
        
        # Add files
        for file_path in files_to_add:
            repo.git.add(file_path)
        
        # Commit changes
        if repo.is_dirty():
            repo.git.commit('-m', commit_message)
            
            # Push to remote
            origin = repo.remote('origin')
            origin.push(branch)
            
            result = {
                'success': True,
                'branch': branch,
                'commit_hash': repo.head.commit.hexsha,
                'message': f'Successfully committed and pushed to branch {branch}'
            }
            
            if create_pr:
                result['pr_message'] = f"Create a pull request for branch {branch} on GitHub"
            
            return result
        else:
            return {
                'success': False,
                'message': 'No changes to commit'
            }
    
    def process_repository(self, repo_url: str, config_override: Optional[Dict[str, Any]] = None,
                          commit_message: str = "Auto-generated documentation update",
                          branch: str = "docs-auto-update") -> Dict[str, Any]:
        """Complete workflow: clone, generate docs, commit, and push."""
        temp_dir = None
        
        try:
            # Clone repository
            temp_dir = self.clone_repository(repo_url)
            
            # Generate documentation
            docs_dir = self.generate_docs_for_repo(temp_dir, config_override)
            
            # Prepare files to commit
            files_to_add = []
            if docs_dir.exists():
                # Add all generated documentation files
                for file_path in docs_dir.rglob('*'):
                    if file_path.is_file():
                        files_to_add.append(str(file_path.relative_to(temp_dir)))
            
            # Add any configuration files
            config_files = ['documentor.yaml', 'mkdocs.yml']
            for config_file in config_files:
                config_path = temp_dir / config_file
                if config_path.exists():
                    files_to_add.append(config_file)
            
            # Commit and push changes
            result = self.commit_and_push(temp_dir, files_to_add, commit_message, branch)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process repository: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to process repository {repo_url}'
            }
        finally:
            # Clean up temporary directory
            if temp_dir and temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)


def cli_remote_edit():
    """Command line interface for remote editing."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Remote Repository Documentation Editor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://github.com/user/repo.git
  %(prog)s https://github.com/user/repo.git --branch main --commit-msg "Updated docs"
  %(prog)s https://github.com/user/repo.git --config config.yaml
        """
    )
    
    parser.add_argument(
        'repo_url',
        help='URL of the repository to process'
    )
    
    parser.add_argument(
        '--branch',
        default='docs-auto-update',
        help='Branch name for committing changes (default: docs-auto-update)'
    )
    
    parser.add_argument(
        '--commit-msg',
        default='Auto-generated documentation update',
        help='Commit message for changes'
    )
    
    parser.add_argument(
        '--config',
        help='Path to configuration YAML file'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Load config override if provided
    config_override = None
    if args.config:
        config_path = Path(args.config)
        if config_path.exists():
            with open(config_path, 'r') as f:
                config_override = yaml.safe_load(f)
        else:
            print(f"Warning: Config file {args.config} not found")
    
    # Process repository
    editor = RemoteEditor()
    result = editor.process_repository(
        args.repo_url,
        config_override=config_override,
        commit_message=args.commit_msg,
        branch=args.branch
    )
    
    # Print results
    if result['success']:
        print(f"✅ {result['message']}")
        if 'commit_hash' in result:
            print(f"📝 Commit: {result['commit_hash']}")
        if 'pr_message' in result:
            print(f"🔀 {result['pr_message']}")
    else:
        print(f"❌ {result['message']}")
        if 'error' in result:
            print(f"Error: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    cli_remote_edit()
