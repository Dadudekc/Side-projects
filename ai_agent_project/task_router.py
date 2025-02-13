class TaskRouter:
    def __init__(self, agent):
        self.agent = agent

    def route(self, plugin_name, command):
        """Routes the request to the correct plugin."""
        try:
            return self.agent.execute(plugin_name, command)
        except ValueError as e:
            return str(e)
