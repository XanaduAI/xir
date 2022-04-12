XIR Documentation
#################

.. rst-class:: lead grey-text ml-2

:Release: |release|

.. raw:: html

    <style>
        .breadcrumb {
            display: none;
        }
        h1 {
            text-align: center;
            margin-bottom: 15px;
        }
        p.lead.grey-text {
            margin-bottom: 30px;
        }
        .footer-relations {
            border-top: 0px;
        }
    </style>

    <div class="container mt-2 mb-2">
        <p align="center" class="lead grey-text">
            XIR is an intermediate representation language for quantum programs.
        </p>
        <div class="row mt-3">

.. index-card::
    :name: Key Concepts
    :link: use/introduction.html
    :description: Learn about XIR syntax

.. index-card::
    :name: Getting Started
    :link: dev/guide.html
    :description: Learn how to quickly get started using XIR

.. index-card::
    :name: API
    :link: api/xir.html
    :description: Explore the XIR package

.. raw:: html

        </div>
    </div>

Features
========

* *Simple.* Easy to learn, write, and understand.

..

* *Flexible.* Define your own gates, observables, and outputs.

..

* *Modular.* Share declarations and definitions across multiple programs.

Support
=======

- **Source Code:** https://github.com/XanaduAI/xir
- **Issue Tracker:** https://github.com/XanaduAI/xir/issues

If you are having issues, please let us know, either by email or by posting the
issue on our GitHub issue tracker.

License
=======

XIR is **free** and **open source**, released under the Apache License, Version 2.0.

.. toctree::
   :maxdepth: 2
   :caption: Using XIR
   :hidden:

   use/introduction
   use/grammar
   use/examples

.. toctree::
   :maxdepth: 2
   :caption: Development
   :hidden:

   dev/guide
   dev/research
   dev/releases

.. toctree::
   :maxdepth: 2
   :caption: API
   :hidden:

   api/xir