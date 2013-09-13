**DEPRECATED Look at [medlemssystem_django](https://github.com/vegarang/medlemssystem_django) for the replacement - a Django-based system with a proper database and web-ui based on twitters bootstrap!**


cybmedlem
=========

A small system to organize members for the student-society Cybernetisk Selskab


The system is still a work in progress and will se further updates in time.

setup
------
to install dependencies run:
    
    sudo sh install_dependencies.sh


start and run
--------------
cd to folder and run:

    python cyb_medlem2.py

to start the program


docs
------
documentation is created with sphinx. to see it enter the docs folder in terminal and enter:

    make clean && make html

then open build/index.html in your favourite web-browser :-)
the documentation is still a work in progress and does not cover everything just yet..


notes
-------
This system is developed in Ubuntu 12.04 with python 2.7. Not tested in any other os/distro.

The scrolledlist.py file is not my work, found online at [new mexico tech](http://infohost.nmt.edu/tcc/help/lang/python/examples/scrolledlist/module-scrolledlist.html) after some googleing.
