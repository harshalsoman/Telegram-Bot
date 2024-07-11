import yaml


class Credentials:
    def __init__(self, filename: str = "config.yaml") -> None:
        self.creds = None
        self.load(filename)
        pass

    def load(self, filename):
        with open(filename, "r") as yamlfile:
            self.creds = yaml.load(yamlfile, Loader=yaml.FullLoader)

    def get_openai_key(self):
        return self.creds["OPENAI"]["API_KEY"]

    def get_bhashini_headers(self):
        return self.creds["BHASHINI"]["HEADERS"]

    def get_telegram_token(self):
        return self.creds["TELEGRAM"]["TOKEN"]
