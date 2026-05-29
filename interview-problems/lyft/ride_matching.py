# Ride matching system
# Problema

# “Tienes conductores y pasajeros en un mapa. Encuentra el conductor más cercano.”

# Inputs:
# drivers = [
#   (driver_id, x, y)
# ]

# request = (x, y)

# Lo que evalúan
# * Algoritmos
# * Spatial indexing
# * Escalabilidad


class RideMatching(object):
    def __init__(self):
        pass

    def closest_driver(self, drivers: list[tuple[str, float, float]], rider: tuple[float, float]) -> str | None:
        """
        Find the closest driver to the rider
        type drivers: list[tuple[str, float, float]]
        type rider: tuple[float, float]
        rtype: str | None
        """
        if not drivers:
            return None

        rx, ry = rider
        best_driver = None
        best_distance = float("inf")

        for driver_id, dx, dy in drivers:
            distance = (dx - rx) ** 2 + (dy - ry) ** 2

            if distance < best_distance:
                best_distance = distance
                best_driver = driver_id

        return best_driver

    def closest_driver_grid_partitioning(self, drivers: list[tuple[str, float, float]], rider: tuple[float, float]) -> str | None:
        """
        Find the closest driver to the rider using grid partitioning
        type drivers: list[tuple[str, float, float]]
        type rider: tuple[float, float]
        rtype: str | None
        """
        if not drivers:
            return None

        rx, ry = rider
        best_driver = None
        best_distance = float("inf")
        
        
        for driver_id, dx, dy in drivers:
            distance = (dx - rx) ** 2 + (dy - ry) ** 2

            if distance < best_distance:
                best_distance = distance
                best_driver = driver_id

        return best_driver
