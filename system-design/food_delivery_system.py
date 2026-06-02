"""Food Delivery System - interview-grade reference implementation.

This module models a simplified DoorDash/Uber Eats style backend with:
- Restaurant management
- Order lifecycle management
- Driver assignment
- Live tracking and ETA updates
- Batch delivery planning

The design intentionally keeps infrastructure in-memory so the core
object model and system behavior are easy to discuss in an interview.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import math
from typing import Dict, List, Optional, Sequence, Tuple
from uuid import uuid4


class OrderStatus(Enum):
    """Represents the lifecycle state of an order."""

    CREATED = "created"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY_FOR_PICKUP = "ready_for_pickup"
    PICKED_UP = "picked_up"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class DriverStatus(Enum):
    """Represents the current availability state of a driver."""

    OFFLINE = "offline"
    AVAILABLE = "available"
    ASSIGNED = "assigned"


@dataclass(frozen=True)
class Location:
    """Stores latitude/longitude coordinates and offers distance helpers."""

    lat: float
    lon: float

    def distance_to(self, other: "Location") -> float:
        """Returns straight-line distance in kilometers using Haversine."""
        earth_radius_km = 6371.0
        lat1 = math.radians(self.lat)
        lat2 = math.radians(other.lat)
        dlat = lat2 - lat1
        dlon = math.radians(other.lon - self.lon)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        return 2 * earth_radius_km * math.asin(math.sqrt(a))


@dataclass(frozen=True)
class MenuItem:
    """Represents an item a restaurant can sell."""

    item_id: str
    name: str
    price: float


@dataclass
class Restaurant:
    """Represents a restaurant with location and menu metadata."""

    restaurant_id: str
    name: str
    location: Location
    menu: Dict[str, MenuItem] = field(default_factory=dict)
    is_open: bool = True


@dataclass
class Driver:
    """Represents a delivery driver and the orders assigned to them."""

    driver_id: str
    name: str
    location: Location
    status: DriverStatus = DriverStatus.OFFLINE
    active_order_ids: List[str] = field(default_factory=list)


@dataclass
class OrderItem:
    """Represents a requested menu item and quantity for an order."""

    item_id: str
    quantity: int


@dataclass
class Order:
    """Represents an end-to-end customer order."""

    order_id: str
    customer_id: str
    restaurant_id: str
    delivery_address: Location
    items: List[OrderItem]
    status: OrderStatus = OrderStatus.CREATED
    assigned_driver_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    estimated_delivery_at: Optional[datetime] = None


class FoodDeliverySystem:
    """Coordinates restaurants, orders, drivers, assignment, and tracking."""

    def __init__(
        self,
        max_batch_size: int = 2,
        prep_minutes_default: int = 12,
        avg_driver_speed_kmh: float = 28.0,
    ) -> None:
        """Initializes the in-memory stores and routing parameters."""
        self._restaurants: Dict[str, Restaurant] = {}
        self._drivers: Dict[str, Driver] = {}
        self._orders: Dict[str, Order] = {}
        self.max_batch_size = max_batch_size
        self.prep_minutes_default = prep_minutes_default
        self.avg_driver_speed_kmh = avg_driver_speed_kmh

    # -------- Restaurant management --------
    def add_restaurant(self, name: str, location: Location) -> Restaurant:
        """Creates and stores a restaurant."""
        restaurant = Restaurant(restaurant_id=str(uuid4()), name=name, location=location)
        self._restaurants[restaurant.restaurant_id] = restaurant
        return restaurant

    def add_menu_item(
        self, restaurant_id: str, item_name: str, price: float
    ) -> MenuItem:
        """Adds a menu item to an existing restaurant."""
        restaurant = self._get_restaurant_or_raise(restaurant_id)
        menu_item = MenuItem(item_id=str(uuid4()), name=item_name, price=price)
        restaurant.menu[menu_item.item_id] = menu_item
        return menu_item

    def set_restaurant_open_state(self, restaurant_id: str, is_open: bool) -> None:
        """Updates whether a restaurant is currently accepting orders."""
        restaurant = self._get_restaurant_or_raise(restaurant_id)
        restaurant.is_open = is_open

    # -------- Driver management --------
    def register_driver(self, name: str, location: Location) -> Driver:
        """Creates and registers a driver in offline state."""
        driver = Driver(driver_id=str(uuid4()), name=name, location=location)
        self._drivers[driver.driver_id] = driver
        return driver

    def set_driver_status(self, driver_id: str, status: DriverStatus) -> None:
        """Sets a driver's availability status."""
        driver = self._get_driver_or_raise(driver_id)
        driver.status = status

    def update_driver_location(self, driver_id: str, location: Location) -> None:
        """Updates a driver's current location for tracking and assignment."""
        driver = self._get_driver_or_raise(driver_id)
        driver.location = location
        for order_id in driver.active_order_ids:
            order = self._orders[order_id]
            order.estimated_delivery_at = self._predict_eta(order, driver)

    # -------- Order management --------
    def place_order(
        self,
        customer_id: str,
        restaurant_id: str,
        delivery_address: Location,
        items: Sequence[OrderItem],
    ) -> Order:
        """Creates a customer order after validating restaurant and menu items."""
        restaurant = self._get_restaurant_or_raise(restaurant_id)
        if not restaurant.is_open:
            raise ValueError(f"Restaurant '{restaurant.name}' is currently closed.")
        if not items:
            raise ValueError("Order must contain at least one item.")

        for item in items:
            if item.item_id not in restaurant.menu:
                raise ValueError(f"Menu item {item.item_id} not offered by restaurant.")
            if item.quantity <= 0:
                raise ValueError("Quantity must be a positive integer.")

        order = Order(
            order_id=str(uuid4()),
            customer_id=customer_id,
            restaurant_id=restaurant_id,
            delivery_address=delivery_address,
            items=list(items),
            status=OrderStatus.CONFIRMED,
        )
        self._orders[order.order_id] = order
        return order

    def update_order_status(self, order_id: str, new_status: OrderStatus) -> None:
        """Transitions an order status with basic state machine constraints."""
        order = self._get_order_or_raise(order_id)
        allowed_transitions = {
            OrderStatus.CREATED: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
            OrderStatus.CONFIRMED: {OrderStatus.PREPARING, OrderStatus.CANCELLED},
            OrderStatus.PREPARING: {
                OrderStatus.READY_FOR_PICKUP,
                OrderStatus.CANCELLED,
            },
            OrderStatus.READY_FOR_PICKUP: {OrderStatus.PICKED_UP, OrderStatus.CANCELLED},
            OrderStatus.PICKED_UP: {OrderStatus.DELIVERED},
            OrderStatus.DELIVERED: set(),
            OrderStatus.CANCELLED: set(),
        }
        if new_status not in allowed_transitions[order.status]:
            raise ValueError(f"Illegal status transition: {order.status} -> {new_status}")
        order.status = new_status

        if new_status in {OrderStatus.DELIVERED, OrderStatus.CANCELLED}:
            self._release_driver_assignment(order)

    # -------- Assignment, ETA, and tracking --------
    def assign_driver(self, order_id: str) -> Optional[Driver]:
        """Assigns the best available driver to an order based on distance."""
        order = self._get_order_or_raise(order_id)
        if order.assigned_driver_id:
            return self._drivers[order.assigned_driver_id]

        restaurant = self._get_restaurant_or_raise(order.restaurant_id)
        candidates = [
            driver
            for driver in self._drivers.values()
            if driver.status == DriverStatus.AVAILABLE
            and len(driver.active_order_ids) < self.max_batch_size
        ]
        if not candidates:
            return None

        best_driver = min(
            candidates,
            key=lambda d: self._assignment_cost(d, restaurant.location, order.delivery_address),
        )

        order.assigned_driver_id = best_driver.driver_id
        best_driver.active_order_ids.append(order.order_id)
        best_driver.status = DriverStatus.ASSIGNED
        order.estimated_delivery_at = self._predict_eta(order, best_driver)
        return best_driver

    def get_order_tracking(self, order_id: str) -> Dict[str, object]:
        """Returns live tracking details for client apps and support tooling."""
        order = self._get_order_or_raise(order_id)
        driver = self._drivers.get(order.assigned_driver_id) if order.assigned_driver_id else None
        return {
            "order_id": order.order_id,
            "status": order.status.value,
            "driver_id": order.assigned_driver_id,
            "driver_location": (driver.location.lat, driver.location.lon) if driver else None,
            "eta": order.estimated_delivery_at.isoformat() if order.estimated_delivery_at else None,
        }

    def plan_batch_route(self, driver_id: str) -> List[Tuple[str, str]]:
        """Builds a simple dynamic route plan for a driver's active deliveries."""
        driver = self._get_driver_or_raise(driver_id)
        if not driver.active_order_ids:
            return []

        route: List[Tuple[str, str]] = []
        current_position = driver.location
        pending_orders = [self._orders[oid] for oid in driver.active_order_ids]

        # Nearest-neighbor route over pickup and drop-off waypoints.
        while pending_orders:
            next_order = min(
                pending_orders,
                key=lambda order: current_position.distance_to(
                    self._restaurants[order.restaurant_id].location
                    if order.status in {OrderStatus.CONFIRMED, OrderStatus.PREPARING, OrderStatus.READY_FOR_PICKUP}
                    else order.delivery_address
                ),
            )
            if next_order.status in {OrderStatus.CONFIRMED, OrderStatus.PREPARING, OrderStatus.READY_FOR_PICKUP}:
                current_position = self._restaurants[next_order.restaurant_id].location
                route.append((next_order.order_id, "pickup"))
            else:
                current_position = next_order.delivery_address
                route.append((next_order.order_id, "dropoff"))
                pending_orders.remove(next_order)
                continue

            # Simulate pickup complete and proceed to its drop-off on next pass.
            next_order.status = OrderStatus.PICKED_UP
        return route

    # -------- Internal helpers --------
    def _assignment_cost(
        self, driver: Driver, restaurant_location: Location, customer_location: Location
    ) -> float:
        """Computes weighted cost of assigning a driver to an order."""
        to_restaurant = driver.location.distance_to(restaurant_location)
        to_customer = restaurant_location.distance_to(customer_location)
        load_penalty = 1.8 * len(driver.active_order_ids)
        return to_restaurant + to_customer + load_penalty

    def _predict_eta(self, order: Order, driver: Driver) -> datetime:
        """Estimates delivery time using prep delay and travel durations."""
        restaurant = self._get_restaurant_or_raise(order.restaurant_id)
        km_to_pickup = driver.location.distance_to(restaurant.location)
        km_to_dropoff = restaurant.location.distance_to(order.delivery_address)
        total_hours = (km_to_pickup + km_to_dropoff) / self.avg_driver_speed_kmh
        travel_minutes = max(1, int(total_hours * 60))
        eta_minutes = self.prep_minutes_default + travel_minutes
        return datetime.utcnow() + timedelta(minutes=eta_minutes)

    def _release_driver_assignment(self, order: Order) -> None:
        """Releases the assigned driver when an order completes or is cancelled."""
        if not order.assigned_driver_id:
            return
        driver = self._drivers[order.assigned_driver_id]
        if order.order_id in driver.active_order_ids:
            driver.active_order_ids.remove(order.order_id)
        if not driver.active_order_ids:
            driver.status = DriverStatus.AVAILABLE
        order.assigned_driver_id = None

    def _get_restaurant_or_raise(self, restaurant_id: str) -> Restaurant:
        """Returns a restaurant by id or raises a descriptive error."""
        restaurant = self._restaurants.get(restaurant_id)
        if not restaurant:
            raise KeyError(f"Restaurant {restaurant_id} not found.")
        return restaurant

    def _get_driver_or_raise(self, driver_id: str) -> Driver:
        """Returns a driver by id or raises a descriptive error."""
        driver = self._drivers.get(driver_id)
        if not driver:
            raise KeyError(f"Driver {driver_id} not found.")
        return driver

    def _get_order_or_raise(self, order_id: str) -> Order:
        """Returns an order by id or raises a descriptive error."""
        order = self._orders.get(order_id)
        if not order:
            raise KeyError(f"Order {order_id} not found.")
        return order


ARCHITECTURE_MERMAID = """
```mermaid
flowchart TD
    CustomerApp[Customer App] -->|Place / Track Order| API[FoodDeliverySystem API Layer]
    DriverApp[Driver App] -->|Location & Status Updates| API
    RestaurantPanel[Restaurant Panel] -->|Menu / Order Readiness| API

    API --> OrderSvc[Order Service]
    API --> AssignSvc[Driver Assignment Service]
    API --> TrackSvc[Tracking & ETA Service]
    API --> RouteSvc[Batch Routing Service]
    API --> RestSvc[Restaurant Service]
    API --> DriverSvc[Driver Service]

    RestSvc --> RestaurantStore[(Restaurant Store)]
    DriverSvc --> DriverStore[(Driver Store)]
    OrderSvc --> OrderStore[(Order Store)]

    AssignSvc --> DriverStore
    AssignSvc --> RestaurantStore
    AssignSvc --> OrderStore

    TrackSvc --> DriverStore
    TrackSvc --> OrderStore
    TrackSvc --> ETAEngine[ETA Predictor]

    RouteSvc --> DriverStore
    RouteSvc --> OrderStore
    RouteSvc --> RouteEngine[Dynamic Route Planner]

    OrderSvc --> Events[(Order Lifecycle Events)]
    DriverSvc --> Events
    Events --> Notifications[Push Notifications / Webhooks]
```
"""