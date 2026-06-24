import os
import time
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - QA Agent - %(message)s')

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def auto_qa_loop():
    logging.info("Starting QA Subagent Loop...")
    while True:
        try:
            # 1. Run formatting
            logging.info("Running code formatters (ruff, prettier)...")
            run_cmd(r"backend\venv\Scripts\python -m ruff format backend/")
            run_cmd(r"npx prettier --write frontend/**/*.{js,css,html}")
            
            # 2. Check for changes
            success, stdout, stderr = run_cmd("git status --porcelain")
            if stdout.strip():
                logging.info("Detected changes after formatting or by user. Committing locally...")
                run_cmd("git add .")
                run_cmd('git commit -m "Auto-QA: formatting and local changes"')
                logging.info("Local commit successful.")
            else:
                logging.debug("No changes detected.")
            
        except Exception as e:
            logging.error(f"QA Loop Error: {e}")
        
        # Run every 30 seconds
        time.sleep(30)

if __name__ == "__main__":
    auto_qa_loop()
