from pathlib import Path

import pandas as pd
import sqlalchemy as sa

DB_URL = "sqlite:///db.db"

if __name__ == '__main__':
    con = sa.create_engine(DB_URL)

    data_path = Path("adam_ondra_ascents.csv")
    df = pd.read_csv(data_path, index_col=0)

    df.to_sql("ascents", con=con, index=False)
