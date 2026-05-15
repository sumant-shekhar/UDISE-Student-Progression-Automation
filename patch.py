import re

with open('EP_GP_SP_PP.py', 'r') as f:
    content = f.read()

# Make it faster
content = content.replace('time.sleep(0.5)', 'time.sleep(0.2)')
content = content.replace('time.sleep(1)', 'time.sleep(0.3)')

# Fix the infinite loop on failure
old_except = """    except Exception as e:
        student_log["status"] = "failed"
        student_log["error"] = str(e)
        log_data["summary"]["failed"] += 1
        print(f"\\n  ❌ Student #{student_count} FAILED: {e}")

    finally:"""

new_except = """    except Exception as e:
        student_log["status"] = "failed"
        student_log["error"] = str(e)
        log_data["summary"]["failed"] += 1
        print(f"\\n  ❌ Student #{student_count} FAILED: {e}")
        print("  🛑 Fatal error encountered. Stopping to prevent infinite error loops.")
        print("  👉 Please fix the page manually, navigate to the next student, and restart the script.")
        break  # Exit the while True loop

    finally:"""

content = content.replace(old_except, new_except)

# Reduce log pollution: Remove print statements that are just field-level confirmations
# We will match print("  ✅ ...") or print(f"  ✅ ...") but keep the major ones
major_prints = [
    "General Profile saved",
    "Enrolment Profile saved",
    "Facility/Other Profile saved",
    "Moved to Enrolment Profile tab",
    "Complete Data clicked",
    "Moved to next student",
    "Login clicked!"
]

def clean_print(match):
    text = match.group(0)
    for mp in major_prints:
        if mp in text:
            return text
    # Otherwise, replace with empty string
    return ""

# remove all print(f"  ✅ ...") or print("  ✅ ...")
content = re.sub(r'^.*?print\([f]?"\s*✅\s+.*?"\).*?$\n', clean_print, content, flags=re.MULTILINE)
# Also remove info prints like print("  ℹ️ ...")
content = re.sub(r'^.*?print\([f]?"\s*ℹ️\s+.*?"\).*?$\n', '', content, flags=re.MULTILINE)

with open('EP_GP_SP_PP.py', 'w') as f:
    f.write(content)

