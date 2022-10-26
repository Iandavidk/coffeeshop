import os
database_filename = "database.db"
project_dir = os.path.dirname(os.path.abspath(__file__))


database_link="sqlite:///{}".format(os.path.join(project_dir, database_filename))

