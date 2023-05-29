import os
import sys
import logging
import json

import pymysql
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client("secretsmanager")

# rds settings

CONNECTION = None


def get_secret():
    response = client.get_secret_value(SecretId=os.environ.get("SECRET_NAME"))

    secret = json.loads(response["SecretString"])
    return secret


def get_connection():
    global CONNECTION
    if CONNECTION:
        return CONNECTION

    secret = get_secret()

    rds_host = secret["host"]
    user_name = secret["username"]
    password = secret["password"]
    db_name = secret["database"]

    # create the database connection outside of the handler to allow connections to be
    # re-used by subsequent function invocations.
    try:
        CONNECTION = pymysql.connect(
            host=rds_host,
            user=user_name,
            passwd=password,
            db=db_name,
            connect_timeout=5,
        )
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()

    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")
    return CONNECTION


def lambda_handler(event, context):
    # Parameter validation
    name = event.get("name", None)
    category = event.get("category", None)

    if name is None or category is None:
        return {"message": "You must provide name and category"}

    # Execute query
    conn = get_connection()
    sql_product_insert = "insert into product (name, category) values(%s, %s)"
    with conn.cursor() as cur:
        cur.execute(sql_product_insert, (name, category))
        conn.commit()
        id = cur.lastrowid

    # Return response
    item = {"id": id, "name": name, "category": category}
    return {"message": f"Product {id} created", "item": json.dumps(item)}
