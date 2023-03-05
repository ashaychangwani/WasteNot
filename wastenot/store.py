"""
Storage for the WasteNot application.

What needs to be stored?
- Food banks
- Pickup locations
"""

from pathlib import Path

import pandas as pd

from .models import Address


class Store:
    """
    Storage class
    """

    FOOD_BANKS_CSV: Path = Path(__file__).parent.parent.joinpath("data/food_banks.csv")
    PICKUP_LOCATIONS_CSV: Path = Path(__file__).parent.parent.joinpath(
        "data/pickup_locations.csv"
    )

    food_banks_df: pd.DataFrame = pd.read_csv(FOOD_BANKS_CSV)
    pickup_locations_df: pd.DataFrame = pd.read_csv(PICKUP_LOCATIONS_CSV)

    food_banks: dict[str, Address] = {}
    pickup_locations: dict[str, Address] = {}
    pickup_weights: dict[str, float] = {}

    def __init__(self):
        if self.food_banks == {}:
            self.load_food_banks()
        if self.pickup_locations == {}:
            self.load_pickup_locations()

    def load_food_banks(self) -> dict[str, Address]:
        """
        Load food banks from the CSV file
        :return: Dictionary of food banks
        """
        self.food_banks_df["address"] = self.food_banks_df.apply(
            lambda row: Address(
                row["street1"], row["street2"], row["city"], row["state"], row["zip"]
            ),
            axis=1,
        )

        # Add food banks to the dictionary
        for _, row in self.food_banks_df.iterrows():
            self.add_food_bank(row["name"], row["address"], save=False)

        return self.food_banks

    def load_pickup_locations(self) -> dict[str, Address]:
        """
        Load pickup locations from the CSV file
        :return: Dictionary of pickup locations
        """
        self.pickup_locations_df["address"] = self.pickup_locations_df.apply(
            lambda row: Address(
                row["street1"], row["street2"], row["city"], row["state"], row["zip"]
            ),
            axis=1,
        )

        # Add pickup locations to the dictionary
        for _, row in self.pickup_locations_df.iterrows():
            self.add_pickup_location(
                row["name"], row["address"], row["weight"], save=False
            )

        return self.pickup_locations

    def get_food_bank(self, name: str) -> Address or None:
        """
        Get a food bank from the store
        :param name: Food bank name
        :return: Food bank address
        """
        return self.food_banks.get(name, None)

    def get_pickup_location(self, name: str) -> Address or None:
        """
        Get a pickup location from the store
        :param name: Pickup location name
        :return: Pickup location address
        """
        return self.pickup_locations.get(name, None)

    def add_food_bank(
        self, name: str, address: Address, save: bool = True
    ) -> dict[str, Address]:
        """
        Add a food bank to the store
        :param name: Food bank name
        :param address: Food bank address
        :param save: Save the food bank to the CSV file
        :return: Dictionary of food banks

        Note: If the food bank already exists, it will be overwritten.
        """
        self.food_banks[name] = address

        if save:
            # Add the food bank to the end of the file
            with open(self.FOOD_BANKS_CSV, "a") as f:
                f.write(
                    f"{name},{address.street1},{address.street2},{address.city},{address.state},{address.zip},"
                    f"{address.coordinates[0]},{address.coordinates[1]},\n"
                )

        return self.food_banks

    def add_pickup_location(
        self, name: str, address: Address, weight: float = 0, save: bool = True
    ) -> dict[str, Address]:
        """
        Add a pickup location to the store
        :param name: Pickup location name
        :param address: Pickup location address
        :param weight: Weight of the pickup location
        :param save: Save the pickup location to the CSV file
        :return: Dictionary of pickup locations

        Note: If the pickup location already exists, it will be overwritten.
        """
        self.pickup_locations[name] = address

        # Add the weight to the dataframe
        self.pickup_locations_df.append(
            {
                "name": name,
                "street1": address.street1,
                "street2": address.street2,
                "city": address.city,
                "state": address.state,
                "zip": address.zip,
                "weight": weight,
            },
            ignore_index=True,
        )

        if save:
            # Add the pickup location to the end of the file
            with open(self.PICKUP_LOCATIONS_CSV, "a") as f:
                f.write(
                    f"{name},{address.street1},{address.street2},{address.city},{address.state},{address.zip},"
                    f"{address.coordinates[0]},{address.coordinates[1]},{weight}\n"
                )

        return self.pickup_locations

    def remove_food_bank(self, name: str) -> dict[str, Address]:
        """
        Remove a food bank from the store
        :param name: Food bank name
        :return: Dictionary of food banks

        Note: If the food bank does not exist, nothing will happen.
        """
        if name in self.food_banks:
            del self.food_banks[name]

        # Remove the food bank from the dataframe
        self.food_banks_df = self.food_banks_df[self.food_banks_df["name"] != name]

        # Iterate through the file and delete the line
        with open(self.FOOD_BANKS_CSV, "r") as f:
            lines = f.readlines()
        with open(self.FOOD_BANKS_CSV, "w") as f:
            for line in lines:
                if not line.startswith(name):
                    f.write(line)

        return self.food_banks

    def remove_pickup_location(self, name: str) -> dict[str, Address]:
        """
        Remove a pickup location from the store
        :param name: Pickup location name
        :return: Dictionary of pickup locations

        Note: If the pickup location does not exist, nothing will happen.
        """
        if name in self.pickup_locations:
            del self.pickup_locations[name]

        # Remove the pickup location from the dataframe
        self.pickup_locations_df = self.pickup_locations_df[
            self.pickup_locations_df["name"] != name
        ]

        # Iterate through the file and delete the line
        with open(self.PICKUP_LOCATIONS_CSV, "r") as f:
            lines = f.readlines()
        with open(self.PICKUP_LOCATIONS_CSV, "w") as f:
            for line in lines:
                if not line.startswith(name):
                    f.write(line)

        return self.pickup_locations
