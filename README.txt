PEAK Release 0.5 alpha 3

 Copyright (C) 1996-2003 by Phillip J. Eby and Tyler C. Sarna.
 All rights reserved.  This software may be used under the same terms
 as Zope or Python.  THERE ARE ABSOLUTELY NO WARRANTIES OF ANY KIND.
 Code quality varies between modules, from "beta" to "experimental
 pre-alpha".  :)

 Package Description

    PEAK is the "Python Enterprise Application Kit". If you develop
    "enterprise" applications with Python, or indeed almost any sort of
    application with Python, PEAK may help you do it faster, easier, on a
    larger scale, and with fewer defects than ever before. The key is
    component-based development, on a reliable infrastructure.

    PEAK is an application kit, and applications are made from components.
    PEAK provides you with a component architecture, component infrastructure,
    and various general-purpose components and component frameworks for
    building applications.  As with J2EE, the idea is to let you stop
    reinventing architectural and infrastructure wheels, so you can put more
    time into your actual application.

    But PEAK is different from J2EE: it's a single, free implementation of
    simpler API's based on an easier-to-use language that can nonetheless
    scale with better performance than J2EE.

    PEAK is the successor to TransWarp, an experimental toolkit for software
    automation in Python.  PEAK takes the best of the techniques and ideas
    from TransWarp, and repackages them as an enterprise software toolkit.
    Where TransWarp emphasized techniques like generative programming and
    aspect-oriented programming, PEAK emphasizes enterprise applications,
    and hides the computer science stuff "under the hood", so you can focus
    on building your application.

    PEAK tools can be used with other "Python Enterprise" frameworks such as
    Zope, Twisted, and the Python DBAPI to construct web-based, GUI, or
    command-line applications, interacting with any kind of storage, or with
    no storage at all.  Whatever the application type, PEAK can help you put
    it together.

 Package Features

    As of version 0.5a3, PEAK features include:

    * A component binding framework that makes it easy to parameterize
      components and thus more easily combine and "wire" them together.
      Interfaces, adaptation, and "assembly events" (notification when
      components have been engaged as part of a "complete" application)
      are all available.

    * A comprehensive configuration framework that allows accessing
      "utilities" and "configuration properties" in context.  Properties
      and utilities can be loaded or computed on demand, supplied by rules,
      defined in configuration files or code, in a supplied or custom
      format.  Properties and utilities are contextual and can be safely
      acquired from parent/context components automatically.

    * Naming system/framework that's midway between J2EE's JNDI and CORBA's
      cosNaming in features, but much easier to use and extend than either
      of those systems.

    * A storage management and persistence system, including:

        - Atomic, multi-database transactions with two-phase commit.

        - "Data Manager" class framework for persistence management, that
          allows you to separate business logic from storage implementation.
          If you can write a few simple methods like "load" and "save" for
          a given object type and storage approach, you can create your own
          "DM" components.  You can think of a DM as an advanced form of
          Python "shelve", that supports references to other objects,
          transactions, arbitrary back-end storages, and caching.

        - "Stackable" data managers: one DM might serialize a set of objects
          to XML, which could then be stored in a database record by another
          DM, and then the database record might be implemented via a DM
          that writes to disk files!  Each DM only needs to know how to
          manipulate objects offered by the next-level DM, not the details
          of the next DM's implementation, so all the DM's are potentially
          replaceable with alternate storage mechanisms.

        - RDBMS and LDAP connection framework based on the Python DBAPI,
          that handles data type conversions (via the configuration
          framework) and seamlessly integrates with the transaction system
          and naming services framework.  DB Connections can be accessed
          by name or URL, and bound as default collaborators or utilities
          for access by other application components.

    * CASE/modelling tools: PEAK includes APIs to read object
      models created in the XML-based XMI format.  Many open-source and
      commercial modelling tools support XMI, inlcuding Argo/Poseidon and
      MagicDraw UML.  PEAK includes pre-built support for UML versions 1.3
      and 1.4, and MOF 1.3.1, using XMI versions 1.0 and 1.1. (UML 1.5,
      CWM 1.0, CWM 1.1, and XMI 1.2-2.0 are anticipated for version 0.6.)
      Also included is a MOF->Python code generator, which was used to generate
      the UML support, and which you can use to generate support for other
      modelling languages based on the MOF.

      For the specifications of XMI, MOF, CWM, and UML, visit:
      http://www.omg.org/technology/documents/modeling_spec_catalog.htm

    * A domain modelling framework for creating "business object models"
      with unidirectional and bidirectional associations, generated
      getters/setters and validators for fields, etc., and all necessary
      persistence support for use with the PEAK storage framework.  Domain
      types can also define string parsing and formatting syntax, so you can
      create domain-specific data languages or just string formats for data
      types (such as specialized date/time or currency types).

      The business object framework supplies structural metadata about
      classes built with it, so you can query a class for its fields and
      links, and their names, types, etc.  This can be useful for
      implementing model-driven storage or user interfaces.  And the
      metadata is aligned with the MOF, so generating MOF, UML, or CWM
      from PEAK models (and vice versa) is possible (although
      not yet implemented for anything but MOF->PEAK).






    * Application Runtime tools, including:

      - a "command objects" framework for creating command-line applications,
        including the ability to create "executable configuration files"
        or "configuration interpreters" that can load a configuration file
        and run an application instance constructed using the configuration
        data.  Supported formats include an .ini-like PEAK format, and
        arbitrary schemas defined using ZConfig.

      - a "periodic tasks" framework for executing tasks that perform "as
        needed", scheduling themselves in response to their available workloads

      - a CGI/FastCGI publishing framework that uses 'zope.publisher' to
        publish a PEAK component tree and its associated transaction service

      - an event-driven "reactor" framework that seamlessly integrates with
        Twisted, but can also be used without Twisted for applications that are
        mostly scheduling-oriented, or which use only third-party protocol
        implementations such as FAM, FastCGI, ReadyExec, etc.

      - a robust and flexible logging framework that can integrate with the
        PEP 282 logging module, or stand alone.  It's simpler than the PEP 282
        system for simple log configuration, and is configured on demand
        rather than "up front", and is thus more manageably configurable for
        large or complex applications consisting of components from diverse
        providers.

      - a "process supervisor" framework for multiprocess servers using
        long-running child processes (created via 'fork()') to take maximum
        advantage of multiprocessor machines for CPU-intensive services.

    * AOP and SOP: PEAK allows you to separate concerns as modules, then
      combine the modules via a "module inheritance" technique.  This
      lets you define a generated business object model as a
      "structural" concern, and then combine it with a "behavioral"
      concern.  This is as simple as writing classes that contain only
      what you want to add, and then telling PEAK that your new module
      "inherits" from the generated module.  This is similar to (but
      designed independently from) the "MixJuice" tool for AOP in Java.


 Known Issues and Risks of this Version

   This is ALPHA software.  Although much of the system is extensively
   tested by a battery of automated tests, it may contain bugs, especially
   in areas not covered by the test suites.  Also, many system interfaces
   are still subject to change.

   PEAK includes early copies of Zope X3's 'ZConfig' and 'persistence'
   packages, which have had - and may continue to have - significant
   implementation changes.  We will be tracking Zope X3 periodically, but
   can't guarantee compatibility with arbitrary (e.g. CVS) versions of
   Zope X3.

   Documentation at present is limited, and scattered.  The principal
   documentation is an API reference generated from the code's lengthy
   docstrings (which usually contain motivating examples for using that
   class, method, or function).  The mailing list and its archives
   provide a wealth of information on actual usage scenarios,
   recommended approaches, etc.  There is also the beginnings of a
   tutorial on using the component binding package.





















 Third-Party Software Included with PEAK

     All third-party software included with PEAK are understood by PEAK's
     authors to be distributable under terms comparable to those PEAK is
     offered under.  However, it is up to you to understand any obligations
     those licenses may impose upon you.  For your reference, here are the
     third-party packages and where to find their license terms:

     The 'kjbuckets' module is Copyright Aaron Watters and contributors;
     please see the 'src/kjbuckets/COPYRIGHT.txt' file for details of its
     license.

     The 'datetime', 'persistence' and 'ZConfig' packages are Copyright Zope
     Corporation and contributors; please see the 'LICENSE.txt' files in their
     directories for details of their licenses.

     The 'fcgiapp' module is Copyright Digital Creations, LC (now Zope Corp.);
     see the 'fcgiappmodule.c' for details of its license.  In the same
     directory are distributed portions of the FastCGI Development Kit, which
     is Copyright Open Market, Inc.  See the 'LICENSE.TERMS' file in that
     directory for details of its license.

 Installation Instructions

    Please see the INSTALL.txt file.
















