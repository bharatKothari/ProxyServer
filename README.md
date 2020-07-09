# HTTP/HTTPS Proxy Server in Python


A proxy server is a server application or appliance that acts as an intermediary for requests from clients seeking resources from servers that provide those resources.A proxy server thus functions on behalf of the client when requesting service, potentially masking the true origin of the request to the resource server.   

Instead of connecting directly to a server that can fulfill a requested resource, such as a file or web page for example, the client directs the request to the proxy server, which evaluates the request and performs the required network transactions. This serves as a method to simplify or control the complexity of the request, or provide additional benefits such as load balancing, privacy, or security.

## Forward Proxy

Forward Proxies can make requests appear as if they originated from the proxy's IP address. This can be useful if a proxy is used to provide client anonymity, but in other cases information from the original request is lost. The IP address of the original client is often used for debugging, statistics, or generating location-dependent content.
![Forward Proxy Server](https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Open_proxy_h2g2bob.svg/1920px-Open_proxy_h2g2bob.svg.png)

## Features 

* HTTP/ HTTPS protocol
* Supports caching of HTTPS websites.
* IP Hiding.
* Dynamic blocking/unblocking of websites.
* Socket and other parameters configurable.
* Configuration file supported for deployment (CLI version)
* Deployed on EC2, can be used as a cloud based web proxy.


## Script Info

* A single script written in Python 3.x
* Uses socket API in Python, based on Berkeley sockets API. 
* GUI added using Tkinter library.
* Used AWS EC2 for deployment.
* Tested on EC2 and local LAN server.


