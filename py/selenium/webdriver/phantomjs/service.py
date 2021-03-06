#!/usr/bin/python
#
# Copyright 2012 Software Freedom Conservancy
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import absolute_import

import platform
import signal
import subprocess
import time

from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.baseservice import BaseService
from selenium.webdriver.common import utils


class Service(BaseService):
    """
    Object that manages the starting and stopping of PhantomJS / Ghostdriver
    """

    def __init__(self, executable_path, port=0, service_args=None, log_path=None):
        """
        Creates a new instance of the Service

        :Args:
         - executable_path : Path to PhantomJS binary
         - port : Port the service is running on
         - service_args : A List of other command line options to pass to PhantomJS
         - log_path: Path for PhantomJS service to log to
        """
        super(Service, self).__init__(executable_path, port=port)
        self.service_args = service_args
        if self.service_args is None:
            self.service_args = []
        else:
            self.service_args = service_args[:]
        self.service_args.insert(0, self.path)
        self.service_args.append("--webdriver=%d" % self.port)
        self.process = None
        if not log_path:
            log_path = "ghostdriver.log"
        self._log = open(log_path, 'w')

    def __del__(self):
        # subprocess.Popen doesn't send signal on __del__;
        # we have to try to stop the launched process.
        self.stop()

    @property
    def _start_kwargs(self):
        return dict(stdin=subprocess.PIPE,
                    close_fds=platform.system() != 'Windows',
                    stdout=self._log, stderr=self._log)

    @property
    def _start_args(self):
        return self.service_args

    @property
    def service_url(self):
        """
        Gets the url of the GhostDriver Service
        """
        return "{0}/wd/hub".format(super(Service, self).service_url)

    def stop(self):
        """
        Cleans up the process
        """
        if self._log:
            self._log.close()
            self._log = None
        #If its dead dont worry
        if self.process is None:
            return

        #Tell the Server to properly die in case
        try:
            if self.process:
                self.process.send_signal(signal.SIGTERM)
                self.process.wait()
        except OSError:
            # kill may not be available under windows environment
            pass
