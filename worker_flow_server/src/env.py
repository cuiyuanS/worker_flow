from configparser import ConfigParser, ExtendedInterpolation
import os

basedir = os.path.abspath(os.path.dirname(__file__))

cf = ConfigParser(interpolation=ExtendedInterpolation())
cf.read(os.path.abspath(os.path.join(basedir, "..", "config.ini")), encoding="utf-8")