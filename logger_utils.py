import json
import os
from datetime import datetime

class JSONLogger:
    def __init__(self, username):
        self.log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json"
        self.log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.log_filename)
        self.log_data = {
            "session": {
                "started_at": datetime.now().isoformat(),
                "log_file": self.log_filename,
                "username": username
            },
            "summary": {
                "total_students": 0,
                "successful": 0,
                "failed": 0,
                "finished_at": None
            },
            "students": []
        }
        self.save_log()
        print(f"📄 Log file created: {self.log_filename}")

    def save_log(self):
        with open(self.log_path, "w", encoding="utf-8") as f:
            json.dump(self.log_data, f, indent=4, ensure_ascii=False)

    def mark_login_clicked(self):
        self.log_data["session"]["login_clicked_at"] = datetime.now().isoformat()
        self.save_log()

    def add_student_log(self, student_log):
        self.log_data["students"].append(student_log)
        self.save_log()

    def update_summary(self, total_students, successful, failed, finished=False):
        self.log_data["summary"]["total_students"] = total_students
        self.log_data["summary"]["successful"] = successful
        self.log_data["summary"]["failed"] = failed
        if finished:
            self.log_data["summary"]["finished_at"] = datetime.now().isoformat()
        self.save_log()
