from db import database
from frame import Window

database.configurar_banco()
with database.conn as conn:
    window = Window(database)
    window.setup()
