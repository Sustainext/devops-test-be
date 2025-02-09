# snowflake.py
import os
import time
import threading
import hashlib


def generate_location_id(location_string):
    """
    Generates a unique integer ID from a location string using SHA-256 hashing.

    This method takes a location string as input and produces a large, unique integer ID.
    It uses SHA-256 hashing to ensure a high degree of uniqueness and a large output space,
    suitable for replacing datacenter_id in snowflake ID generation.

    Args:
        location_string: The string representing the location of the backend instance.

    Returns:
        int: A unique integer ID derived from the location string.
             This will be a large integer representing the SHA-256 hash of the location string.

    Raises:
        TypeError: if the input is not a string.
    """
    if not isinstance(location_string, str):
        raise TypeError("Input must be a string.")

    # Encode the location string to bytes (UTF-8 encoding is common and good default)
    encoded_location = location_string.encode("utf-8")

    # Generate SHA-256 hash of the encoded location
    hashed_location = hashlib.sha256(encoded_location)

    # Get the hexadecimal representation of the hash
    hex_digest = hashed_location.hexdigest()

    # Convert the hexadecimal digest to an integer (base 16)
    location_id_int = int(hex_digest, 16)
    return location_id_int


class SnowflakeGenerator:
    """
    A simplified Snowflake ID generator using:
      - 41 bits for the timestamp (in milliseconds)
      - 5 bits for the worker id (0-31)
      - 12 bits for a sequence number (0-4095)
    """

    def __init__(self, worker_id: int, sequence: int = 0):
        self.worker_id = worker_id  # 5 bits (0-31)
        self.sequence = sequence  # 12 bits (0-4095)
        self.lock = threading.Lock()
        self.last_timestamp = -1

        self.sequence_bits = 12
        self.worker_bits = 5
        self.max_sequence = (1 << self.sequence_bits) - 1  # 4095

        # The worker ID is shifted by the number of sequence bits.
        self.worker_id_shift = self.sequence_bits  # 12 bits
        # The timestamp is shifted by (worker_bits + sequence_bits) = 5 + 12 = 17 bits.
        self.timestamp_shift = self.worker_bits + self.sequence_bits

        # Custom epoch (e.g., Jan 1, 2020 in milliseconds)
        self.epoch = 1577836800000

    def _timestamp(self) -> int:
        """Return the current time in milliseconds."""
        return int(time.time() * 1000)

    def next_id(self) -> int:
        """Generate and return the next Snowflake ID."""
        with self.lock:
            timestamp = self._timestamp()

            if timestamp < self.last_timestamp:
                raise ValueError("Clock moved backwards. Refusing to generate id.")

            if timestamp == self.last_timestamp:
                # Same millisecond: increment the sequence.
                self.sequence = (self.sequence + 1) & self.max_sequence
                if self.sequence == 0:
                    # Sequence exhausted in the current millisecond; wait for the next millisecond.
                    while timestamp <= self.last_timestamp:
                        timestamp = self._timestamp()
            else:
                # New millisecond: reset sequence.
                self.sequence = 0

            self.last_timestamp = timestamp

            # Build the ID by shifting and combining components.
            snowflake_id = (
                ((timestamp - self.epoch) << self.timestamp_shift)
                | (self.worker_id << self.worker_id_shift)
                | self.sequence
            )
            return snowflake_id


def get_snowflake_generator() -> SnowflakeGenerator:
    """
    Return a singleton instance of the SnowflakeGenerator.
    The instance is stored as an attribute of this function.
    """
    if not hasattr(get_snowflake_generator, "_generator"):
        # Read the worker id from an environment variable; default to 0 if not provided.
        worker_id = generate_location_id(os.getcwd().split("/")[-2])
        get_snowflake_generator._generator = SnowflakeGenerator(worker_id=worker_id)
    return get_snowflake_generator._generator


def generate_snowflake_id() -> int:
    """
    Return the next Snowflake ID using the generator instance.
    """
    generator = get_snowflake_generator()
    return generator.next_id()
