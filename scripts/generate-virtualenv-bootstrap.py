import virtualenv, textwrap
output = virtualenv.create_bootstrap_script(textwrap.dedent("""
import os, subprocess
def after_install(options, home_dir):
    etc = join(home_dir, 'etc')
    if not os.path.exists(etc):
        os.makedirs(etc)
    subprocess.call([join(home_dir, 'bin', 'pip'),
                     'install', '-r', 'scripts/requirements.txt'])

def extend_parser(optparse_parser):
	optparse_parser.remove_option("--no-site-packages")
	optparse_parser.remove_option("--system-site-packages")

def adjust_options(options, args):
	options.system_site_packages = True
"""))

f = open('virtualenv-bootstrap.py', 'w').write(output)