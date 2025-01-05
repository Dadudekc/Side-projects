import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime

# File to store tasks
TASKS_FILE = "tasks.json"

class Task:
    def __init__(self, id, name, priority="Medium", due_date="", status="Pending"):
        self.id = id
        self.name = name
        self.priority = priority
        self.due_date = due_date
        self.status = status

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "priority": self.priority,
            "due_date": self.due_date,
            "status": self.status
        }

class WorkflowManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Workflow Manager")
        self.tasks = []
        self.load_tasks()

        self.create_widgets()
        self.refresh_task_view()

    def create_widgets(self):
        # Top Frame for buttons
        top_frame = ttk.Frame(self.root)
        top_frame.pack(pady=10)

        add_btn = ttk.Button(top_frame, text="Add Task", command=self.add_task)
        add_btn.grid(row=0, column=0, padx=5)

        edit_btn = ttk.Button(top_frame, text="Edit Task", command=self.edit_task)
        edit_btn.grid(row=0, column=1, padx=5)

        delete_btn = ttk.Button(top_frame, text="Delete Task", command=self.delete_task)
        delete_btn.grid(row=0, column=2, padx=5)

        export_btn = ttk.Button(top_frame, text="Export Summary", command=self.export_summary)
        export_btn.grid(row=0, column=3, padx=5)

        # Search Frame
        search_frame = ttk.Frame(self.root)
        search_frame.pack(pady=5)

        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, padx=5)
        search_entry.bind("<KeyRelease>", lambda event: self.refresh_task_view())

        ttk.Label(search_frame, text="Filter by Status:").grid(row=0, column=2, padx=5)
        self.status_filter = tk.StringVar(value="All")
        status_combo = ttk.Combobox(search_frame, textvariable=self.status_filter, values=["All", "Pending", "Completed"], state="readonly")
        status_combo.grid(row=0, column=3, padx=5)
        status_combo.bind("<<ComboboxSelected>>", lambda event: self.refresh_task_view())

        # Treeview for tasks
        columns = ("ID", "Name", "Priority", "Due Date", "Status")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
        self.tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Right-click menu
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="Mark as Completed", command=self.mark_completed)
        self.menu.add_command(label="Mark as Pending", command=self.mark_pending)
        self.tree.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        selected_item = self.tree.identify_row(event.y)
        if selected_item:
            self.tree.selection_set(selected_item)
            self.menu.post(event.x_root, event.y_root)

    def mark_completed(self):
        selected = self.get_selected_task()
        if selected:
            selected.status = "Completed"
            self.save_tasks()
            self.refresh_task_view()

    def mark_pending(self):
        selected = self.get_selected_task()
        if selected:
            selected.status = "Pending"
            self.save_tasks()
            self.refresh_task_view()

    def add_task(self):
        TaskDialog(self, "Add Task")

    def edit_task(self):
        selected = self.get_selected_task()
        if selected:
            TaskDialog(self, "Edit Task", task=selected)
        else:
            messagebox.showwarning("No selection", "Please select a task to edit.")

    def delete_task(self):
        selected = self.get_selected_task()
        if selected:
            confirm = messagebox.askyesno("Delete Task", f"Are you sure you want to delete '{selected.name}'?")
            if confirm:
                self.tasks = [task for task in self.tasks if task.id != selected.id]
                self.save_tasks()
                self.refresh_task_view()
        else:
            messagebox.showwarning("No selection", "Please select a task to delete.")

    def get_selected_task(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected)
            task_id = int(item["values"][0])
            for task in self.tasks:
                if task.id == task_id:
                    return task
        return None

    def refresh_task_view(self):
        search_query = self.search_var.get().lower()
        status = self.status_filter.get()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for task in self.tasks:
            if search_query and search_query not in task.name.lower():
                continue
            if status != "All" and task.status != status:
                continue
            self.tree.insert("", "end", values=(task.id, task.name, task.priority, task.due_date, task.status))

    def load_tasks(self):
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, "r") as f:
                data = json.load(f)
                for item in data:
                    task = Task(**item)
                    self.tasks.append(task)

    def save_tasks(self):
        with open(TASKS_FILE, "w") as f:
            json.dump([task.to_dict() for task in self.tasks], f, indent=4)

    def export_summary(self):
        summary = {
            "total": len(self.tasks),
            "completed": sum(1 for task in self.tasks if task.status == "Completed"),
            "pending": sum(1 for task in self.tasks if task.status == "Pending"),
            "overdue": sum(1 for task in self.tasks if task.due_date and self.is_overdue(task))
        }
        ExportDialog(self, summary)

    def is_overdue(self, task):
        try:
            due = datetime.strptime(task.due_date, "%Y-%m-%d")
            return due < datetime.now()
        except:
            return False

class TaskDialog:
    def __init__(self, app, title, task=None):
        self.app = app
        self.task = task
        self.window = tk.Toplevel()
        self.window.title(title)
        self.window.grab_set()

        ttk.Label(self.window, text="Task Name:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.name_var = tk.StringVar(value=task.name if task else "")
        self.name_entry = ttk.Entry(self.window, textvariable=self.name_var, width=30)
        self.name_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(self.window, text="Priority:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.priority_var = tk.StringVar(value=task.priority if task else "Medium")
        self.priority_combo = ttk.Combobox(self.window, textvariable=self.priority_var, values=["High", "Medium", "Low"], state="readonly")
        self.priority_combo.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(self.window, text="Due Date (YYYY-MM-DD):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.due_var = tk.StringVar(value=task.due_date if task else "")
        self.due_entry = ttk.Entry(self.window, textvariable=self.due_var, width=30)
        self.due_entry.grid(row=2, column=1, padx=10, pady=5)

        save_btn = ttk.Button(self.window, text="Save", command=self.save_task)
        save_btn.grid(row=3, column=0, columnspan=2, pady=10)

    def save_task(self):
        name = self.name_var.get().strip()
        priority = self.priority_var.get()
        due_date = self.due_var.get().strip()

        if not name:
            messagebox.showerror("Input Error", "Task name cannot be empty.")
            return

        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Input Error", "Due date must be in YYYY-MM-DD format.")
                return

        if self.task:
            # Edit existing task
            self.task.name = name
            self.task.priority = priority
            self.task.due_date = due_date
        else:
            # Add new task
            new_id = max([task.id for task in self.app.tasks], default=0) + 1
            new_task = Task(id=new_id, name=name, priority=priority, due_date=due_date)
            self.app.tasks.append(new_task)

        self.app.save_tasks()
        self.app.refresh_task_view()
        self.window.destroy()

class ExportDialog:
    def __init__(self, app, summary):
        self.app = app
        self.window = tk.Toplevel()
        self.window.title("Export Summary")
        self.window.grab_set()

        ttk.Label(self.window, text="Choose export format:").pack(padx=10, pady=10)

        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(pady=5)

        json_btn = ttk.Button(btn_frame, text="Export as JSON", command=lambda: self.export("json", summary))
        json_btn.grid(row=0, column=0, padx=5)

        csv_btn = ttk.Button(btn_frame, text="Export as CSV", command=lambda: self.export("csv", summary))
        csv_btn.grid(row=0, column=1, padx=5)

        close_btn = ttk.Button(self.window, text="Close", command=self.window.destroy)
        close_btn.pack(pady=10)

    def export(self, format, summary):
        filename = f"task_summary.{format}"
        try:
            if format == "json":
                with open(filename, "w") as f:
                    json.dump(summary, f, indent=4)
            elif format == "csv":
                with open(filename, "w") as f:
                    f.write("Metric,Value\n")
                    for key, value in summary.items():
                        f.write(f"{key},{value}\n")
            messagebox.showinfo("Export Successful", f"Summary exported as {filename}")
            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Export Failed", f"An error occurred: {e}")

def main():
    root = tk.Tk()
    app = WorkflowManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
