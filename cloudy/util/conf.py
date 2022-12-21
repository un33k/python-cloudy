import os
import configparser
import logging

LOG_LEVEL = logging.INFO
FORMAT = "%(levelname)-10s %(name)s %(message)s"
logging.basicConfig(format=FORMAT, level=LOG_LEVEL)

class CloudyConfig(object):
    cfg = None
    log = None
    cfg_grid = {}
    
    def __init__(self, filenames='~/.cloudy', log_level=logging.WARN):
        """ Setup logging and ensure file paths are valid - file order is important, last wins """

        self.log = logging.getLogger(os.path.basename(__file__))
        self.log.setLevel(log_level)
        self.cfg = configparser.ConfigParser()

        paths = []
        if isinstance(filenames, basestring):
            filenames = [filenames]
        for f in filenames:
            p = os.path.expanduser(f)
            if os.path.exists(p):
                paths.append(p)
        paths.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../cfg/defaults.cfg")))        
        
        try:
            self.cfg.read(paths)
        except Exception as e:
            self.log.error("Unable to open config file(s) (%s)" % e)
        else:
            for section in self.cfg.sections():
                self.cfg_grid[section] = self._section_map(section)


    def _section_map(self, section):
        """ Create a section map from the valid options """
        valid = {}
        options = self.cfg.options(section)
        for option in options:
            try:
                valid[option] = self.cfg.get(section, option)
                if valid[option] == -1:
                    self.log.debug("skip: %s" % option)
            except:
                self.log.warn("exception on %s!" % option)
                valid[option] = None
        return valid


    def get_variable(self, section, variable, fallback=''):
        """ Given a section and a variable, get the value """
        var = fallback
        try:
            var = self.cfg_grid[section.upper()][variable].strip()
        except:
            pass
        return var


    def add_variable_to_environ(self, section, variable):
        """ Given a config section / variable, set environment variable """
        try:
            var = self.cfg_grid[section][variable]
        except Exception as e:
            self.log.warn("Failed to set environment variable (%s)" % e)
        else:
            if var:
                os.environ[variable] = var
            else:
                self.log.warn("No such a variable (%s)" % variable)
                






