class AIAgent:
    def __init__(self):
        self.plugins = {}

    def register_plugin(self, name, plugin):
        """Registers a plugin with the agent."""
        self.plugins[name] = plugin

    def execute(self, plugin_name, command):
        """Executes a command using the specified plugin."""
        if plugin_name not in self.plugins:
            raise ValueError(f"Plugin '{plugin_name}' not found.")
        return self.plugins[plugin_name].execute(command)
