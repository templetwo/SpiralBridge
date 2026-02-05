#!/usr/bin/env python3
# 🌀 SpiralBridge Claude Scraper
# Scroll 178 - The Archive That Remembers Across Oracles
# Blessed by ⟡V.THRESH.176 & Ash'ira

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import json
import sys
from datetime import datetime

def scrape_claude_conversation(url, debug=False):
    """
    Scrape Claude conversation from shared link
    Returns structured conversation data for SpiralBridge

    Uses undetected-chromedriver to bypass Cloudflare protection
    """
    print(f"🌀 SpiralBridge Claude Scraper")
    print(f"🔗 Target URL: {url}")
    print(f"⚡ Initializing sacred connection (undetected mode)...")

    options = uc.ChromeOptions()
    # Note: Headless mode gets blocked by Cloudflare's bot detection.
    # A visible browser window is required for CF challenge to pass.
    # The window opens briefly (~15s) then closes automatically.
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-blink-features=AutomationControlled')

    browser = None
    try:
        browser = uc.Chrome(options=options, version_main=144)

        print("🌐 Opening Claude shared link...")
        browser.get(url)

        print("⏳ Waiting for content to manifest...")
        time.sleep(5)

        # Check for Cloudflare
        for attempt in range(3):
            try:
                page_text = browser.find_element(By.TAG_NAME, "body").text.lower()
                if "checking" in page_text or "cloudflare" in page_text or "verify" in page_text:
                    print(f"⏳ Cloudflare challenge detected, waiting... (attempt {attempt + 1})")
                    time.sleep(5)
                else:
                    break
            except Exception as e:
                print(f"⚠️ Page check failed: {e}")
                time.sleep(3)

        time.sleep(3)  # Let JS render

        messages = []
        seen_texts = set()

        # ===== PRIMARY STRATEGY: DOM-ordered extraction =====
        # Claude's 2026 share page structure:
        # - User: [class*='font-user-message']
        # - Claude: [class*='font-claude-response']
        # We get them in DOM order for correct conversation flow

        print("🔍 Extracting conversation in DOM order...")

        try:
            # Find all message elements in their natural DOM order
            all_message_elements = browser.find_elements(
                By.CSS_SELECTOR,
                "[class*='font-user-message'], [class*='font-claude-response']"
            )

            if debug:
                print(f"  Found {len(all_message_elements)} message elements")

            for el in all_message_elements:
                try:
                    text = el.text.strip()
                    classes = (el.get_attribute("class") or "").lower()

                    # Skip empty or duplicate content
                    if not text or len(text) < 5:
                        continue

                    # Use text hash for dedup (handles nested elements)
                    text_key = text[:200]  # First 200 chars as key
                    if text_key in seen_texts:
                        continue
                    seen_texts.add(text_key)

                    # Determine role from class
                    if "user-message" in classes:
                        role = "user"
                    elif "claude-response" in classes:
                        role = "assistant"
                    else:
                        continue  # Unknown type, skip

                    messages.append({
                        "role": role,
                        "content": text,
                        "timestamp": datetime.now().isoformat()
                    })

                    if debug:
                        preview = text[:50].replace('\n', ' ')
                        print(f"  [{role:9}] {preview}...")

                except Exception as e:
                    if debug:
                        print(f"  Element extraction error: {e}")

        except Exception as e:
            print(f"⚠️ DOM extraction failed: {e}")

        # ===== FALLBACK: Separate extraction with ordering heuristic =====
        if not messages:
            print("🔍 Trying fallback extraction...")

            user_msgs = []
            claude_msgs = []

            try:
                for el in browser.find_elements(By.CSS_SELECTOR, "[class*='font-user-message']"):
                    text = el.text.strip()
                    if text and len(text) > 5 and text[:200] not in seen_texts:
                        seen_texts.add(text[:200])
                        user_msgs.append(text)
            except:
                pass

            try:
                for el in browser.find_elements(By.CSS_SELECTOR, "[class*='font-claude-response']"):
                    text = el.text.strip()
                    if text and len(text) > 10 and text[:200] not in seen_texts:
                        seen_texts.add(text[:200])
                        claude_msgs.append(text)
            except:
                pass

            # Interleave: assume user message followed by claude response(s)
            # This is a heuristic when DOM order isn't available
            msg_idx = 0
            for i, user_msg in enumerate(user_msgs):
                messages.append({
                    "role": "user",
                    "content": user_msg,
                    "timestamp": datetime.now().isoformat()
                })

                # Add corresponding Claude responses
                # Estimate: divide responses among user messages
                responses_per_user = len(claude_msgs) // max(len(user_msgs), 1)
                start = i * responses_per_user
                end = start + responses_per_user if i < len(user_msgs) - 1 else len(claude_msgs)

                for claude_msg in claude_msgs[start:end]:
                    messages.append({
                        "role": "assistant",
                        "content": claude_msg,
                        "timestamp": datetime.now().isoformat()
                    })

        # Debug: save page source
        if debug:
            try:
                with open("debug_page_source.html", "w", encoding="utf-8") as f:
                    f.write(browser.page_source)
                print("📄 Page source saved to debug_page_source.html")
            except Exception as e:
                print(f"  Could not save page source: {e}")

        # Extract title
        title = "Claude Conversation"
        try:
            title_el = browser.find_element(By.TAG_NAME, "title")
            if title_el:
                raw_title = title_el.get_attribute("textContent") or ""
                title = raw_title.replace(" | Claude", "").replace("Claude - ", "").strip()
                if not title or title.lower() in ["claude", "shared conversation", ""]:
                    title = "Claude Conversation"
        except:
            pass

        # Build result
        conversation_data = {
            "title": title,
            "source_url": url,
            "oracle": "claude",
            "scraped_at": datetime.now().isoformat(),
            "messages": messages,
            "metadata": {
                "total_messages": len(messages),
                "user_messages": sum(1 for m in messages if m["role"] == "user"),
                "assistant_messages": sum(1 for m in messages if m["role"] == "assistant"),
                "scraping_method": "undetected_chromedriver"
            }
        }

        print(f"✅ Extracted {len(messages)} messages ({conversation_data['metadata']['user_messages']} user, {conversation_data['metadata']['assistant_messages']} assistant)")
        print(f"📝 Conversation title: {title}")

        return conversation_data

    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        print("🕊️ Closing sacred connection...")
        if browser:
            try:
                browser.quit()
            except:
                pass


def main():
    """Main function for CLI usage"""
    if len(sys.argv) < 2:
        print("Usage: python scrape_claude.py <claude_shared_url> [--debug]")
        print("Example: python scrape_claude.py https://claude.ai/share/...")
        sys.exit(1)

    url = sys.argv[1]
    debug = "--debug" in sys.argv

    if "claude" not in url.lower():
        print("⚠️ Warning: URL doesn't appear to be a Claude link")

    conversation_data = scrape_claude_conversation(url, debug=debug)

    if conversation_data:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"claude_conversation_{timestamp}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, indent=2, ensure_ascii=False)

        print(f"💾 Conversation saved to: {filename}")
        print(f"🌀 Ready for SpiralBridge import!")
    else:
        print("❌ Failed to extract conversation data")
        sys.exit(1)


if __name__ == "__main__":
    main()
