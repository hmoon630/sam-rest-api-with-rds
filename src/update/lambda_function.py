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
    product_columns = ["name", "category"]
    id = event.pop("id", None)
    valid_attributes = [
        (key, value) for key, value in event.items() if key in product_columns
    ]

    condition = ", ".join([f"{key}=%s" for key, _ in valid_attributes])
    sql_args = tuple([value for _, value in valid_attributes] + [id])

    if id is None:
        return {"message": "You must provide id"}
    if not condition:
        return {"message": "You must provide name or category or both."}

    # Exequte query
    conn = get_connection()
    sql_product_update = f"UPDATE product SET {condition} WHERE id=%s"
    sql_product_select_id = "SELECT * FROM product WHERE id=%s"

    with conn.cursor() as cur:
        cur.execute(sql_product_update, sql_args)
        cur.execute(sql_product_select_id, id)
        result = cur.fetchone()
        conn.commit()

    # Return response
    if result is None:
        return {"message": f"Product {id} not found"}
    item = {"id": result[0], "name": result[1], "category": result[2]}
    return {"message": f"Product {id} updated", "item": json.dumps(item)}
