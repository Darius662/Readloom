def add_ebook_file(series_id: int, volume_id: int, file_path: str, file_type: Optional[str] = None, max_retries: int = 5) -> Dict:
    """Add an e-book file to the database and storage.
    
    Args:
        series_id (int): The series ID.
        volume_id (int): The volume ID.
        file_path (str): The path to the e-book file.
        file_type (Optional[str]): The file type. If None, it will be detected from the file extension.
        max_retries (int, optional): Maximum number of retries for database operations. Defaults to 5.
        
    Returns:
        Dict: The file information if successful, empty dict otherwise.
    """
    retries = 0
    retry_delay = 0.5
    
    # Check if the file exists before entering retry loop
    source_path = Path(file_path)
    if not source_path.exists() or not source_path.is_file():
        LOGGER.error(f"File does not exist: {file_path}")
        return {}
    
    # Get file info
    file_name = source_path.name
    file_size = source_path.stat().st_size
    
    # Detect file type from extension if not provided
    if file_type is None:
        ext = source_path.suffix.lower()
        if ext in ['.pdf']:
            file_type = 'PDF'
        elif ext in ['.epub']:
            file_type = 'EPUB'
        elif ext in ['.cbz']:
            file_type = 'CBZ'
        elif ext in ['.cbr']:
            file_type = 'CBR'
        elif ext in ['.mobi']:
            file_type = 'MOBI'
        elif ext in ['.azw', '.azw3']:
            file_type = 'AZW'
        else:
            file_type = ext.lstrip('.')
    
    # Check if the file is already in a managed location
    from backend.internals.settings import Settings
    from backend.base.helpers import get_safe_folder_name as safe_folder_name
    settings = Settings().get_settings()
    root_folders = settings.root_folders
    
    # Get the series info for folder name comparison
    series_info = execute_query("SELECT title FROM series WHERE id = ?", (series_id,))
    if not series_info:
        LOGGER.error(f"Series with ID {series_id} not found")
        return {}
    
    series_title = series_info[0]['title']
    safe_series_title = safe_folder_name(series_title)
    
    # Check if the file is already in a managed location
    is_already_managed = False
    file_in_correct_location = False
    
    # Convert source_path to absolute path
    source_path_abs = source_path.absolute()
    LOGGER.info(f"Checking if file is already managed: {source_path_abs}")
    
    # Special case: if the source path contains the series name, consider it already managed
    if safe_series_title in str(source_path_abs):
        is_already_managed = True
        file_in_correct_location = True
        LOGGER.info(f"File is already in a folder with the series name: {source_path_abs}")
    else:
        # Check if file is in any root folder
        for root_folder in root_folders:
            root_path = Path(root_folder['path'])
            if str(source_path_abs).startswith(str(root_path)):
                # File is in a managed root folder
                is_already_managed = True
                
                # Check if it's in the correct series folder
                expected_series_path = root_path / safe_series_title
                if str(source_path_abs).startswith(str(expected_series_path)):
                    file_in_correct_location = True
                    LOGGER.info(f"File is already in the correct location: {source_path_abs}")
                    break
    
    if is_already_managed and file_in_correct_location:
        # Use the existing file path without copying
        target_path = source_path_abs
        unique_file_name = source_path.name
        LOGGER.info(f"Using existing file in managed location: {target_path}")
    else:
        # Generate a unique filename to prevent overwriting
        unique_file_name = file_name  # Use original filename without timestamp
        
        # Organize the file path
        target_path = organize_ebook_path(series_id, volume_id, unique_file_name)
        
        # Copy the file to the storage location if it's not already there
        if source_path_abs != target_path:
            LOGGER.info(f"Copying file from {source_path_abs} to {target_path}")
            if not copy_file_to_storage(source_path, target_path):
                LOGGER.error(f"Failed to copy file: {file_path}")
                return {}
        else:
            LOGGER.info(f"File is already at target path: {target_path}")

    
    # Start retry loop for database operations
    while retries <= max_retries:
        try:
            # Add file to the database
            try:
                # First try with RETURNING id
                result = execute_query("""
                INSERT INTO ebook_files (
                    series_id, volume_id, file_path, file_name, file_size,
                    file_type, original_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                RETURNING id
                """, (
                    series_id,
                    volume_id,
                    str(target_path),
                    unique_file_name,
                    file_size,
                    file_type,
                    file_name
                ), commit=True)
                
                # Get the inserted ID
                if result and len(result) > 0:
                    file_id = result[0]['id']
                    # Get the created file
                    file_info = get_ebook_file(file_id)
                else:
                    # If RETURNING id didn't work, get the last inserted ID
                    LOGGER.info(f"RETURNING id didn't work, trying to get last_insert_rowid() for: {target_path}")
                    last_id_result = execute_query("SELECT last_insert_rowid() as id")
                    if last_id_result and len(last_id_result) > 0:
                        file_id = last_id_result[0]['id']
                        file_info = get_ebook_file(file_id)
                    else:
                        LOGGER.error(f"Failed to get ID for inserted file: {target_path}")
                        file_info = None
            except Exception as e:
                LOGGER.error(f"Error during file insertion: {e}")
                # Try a simpler insert without RETURNING
                execute_query("""
                INSERT INTO ebook_files (
                    series_id, volume_id, file_path, file_name, file_size,
                    file_type, original_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    series_id,
                    volume_id,
                    str(target_path),
                    unique_file_name,
                    file_size,
                    file_type,
                    file_name
                ), commit=True)
                
                # Get the last inserted ID
                last_id_result = execute_query("SELECT last_insert_rowid() as id")
                if last_id_result and len(last_id_result) > 0:
                    file_id = last_id_result[0]['id']
                    file_info = get_ebook_file(file_id)
                else:
                    LOGGER.error(f"Failed to get ID for inserted file after fallback: {target_path}")
                    file_info = None
            
            if file_info:
                # Update the collection item to link to this file
                execute_query("""
                UPDATE collection_items 
                SET has_file = 1, ebook_file_id = ?,
                    digital_format = ?,
                    format = CASE
                        WHEN format = 'PHYSICAL' THEN 'BOTH'
                        ELSE 'DIGITAL'
                    END
                WHERE series_id = ? AND volume_id = ? AND item_type = 'VOLUME'
                """, (file_id, file_type, series_id, volume_id), commit=True)
            
            return file_info
        
        except Exception as e:
            if "database is locked" in str(e) and retries < max_retries:
                retries += 1
                LOGGER.warning(f"Database locked while adding e-book file, retrying ({retries}/{max_retries}) in {retry_delay}s")
                time.sleep(retry_delay)
                retry_delay *= 1.5
            else:
                LOGGER.error(f"Error adding e-book file: {e}")
                return {}
    
    LOGGER.error(f"Failed to add e-book file after {max_retries} retries")
    return {}
