import os
import time
import threading
import hashlib


def generate_worker_id(location: str) -> int:
    """
    Generate a worker id in the range [0, 31] from a location string.
    """
    if not isinstance(location, str):
        raise TypeError("location must be a string")
    # Get SHA-256 digest and convert it to an integer.
    h = int(hashlib.sha256(location.encode("utf-8")).hexdigest(), 16)
    return h % 32  # Ensure the worker id fits in 5 bits (0-31)


class Snowflake:
    """
    A simplified Snowflake ID generator using:
      - 41 bits for the timestamp (milliseconds since a custom epoch)
      - 5 bits for the worker id
      - 12 bits for the sequence number
    """

    def __init__(self, worker_id: int, epoch: int = 1577836800000):
        self.worker_id = worker_id & 0x1F  # Ensure it's within 5 bits.
        self.epoch = epoch
        self.sequence = 0
        self.last_ts = -1
        self.lock = threading.Lock()
        self.sequence_mask = (1 << 12) - 1  # 12 bits: 4095
        self.worker_shift = 12  # Worker id is shifted left by 12 bits.
        self.timestamp_shift = 17  # Timestamp is shifted left by (5+12)=17 bits.

    def _timestamp(self) -> int:
        """Return the current time in milliseconds."""
        return int(time.time() * 1000)

    def get_id(self) -> int:
        """Generate and return the next Snowflake ID."""
        with self.lock:
            ts = self._timestamp()

            if ts < self.last_ts:
                raise ValueError("Clock moved backwards. Refusing to generate id.")

            if ts == self.last_ts:
                self.sequence = (self.sequence + 1) & self.sequence_mask
                if self.sequence == 0:
                    # Wait until the next millisecond.
                    while ts <= self.last_ts:
                        ts = self._timestamp()
            else:
                self.sequence = 0

            self.last_ts = ts
            # Construct the 64-bit ID.
            return (
                ((ts - self.epoch) << self.timestamp_shift)
                | (self.worker_id << self.worker_shift)
                | self.sequence
            )


def get_generator() -> Snowflake:
    """
    Returns a singleton Snowflake generator.
    The worker ID is derived from the parent directory name.
    """
    if not hasattr(get_generator, "_generator"):
        # Use the parent directory name to generate a worker id.
        location = os.path.basename(os.path.dirname(os.getcwd()))
        worker_id = generate_worker_id(location)
        get_generator._generator = Snowflake(worker_id)
    return get_generator._generator


def generate_snowflake_id() -> int:
    """Return the next Snowflake ID using the singleton generator."""
    return get_generator().get_id()
