import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.database import get_db_connection
from app.models import init_db


products = [
    (
        "Jenkins",
        "CI/CD",
        "Open-source automation server for building, testing, and deploying applications.",
        59.00
    ),
    (
        "Docker",
        "Containers",
        "Container platform for packaging and running applications.",
        49.00
    ),
    (
        "Kubernetes",
        "Containers",
        "Container orchestration platform for deploying and managing workloads.",
        79.00
    ),
    (
        "Terraform",
        "Infrastructure as Code",
        "Infrastructure as Code tool for provisioning cloud infrastructure.",
        69.00
    ),
    (
        "Ansible",
        "Automation",
        "Automation and configuration management platform.",
        55.00
    ),
    (
        "Prometheus",
        "Monitoring",
        "Monitoring and alerting toolkit for cloud-native environments.",
        39.00
    ),
    (
        "Grafana",
        "Monitoring",
        "Visualization and observability platform for metrics and data.",
        45.00
    ),
    (
        "Apache Kafka",
        "Messaging",
        "Distributed event streaming platform.",
        65.00
    ),
    (
        "AWS",
        "Cloud",
        "Cloud computing platform offering infrastructure and managed services.",
        99.00
    ),
    (
        "Microsoft Azure",
        "Cloud",
        "Cloud computing platform for applications and infrastructure.",
        99.00
    ),
    (
        "Google Cloud",
        "Cloud",
        "Cloud platform for computing, storage, networking, and managed services.",
        99.00
    ),
    (
        "Helm",
        "Kubernetes",
        "Package manager for Kubernetes applications.",
        35.00
    )
]


def seed_products():
    init_db()

    connection = get_db_connection()

    connection.execute("DELETE FROM products")
    connection.execute("DELETE FROM sqlite_sequence WHERE name='products'")

    connection.executemany(
        """
        INSERT INTO products
        (name, category, description, price)
        VALUES (?, ?, ?, ?)
        """,
        products
    )

    connection.commit()
    connection.close()

    print("DevOpsMart products seeded successfully.")


if __name__ == "__main__":
    seed_products()
