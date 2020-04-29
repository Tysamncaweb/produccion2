{
    'name': 'Biometric Device',
    'version': '1.0',
    'summary': """Biometric Device With Attendance""",
    'category': 'human resources',
    'website': "http://www.ourcompany.com",
    'depends': ['base_setup', 'hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'views/zk_machine_view.xml',
        'views/zk_machine_attendance_view.xml',
    ],
    'external_dependencies': {
        'python2.7': ['zklib']
    },
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
