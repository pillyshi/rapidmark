"""Generator management for RapidMark frontend."""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional
from rich.console import Console

try:
    from importlib.resources import files
except ImportError:
    # Fallback for Python < 3.9
    from importlib_resources import files # type: ignore

console = Console()


class GeneratorManager:
    """Manages the Vue.js generator with caching."""
    
    def __init__(self):
        self.cache_dir = self._get_cache_dir()
        self.generator_path = self.cache_dir / 'generator'
    
    def _get_cache_dir(self) -> Path:
        """Get or create cache directory."""
        # Use platform-appropriate cache directory
        if os.name == 'nt':  # Windows
            cache_base = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
        else:  # Unix-like (macOS, Linux)
            cache_base = Path(os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache'))
        
        cache_dir = cache_base / 'rapidmark'
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
    
    def _get_version(self) -> str:
        """Get current package version."""
        from . import __version__
        return __version__
    
    def _extract_generator(self) -> None:
        """Extract generator assets from package to cache directory."""
        console.print("🏗️ Setting up generator environment...")
        
        # Remove old generator if exists
        if self.generator_path.exists():
            shutil.rmtree(self.generator_path)
        
        # Extract generator from package using importlib.resources
        generator_package = files('rapidmark') / 'generator'
        if not generator_package.is_dir():
            raise RuntimeError("Generator assets not found in package")
        
        # Copy generator directory
        self._copy_resource_tree(generator_package, self.generator_path)
        
        # Create version marker
        version_file = self.cache_dir / 'version'
        version_file.write_text(self._get_version())
        
        console.print(f"📦 Generator extracted to: {self.generator_path}")
    
    def _copy_resource_tree(self, source, dest):
        """Recursively copy resource tree from package."""
        dest.mkdir(parents=True, exist_ok=True)
        
        for item in source.iterdir():
            dest_item = dest / item.name
            if item.is_dir():
                self._copy_resource_tree(item, dest_item)
            else:
                # Read file content and write to destination
                content = item.read_bytes()
                dest_item.write_bytes(content)
    
    def _is_setup_valid(self) -> bool:
        """Check if generator setup is valid and up-to-date."""
        if not self.generator_path.exists():
            return False
        
        # Check version
        version_file = self.cache_dir / 'version'
        if not version_file.exists():
            return False
        
        cached_version = version_file.read_text().strip()
        current_version = self._get_version()
        
        if cached_version != current_version:
            console.print(f"🔄 Version changed ({cached_version} → {current_version}), updating generator...")
            return False
        
        # Check if node_modules exists and npm install was successful
        node_modules = self.generator_path / 'node_modules'
        package_lock = self.generator_path / 'package-lock.json'
        
        return node_modules.exists() and package_lock.exists()
    
    def _ensure_node_available(self) -> None:
        """Check if Node.js is available."""
        if not shutil.which('node'):
            raise RuntimeError(
                "Node.js is required but not found.\n"
                "Please install Node.js from: https://nodejs.org/"
            )
        
        if not shutil.which('npm'):
            raise RuntimeError(
                "npm is required but not found.\n"
                "Please install npm (usually comes with Node.js)"
            )
    
    def _setup_dependencies(self) -> None:
        """Install npm dependencies."""
        self._ensure_node_available()
        
        console.print("📦 Installing npm dependencies...")
        
        # Run npm ci for reproducible builds
        result = subprocess.run(
            ['npm', 'ci'],
            cwd=self.generator_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            console.print(f"❌ npm ci failed:\n{result.stderr}")
            raise RuntimeError(f"Failed to install dependencies: {result.stderr}")
        
        console.print("✅ Dependencies installed successfully")
    
    def ensure_generator_ready(self) -> Path:
        """Ensure generator is extracted and dependencies are installed."""
        if not self._is_setup_valid():
            self._extract_generator()
            self._setup_dependencies()
        else:
            console.print("✅ Generator already set up and ready")
        
        return self.generator_path
    
    def build_html(self, task_file: Path, output_file: Path, worker_name: str, result_file: Optional[Path] = None) -> None:
        """Build HTML file from task configuration."""
        generator_path = self.ensure_generator_ready()

        console.print(f"🏗️ Building HTML for: {task_file}")

        # Copy task file to generator directory
        task_dest = generator_path / 'task.rapidmark.json'
        shutil.copy2(task_file, task_dest)

        # Prepare environment variables
        env = os.environ.copy()
        env['RAPIDMARK_TASK_FILE'] = str(task_dest)
        env['RAPIDMARK_WORKER_NAME'] = worker_name
        console.print(f"👤 Worker: {worker_name}")

        if result_file is not None:
            result_dest = generator_path / 'result.rapidmark.json'
            shutil.copy2(result_file, result_dest)
            env['RAPIDMARK_RESULT_FILE'] = str(result_dest)
            console.print(f"📊 Embedding results from: {result_file}")

        # Run npm build
        result = subprocess.run(
            ['npm', 'run', 'build'],
            cwd=generator_path,
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            console.print(f"❌ Build failed:\n{result.stderr}")
            raise RuntimeError(f"Build failed: {result.stderr}")
        
        # Copy generated HTML to output location
        built_html = generator_path / 'dist' / 'index.html'
        if not built_html.exists():
            raise RuntimeError("Generated HTML file not found")
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(built_html, output_file)
        
        # Show file size
        file_size = output_file.stat().st_size
        size_mb = file_size / (1024 * 1024)
        console.print(f"✅ Generated: {output_file} ({size_mb:.1f}MB)")
    
    def cleanup_cache(self) -> None:
        """Remove all cached generator files."""
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            console.print("🗑️ Cache cleared")


# Global instance
generator_manager = GeneratorManager()
