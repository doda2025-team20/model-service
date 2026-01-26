import argparse
import re
import sys
from pathlib import Path

def get_version(file_path):
    content = file_path.read_text()
    match = re.search(r'version\s*=\s*"(.*)"', content)
    if match:
        return match.group(1)
    raise ValueError("Version not found in pyproject.toml")

def set_version(file_path, new_version):
    content = file_path.read_text()
    new_content = re.sub(r'version\s*=\s*".*"', f'version = "{new_version}"', content)
    file_path.write_text(new_content)
    print(f"Updated version to {new_version}")

def strip_snapshot(version):
    return version.replace("-SNAPSHOT", "")

def bump_patch(version):
    # Assumes version is X.Y.Z or X.Y.Z-SNAPSHOT
    base = version.replace("-SNAPSHOT", "")
    parts = base.split('.')
    if len(parts) < 3:
        parts.extend(['0'] * (3 - len(parts)))
    
    parts[-1] = str(int(parts[-1]) + 1)
    return ".".join(parts)

def main():
    parser = argparse.ArgumentParser(description="Manage project version")
    parser.add_argument("file", type=Path, help="Path to pyproject.toml")
    parser.add_argument("--get", action="store_true", help="Get current version")
    parser.add_argument("--strip-snapshot", action="store_true", help="Strip -SNAPSHOT from version")
    parser.add_argument("--bump-patch", action="store_true", help="Bump patch version")
    parser.add_argument("--next-snapshot", action="store_true", help="Bump patch and add -SNAPSHOT")
    
    args = parser.parse_args()
    
    if not args.file.exists():
        print(f"File {args.file} not found")
        sys.exit(1)
        
    current_version = get_version(args.file)
    
    if args.get:
        print(current_version)
        return

    new_version = current_version
    
    if args.strip_snapshot:
        new_version = strip_snapshot(new_version)
        
    if args.bump_patch:
        new_version = bump_patch(new_version)
        
    if args.next_snapshot:
        # If we haven't bumped yet, bump now
        if not args.bump_patch:
             new_version = bump_patch(new_version)
        if not new_version.endswith("-SNAPSHOT"):
            new_version += "-SNAPSHOT"
            
    if new_version != current_version:
        set_version(args.file, new_version)
    else:
        print("Version unchanged")

if __name__ == "__main__":
    main()

