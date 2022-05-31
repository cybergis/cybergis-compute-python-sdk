About
=====

What is CyberGIS-Compute?
-------------------------

CyberGIS-Compute is an open-sourced geospatial middleware framework that provides integrated access to high-performance computing (HPC) resources through a Python-based SDK and core middleware services. The key components of CyberGIS-Compute include CyberGIS-Compute SDK and CyberGIS-Compute Core. CyberGIS-Compute is released under Apache 2.0 license.

.. figure:: _static/img/Compute.png
    :alt: A diagram illustrating that CyberGIS-Compute functions as a bridge between CyberGIS-Jupyter and High Performance Computing resources.

    You can think of CyberGIS-Compute as a bridge between Jupyter notebooks and High Performance Computing (HPC) resources.


Who Are We?
-----------

The CyberGIS-Compute project is primarily run by the `CyberGIS Center <https://cybergis.illinois.edu/>`_. However, we are an open-source project and welcome contributions from anyone! `Click here to view our contributors <https://github.com/cybergis/cybergis-compute-python-sdk/graphs/contributors>`_.

Why?
----

Here is a a short excerpt from a recent paper that explains our motiviation:

    Geospatial research and education have become increasingly dependent on cyberGIS to tackle computation and data challenges. However, the use of advanced cyberinfrastructure resources for geospatial research and education is extremely challenging due to both high learning curve for users and high software development and integration costs for developers, due to limited availability of middleware tools available to make such resources easily accessible. This tutorial describes CyberGIS-Compute as a middleware framework that addresses these challenges and provides access to high-performance resources through simple easy to use interfaces. The CyberGIS-Compute framework provides an easy to use application interface and a Python SDK to provide access to CyberGIS capabilities, allowing geospatial applications to easily scale and employ advanced cyberinfrastructure resources.

.. seealso::
    `Click here to read the paper <https://doi.org/10.1145/3486189.3490017>`_.

Presentations
-------------

We have given a few presentations at conferences based on the CyberGIS-Compute work. They are helpful for obtaining an understanding of the overall project, but may not provide insight into usage.

Below, you can see a quick presentation by Dr. Anand Padmanabhan from the Gateways 2021 conference:

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/KJGBIx0MzWw" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

For a more in-depth presentation, you can view our presentation from the 3rd ACM SIGSPATIAL International Workshop on APIs and Libraries for Geospatial Data Science (SpatialAPI 2021):

.. raw:: html

    <iframe width="560" height="315" src="https://www.youtube.com/embed/q976uxOPg84" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

Citing
------

Below is an example reference for CyberGIS-Compute and bibtex entry::


    @inproceedings{10.1145/3486189.3490017,
        author = {Padmanabhan, Anand and Ziao, Ximo and Vandewalle, Rebecca C. and Baig, Furqan and Michel, Alexander and Li, Zhiyu and Wang, Shaowen},
        title = {CyberGIS-Compute for Enabling Computationally Intensive Geospatial Research},
        year = {2021},
        isbn = {9781450391030},
        publisher = {Association for Computing Machinery},
        address = {New York, NY, USA},
        url = {https://doi.org/10.1145/3486189.3490017},
        doi = {10.1145/3486189.3490017},
        booktitle = {Proceedings of the 3rd ACM SIGSPATIAL International Workshop on APIs and Libraries for Geospatial Data Science},
        articleno = {3},
        numpages = {2},
        keywords = {CyberGIS, CyberGIS-Jupyter, GIScience, high performance computing},
        location = {Beijing, China},
        series = {SpatialAPI '21}
    }
