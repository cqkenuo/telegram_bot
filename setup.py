from cx_Freeze import setup, Executable
import os

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

buildOptions = dict(
    packages=['test_bot', 'generator', 'bot'],
    includes=['selenium', 'cx_Freeze', 'nmap', 'telepot',
              'pyodbc', 'bs4', 'mysql', 'scapy'],
    include_files=['chromedriver.exe', 'config.json'],
    excludes=[])

executables = [
    Executable('test_bot.py')
]

setup(name="telegram_bot",
      version="1.0.0",
      description="telegram bot",
      author="Francois van Wyk",
      author_email="searchnot4213@gmail.com",
      url="https://github.com/takenagain/telegram_bot",
      license="MIT License (MIT)",
      options=dict(build_exe=buildOptions),
      executables=executables)
