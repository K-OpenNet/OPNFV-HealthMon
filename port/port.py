#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

from oslo_config import cfg

from tacker.agent.linux import utils as linux_utils
from tacker.common import log
from tacker.i18n import _LW
from tacker.openstack.common import log as logging
from tacker.vm.monitor_drivers import abstract_driver
from socket import *

LOG = logging.getLogger(__name__)
OPTS = [
    cfg.StrOpt('count', default='3', help=_('number of checking port to decide port error.')),
    cfg.StrOpt('timeout', default='1', help=_('number of seconds to wait for a response')),
    cfg.StrOpt('sockmode', default='1', help=_('socket mode of TCP, UDP(TCP:1, UDP:0)')),
    cfg.StrOpt('scanports', default='22', help=_('number of Target port'))
]
cfg.CONF.register_opts(OPTS, 'monitor_port')

class VNFMonitorPort(abstract_driver.VNFMonitorAbstractDriver):
    def get_type(self):
        return 'port'

    def get_name(self):
        return 'port'

    def get_description(self):
        return 'Tacker VNFMonitor Port Driver'

    def monitor_url(self, plugin, context, device):
        LOG.debug(_('monitor_url %s'), device)
        return device.get('monitor_url', '')

    def _is_portable(self, mgmt_ip="", count=3, timeout=1, sockmode=1, scanports=22, **kwargs):

        """Checks whether an port is used by application.
        Using portscanning , it can check application port which is used by application. 
        Use socket library , it can check port of target VM.
        
        :param mgmt_ip: Target VM management IP address
        :param count: number of port error.
        :param timeout: number of seconds to wait for a response
        :param sockmode:socket mode of TCP, UDP(TCP:1, UDP:0)
        :param scanports: number of Target port
        :return: bool - True or string 'failure' depending on portability.
        """

        try:
            while count > 0:
                if sockmode:
                    connskt = socket(AF_INET, SOCK_STREAM)
                else:
                    connskt = socket(AF_INET, SOCK_DGRAM)
                connskt.settimeout(timeout)
                result = connskt.connect_ex((mgmt_ip,scanports))
                if result == 0:
                    LOG.debug(_("OPEN ip address: %s, port: %d\n"), mgmt_ip, scanports)
                    connskt.close()
                    break
                else:
                    LOG.debug(_("Close ip address: %s, port: %d\n"), mgmt_ip, scanports)
                    connskt.close()
                    count = count-1

            if count == 0:
                return 'failure'
            else:
                return True
        except RuntimeError:
            return 'failure'

    @log.log
    def monitor_call(self, device, kwargs):
        if not kwargs['mgmt_ip']:
            return

        return self._is_portable(**kwargs)