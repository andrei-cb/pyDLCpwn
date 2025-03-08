import os
from collections import deque

async def find_dll_directory(directory, files_to_search):
    """
    Find directory containing any of the target files using Breadth-First Search.
    Returns the directory closest to the root that contains any target file.
    """
    if not os.path.isdir(directory):
        return None
        
    target_files = {os.path.basename(f) for f in files_to_search}
    
    queue = deque([(directory, 0)])
    visited = {directory}
    
    while queue:
        current_dir, depth = queue.popleft()
        try:
            files = os.listdir(current_dir)
            if any(f in target_files for f in files):
                return current_dir
            
            for item in files:
                full_path = os.path.join(current_dir, item)
                if os.path.isdir(full_path) and full_path not in visited:
                    queue.append((full_path, depth + 1))
                    visited.add(full_path)
        except (PermissionError, OSError):
            continue
    
    return None