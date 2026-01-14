# StudyTaskTracker
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import json
import os
import threading
import time
from plyer import notification

class StudyTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Study / Task Tracker")
        self.root.geometry("650x420")
        self.root.configure(bg="#eef2f3")

        self.study_sessions = []
        self.create_widgets()
        self.load_data()
        threading.Thread(target=self.reminder_check, daemon=True).start()

    def create_widgets(self):
        title = tk.Label(self.root, text="📘 Study / Task Tracker", font=("Arial", 18, "bold"), bg="#eef2f3")
        title.pack(pady=10)

        frame = tk.Frame(self.root, bg="#eef2f3")
        frame.pack(pady=5)

        tk.Label(frame, text="Subject/Topic:", bg="#eef2f3").grid(row=0, column=0, padx=5, pady=5)
        self.subject_entry = tk.Entry(frame, width=30)
        self.subject_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Reminder Time (HH:MM):", bg="#eef2f3").grid(row=1, column=0, padx=5, pady=5)
        self.reminder_entry = tk.Entry(frame, width=30)
        self.reminder_entry.grid(row=1, column=1, padx=5, pady=5)

        btn_frame = tk.Frame(self.root, bg="#eef2f3")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Task", command=self.add_session, bg="#4CAF50", fg="white", width=12).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="View Tasks", command=self.view_sessions, bg="#2196F3", fg="white", width=12).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Mark Completed", command=self.mark_completed, bg="#FF9800", fg="white", width=12).grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Remove Task", command=self.remove_task, bg="#f44336", fg="white", width=12).grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Save Progress", command=self.save_data, bg="#9C27B0", fg="white", width=12).grid(row=0, column=4, padx=5)

        self.tree = ttk.Treeview(self.root, columns=("Subject", "Reminder", "Date", "Status"), show="headings")
        self.tree.heading("Subject", text="Subject/Topic")
        self.tree.heading("Reminder", text="Reminder (HH:MM)")
        self.tree.heading("Date", text="Date Added")
        self.tree.heading("Status", text="Status")
        self.tree.pack(fill="both", expand=True, pady=10)

    def add_session(self):
        subject = self.subject_entry.get().strip()
        reminder_time = self.reminder_entry.get().strip()

        if subject == "" or reminder_time == "":
            messagebox.showwarning("Input Error", "Please fill both fields.")
            return

        session = {
            "subject": subject,
            "reminder": reminder_time,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "Pending"
        }

        self.study_sessions.append(session)
        messagebox.showinfo("Added", f"Task '{subject}' added!")
        self.subject_entry.delete(0, tk.END)
        self.reminder_entry.delete(0, tk.END)
        self.view_sessions()

    def view_sessions(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for session in self.study_sessions:
            self.tree.insert("", tk.END, values=(session["subject"], session["reminder"], session["date"], session["status"]))

    def mark_completed(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a task to mark as completed.")
            return
        index = self.tree.index(selected)
        self.study_sessions[index]["status"] = "Completed"
        messagebox.showinfo("Updated", "Task marked as Completed!")
        self.view_sessions()

    def remove_task(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a task to remove.")
            return
        index = self.tree.index(selected)
        del self.study_sessions[index]
        messagebox.showinfo("Removed", "Task removed successfully!")
        self.view_sessions()

    def save_data(self):
        with open("study_tasks.json", "w") as f:
            json.dump(self.study_sessions, f, indent=4)
        messagebox.showinfo("Saved", "Progress saved successfully!")

    def load_data(self):
        if os.path.exists("study_tasks.json"):
            with open("study_tasks.json", "r") as f:
                self.study_sessions = json.load(f)
            self.view_sessions()

    def reminder_check(self):
        while True:
            now = datetime.datetime.now().strftime("%H:%M")
            for session in self.study_sessions:
                # ✅ Only send reminder if still pending
                if session["reminder"] == now and session["status"] == "Pending":
                    notification.notify(
                        title="Study Reminder ⏰",
                        message=f"It's time to study: {session['subject']}",
                        timeout=8
                    )
                    session["status"] = "Reminded"
                    self.view_sessions()
            time.sleep(30)

if __name__ == "__main__":
    root = tk.Tk()
    app = StudyTracker(root)
    root.mainloop()
