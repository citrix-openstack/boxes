class CannotFindOrMultipleFound(Exception):
    pass


def template_uuid(xenhost, label):
    return xenhost.run(
        'xe template-list name-label="{0}" --minimal'.format(label))


def clone_template(xenhost, src_uuid, tgt_label):
    return xenhost.run(
        'xe vm-clone uuid={0} new-name-label="{1}"'
        .format(src_uuid, tgt_label))


def vm_names(xenhost):
    vm_names = xenhost.run(
        'xe vm-list is-control-domain=false params=name-label --minimal')

    return [vm_name for vm_name in vm_names.split(',') if vm_name]


def vm_halted(xenhost, vm_uuid):
    return 'halted' == xenhost.run(
        'xe vm-param-get param-name=power-state uuid={vm_uuid}'.format(
            vm_uuid=vm_uuid))


def no_vm_with_name(xenhost, guest):
    uuid = xenhost.run("xe vm-list name-label={0} --minimal".format(guest))
    return not bool(uuid.strip())


def vm_by_name(xenhost, vm_name):
    uuids = xenhost.run(
        'xe vm-list name-label={vm_name} --minimal'.format(
            vm_name=vm_name)).strip()

    uuid_list = [uuid for uuid in uuids.split(',') if uuid]

    if len(uuid_list) != 1:
        raise CannotFindOrMultipleFound(vm_name)

    return uuid_list[0]


def vdis_of(xenhost, vm_uuid):
    vdis = xenhost.run(
        'xe vbd-list vm-uuid={vm_uuid} params=vdi-uuid --minimal'.format(
            vm_uuid=vm_uuid)).split(',')
    return [vdi for vdi in vdis if vdi]


def xva_location(xenhost):
    sr_uuid = xenhost.run('xe sr-list name-label="Local storage" --minimal')
    location = '/var/run/sr-mount/' + sr_uuid + '/xvas'
    xenhost.run('mkdir -p {location}'.format(location=location))
    return location


def delete_xva(xenhost, xva_name):
    location = xva_location(xenhost)
    xva_path = location + '/' + xva_name
    xenhost.run('rm -f {xva_path}'.format(xva_path=xva_path))


def filenames_of(xenhost, location):
    return xenhost.run('ls {location}'.format(
            location=location)
        ).strip().split()


def xvas(xenhost):
    location = xva_location(xenhost)
    return filenames_of(xenhost, location)


def export_xva(xenhost, vm_uuid, xva_name):
    location = xva_location(xenhost)
    xva_path = location + '/' + xva_name

    xenhost.run('rm -f {xva_path}.saving'.format(xva_path=xva_path))

    xenhost.run(
        'xe vm-export vm={vm_uuid} compress=true'
        ' filename={xva_path}.saving'.format(
            vm_uuid=vm_uuid, xva_path=xva_path))

    xenhost.run('mv {xva_path}.saving {xva_path}'.format(xva_path=xva_path))


def import_xva(xenhost, xva_name, vm_name):
    location = xva_location(xenhost)
    xva_path = location + '/' + xva_name

    vm_uuid = xenhost.run(
        'xe vm-import filename={xva_path}'.format(xva_path=xva_path))

    xenhost.run(
        'xe vm-param-set uuid={vm_uuid} name-label={vm_name}'.format(
            vm_uuid=vm_uuid, vm_name=vm_name))


def start_vm(xenhost, vm_uuid):
    xenhost.run('xe vm-start uuid={vm_uuid}'.format(vm_uuid=vm_uuid))


def stop_vm(xenhost, vm_uuid):
    xenhost.run('xe vm-shutdown uuid={vm_uuid}'.format(vm_uuid=vm_uuid))
