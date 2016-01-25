
from charmhelpers.core.hookenv import config
from charmhelpers.core.hookenv import status_set
from charmhelpers.core.hookenv import action_get
from charmhelpers.core.hookenv import log

from charms.reactive import hook
from charms.reactive import when

from charms import router


cfg = config()


@hook('install')
def deps():
    pass
    # apt_install('some-stuff')


@hook('config-changed')
def configure():
    pass


@when('vpe.add-site')
def add_site():
    site = action_get('name')
    cidr = action_get('cidr')
    vlan = action_get('vland-tag')
    ethN = action_get('interface')

    link_name = '%s.%s' % (ethN, vlan)

    # move these into router which will ultimately just call ip?
    # need to figure out explicit vs abstracted
    # router.new_site(site, ethN, vlan, cidr)
    #  router.create_namespace(site)
    router.ip('netns', 'add', site)
    #  router.create_vlan(ethN, vlan)
    router.ip('link', 'add', 'link', ethN, 'name', link_name, 'type', 'vlan',
              'id', vlan)
    #  router.vlan_ns(ethN, vlan, site)
    router.ip('link', 'set', 'dev', link_name, 'netns', site)
    #  router.link_up_ns(site, link_name, cidr)
    router.ip('netns', 'exec', site, 'ip', 'link', 'set', 'dev',
              link_name, 'up')
    router.ip('netns', 'exec', site, 'ip', 'address', 'add', cidr,
              'dev', link_name)


@when('vpe.add-corporation')
def add_corporation():
    '''
    Create and Activate the network corporation
    '''

    domain_name = action_get('domain_name')
    iface_name = action_get('iface_name')
    vlan_id = action_get('vlan_id')
    cidr = action_get('cidr')

    missing = []
    for item in [domain_name, iface_name, vlan_id, cidr]:
        if not item:
            missing.append(item)

    if len(missing) > 0:
        log('CRITICAL', 'Unable to complete operation due to missing required'
            'param: {}'.format('item'))

    iface_vlanid = '%s.%s' % (iface_name, vlan_id)

    status_set('maintenance', 'Adding corporation {}'.format(domain_name))

    router.ip('link', 'add', 'link', iface_name, domain_name, vlan_id,
              'type', 'vlan', 'id', vlan_id)
    router.ip('link', 'set', 'dev', iface_vlanid, 'netns', domain_name)
    router.ip('netns', 'exec', domain_name, 'ip', 'link', 'set', 'dev',
              iface_vlanid, 'up')
    router.ip('netns', 'exec', domain_name, 'ip', 'address', 'add', cidr,
              'dev', iface_vlanid)


@when('vpe.remove-site')
def remove_route():
    pass
