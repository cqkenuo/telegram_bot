import sys
from cx_Freeze import setup, Executable
import os
import pyx.normpath
PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

# base = 'Win32GUI' if sys.platform == 'win32' else None
base = None

buildOptions = dict(
    packages=['test_bot'],
    includes=['selenium', 'nmap', 'telepot', 'pyx', 'pyx.attr',
              'pyx.box', 'pyx.bitmap', 'pyx.mesh', 'pyx.canvas',
              'pyx.color', 'pyx.text', 'pyx.config', 'pyx.bbox',
              'pyx.writer', 'pyx.reader', 'pyx.baseclasses',
              'pyx.connector', 'pyx.pdfwriter', 'pyx.pdfextra',
              'pyx.style', 'pyx.graph', 'pyx.font', 'pyx.document',
              'pyx.deformer', 'pyx.svgfile', 'pyx.svgwriter',
              'pyx.graph.data', 'pyx.graph.style', 'pyx.graph.key',
              'pyx.graph.graph', 'pyx.graph.axis.axis',
              'pyx.graph.axis.painter', 'pyx.pattern',
              'pyx.normpath',
              'pyodbc', 'bs4', 'mysql', 'scapy'],
    include_files=['chromedriver.exe', 'config.json'],
    excludes=[])

executables = [
    Executable(script='test_bot.py',
               base=base,
               icon="icon.ico")
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
