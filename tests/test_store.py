"""
Test Store
"""

from wastenot import Store
from wastenot.models import Address

if __name__ == "__main__":
    print(Store.FOOD_BANKS_CSV)
    print(Store.PICKUP_LOCATIONS_CSV)
    print(Store().load_food_banks())
    print(Store().load_pickup_locations())

    print("\n\nTest add and remove food bank")
    # Test add and remove food bank
    store = Store()
    store.add_food_bank(
        "Test Food Bank",
        Address("123 Test Food Bank", None, "Test City", "NY", "12345"),
        save=True,
    )
    print(store.get_food_bank("Test Food Bank"))
    store.remove_food_bank("Test Food Bank")
    print(store.get_food_bank("Test Food Bank"))

    # Test add and remove pickup location
    store = Store()
    store.add_pickup_location(
        "Test Pickup Location",
        Address("123 Test Pickup", None, "Test City", "NJ", "12345"),
        save=True,
    )
    print(store.get_pickup_location("Test Pickup Location"))
    store.remove_pickup_location("Test Pickup Location")
    print(store.get_pickup_location("Test Pickup Location"))

    # Check persistence
    print("\n\nCheck persistence")
    store = Store()
    store.add_food_bank(
        "Test Food Bank",
        Address("123 Test Food Bank", None, "Test City", "NY", "12345"),
    )
    store.add_pickup_location(
        "Test Pickup Location",
        Address("123 Test Pickup", None, "Test City", "NJ", "12345"),
    )
    store = Store()
    print(store.get_food_bank("Test Food Bank"))
    print(store.get_pickup_location("Test Pickup Location"))
    store.remove_food_bank("Test Food Bank")
    store.remove_pickup_location("Test Pickup Location")
    store = Store()
    print(store.get_food_bank("Test Food Bank"))
    print(store.get_pickup_location("Test Pickup Location"))
