import sys, os

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(os.path.join(PROJECT_PATH,'recorders'))
sys.path.append(os.path.join(PROJECT_PATH,'portobject'))

from profilerecorder import ProfileRecorder



