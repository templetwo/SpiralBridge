import os
from datetime import datetime


def archive_conversation(content, platform):
    """
    Archives conversation content to a platform-specific directory with timestamp-based filename.
    
    Args:
        content (str): The content to archive
        platform (str): The platform name (e.g., 'discord', 'slack', 'teams')
    
    Returns:
        str: The filepath where the content was saved
    """
    # Generate timestamp in format YYYYMMDD_HHMMSS
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create platform-specific directory path
    directory = f"memory_logs/{platform}"
    
    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)
    
    # Generate filename with session prefix and timestamp
    filename = f"session-{timestamp}.txt"
    filepath = os.path.join(directory, filename)
    
    # Write content to file
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(content)
    
    return filepath


# Example usage:
if __name__ == "__main__":
    # Test the function
    test_content = "This is a test conversation content\nWith multiple lines\nFor archiving purposes"
    test_platform = "discord"
    
    saved_path = archive_conversation(test_content, test_platform)
    print(f"Content archived to: {saved_path}")
