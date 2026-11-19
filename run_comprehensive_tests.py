"""
Comprehensive End-to-End Test Suite for ClipperAI Studio
- Tests Launcher & Desktop Shortcuts
- Tests Backend REST Endpoints
- Tests Playwright E2E UI, Console Errors, and AI Script Generation Flow
- Captures Proof Screenshots
"""
import os
import sys
import time
import json
import socket
import urllib.request
import win32com.client
from playwright.sync_api import sync_playwright

ARTIFACTS_DIR = r"C:\Users\p\.gemini\antigravity-cli\brain\9ccd28c9-9088-4c95-87fa-da3326e7465f"
BASE_URL = "http://127.0.0.1:8000"

results = {
    "launcher_tests": {},
    "desktop_shortcuts": {},
    "api_tests": {},
    "e2e_browser_tests": {},
    "passed": 0,
    "failed": 0
}

def record_pass(category, name, details=""):
    results[category][name] = {"status": "PASSED", "details": details}
    results["passed"] += 1
    print(f"  [PASS] {name}: {details}")

def record_fail(category, name, error=""):
    results[category][name] = {"status": "FAILED", "error": str(error)}
    results["failed"] += 1
    print(f"  [FAIL] {name}: {error}")

print("==================================================================")
print("     STARTING COMPREHENSIVE TEST SUITE - CLIPPERAI STUDIO        ")
print("==================================================================")

# ---------------------------------------------------------
# 1. LAUNCHER & PORT DETECTION TESTS
# ---------------------------------------------------------
print("\n[TEST 1] Testing Launcher & Port Detection...")
try:
    with socket.create_connection(('127.0.0.1', 8000), timeout=2.0):
        record_pass("launcher_tests", "port_8000_listening", "Port 8000 is open and accepting TCP connections.")
except Exception as e:
    record_fail("launcher_tests", "port_8000_listening", e)

# Test open_browser_when_ready.py logic
t0 = time.time()
try:
    with urllib.request.urlopen(f"{BASE_URL}/", timeout=10.0) as resp:
        if resp.status == 200:
            duration = (time.time() - t0) * 1000
            record_pass("launcher_tests", "http_200_readiness_check", f"HTTP 200 OK returned in {duration:.1f} ms.")
        else:
            record_fail("launcher_tests", "http_200_readiness_check", f"HTTP status was {resp.status}")
except Exception as e:
    record_fail("launcher_tests", "http_200_readiness_check", e)

# ---------------------------------------------------------
# 2. DESKTOP SHORTCUTS VERIFICATION
# ---------------------------------------------------------
print("\n[TEST 2] Testing Desktop Shortcuts on E:\\USER_DATA_C\\Desktop...")
desktop_dir = r"E:\USER_DATA_C\Desktop"
shell = win32com.client.Dispatch("WScript.Shell")

# ClipperAI Studio.lnk
clipper_lnk = os.path.join(desktop_dir, "ClipperAI Studio.lnk")
if os.path.exists(clipper_lnk):
    s = shell.CreateShortcut(clipper_lnk)
    if "Start_ClipperAI.bat" in s.TargetPath:
        record_pass("desktop_shortcuts", "ClipperAI Studio.lnk", f"Points to {s.TargetPath}")
    else:
        record_fail("desktop_shortcuts", "ClipperAI Studio.lnk", f"Target is unexpected: {s.TargetPath}")
else:
    record_fail("desktop_shortcuts", "ClipperAI Studio.lnk", "File not found on desktop.")

# AutoClip Studio.lnk
autoclip_lnk = os.path.join(desktop_dir, "AutoClip Studio.lnk")
if os.path.exists(autoclip_lnk):
    s = shell.CreateShortcut(autoclip_lnk)
    if "Start_ClipperAI.bat" in s.TargetPath:
        record_pass("desktop_shortcuts", "AutoClip Studio.lnk", f"Synced to {s.TargetPath}")
    else:
        record_fail("desktop_shortcuts", "AutoClip Studio.lnk", f"Target is unexpected: {s.TargetPath}")
else:
    record_fail("desktop_shortcuts", "AutoClip Studio.lnk", "File not found on desktop.")

# ClipperAI Studio Web.url
web_url = os.path.join(desktop_dir, "ClipperAI Studio Web.url")
if os.path.exists(web_url):
    with open(web_url, "r", encoding="utf-8", errors="ignore") as f:
        c = f.read()
    if "127.0.0.1:8000" in c:
        record_pass("desktop_shortcuts", "ClipperAI Studio Web.url", "Valid internet shortcut pointing to 127.0.0.1:8000")
    else:
        record_fail("desktop_shortcuts", "ClipperAI Studio Web.url", f"Unexpected content: {c}")
else:
    record_fail("desktop_shortcuts", "ClipperAI Studio Web.url", "File not found on desktop.")

# ---------------------------------------------------------
# 3. BACKEND API ENDPOINTS
# ---------------------------------------------------------
print("\n[TEST 3] Testing Backend API Endpoints...")

# GET /
try:
    with urllib.request.urlopen(f"{BASE_URL}/", timeout=10.0) as resp:
        body = resp.read().decode('utf-8', errors='ignore')
        if "ClipperAI Studio" in body:
            record_pass("api_tests", "GET_root_html", f"Status 200, HTML contains 'ClipperAI Studio' ({len(body)} chars)")
        else:
            record_fail("api_tests", "GET_root_html", "HTML does not contain ClipperAI Studio")
except Exception as e:
    record_fail("api_tests", "GET_root_html", e)

# GET /api/ai/config
try:
    with urllib.request.urlopen(f"{BASE_URL}/api/ai/config", timeout=5.0) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        record_pass("api_tests", "GET_ai_config", f"Status 200, active provider: {data.get('provider')}")
except Exception as e:
    record_fail("api_tests", "GET_ai_config", e)

# POST /api/ai/ideas (The exact bug scenario)
try:
    payload = json.dumps({
        "topic": "kisah taubatnya ka`ab bin malik, memilih jujur dan mengakui kesalahannya",
        "style": "anymotion",
        "duration": 45
    }).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/ai/ideas", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10.0) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        if data.get("ok") and len(data.get("script", "")) > 50:
            record_pass("api_tests", "POST_ai_ideas_kaab_bin_malik", 
                        f"Status 200, Script generated ({len(data['script'])} chars), Title: {data.get('header_title')}")
        else:
            record_fail("api_tests", "POST_ai_ideas_kaab_bin_malik", f"Unexpected response: {data}")
except Exception as e:
    record_fail("api_tests", "POST_ai_ideas_kaab_bin_malik", e)

# ---------------------------------------------------------
# 4. PLAYWRIGHT E2E BROWSER TESTING
# ---------------------------------------------------------
print("\n[TEST 4] Running Playwright E2E UI & Workflow Test...")
console_errors = []
dialog_messages = []

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # Monitor console errors
        def on_console(msg):
            if msg.type in ["error"]:
                console_errors.append(msg.text)
        page.on("console", on_console)

        # Monitor alert/dialog popups
        def on_dialog(dialog):
            dialog_messages.append({"type": dialog.type, "message": dialog.message})
            print(f"    [DIALOG DETECTED] {dialog.type}: {dialog.message}")
            dialog.accept()
        page.on("dialog", on_dialog)

        # 4.1 Goto page
        page.goto(BASE_URL, wait_until="load", timeout=15000)
        time.sleep(1.0)
        
        # Verify page title
        title = page.title()
        if "ClipperAI Studio" in title:
            record_pass("e2e_browser_tests", "page_load_and_title", f"Title: '{title}'")
        else:
            record_fail("e2e_browser_tests", "page_load_and_title", f"Unexpected title: '{title}'")

        # Capture initial screenshot
        screenshot_initial = os.path.join(ARTIFACTS_DIR, "test_ui_initial_load.png")
        page.screenshot(path=screenshot_initial, full_page=False)
        print(f"    Saved initial UI screenshot: {screenshot_initial}")

        # 4.2 Switch to Faceless Tab
        faceless_tab_btn = page.locator("#tab-mode-faceless")
        if faceless_tab_btn.count() > 0:
            faceless_tab_btn.click()
            time.sleep(0.5)
            record_pass("e2e_browser_tests", "tab_navigation_faceless", "Switched to AI Faceless tab.")
        else:
            record_fail("e2e_browser_tests", "tab_navigation_faceless", "Tab button #tab-mode-faceless not found")

        # 4.3 Fill AI Topic and Click Generate Script
        topic_input = page.locator("#faceless-ai-topic")
        if topic_input.count() > 0:
            test_topic = "kisah taubatnya ka`ab bin malik, memilih jujur dan mengakui kesalahannya"
            topic_input.fill(test_topic)
            record_pass("e2e_browser_tests", "fill_ai_topic_input", f"Filled topic: '{test_topic[:35]}...'")

            # Click generate button
            gen_btn = page.locator("#btn-ai-write-script")
            if gen_btn.count() > 0:
                print("    Clicking 'Tulis Naskah AI' button...")
                gen_btn.click()
                
                # Wait for script textarea to be populated
                script_box = page.locator("#faceless-script-input")
                page.wait_for_function("document.getElementById('faceless-script-input').value.length > 30", timeout=12000)
                generated_script = script_box.input_value()
                
                record_pass("e2e_browser_tests", "ai_script_generation_flow", 
                            f"Successfully generated script ({len(generated_script)} chars) in textarea!")

                # Screenshot with generated script
                screenshot_script = os.path.join(ARTIFACTS_DIR, "test_ui_generated_script.png")
                page.screenshot(path=screenshot_script, full_page=False)
                print(f"    Saved script generation screenshot: {screenshot_script}")
            else:
                record_fail("e2e_browser_tests", "ai_script_generation_flow", "Generate button #btn-ai-write-script not found")
        else:
            record_fail("e2e_browser_tests", "fill_ai_topic_input", "Topic input #faceless-ai-topic not found")

        # 4.4 Check if any dialog error appeared
        error_dialogs = [d for d in dialog_messages if "Gagal" in d["message"] or "Internal Server" in d["message"]]
        if not error_dialogs:
            record_pass("e2e_browser_tests", "no_error_alerts", "Zero error alerts triggered during AI generation!")
        else:
            record_fail("e2e_browser_tests", "no_error_alerts", f"Error alerts detected: {error_dialogs}")

        # Check console errors
        critical_errors = [e for e in console_errors if "favicon" not in e.lower() and "404" not in e.lower()]
        if not critical_errors:
            record_pass("e2e_browser_tests", "clean_browser_console", "Zero critical JS errors in browser console.")
        else:
            record_fail("e2e_browser_tests", "clean_browser_console", f"Console errors: {critical_errors}")

        browser.close()

except Exception as e:
    record_fail("e2e_browser_tests", "playwright_execution", e)

# ---------------------------------------------------------
# FINAL SUMMARY
# ---------------------------------------------------------
print("\n==================================================================")
print(f"TEST RESULTS: {results['passed']} PASSED | {results['failed']} FAILED")
print("==================================================================")

# Write summary json
output_json = os.path.join(ARTIFACTS_DIR, "test_execution_summary.json")
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print(f"Detailed summary written to: {output_json}")
if results["failed"] == 0:
    print("ALL TESTS PASSED WITH 100% SUCCESS!")
    sys.exit(0)
else:
    print(f"WARNING: {results['failed']} test(s) failed.")
    sys.exit(1)
