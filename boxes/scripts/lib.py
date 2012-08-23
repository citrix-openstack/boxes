def template_uuid(xenhost, label):
    return xenhost.run(
        'xe template-list name-label="{0}" --minimal'.format(label))


def clone_template(xenhost, src_uuid, tgt_label):
    return xenhost.run(
        'xe vm-clone uuid={0} new-name-label="{1}"'
        .format(src_uuid, tgt_label))
