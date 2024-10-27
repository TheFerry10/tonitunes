import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SLEEP_TIME_BETWEEN_READS_IN_SECONDS = 1


class DevelopmentConfig(Config):
    def init_queue_client(self):
        pass

    def init_rfid_module(self):
        pass


class TestingConfig(Config):
    pass


class ProductionConfig(Config):
    QUEUE_NAME = os.getenv("QUEUE_NAME")


class AzureConfig(ProductionConfig):

    CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    @classmethod
    def init_queue_client(cls):
        import logging

        from azure.core.exceptions import ResourceExistsError
        from azure.storage.queue import QueueServiceClient

        logging.basicConfig(
            level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
        )

        queue_service_client = QueueServiceClient.from_connection_string(
            cls.CONNECTION_STRING
        )
        queue_client = queue_service_client.get_queue_client(queue=cls.QUEUE_NAME)

        try:
            queue_client.create_queue()
            logging.info("Queue %s created successfully.", cls.QUEUE_NAME)

        except ResourceExistsError:
            logging.info("Queue %s already exists.", cls.QUEUE_NAME)
        return queue_client


config = {
    "default": DevelopmentConfig,
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "azure": AzureConfig,
}
