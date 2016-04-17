default['server']['hosts'] = [
  {% for value1 in values %}
  {
   'hostname'  => '{{ value1['hostname'] }}',
   'mac' => '{{ value1['int1mac'] }}',
   'ip_address' => '{{ value1['pxe_ip'] }}',
   'perm_address' => '{{ value1['perm_ip'] }}',
   'kick_start_template' => '{{ value1['template'] }}',
   'operating_system_version' => '{{ value1['osversion'] }}',
   'operating_system' => '{{ value1['operatingsystem'] }}'
  {% if not loop.last %}
 },
  {% endif %}
  {% if loop.last %}
 }
  {% endif %}
  {% endfor %}
]

