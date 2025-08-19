import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
import time
import datetime
import sys
import os
import re
from local_memory_system import LocalMemorySystem

def get_platform_error_message(platform, error):
    """Get platform-specific error messages."""
    error_str = str(error).lower()
    
    if platform == 'claude':
        if 'timeout' in error_str:
            return "Claude Error: Page took too long to load. Claude may be experiencing high traffic or the shared link may be invalid."
        elif 'element not found' in error_str or 'no such element' in error_str:
            return "Claude Error: Could not find conversation content. The shared link may be private or expired."
        elif 'connection' in error_str or 'network' in error_str:
            return "Claude Error: Network connection issue. Please check your internet connection and try again."
        elif 'cloudflare' in error_str or 'protection' in error_str:
            return "Claude Error: Bot detection triggered. Try again in a few minutes or use a different network."
        else:
            return f"Claude Error: {error}"
    
    elif platform == 'gemini':
        if 'timeout' in error_str:
            return "Gemini Error: Page load timeout. Google services may be slow or the shared link may be invalid."
        elif 'element not found' in error_str or 'no such element' in error_str:
            return "Gemini Error: Could not locate conversation content. The shared link may be private, expired, or require sign-in."
        elif 'connection' in error_str or 'network' in error_str:
            return "Gemini Error: Network connectivity issue. Check your connection and try again."
        elif 'access denied' in error_str or 'forbidden' in error_str:
            return "Gemini Error: Access denied. The conversation may be private or require Google account sign-in."
        else:
            return f"Gemini Error: {error}"
    
    elif platform == 'chatgpt':
        if 'timeout' in error_str:
            return "ChatGPT Error: Page load timeout. OpenAI servers may be busy or the shared link may be invalid."
        elif 'element not found' in error_str or 'no such element' in error_str:
            return "ChatGPT Error: Could not find conversation content. The shared link may be private or expired."
        elif 'connection' in error_str or 'network' in error_str:
            return "ChatGPT Error: Network connection problem. Please verify your internet connection."
        elif 'rate limit' in error_str or 'too many requests' in error_str:
            return "ChatGPT Error: Rate limit exceeded. Please wait a few minutes before trying again."
        else:
            return f"ChatGPT Error: {error}"
    
    elif platform == 'warp':
        if 'timeout' in error_str:
            return "Warp Error: Session load timeout. The session may be expired or you may need to sign in."
        elif 'element not found' in error_str or 'no such element' in error_str:
            return "Warp Error: Could not find session content. The session may be private, expired, or require authentication."
        elif 'connection' in error_str or 'network' in error_str:
            return "Warp Error: Network connectivity issue. Check your connection and try again."
        elif 'access denied' in error_str or 'forbidden' in error_str or 'authentication' in error_str:
            return "Warp Error: Access denied. The session may require sign-in or may be private."
        elif 'javascript' in error_str:
            return "Warp Error: JavaScript execution required. The session content couldn't be loaded properly."
        else:
            return f"Warp Error: {error}"
    
    else:
        return f"Unknown Platform Error: {error}"

def print_progress(message, step=None, total_steps=None):
    """Print progress indicator with optional step counter."""
    if step and total_steps:
        progress_bar = '█' * int((step / total_steps) * 20)
        empty_bar = '░' * (20 - int((step / total_steps) * 20))
        percentage = int((step / total_steps) * 100)
        print(f"[{progress_bar}{empty_bar}] {percentage}% - {message}")
    else:
        print(f"⏳ {message}")

def scrape_with_retry(scraping_function, browser, url, platform, timeout=20, max_attempts=3):
    """Generic retry wrapper for scraping functions with platform-specific error handling."""
    print_progress(f"Starting {platform.upper()} scraping", 1, 4)
    
    for attempt in range(1, max_attempts + 1):
        try:
            print_progress(f"Attempt {attempt}/{max_attempts} - Loading {platform.upper()} page", 2, 4)
            
            # Call the actual scraping function
            result = scraping_function(browser, url, timeout)
            
            if result:
                print_progress(f"Successfully scraped content from {platform.upper()}", 4, 4)
                return result
            else:
                print(f"⚠️  Attempt {attempt}: No content found")
                if attempt < max_attempts:
                    print(f"🔄 Retrying in 2 seconds...")
                    time.sleep(2)
                    
        except TimeoutException as e:
            error_msg = get_platform_error_message(platform, e)
            print(f"❌ Attempt {attempt}: {error_msg}")
            if attempt < max_attempts:
                print(f"🔄 Retrying in 3 seconds...")
                time.sleep(3)
            
        except (NoSuchElementException, WebDriverException) as e:
            error_msg = get_platform_error_message(platform, e)
            print(f"❌ Attempt {attempt}: {error_msg}")
            if attempt < max_attempts:
                print(f"🔄 Retrying in 2 seconds...")
                time.sleep(2)
                
        except Exception as e:
            error_msg = get_platform_error_message(platform, e)
            print(f"❌ Attempt {attempt}: {error_msg}")
            if attempt < max_attempts:
                print(f"🔄 Retrying in 2 seconds...")
                time.sleep(2)
    
    print(f"❌ All {max_attempts} attempts failed for {platform.upper()}")
    return None

def initialize_driver():
    """Initialize the Chrome browser with undetected_chromedriver."""
    print_progress("Initializing Chrome browser")
    
    try:
        options = uc.ChromeOptions()
        
        # Chrome binary paths to try on macOS
        chrome_paths = [
            '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
            '/Applications/Chrome.app/Contents/MacOS/Chrome',
            '/usr/bin/google-chrome',
            '/usr/local/bin/google-chrome'
        ]
        
        # Try to find Chrome binary
        chrome_binary = None
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_binary = path
                break
        
        # Set Chrome binary if found
        if chrome_binary:
            options.binary_location = chrome_binary
            print(f"🔍 Found Chrome at: {chrome_binary}")
        else:
            print("⚠️  Chrome not found in standard locations, trying default...")
        
        # Simplified Chrome options for better compatibility
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Skip experimental options that cause issues with newer Chrome versions
        
        # Try to initialize the driver
        driver = uc.Chrome(options=options)
        print("✅ Browser initialized successfully")
        return driver
        
    except Exception as e:
        error_msg = str(e)
        if "Binary Location Must be a String" in error_msg or "chrome" in error_msg.lower():
            print("❌ Chrome browser not found or not properly installed.")
            print("💡 To fix this issue:")
            print("   1. Install Google Chrome from: https://www.google.com/chrome/")
            print("   2. Or install Chromium as an alternative")
            print("   3. Make sure Chrome is in /Applications/Google Chrome.app/")
            raise Exception("Chrome browser is required but not found. Please install Google Chrome.")
        else:
            print(f"❌ Browser initialization failed: {error_msg}")
            raise Exception(f"Failed to initialize browser: {error_msg}")

def scrape_claude_content(browser, url, timeout=20):
    """Scrape content from Claude shared link."""
    try:
        browser.get(url)
        time.sleep(timeout)

        content = browser.find_element(By.TAG_NAME, 'body').text
        if content and content.strip():
            return content
        else:
            return None

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def scrape_claude_conversation(browser, url, timeout=20):
    """Scrape and clean Claude conversation content.
    
    Args:
        browser: Selenium WebDriver instance
        url: Claude shared conversation URL
        timeout: Wait time in seconds (default: 20)
        
    Returns:
        str: Cleaned conversation text, or None if scraping failed
    """
    try:
        browser.get(url)
        time.sleep(timeout)

        content = browser.find_element(By.TAG_NAME, 'body').text
        if not content or not content.strip():
            return None
            
        # Claude-specific content cleaning
        start_marker = "Files hidden in shared chats"
        end_marker = "Start your own conversation"

        start_index = content.find(start_marker)
        if start_index != -1:
            content_after_header = content[start_index + len(start_marker):].lstrip()
        else:
            content_after_header = content

        end_index = content_after_header.rfind(end_marker)
        if end_index != -1:
            cleaned_content = content_after_header[:end_index].rstrip()
        else:
            cleaned_content = content_after_header
        
        return cleaned_content

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def scrape_gemini_content(browser, url, timeout=20):
    """Scrape content from Gemini shared link."""
    try:
        browser.get(url)
        time.sleep(timeout)

        content = browser.find_element(By.TAG_NAME, 'body').text
        if content and content.strip():
            return content
        else:
            return None

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def scrape_gemini_conversation(browser, url, timeout=20):
    """Scrape and clean Gemini conversation content.
    
    Args:
        browser: Selenium WebDriver instance
        url: Gemini shared conversation URL
        timeout: Wait time in seconds (default: 20)
        
    Returns:
        str: Cleaned conversation text, or None if scraping failed
    """
    try:
        browser.get(url)
        time.sleep(timeout)
        
        # Wait for the page to fully load by checking for specific Gemini elements
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        wait = WebDriverWait(browser, timeout)
        
        # Try multiple selectors to identify Gemini conversation content
        conversation_selectors = [
            '[data-testid="conversation-turn"]',  # Common Gemini conversation selector
            '.conversation-turn',
            '[role="main"] .message',
            '.chat-message',
            '.turn-container',
            '[data-message-author-role]'
        ]
        
        conversation_elements = []
        for selector in conversation_selectors:
            try:
                elements = browser.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    conversation_elements = elements
                    break
            except:
                continue
        
        # If specific conversation elements found, extract from them
        if conversation_elements:
            conversation_text = []
            for element in conversation_elements:
                try:
                    # Try to identify if it's a user or assistant message
                    element_text = element.text.strip()
                    if element_text:
                        # Check for role indicators
                        role_element = element.find_element(By.CSS_SELECTOR, '[data-message-author-role]') if element.find_elements(By.CSS_SELECTOR, '[data-message-author-role]') else None
                        if role_element:
                            role = role_element.get_attribute('data-message-author-role')
                            if role == 'user':
                                conversation_text.append(f"User: {element_text}")
                            elif role == 'assistant':
                                conversation_text.append(f"Gemini: {element_text}")
                            else:
                                conversation_text.append(element_text)
                        else:
                            conversation_text.append(element_text)
                except:
                    # Fallback to just getting text
                    try:
                        text = element.text.strip()
                        if text:
                            conversation_text.append(text)
                    except:
                        continue
            
            if conversation_text:
                content = '\n\n'.join(conversation_text)
            else:
                # Fallback to full body text
                content = browser.find_element(By.TAG_NAME, 'body').text
        else:
            # Fallback to full body text
            content = browser.find_element(By.TAG_NAME, 'body').text
        
        if not content or not content.strip():
            return None
            
        # Gemini-specific content cleaning
        cleaned_content = clean_gemini_conversation_content(content)
        
        return cleaned_content

    except Exception as e:
        print(f"An error occurred while scraping Gemini conversation: {str(e)}")
        return None

def clean_gemini_conversation_content(content):
    """Clean Gemini-specific content markers and formatting.
    
    Args:
        content: Raw scraped content from Gemini
        
    Returns:
        str: Cleaned conversation content
    """
    if not content:
        return content
    
    # Common Gemini header/footer markers to remove
    gemini_markers = [
        "Gemini Apps",
        "Try Gemini Advanced",
        "New chat",
        "Gemini can make mistakes",
        "Privacy & Terms",
        "Your conversations with Bard",
        "Export & Share",
        "Bard may display inaccurate info",
        "Sign in to save your chats",
        "Welcome to Bard",
        "Hi! I'm Bard",
        "View other drafts",
        "Share & export",
        "Share this chat",
        "Copy link",
        "Export to Docs",
        "Export to Gmail",
        "Made by Google",
        "Help improve Bard",
        "Bard is experimental"
    ]
    
    # Remove common UI elements and navigation
    lines = content.split('\n')
    cleaned_lines = []
    
    skip_next_lines = 0
    for i, line in enumerate(lines):
        if skip_next_lines > 0:
            skip_next_lines -= 1
            continue
            
        line_stripped = line.strip()
        
        # Skip empty lines at the beginning
        if not cleaned_lines and not line_stripped:
            continue
            
        # Skip lines that are just UI elements
        if any(marker.lower() in line_stripped.lower() for marker in gemini_markers):
            continue
            
        # Skip navigation elements
        if line_stripped in ['Menu', 'Close', 'Share', 'Export', 'New', '+', '⋮', '•']:
            continue
            
        # Skip very short lines that are likely UI elements
        if len(line_stripped) <= 2 and line_stripped.isalpha():
            continue
            
        # Skip lines with only special characters or numbers
        if line_stripped and all(c in '.,!?;:-()[]{}"\'/\\|_=+*&^%$#@~`' for c in line_stripped):
            continue
            
        # Skip timestamp-like patterns
        if re.match(r'^\d{1,2}:\d{2}\s*(AM|PM)?$', line_stripped, re.IGNORECASE):
            continue
            
        # Skip date-like patterns
        if re.match(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}$', line_stripped, re.IGNORECASE):
            continue
            
        cleaned_lines.append(line)
    
    # Join back and clean up extra whitespace
    cleaned_content = '\n'.join(cleaned_lines)
    
    # Remove excessive blank lines
    cleaned_content = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_content)
    
    # Clean up beginning and end
    cleaned_content = cleaned_content.strip()
    
    return cleaned_content

def scrape_chatgpt_content(browser, url, timeout=20):
    """Scrape content from ChatGPT shared link."""
    try:
        browser.get(url)
        time.sleep(timeout)

        content = browser.find_element(By.TAG_NAME, 'body').text
        if content and content.strip():
            return content
        else:
            return None

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def scrape_chatgpt_conversation(browser, url, timeout=20):
    """Scrape and clean ChatGPT conversation content.
    
    Args:
        browser: Selenium WebDriver instance
        url: ChatGPT shared conversation URL
        timeout: Wait time in seconds (default: 20)
        
    Returns:
        str: Cleaned conversation text, or None if scraping failed
    """
    try:
        browser.get(url)
        time.sleep(timeout)
        
        # Wait for the page to fully load by checking for specific ChatGPT elements
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        wait = WebDriverWait(browser, timeout)
        
        # Try multiple selectors to identify ChatGPT conversation content
        conversation_selectors = [
            '[data-message-author-role]',  # Main ChatGPT message selector
            '.conversation-content .message',  # Alternative message selector
            '[role="article"]',  # ChatGPT uses article role for messages
            '.flex.flex-col.items-start',  # Common ChatGPT message container
            '.group.w-full',  # Another common ChatGPT message wrapper
            '.text-base',  # Basic text content selector
            '[data-testid*="conversation"]',  # Generic conversation test ID
            '.markdown.prose',  # Markdown content in messages
        ]
        
        conversation_elements = []
        for selector in conversation_selectors:
            try:
                elements = browser.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    conversation_elements = elements
                    break
            except:
                continue
        
        # If specific conversation elements found, extract from them
        if conversation_elements:
            conversation_text = []
            for element in conversation_elements:
                try:
                    # Try to identify if it's a user or assistant message
                    element_text = element.text.strip()
                    if element_text:
                        # Check for role indicators in ChatGPT
                        role_element = None
                        if element.find_elements(By.CSS_SELECTOR, '[data-message-author-role]'):
                            role_element = element.find_element(By.CSS_SELECTOR, '[data-message-author-role]')
                        
                        if role_element:
                            role = role_element.get_attribute('data-message-author-role')
                            if role == 'user':
                                conversation_text.append(f"User: {element_text}")
                            elif role == 'assistant':
                                conversation_text.append(f"ChatGPT: {element_text}")
                            else:
                                conversation_text.append(element_text)
                        else:
                            # Try to detect role from parent elements or context
                            parent_classes = element.get_attribute('class') or ''
                            parent_element = element.find_element(By.XPATH, '..')
                            parent_classes += ' ' + (parent_element.get_attribute('class') or '')
                            
                            # Look for ChatGPT-specific role indicators
                            if 'user' in parent_classes.lower() or 'human' in parent_classes.lower():
                                conversation_text.append(f"User: {element_text}")
                            elif 'assistant' in parent_classes.lower() or 'gpt' in parent_classes.lower() or 'ai' in parent_classes.lower():
                                conversation_text.append(f"ChatGPT: {element_text}")
                            else:
                                # Try to infer from content patterns
                                if element_text.startswith(('You:', 'User:', 'Human:')):
                                    conversation_text.append(element_text)
                                elif element_text.startswith(('ChatGPT:', 'Assistant:', 'AI:')):
                                    conversation_text.append(element_text)
                                else:
                                    conversation_text.append(element_text)
                except:
                    # Fallback to just getting text
                    try:
                        text = element.text.strip()
                        if text:
                            conversation_text.append(text)
                    except:
                        continue
            
            if conversation_text:
                content = '\n\n'.join(conversation_text)
            else:
                # Fallback to full body text
                content = browser.find_element(By.TAG_NAME, 'body').text
        else:
            # Fallback to full body text
            content = browser.find_element(By.TAG_NAME, 'body').text
        
        if not content or not content.strip():
            return None
            
        # ChatGPT-specific content cleaning
        cleaned_content = clean_chatgpt_conversation_content(content)
        
        return cleaned_content

    except Exception as e:
        print(f"An error occurred while scraping ChatGPT conversation: {str(e)}")
        return None

def detect_platform(url):
    """Detect the platform based on URL pattern.
    
    Args:
        url: The URL to check
        
    Returns:
        str: Platform name ('claude', 'gemini', 'chatgpt', 'warp') or None for unrecognized URLs
    """
    url = url.lower()
    
    if 'claude.ai' in url:
        return 'claude'
    elif 'gemini.google.com' in url or 'g.co' in url or 'bard.google.com' in url:
        return 'gemini'
    elif 'chat.openai.com' in url or 'chatgpt.com' in url:
        return 'chatgpt'
    elif 'app.warp.dev' in url:
        return 'warp'
    else:
        return None

def ensure_platform_directory(platform):
    """Create platform-specific directory under memory_logs/ if it doesn't exist."""
    base_dir = "memory_logs"
    platform_dir = os.path.join(base_dir, platform)
    
    # Create base directory if it doesn't exist
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    # Create platform-specific directory if it doesn't exist
    if not os.path.exists(platform_dir):
        os.makedirs(platform_dir)
        print(f"Created directory: {platform_dir}")
    
    return platform_dir

def print_usage():
    """Print usage information."""
    print("SpiralBridge - Multi-platform AI conversation scraper")
    print("")
    print("Usage:")
    print("  python spiralbridge.py [URL]")
    print("  python spiralbridge.py --help")
    print("")
    print("If no URL is provided, you will be prompted to enter one.")
    print("")
    print("Supported platforms:")
    print("  - Claude: claude.ai")
    print("  - Gemini: gemini.google.com")
    print("  - ChatGPT: chat.openai.com, chatgpt.com")
    print("  - Warp: app.warp.dev")
    print("")
    print("Examples:")
    print("  python spiralbridge.py https://claude.ai/share/12345")
    print("  python spiralbridge.py https://gemini.google.com/share/abc123")
    print("  python spiralbridge.py https://chat.openai.com/share/xyz789")
    print("  python spiralbridge.py https://app.warp.dev/session/abc123")

def get_url_input():
    """Get URL from command-line argument or user input."""
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ['--help', '-h', 'help']:
            print_usage()
            return None
        return arg
    else:
        return input("Enter the URL to scrape: ").strip()

def clean_claude_content(content):
    """Clean Claude-specific content markers."""
    start_marker = "Files hidden in shared chats"
    end_marker = "Start your own conversation"

    start_index = content.find(start_marker)
    if start_index != -1:
        content_after_header = content[start_index + len(start_marker):].lstrip()
    else:
        content_after_header = content

    end_index = content_after_header.rfind(end_marker)
    if end_index != -1:
        cleaned_content = content_after_header[:end_index].rstrip()
    else:
        cleaned_content = content_after_header
    
    return cleaned_content

def clean_gemini_content(content):
    """Clean Gemini-specific content markers."""
    # Add Gemini-specific cleaning logic here
    # For now, return content as-is
    return content

def clean_chatgpt_content(content):
    """Clean ChatGPT-specific content markers."""
    # Add ChatGPT-specific cleaning logic here
    # For now, return content as-is
    return content

def scrape_warp_content(browser, url, timeout=30):
    """Scrape content from Warp session link."""
    try:
        browser.get(url)
        # Longer timeout for JavaScript-heavy Warp sessions
        time.sleep(timeout)

        content = browser.find_element(By.TAG_NAME, 'body').text
        if content and content.strip():
            return content
        else:
            return None

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def scrape_warp_conversation(browser, url, timeout=30):
    """Scrape and clean Warp session content.
    
    Args:
        browser: Selenium WebDriver instance
        url: Warp session URL
        timeout: Wait time in seconds (default: 30 for JS-heavy content)
        
    Returns:
        str: Cleaned session text, or None if scraping failed
    """
    try:
        browser.get(url)
        # Wait longer for JavaScript to load
        time.sleep(timeout)
        
        # Wait for the page to fully load by checking for specific Warp elements
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        wait = WebDriverWait(browser, timeout)
        
        # Try multiple selectors to identify Warp session content
        session_selectors = [
            '[data-testid*="terminal"]',  # Terminal content
            '.terminal-content',  # Terminal session content
            '.xterm-screen',  # XTerm terminal screen
            '.session-content',  # Session content container
            '[class*="terminal"]',  # Any class containing "terminal"
            '[class*="session"]',  # Any class containing "session"
            'pre',  # Pre-formatted text (common for terminal output)
            '.warp-terminal',  # Warp-specific terminal class
            '[data-warp*="terminal"]',  # Warp data attributes
            '.command-line',  # Command line elements
            '.output',  # Command output
        ]
        
        session_elements = []
        for selector in session_selectors:
            try:
                elements = browser.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    session_elements = elements
                    break
            except:
                continue
        
        # If specific session elements found, extract from them
        if session_elements:
            session_text = []
            for element in session_elements:
                try:
                    element_text = element.text.strip()
                    if element_text:
                        # Check if this looks like terminal content
                        if any(marker in element_text.lower() for marker in ['$', '>', '#', 'command', 'output', 'terminal']):
                            session_text.append(f"Terminal: {element_text}")
                        else:
                            session_text.append(element_text)
                except:
                    # Fallback to just getting text
                    try:
                        text = element.text.strip()
                        if text:
                            session_text.append(text)
                    except:
                        continue
            
            if session_text:
                content = '\n\n'.join(session_text)
            else:
                # Fallback to full body text if no specific elements found
                content = browser.find_element(By.TAG_NAME, 'body').text
        else:
            # Fallback to full body text
            content = browser.find_element(By.TAG_NAME, 'body').text
        
        if not content or not content.strip():
            return None
            
        # Warp-specific content cleaning
        cleaned_content = clean_warp_conversation_content(content)
        
        return cleaned_content

    except Exception as e:
        print(f"An error occurred while scraping Warp session: {str(e)}")
        return None

def clean_warp_conversation_content(content):
    """Clean Warp-specific content markers and formatting.
    
    Args:
        content: Raw scraped content from Warp
        
    Returns:
        str: Cleaned session content
    """
    if not content:
        return content
    
    # Common Warp/terminal header/footer markers to remove
    warp_markers = [
        "You need to enable JavaScript",
        "Warp Terminal",
        "Sign in to Warp",
        "Create account",
        "Download Warp",
        "Privacy Policy",
        "Terms of Service",
        "Made by Warp",
        "Warp Drive",
        "Settings",
        "Preferences",
        "Help",
        "Feedback",
        "Share session",
        "Copy link",
        "Export session",
        "New terminal",
        "Close tab",
        "Warp AI",
        "Command palette",
        "Theme",
        "Font size"
    ]
    
    # Remove common UI elements and navigation
    lines = content.split('\n')
    cleaned_lines = []
    
    skip_next_lines = 0
    for i, line in enumerate(lines):
        if skip_next_lines > 0:
            skip_next_lines -= 1
            continue
            
        line_stripped = line.strip()
        
        # Skip empty lines at the beginning
        if not cleaned_lines and not line_stripped:
            continue
            
        # Skip lines that are just UI elements
        if any(marker.lower() in line_stripped.lower() for marker in warp_markers):
            continue
            
        # Skip navigation elements
        if line_stripped in ['Menu', 'Close', 'Share', 'Export', 'New', '+', '⋮', '•', '⚙️', '🎨', '📊']:
            continue
            
        # Skip very short lines that are likely UI elements
        if len(line_stripped) <= 2 and line_stripped.isalpha():
            continue
            
        # Skip lines with only special characters or numbers
        if line_stripped and all(c in '.,!?;:-()[]{}"\'/\\|_=+*&^%$#@~`' for c in line_stripped):
            continue
            
        # Skip timestamp-like patterns
        if re.match(r'^\d{1,2}:\d{2}\s*(AM|PM)?$', line_stripped, re.IGNORECASE):
            continue
            
        # Skip date-like patterns
        if re.match(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}$', line_stripped, re.IGNORECASE):
            continue
            
        # Skip Warp-specific UI patterns
        if line_stripped.lower() in ['warp', 'terminal', 'session', 'tab', 'workspace']:
            continue
            
        # Skip JavaScript error messages
        if 'javascript' in line_stripped.lower() and ('enable' in line_stripped.lower() or 'required' in line_stripped.lower()):
            continue
            
        # Skip generic browser messages
        if line_stripped.lower() in ['loading...', 'please wait', 'connecting...', 'establishing connection']:
            continue
            
        cleaned_lines.append(line)
    
    # Join back and clean up extra whitespace
    cleaned_content = '\n'.join(cleaned_lines)
    
    # Remove excessive blank lines
    cleaned_content = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_content)
    
    # Clean up beginning and end
    cleaned_content = cleaned_content.strip()
    
    # Additional Warp-specific cleaning
    # If content is just JavaScript warning, indicate this
    if len(cleaned_content) < 100 and ('javascript' in cleaned_content.lower() or len(cleaned_content.strip()) == 0):
        # Check if the original content was a JavaScript warning
        if content and 'javascript' in content.lower() and 'enable' in content.lower():
            cleaned_content = f"Warp Session Access Limited: {content.strip()}\n\nNote: This Warp session requires JavaScript and may need authentication to access terminal content."
        elif len(cleaned_content.strip()) == 0 and content and len(content.strip()) > 0:
            # Content was completely filtered out, might be all UI elements
            cleaned_content = "Warp Session Access Limited: No accessible content found.\n\nNote: This Warp session may be private, expired, or require authentication to access terminal content."
    
    return cleaned_content

def extract_conversation_from_url(url, timeout=20, max_attempts=3):
    """Extract conversation content from a URL with automatic platform detection.
    
    Args:
        url: The conversation URL to scrape
        timeout: Wait time in seconds (default: 20)
        max_attempts: Number of retry attempts (default: 3)
        
    Returns:
        dict: Result containing success status, platform, content, and metadata
    """
    result = {
        'success': False,
        'platform': None,
        'content': None,
        'metadata': {},
        'error': None
    }
    
    try:
        # Detect platform
        platform = detect_platform(url)
        if not platform:
            result['error'] = 'Unsupported platform'
            return result
        
        result['platform'] = platform
        
        # Initialize browser
        browser = None
        try:
            browser = initialize_driver()
            
            # Select appropriate scraping function
            scraping_functions = {
                'claude': scrape_claude_conversation,
                'gemini': scrape_gemini_conversation,
                'chatgpt': scrape_chatgpt_conversation,
                'warp': scrape_warp_conversation
            }
            
            scraping_function = scraping_functions.get(platform)
            if not scraping_function:
                result['error'] = f'Scraping for {platform} is not implemented'
                return result
            
            # Use longer timeout for Warp (JavaScript-heavy)
            actual_timeout = 30 if platform == 'warp' else timeout
            
            # Perform scraping with retry logic
            content = scrape_with_retry(
                scraping_function, browser, url, platform, 
                actual_timeout, max_attempts
            )
            
            if content:
                result['success'] = True
                result['content'] = content
                result['metadata'] = {
                    'url': url,
                    'platform': platform,
                    'scraped_at': datetime.datetime.now().isoformat(),
                    'content_length': len(content),
                    'word_count': len(content.split()),
                    'line_count': len(content.split('\n'))
                }
            else:
                result['error'] = f'Could not extract content from {platform.upper()} URL after {max_attempts} attempts'
                
        except Exception as scrape_error:
            result['error'] = get_platform_error_message(platform, scrape_error)
            
        finally:
            if browser:
                try:
                    browser.quit()
                except:
                    pass
                    
    except Exception as e:
        result['error'] = f'Unexpected error: {str(e)}'
    
    return result

def chunk_conversation(content, chunk_size=4000, overlap=200, preserve_speakers=True):
    """Split conversation content into manageable chunks for processing.
    
    Args:
        content: The conversation content to chunk
        chunk_size: Maximum size of each chunk in characters (default: 4000)
        overlap: Number of characters to overlap between chunks (default: 200)
        preserve_speakers: Whether to try to preserve speaker boundaries (default: True)
        
    Returns:
        list: List of content chunks with metadata
    """
    if not content or len(content) <= chunk_size:
        return [{
            'chunk_index': 0,
            'content': content,
            'metadata': {
                'total_chunks': 1,
                'chunk_size': len(content) if content else 0,
                'is_complete': True
            }
        }]
    
    chunks = []
    lines = content.split('\n')
    current_chunk = ''
    current_chunk_lines = []
    
    # Common speaker patterns for different platforms
    speaker_patterns = [
        r'^(User|Human|You):\s*',
        r'^(Assistant|AI|Claude|Gemini|ChatGPT|GPT|Warp):\s*',
        r'^(\*\*User\*\*|\*\*Assistant\*\*):\s*',
        r'^\d+\s*\|\s*(User|Assistant):\s*',
    ]
    
    def is_speaker_line(line):
        """Check if a line starts with a speaker indicator."""
        if not preserve_speakers:
            return False
        line_stripped = line.strip()
        return any(re.match(pattern, line_stripped, re.IGNORECASE) for pattern in speaker_patterns)
    
    def finalize_chunk(chunk_lines, chunk_index):
        """Create a chunk from the accumulated lines."""
        chunk_content = '\n'.join(chunk_lines)
        return {
            'chunk_index': chunk_index,
            'content': chunk_content,
            'metadata': {
                'chunk_size': len(chunk_content),
                'line_count': len(chunk_lines),
                'starts_with_speaker': is_speaker_line(chunk_lines[0]) if chunk_lines else False,
                'ends_with_speaker': is_speaker_line(chunk_lines[-1]) if chunk_lines else False
            }
        }
    
    chunk_index = 0
    i = 0
    
    while i < len(lines):
        line = lines[i]
        potential_chunk = current_chunk + ('\n' if current_chunk else '') + line
        
        # If adding this line would exceed chunk size
        if len(potential_chunk) > chunk_size and current_chunk:
            # If we're preserving speakers and this line starts a new speaker turn,
            # finalize the current chunk here to keep speaker turns together
            if preserve_speakers and is_speaker_line(line) and current_chunk_lines:
                chunks.append(finalize_chunk(current_chunk_lines, chunk_index))
                chunk_index += 1
                
                # Start new chunk with overlap from previous chunk
                if overlap > 0 and current_chunk_lines:
                    overlap_text = '\n'.join(current_chunk_lines[-3:])  # Last 3 lines for context
                    if len(overlap_text) <= overlap:
                        current_chunk = overlap_text
                        current_chunk_lines = current_chunk_lines[-3:]
                    else:
                        current_chunk = ''
                        current_chunk_lines = []
                else:
                    current_chunk = ''
                    current_chunk_lines = []
            
            # If line itself is too long, split it
            elif len(line) > chunk_size:
                # Finalize current chunk first
                if current_chunk_lines:
                    chunks.append(finalize_chunk(current_chunk_lines, chunk_index))
                    chunk_index += 1
                
                # Split the long line
                line_parts = [line[j:j+chunk_size] for j in range(0, len(line), chunk_size)]
                for part_index, part in enumerate(line_parts):
                    chunks.append({
                        'chunk_index': chunk_index,
                        'content': part,
                        'metadata': {
                            'chunk_size': len(part),
                            'line_count': 1,
                            'is_split_line': True,
                            'split_part': part_index + 1,
                            'total_split_parts': len(line_parts)
                        }
                    })
                    chunk_index += 1
                
                current_chunk = ''
                current_chunk_lines = []
                i += 1
                continue
            
            # Otherwise, finalize current chunk and start new one
            else:
                chunks.append(finalize_chunk(current_chunk_lines, chunk_index))
                chunk_index += 1
                
                # Start new chunk with overlap
                if overlap > 0 and current_chunk_lines:
                    overlap_text = '\n'.join(current_chunk_lines[-2:])  # Last 2 lines for context
                    if len(overlap_text) <= overlap:
                        current_chunk = overlap_text + '\n' + line
                        current_chunk_lines = current_chunk_lines[-2:] + [line]
                    else:
                        current_chunk = line
                        current_chunk_lines = [line]
                else:
                    current_chunk = line
                    current_chunk_lines = [line]
        else:
            # Line fits in current chunk
            current_chunk = potential_chunk
            current_chunk_lines.append(line)
        
        i += 1
    
    # Add final chunk if there's remaining content
    if current_chunk_lines:
        chunks.append(finalize_chunk(current_chunk_lines, chunk_index))
    
    # Add total chunk count to all chunks
    total_chunks = len(chunks)
    for chunk in chunks:
        chunk['metadata']['total_chunks'] = total_chunks
        chunk['metadata']['is_complete'] = (chunk['chunk_index'] == total_chunks - 1)
    
    return chunks

def clean_chatgpt_conversation_content(content):
    """Clean ChatGPT-specific conversation content markers and formatting.
    
    Args:
        content: Raw scraped content from ChatGPT
        
    Returns:
        str: Cleaned conversation content
    """
    if not content:
        return content
    
    # Common ChatGPT header/footer markers to remove
    chatgpt_markers = [
        "ChatGPT can make mistakes",
        "Try ChatGPT Plus",
        "New chat",
        "Upgrade to Plus",
        "Share this conversation",
        "Export conversation",
        "Made by OpenAI",
        "Privacy Policy",
        "Terms of Use",
        "ChatGPT Plus",
        "Get ChatGPT Plus",
        "Upgrade your plan",
        "Try ChatGPT-4",
        "ChatGPT-4 Turbo",
        "Sign up",
        "Log in",
        "Create account",
        "Continue conversation",
        "Regenerate response",
        "Copy code",
        "Try again",
        "Share & Export",
        "Download",
        "New conversation",
        "Clear conversations",
        "Settings",
        "Help & FAQ",
        "Updates & FAQ",
        "ChatGPT Mar 14 Version",
        "Free Research Preview",
        "Our goal is to make AI systems more natural",
        "Message ChatGPT…",
        "Send a message",
        "ChatGPT is a sibling model to InstructGPT"
    ]
    
    # Remove common UI elements and navigation
    lines = content.split('\n')
    cleaned_lines = []
    
    skip_next_lines = 0
    for i, line in enumerate(lines):
        if skip_next_lines > 0:
            skip_next_lines -= 1
            continue
            
        line_stripped = line.strip()
        
        # Skip empty lines at the beginning
        if not cleaned_lines and not line_stripped:
            continue
            
        # Skip lines that are just UI elements
        if any(marker.lower() in line_stripped.lower() for marker in chatgpt_markers):
            continue
            
        # Skip navigation elements
        if line_stripped in ['Menu', 'Close', 'Share', 'Export', 'New', '+', '⋮', '•', '↻', '✎', '📎', '⚙️']:
            continue
            
        # Skip very short lines that are likely UI elements
        if len(line_stripped) <= 2 and line_stripped.isalpha():
            continue
            
        # Skip lines with only special characters or numbers
        if line_stripped and all(c in '.,!?;:-()[]{}"\'/\\|_=+*&^%$#@~`' for c in line_stripped):
            continue
            
        # Skip timestamp-like patterns
        if re.match(r'^\d{1,2}:\d{2}\s*(AM|PM)?$', line_stripped, re.IGNORECASE):
            continue
            
        # Skip date-like patterns
        if re.match(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}$', line_stripped, re.IGNORECASE):
            continue
            
        # Skip ChatGPT-specific UI patterns
        if re.match(r'^\d+\s*/\s*\d+$', line_stripped):  # Message counts like "1 / 2"
            continue
            
        # Skip regenerate/retry indicators
        if line_stripped.lower() in ['regenerate response', 'try again', 'stop generating', 'continue generating']:
            continue
            
        # Skip model version indicators
        if re.match(r'^(gpt-\d+(\.\d+)?|chatgpt|gpt)$', line_stripped.lower()):
            continue
            
        # Skip generic copy/download buttons
        if line_stripped.lower() in ['copy', 'download', 'share', 'like', 'dislike', '👍', '👎']:
            continue
            
        # Skip subscription prompts
        if 'upgrade' in line_stripped.lower() and ('plan' in line_stripped.lower() or 'plus' in line_stripped.lower()):
            continue
            
        # Skip login/signup prompts
        if line_stripped.lower() in ['sign up', 'log in', 'sign in', 'get started', 'continue with google', 'continue with microsoft']:
            continue
            
        cleaned_lines.append(line)
    
    # Join back and clean up extra whitespace
    cleaned_content = '\n'.join(cleaned_lines)
    
    # Remove excessive blank lines
    cleaned_content = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_content)
    
    # Clean up beginning and end
    cleaned_content = cleaned_content.strip()
    
    # Additional ChatGPT-specific cleaning
    # Remove conversation metadata that might appear at the start
    if cleaned_content.startswith('ChatGPT'):
        lines = cleaned_content.split('\n')
        # Find first substantial content line
        start_idx = 0
        for i, line in enumerate(lines):
            if len(line.strip()) > 10 and not any(marker.lower() in line.lower() for marker in chatgpt_markers[:5]):
                start_idx = i
                break
        cleaned_content = '\n'.join(lines[start_idx:])
    
    return cleaned_content

def main():
    TIMEOUT = 20  # Increased timeout for better reliability
    MAX_ATTEMPTS = 3  # Number of retry attempts
    
    print("🌉 SpiralBridge - Multi-platform AI Conversation Scraper")
    print("=" * 60)
    
    # Initialize Local Memory System
    print_progress("Initializing Local Memory System")
    memory_system = LocalMemorySystem()
    print("🧠 Local Memory System initialized")
    
    # Get URL from command-line argument or user input
    url = get_url_input()
    
    if not url:
        # If url is None, it means help was displayed or no input provided
        if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
            return  # Help was displayed, exit gracefully
        print("❌ Error: No URL provided.")
        return
    
    # Detect platform from URL
    platform = detect_platform(url)
    
    if not platform:
        print(f"❌ Error: Unsupported platform. URL: {url}")
        print("📝 Supported platforms:")
        print("   • Claude: claude.ai")
        print("   • Gemini: gemini.google.com")
        print("   • ChatGPT: chat.openai.com")
        print("   • Warp: app.warp.dev")
        return
    
    print(f"🎯 Detected platform: {platform.upper()}")
    print(f"🔗 Target URL: {url}")
    print(f"⚙️  Configuration: {MAX_ATTEMPTS} max attempts, {TIMEOUT}s timeout")
    
    # Ensure platform directory exists
    print_progress("Setting up platform directory")
    platform_dir = ensure_platform_directory(platform)
    print(f"📁 Using directory: {platform_dir}")
    
    # Initialize browser
    browser = None
    try:
        # Warning message before browser opens
        print("\n⚠️  BROWSER LAUNCH WARNING")
        print("=" * 30)
        print("🌐 A Chrome browser window will now open to scrape the conversation.")
        print("📋 This is necessary to access the shared conversation content.")
        print("⏳ Please wait while the browser loads and processes the page...")
        print("🔒 The browser will automatically close when scraping is complete.")
        print("\n🚀 Starting browser in 3 seconds...")
        print("=" * 30)
        
        # Brief pause to let user read the warning
        time.sleep(3)
        
        browser = initialize_driver()
        
        # Route to appropriate scraping function with retry logic
        print(f"\n🚀 Starting scraping process for {platform.upper()}...")
        print("-" * 50)
        
        if platform == 'claude':
            cleaned_content = scrape_with_retry(
                scrape_claude_conversation, browser, url, platform, TIMEOUT, MAX_ATTEMPTS
            )
        elif platform == 'gemini':
            cleaned_content = scrape_with_retry(
                scrape_gemini_conversation, browser, url, platform, TIMEOUT, MAX_ATTEMPTS
            )
        elif platform == 'chatgpt':
            cleaned_content = scrape_with_retry(
                scrape_chatgpt_conversation, browser, url, platform, TIMEOUT, MAX_ATTEMPTS
            )
        elif platform == 'warp':
            # Use longer timeout for JavaScript-heavy Warp sessions
            WARP_TIMEOUT = 30
            cleaned_content = scrape_with_retry(
                scrape_warp_conversation, browser, url, platform, WARP_TIMEOUT, MAX_ATTEMPTS
            )
        
        print("-" * 50)
        
        if cleaned_content:
            print(f"\n🎉 SUCCESS! {platform.upper()} conversation extracted")
            print(f"📊 Content length: {len(cleaned_content)} characters")
            print(f"\n{'='*15} {platform.upper()} CONVERSATION CONTENT {'='*15}\n")
            print(cleaned_content)

            # Archive the output to platform-specific directory (legacy support)
            print_progress("Saving raw conversation file", 3, 5)
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = os.path.join(platform_dir, f"session-{timestamp}.txt")
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(cleaned_content)
            
            print(f"\n✅ Raw conversation file saved!")
            print(f"📄 Raw TXT file: {os.path.abspath(filename)}")
            print(f"💾 Size: {os.path.getsize(filename)} bytes")
            
            # Store in Local Memory System
            print_progress("Storing in Local Memory System", 4, 5)
            try:
                # Generate tags based on platform and content analysis
                tags = [platform, 'scraped_conversation', 'ai_conversation']
                
                # Create a basic summary for the conversation
                summary = f"Scraped {platform.upper()} conversation from {url[:50]}..."
                
                # Save to memory system
                memory_path = memory_system.save_conversation_memory(
                    content=cleaned_content,
                    platform=platform,
                    session_type="scraped_conversation",
                    tags=tags,
                    summary=summary
                )
                
                print(f"\n✅ Processed memory file saved!")
                print(f"🧠 Memory MD file: {os.path.abspath(memory_path)}")
                print(f"💾 Size: {os.path.getsize(memory_path)} bytes")
                
                # Show memory system stats
                stats = memory_system.get_project_stats()
                print(f"📊 Memory Stats - Conversations: {stats['total_conversations']}, Storage: {stats['storage_size_mb']} MB")
                
            except Exception as memory_error:
                print(f"⚠️  Warning: Could not store in Local Memory System: {memory_error}")
                print("Content was still saved to legacy file location.")
            
            print_progress("Archiving complete", 5, 5)
            
            # Display comprehensive file summary
            print("\n" + "=" * 60)
            print("📋 FILE SUMMARY - Conversation Successfully Captured!")
            print("=" * 60)
            print("\n🎯 Two files have been created for AI conversation continuity:")
            print()
            print("1️⃣ RAW CONVERSATION FILE (.txt)")
            print(f"   📄 Path: {os.path.abspath(filename)}")
            print(f"   📝 Purpose: Original scraped conversation content")
            print(f"   💾 Size: {os.path.getsize(filename)} bytes")
            print()
            if 'memory_path' in locals():
                print("2️⃣ PROCESSED MEMORY FILE (.md)")
                print(f"   🧠 Path: {os.path.abspath(memory_path)}")
                print(f"   📝 Purpose: Enhanced with metadata for AI memory continuity")
                print(f"   💾 Size: {os.path.getsize(memory_path)} bytes")
                print()
                print("💡 USAGE INSTRUCTIONS:")
                print("   • Upload the .md file to new AI conversations to maintain context")
                print("   • The .md file contains structured metadata and conversation history")
                print("   • The .txt file is a backup of the raw conversation content")
            else:
                print("2️⃣ PROCESSED MEMORY FILE (.md)")
                print("   ⚠️  Memory file creation failed, but raw content is saved")
            print("\n" + "=" * 60)

        else:
            print(f"\n❌ FAILED: Unable to scrape content from {platform.upper()}")
            print("💡 Troubleshooting tips:")
            print("   • Verify the URL is correct and accessible")
            print("   • Check if the conversation is public/shared")
            print("   • Try again in a few minutes (rate limiting)")
            print("   • Ensure stable internet connection")
            
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
    except Exception as e:
        error_msg = get_platform_error_message(platform, e)
        print(f"\n💥 Unexpected error: {error_msg}")
        print("🔧 Please report this issue if it persists")
    finally:
        if browser:
            print_progress("Cleaning up browser session")
            try:
                browser.quit()
                print("🧹 Browser session closed")
            except:
                pass  # Ignore cleanup errors
        
        print("\n" + "=" * 60)
        print("👋 SpiralBridge session completed")

if __name__ == "__main__":
    main()
