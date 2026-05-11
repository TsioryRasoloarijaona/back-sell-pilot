"""MongoDB connection management."""

from pymongo import MongoClient
from pymongo.database import Database


class MongoDB:
    """Small MongoDB client wrapper used by dependency injection."""

    def __init__(self, uri: str, database_name: str) -> None:
        self._uri = uri
        self._database_name = database_name
        self._client: MongoClient | None = None

    def connect(self) -> None:
        """Create the MongoDB client if it does not exist yet."""

        if self._client is None:
            self._client = MongoClient(self._uri)

    def close(self) -> None:
        """Close the MongoDB client."""

        if self._client is not None:
            self._client.close()
            self._client = None

    @property
    def database(self) -> Database:
        """Return the configured MongoDB database."""

        self.connect()
        if self._client is None:
            raise RuntimeError("MongoDB client is not initialized")

        return self._client[self._database_name]
