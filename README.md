The purpose of this program - NodeNs Gateway - is to operate an MQTT gateway for connection to NodeNs sensors. The gateway will detect NodeNs sensors connected to the MQTT host, process their data, and optionally publish to a Cloud service and/or save to local storage.

## Installation
NodeNs Gateway can be installed using pip:
```
pip install nodens.gateway
```

### Troubleshooting
**Installing PyYaml**. Pip sometimes has trouble installing the PyYaml package. If you experience this, it may be easier to install it manually:
```
pip install pyyaml
```

## Operation
NodeNs Gateway can be executed directly from the command line as follows:
```
python -m nodens.gateway
```

It can also be imported as a library into your own scripts:
```import nodens.gateway```

On execution, as a first step it will search for the configuration file ```config-gateway.yaml``` to define the MQTT broker and other basic settings. The program will first search for the config file in the User's (your) default config folder, and then in the folder you've executed the program from. If the config file is not found, it will create one based on a default configuration. [Click here for details of the Configuration](##Configuration).

If a Cloud service operation has been specified, the script will also search for relevant access tokens or certificates.

## Configuration
### Location of configuration file 
The program will search for the configuration file ```config-gateway.yaml``` in the following order:

1.  In the user config folder, e.g.
    - Windows: */Users/\<user>/AppData/Local/NodeNs/Gateway/*
    - Unix:  *~/.config/Gateway/*
2.  In the current working folder.
3.  In *<System documents folder>/NodeNs/*
4.  In *<System documents folder>/*
5.  Otherwise, a default config file will be created in the user folder, and the program will print its location. Feel free to edit it as necessary!

### Description of settings

**Program**

*WRITE_FLAG* : Set to *1* if you require sensor data to be saved to disk. Data will be saved in csv form to: *\<current folder>/Saved/*
*CLOUD_WRITE_TIME* : How often data is saved to a Cloud service (if activated)

**Sensor**

*Sensor_IP* : IP address of the MQTT broker. _Default_: 10.3.141.1.


# Thingsboard setup
Thingsboard provisioning: https://thingsboard.io/docs/paas/getting-started-guides/helloworld/#step-1-provision-device


