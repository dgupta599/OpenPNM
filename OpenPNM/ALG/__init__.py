# Author: Andreas Putz
# Copyright (c) 2013, OpenPNM
# License: TBD.
r"""
**************************************************************************
:mod:`OpenPNM.ALG`: Algorithms on Networks
**************************************************************************

.. module:: OpenPNM.ALG

Contents
--------
This submodule contains all algorithms actiong on a pore network.

.. note::
    The algorithms take a basenet as an argument in the constructor, this
    seems to initialize a full object. Causing a lot of garbage to be written.
 
Import
------
>>> import OpenPNM as PNM
>>> tmp=PNM.ALG.GenericAlgorithm()


Submodules
----------
::

 None                            --- No subpackages at the moment

.. autoclass:: ALG.GenericAlgorithm
   :members:
   :undoc-members:
   :show-inheritance:
       
.. autoclass:: ALG.InvasionPercolation
   :members:
   :undoc-members:
   :show-inheritance:
   
.. autoclass:: ALG.OrdinaryPercolation
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: ALG.FickianDiffusion
   :members:
   :undoc-members:
   :show-inheritance:
    
"""

from __GenericAlgorithm__ import GenericAlgorithm
from __InvasionPercolation__ import InvasionPercolation
from __OrdinaryPercolation__ import OrdinaryPercolation
from __FickianDiffusion__ import FickianDiffusion 