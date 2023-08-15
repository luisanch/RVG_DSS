---
author:
- Luis Fernando Sanchez Martin [^1]
date: July 2023
title: Quickstart Guide
---
## Quickstart

-   install the necessary dependencies via conda or any other method.
    these can be found in the provided .yml or text files and if
    necessary activate the conda environment

In the `RVG_DSS` directory:

        conda env create -f rvgdss.yml
        conda activate rvgdss

In addition to these dependencies, there are two more that need to be
installed locally, these are the `model4dof` and `rvg_ledarstein_core`.
In order to install `model4dof` download the
[repository](#https://github.com/luisanch/package_model4DOF) then
`pip install` the `.tar.gz` file contained in the dist directory.

         pip install .\model4dof-0.0.1.tar.gz

Next, go to the `rvg_ledarstein_core` directory and build and install
the package there. `cd` into the `rvg_ledarstein_core` directory and:

        python -m build
        pip install .\dist\rvg_dss-0.0.1.tar.gz

Note that this step should be repeated when changes are performed in the
code contained in this directory

-   start the `rvg_leidarstein_msg_relay`

`cd` into the `rvg_leidarstein_msg_relay` directory and:

         python .\rvg_leidarstein_msg_relay.py

-   launch the webapp `rvg_leidarstein_frontend`

In a new terminal, `cd` into the `rvg_leidarstein_frontend` directory
and:

        npm install
        npm start

-   launch the `run_leidarstein.py` script

In a new terminal `cd` into `\RVG_DSS\rvg_leidarstein_core\scripts` and:

        python .\run_leidarstein.py
        
[^1]: luissanchezmtn@gmail.com 