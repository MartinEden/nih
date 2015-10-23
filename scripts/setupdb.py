from sys import argv
import migrate
migrate.setup_db(*argv[1:])
