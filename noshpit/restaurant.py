class Restaurant:
    def __init__(self, winner):
        self.name = winner["result"]["name"]
        self.address = winner["result"]["formatted_address"]
        self.number = winner["result"]["formatted_phone_number"]
        self.rating = winner["result"]["rating"]
        self.map_url = winner["result"]["url"]
        self.website = winner["result"]["website"]
        self.opening_hours = winner["result"]["opening_hours"]
