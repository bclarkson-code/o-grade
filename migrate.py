from pathlib import Path

import pandas as pd
import sqlalchemy as sa

DB_URL = "sqlite:///db.db"


def create_submission_table(engine: sa.engine.Engine):
    query = """
    CREATE TABLE IF NOT EXISTS submission(
        zlaggableName TEXT,
        cragName TEXT,
        countryName TEXT,
        date TEXT,
        "O-grade" TEXT,
        difficulty TEXT
    );
    """
    with engine.connect() as db:
        db.execute(sa.text(query))
        db.commit()


if __name__ == "__main__":
    con = sa.create_engine(DB_URL)
    create_submission_table(con)

    data_path = Path("adam_ondra_ascents.csv")
    df = pd.read_csv(data_path, index_col=0)

    df.to_sql("ascents", con=con, index=False)
