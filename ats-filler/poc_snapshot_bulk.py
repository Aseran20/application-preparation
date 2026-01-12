"""POC: Test snapshot + bulk fill approach with Playwright."""

from playwright.sync_api import sync_playwright
import json
import sys

# Test URL - Julius Baer Workday
URL = "https://juliusbaer.wd3.myworkdayjobs.com/en-US/External/job/Zurich/Scrum-Master-with-Front-Arena-focus--Zrich--100---f-m-d-_r-17280-2/apply/autofillWithResume?source=LinkedIn"

# Resume path for testing
RESUME_PATH = r"C:\Users\Adrian\Downloads\devprojects\resume.ai\jobs\Julius Baer - Private Markets Analyst - 11.01.2026\PDF\Adrian Turion - Julius Baer - Resume.pdf"

def snapshot(page) -> list:
    """Extract visible form fields with their selectors."""
    fields = page.evaluate("""() => {
        const fields = [];

        // 1. Standard inputs, selects, textareas
        document.querySelectorAll('input, select, textarea').forEach(el => {
            if (el.offsetParent === null && el.type !== 'file') return;

            const field = {
                selector: null,
                label: null,
                type: el.type || el.tagName.toLowerCase(),
                tag: el.tagName.toLowerCase(),
                isDropdown: false
            };

            if (el.getAttribute('data-automation-id')) {
                field.selector = `[data-automation-id="${el.getAttribute('data-automation-id')}"]`;
            } else if (el.id) {
                field.selector = `#${el.id}`;
            } else if (el.name) {
                field.selector = `[name="${el.name}"]`;
            }

            field.label = el.getAttribute('aria-label')
                || el.getAttribute('placeholder')
                || el.getAttribute('data-automation-id')
                || null;

            if (!field.label && el.id) {
                const labelEl = document.querySelector(`label[for="${el.id}"]`);
                if (labelEl) field.label = labelEl.textContent.trim();
            }

            if (field.selector) {
                fields.push(field);
            }
        });

        // 2. Workday custom dropdowns (buttons with aria-haspopup)
        document.querySelectorAll('button[aria-haspopup="listbox"], [role="combobox"], [data-automation-id*="dropdown"], [data-automation-id*="select"]').forEach(el => {
            if (el.offsetParent === null) return;

            const field = {
                selector: null,
                label: null,
                type: 'dropdown',
                tag: el.tagName.toLowerCase(),
                isDropdown: true,
                currentValue: el.textContent.trim().substring(0, 50)
            };

            if (el.getAttribute('data-automation-id')) {
                field.selector = `[data-automation-id="${el.getAttribute('data-automation-id')}"]`;
            } else if (el.id) {
                field.selector = `#${el.id}`;
            }

            field.label = el.getAttribute('aria-label')
                || el.closest('[data-automation-id]')?.getAttribute('data-automation-id')
                || null;

            if (field.selector) {
                fields.push(field);
            }
        });

        // 3. Workday prompt buttons (another dropdown pattern)
        document.querySelectorAll('[data-automation-id$="promptIcon"], [data-automation-id*="formField"] button').forEach(el => {
            if (el.offsetParent === null) return;

            // Find parent container for label
            const container = el.closest('[data-automation-id*="formField"]');
            const labelEl = container?.querySelector('label');

            const field = {
                selector: el.getAttribute('data-automation-id')
                    ? `[data-automation-id="${el.getAttribute('data-automation-id')}"]`
                    : null,
                label: labelEl?.textContent.trim() || el.getAttribute('aria-label'),
                type: 'dropdown-prompt',
                tag: 'button',
                isDropdown: true
            };

            if (field.selector && !fields.some(f => f.selector === field.selector)) {
                fields.push(field);
            }
        });

        return fields;
    }""")
    return fields


def bulk_fill(page, data: dict):
    """Fill multiple fields at once."""
    results = {"filled": [], "failed": []}

    for selector, value in data.items():
        try:
            el = page.locator(selector)
            if el.count() > 0:
                el.first.fill(str(value))
                results["filled"].append(selector)
            else:
                results["failed"].append({"selector": selector, "reason": "not found"})
        except Exception as e:
            results["failed"].append({"selector": selector, "reason": str(e)})

    return results


def main():
    print("=" * 60)
    print("POC: Snapshot + Bulk Fill")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print(f"\n1. Navigating to: {URL[:50]}...")
        page.goto(URL)
        page.wait_for_load_state("networkidle")

        # Dismiss cookies if present
        print("   Looking for cookies popup...")
        try:
            decline = page.get_by_role("button", name="Decline")
            decline.click(timeout=5000)
            print("   Cookies dismissed (Decline)")
            page.wait_for_timeout(1000)
        except:
            try:
                # Try text-based selector
                decline = page.get_by_text("Decline", exact=True)
                decline.click(timeout=3000)
                print("   Cookies dismissed (text)")
                page.wait_for_timeout(1000)
            except:
                print("   No cookies popup or already dismissed")

        # Wait for page to settle after cookies
        page.wait_for_timeout(1500)

        # Step 1: Upload resume
        print("\n2. Uploading resume...")
        try:
            # Wait for file input to appear
            file_input = page.locator("[data-automation-id='file-upload-input-ref']")
            file_input.wait_for(timeout=5000)
            file_input.set_input_files(RESUME_PATH)
            print("   Resume uploaded")
            page.wait_for_timeout(2000)  # Wait for upload to process
        except Exception as e:
            print(f"   Upload error: {e}")

        # Step 2: Click Next/Save and Continue
        print("\n3. Clicking Next...")
        try:
            # Try multiple button names
            for btn_name in ["Next", "Save and Continue", "Continue"]:
                btn = page.get_by_role("button", name=btn_name)
                if btn.count() > 0:
                    btn.click()
                    page.wait_for_load_state("networkidle")
                    print(f"   Clicked '{btn_name}', navigated to next page")
                    break
        except Exception as e:
            print(f"   Navigation error: {e}")

        page.wait_for_timeout(2000)

        # Debug: What's on the page?
        print("\n   DEBUG - Page title:", page.title())
        print("   DEBUG - Current URL:", page.url[:80])

        # Check what elements exist
        print("   DEBUG - Visible buttons:")
        buttons = page.get_by_role("button").all()
        for btn in buttons[:5]:
            try:
                if btn.is_visible():
                    print(f"     - {btn.text_content()[:50]}")
            except:
                pass

        # Step 3: Take snapshot of current page
        print("\n4. Taking snapshot...")
        fields = snapshot(page)
        print(f"   Found {len(fields)} fields:")
        for f in fields[:15]:  # Show first 15
            print(f"   - {f['label'] or 'no label'}: {f['selector']} ({f['type']})")
        if len(fields) > 15:
            print(f"   ... and {len(fields) - 15} more")

        # Save full snapshot to file
        with open("poc_snapshot_result.json", "w") as f:
            json.dump(fields, f, indent=2)
        print("\n   Full snapshot saved to poc_snapshot_result.json")

        # Step 4: Test bulk fill if we have text fields
        if fields:
            print("\n5. Testing bulk fill...")
            text_fields = [f for f in fields if f['type'] in ('text', 'email', 'tel')]
            if text_fields:
                # Map test data to actual selectors
                test_data = {}
                for f in text_fields[:5]:
                    label = (f['label'] or '').lower()
                    if 'first' in label or 'given' in label:
                        test_data[f['selector']] = "Adrian"
                    elif 'last' in label or 'family' in label:
                        test_data[f['selector']] = "Turion"
                    elif 'email' in label:
                        test_data[f['selector']] = "turionadrian@gmail.com"
                    elif 'phone' in label:
                        test_data[f['selector']] = "+41772623796"

                if test_data:
                    print(f"   Filling {len(test_data)} fields...")
                    for sel, val in test_data.items():
                        print(f"   - {sel}: {val}")
                    result = bulk_fill(page, test_data)
                    print(f"   Filled: {len(result['filled'])}")
                    print(f"   Failed: {len(result['failed'])}")
                else:
                    print("   No matching fields to fill")

        print("\n" + "=" * 60)
        print("POC Complete.")
        print("Check poc_snapshot_result.json for full field list")
        print("Browser stays open - close manually when done")
        print("=" * 60)

        # Keep browser open for manual inspection
        page.wait_for_timeout(60000)  # 60 seconds
        browser.close()


if __name__ == "__main__":
    main()
