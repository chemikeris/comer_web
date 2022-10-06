# Installation instructions

The installation of the COMER web server is done using [ansible](https://www.ansible.com/). There are three installation playbooks:

1. `install_dependencies.yml`: install dependencies using DNF from CentOS repositories, download other necessary software.
2. `configure_db.yml`: configure MySQL/MariaDB databases and users.
3. `install.yml`: installs Django and other Python dependencies and the COMER web server itself.

They should be executed in the given order.

Two installation scripts are called to setup COMER web server by install.yml:

- `generate_secret_key.bash`
- `install_comer_web_server.bash`

These procedures do not setup the backend calculation server, it should be installed separately.
