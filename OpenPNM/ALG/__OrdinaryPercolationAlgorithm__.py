#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Jeff Gostick (jeff@gostick.ca)
# License: TBD
# Copyright (c) 2013


"""
module __OrdinaryPercolationAlgorithm__: Ordinary Percolation Algorithm
========================================================================

.. warning:: The classes of this module should be loaded through the 'ALG.__init__.py' file.

"""

import OpenPNM
import scipy as sp
import numpy as np
import scipy.sparse as sprs
import matplotlib.pyplot as plt

from __GenericAlgorithm__ import GenericAlgorithm

class OrdinaryPercolationAlgorithm(GenericAlgorithm):
    r"""   
    
    OrdinaryPercolationAlgorithm - Class to run OP algorithm on constructed networks
    
    Parameters
    ----------
    
    end_condition : choice between 'full_curve' and 'satn_value'
            
    Examples
    --------
    
    
    TODO:
    """
    
    def __init__(self,net=OpenPNM.NET.GenericNetwork(),**kwargs):
        r"""
        
        """
        super(OrdinaryPercolationAlgorithm,self).__init__(net = net,**kwargs)
        self._logger.debug("Create OP Algorithm Object")
        self.counter = 0
        self._setup(**kwargs)
        
    def _setup(self,npts=25,inv_faces=[],inv_sites=[]):
        r"""
        Calculates a capillary pressure curve by looping through a list
        of capillary pressures and calling the PCpoint function
        
        This function produces a plist called 'invpc' which contains the
        pressure at which a given pore was invaded. This list can be useful for
        reproducing the simulation for plotting or determining late pore filling.

        Parameters
        ----------
        
        npts: number of simulation steps (pressures); default 25
        
        inv_faces: invasion faces i.e. [1] or [1,2]; default [] but errors if inv_sites is also empty

        inv_sites: invasion pores i.e. [1,2,3,4,10]; default [] but errors if inv_faces is also empty
        
        Dependencies:
            - 
        Creates:
            - 
        """
        self._OP = 0
        self._ALOP = 0
        #Interpret input values to create invasion source list        
        if((np.size(inv_faces) + np.size(inv_sites)) == 0 ):
            self._logger.info("No invasion sites specfied, performing Ordinary Percolation")
            self._OP = 1
        elif np.size(inv_faces) > 0:
            self._ALOP = 1
            self._inv_src = np.in1d(self._net.pore_properties['type'],inv_faces)
        elif np.size(inv_sites) > 0:
            self._ALOP = 1
            self._inv_src = np.in1d(self._net.pore_properties['numbering'],inv_sites)
        
        #Create a pore and throat list to store inv_val at which each is invaded
        self._net.pore_properties['Pc_invaded'] = np.zeros(self._net.get_num_pores(),np.float)
        self._net.throat_properties['Pc_invaded'] = np.zeros(self._net.get_num_throats(),np.float)
        #Create a throat list to temporarily store the invasion state of throats
        self._net.throat_properties['invaded'] = np.zeros(self._net.get_num_throats())
        #Determine the invasion pressures to apply
        min_p = np.min(self._net.throat_properties['Pc_entry'])
        max_p = np.max(self._net.throat_properties['Pc_entry'])
        self._inv_points = np.linspace(min_p,max_p,npts)
        
    def _do_outer_iteration_stage(self):
        #Generate curve from points
        for inv_val in self._inv_points:
            self._logger.info("Applying Pc = "+str(int(inv_val)))
            #Apply one applied pressure and determine invaded pores
            inv_clusters = self._do_one_inner_iteration(inv_val)
            #Store result of invasion step
            self._net.pore_properties['Pc_invaded'][(self._net.pore_properties['Pc_invaded']==0)*(inv_clusters>0)] = inv_val
            r"""
            TODO:
            Tracking the pressure at which each throat is invaded has not been
            implimented yet.  This means that calculation of invaded volume is
            based only on volume of the pores.
            """
#            invaded_pores = self._net.pore_properties['numbering'][inv_clusters>0]
#            connected_throats = self._net.get_neighbor_throats(invaded_pores)
#            self._net.throat_properties['Pc_invaded'][self._net.throat_properties['Pc_invaded']==0] = inv_val
        del self._net.throat_properties['invaded']
            
    def _do_one_inner_iteration(self,inv_val):
        r"""
        Determines which throats are invaded at a given applied capillary pressure
        
        This function uses the scipy.csgraph module for the graph theory cluster
        labeling algorithm (connected_components)
        
        Dependencies:
            - 
        Creates:
            - 
        """
        #Generate a tlist containing boolean values for throat state
        self._net.throat_properties['invaded'] = self._net.throat_properties['Pc_entry']<inv_val
        #Fill adjacency matrix with invasion state info
        self._net.create_adjacency_matrix('invaded',sprsfmt='csr',dropzeros=True)
        #This step seems to be very slow!
        clusters = sprs.csgraph.connected_components(self._net._adjmatrix_csr)[1]
        #Clean up (not invaded = -2, invaded >0)
        clusters = (clusters[0:]>=0)*(clusters[0:]+1)
        if self._ALOP == 1:
            #Identify clusters connected to invasion sites
            inj_clusters = self._inv_src*clusters
        elif self._OP == 1:
            #Determine which pores are actually invaded
            temp1 = self._net.throat_properties['invaded']*((self._net.throat_properties['connections'][:,0]+1)-1)
            temp2 = self._net.throat_properties['invaded']*((self._net.throat_properties['connections'][:,1]+1)-1)
            inj_clusters = np.append(self._net.pore_properties['numbering'][temp1[temp1>=0]],self._net.pore_properties['numbering'][temp2[temp2>=0]])
        #Trim non-connected clusters
        inv_clusters2 = sp.zeros([np.size(clusters,0)],np.int32)
        inv_clusters2[np.in1d(clusters,inj_clusters)] = 1
        temp = sp.unique(inj_clusters[sp.nonzero(inj_clusters)])
        inv_clusters = sp.zeros([np.size(clusters,0)],np.int32)
        for i in range(0,np.shape(temp)[0]):
            pores=sp.where(clusters==temp[i])[0]
            inv_clusters[pores] = temp[i]
        return(inv_clusters)
            
    def _plot_results(self):
        r"""
        Plot the numerical output of the OP algorithm
        """
        PcPoints = np.unique(self._net.pore_properties['Pc_invaded'])
        Snwp = np.zeros_like(PcPoints)
        Ps = np.where(self._net.pore_properties['type']==0)
        for i in range(1,np.size(PcPoints)):
            Pc = PcPoints[i]
            Snwp[i] = sum((self._net.pore_properties['Pc_invaded'][Ps]<Pc)*(self._net.pore_properties['volume'][Ps]))/sum(self._net.pore_properties['volume'][Ps])
        plt.plot(PcPoints,Snwp,'r.-')
        plt.show(block = False)
        self._results = np.vstack((PcPoints,Snwp)).T
        
        
if __name__ == '__main__':
    print "Create a test"