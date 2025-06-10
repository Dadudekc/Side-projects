class APIWizard:
    def __init__(self, api_name):
        self.api_name = api_name

    def get_api_name(self):
        return self.api_name

if __name__ == "__main__":
    wizard = APIWizard("Test API")
    print(wizard.get_api_name())
