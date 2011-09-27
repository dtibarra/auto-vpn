Connects to a remote website and fetches a password, or bails on failure.

Batteries not included. Requires a 'auto-vpn.conf' file that has the following setup:

"""
[auth]
url = <url_of_portal>
email =<email_address>
password = <password>

[etc]
result_regex = <font color='green'>[a-z]+ -- (?P<vpn_password>[a-zA-Z0-9]+)</font>
"""
