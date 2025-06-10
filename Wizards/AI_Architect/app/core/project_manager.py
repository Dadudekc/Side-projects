class ProjectManager:
    def __init__(self, project_name):
        self.project_name = project_name

    def get_project_name(self):
        return self.project_name

if __name__ == "__main__":
    manager = ProjectManager("Test Project")
    print(manager.get_project_name())
