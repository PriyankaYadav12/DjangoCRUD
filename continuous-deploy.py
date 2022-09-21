import os
import sys
import shutil
import subprocess
import time
from optparse import OptionParser

JAVA_HOME="C:/Program Files/Java/jdk-11.0.12"

SLEEP_SECONDS=2

def message(msg):
    now = time.strftime("%H:%M:%S %d %b %Y")
    print >> sys.stderr, ("%s >> %s" % (now, msg))


class TomcatDeployer(object):

    def __init__(self, catalina_home):
        self.catalina_home = catalina_home
    
    def clear_webapps_directory (self):
        webapps_dir = self.get_webapps_dir ()

        message("rm -rf %s" % webapps_dir)
        if os.path.exists(webapps_dir):
            shutil.rmtree(webapps_dir, True)

        message("mkdir %s" % webapps_dir)
        if not os.path.exists(webapps_dir):
            os.makedirs(webapps_dir)

    def clear_work_directory (self):
        work_dir = "%s/work/" % self.catalina_home

        message("rm -rf %s" % work_dir)
        if os.path.exists(work_dir):
            shutil.rmtree(work_dir, True)

    def get_catalina_sh (self) :
        return "%s/bin/catalina.sh" % self.catalina_home

    def get_webapps_dir (self) :
        return "%s/webapps/" % self.catalina_home

    def stop_tomcat (self):
        catalina_sh = self.get_catalina_sh () 
        ret = subprocess.call([ catalina_sh, "stop" ], 
                                env={"JAVA_HOME": JAVA_HOME})

    def start_tomcat (self):
        catalina_sh = self.get_catalina_sh ()
        ret = subprocess.call([ catalina_sh, "start" ], 
                                env={"JAVA_HOME": JAVA_HOME})

    def copy_file (self, warfile):
        webapps_dir = self.get_webapps_dir ()
        root_war = "%s/ROOT.war" % webapps_dir
        
        message("cp %s %s" % (warfile, root_war))
        shutil.copy(warfile, root_war)
        
    def message(self, msg):
        now = time.strftime("%H:%M:%S %d %b %Y")
        print >> sys.stderr, ("%s >> %s" % (now, msg))

    def deploy(self, warfile):
        message("Tomcat Restarting")

        self.clear_webapps_directory ()
        self.clear_work_directory ()

        self.stop_tomcat ()
        time.sleep(2)
        self.copy_file (warfile)
        self.start_tomcat ()

        message("Tomcat Restarted")


class FileWatcher(object):
    """
    Watch a file for changes; trigger a callback.
    """
    
    def __init__(self, warfile, callback):
        self.warfile = warfile
        self.callback = callback

    def get_last_modified(self):
        return os.stat(self.warfile).st_atime

    def watch(self):
        last_modified = self.get_last_modified()
        just_updated = False
        message ("Waiting for Changes.")

        while True:
            time.sleep(SLEEP_SECONDS)
            new_last_modified = self.get_last_modified()
            
            was_updated = False
            if (new_last_modified > last_modified):
                message ("File was updated.")
                message ("Old modified time: %.3f" % last_modified)
                message ("New modified time: %.3f" % new_last_modified)

                was_updated = True

            if (was_updated == False and just_updated == True):
                message ("File has stopped changing.  Deploying.")
                self.callback.deploy (self.warfile)
                new_last_modified = self.get_last_modified()


            just_updated = was_updated
            last_modified = new_last_modified
        
def continuous_deploy(warfile, catalina_home):
    deployer = TomcatDeployer (catalina_home)
    watcher = FileWatcher(warfile, deployer)

    watcher.watch()

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-w", "--war", dest="warfile",
                      help="WAR file to watch")
    parser.add_option("-t", "--tomcat", dest="catalina_home",
                      help="Tomcat file")
    
    (options, args) = parser.parse_args()
    continuous_deploy (options.warfile, options.catalina_home)
