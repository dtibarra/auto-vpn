Connects to a remote website and fetches a password, or bails on failure.

Batteries not included. Requires a 'auto-vpn.conf' file that has the following setup:

"""
[auth]
url = <url of portal>
email =<email address>
password = <password>
vpn_name = <pptp vpn name>
vpn_server = <server of vpn server>

[etc]
result_regex = <font color='green'>[a-z]+ -- (?P<vpn_password>[a-zA-Z0-9]+)</font>
"""
