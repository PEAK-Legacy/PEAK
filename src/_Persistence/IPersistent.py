##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
try:
    from Interface import Interface
    from Interface.Attribute import Attribute
except ImportError:
    class Interface: pass
    def Attribute(*args): return args

class IPersistent(Interface):
    """Python persistence interface

    A persistent object can eb in one of several states:

    - Unsaved

      The object has been created but not saved in a data manager.

      In this state, the _p_changed attribute is non-None and false
      and the _p_jar attribute is None.

    - Saved

      The object has been saved and has not been changed since it was saved.

      In this state, the _p_changed attribute is non-None and false
      and the _p_jar attribute is set to a data manager.

    - Sticky

      This state is identical to the up-to-date state except that the
      object cannot transition to the ghost state. This is a special
      state used by C methods of persistent objects to make sure that
      state is not unloaded in the middle of computation. 

      In this state, the _p_changed attribute is non-None and false
      and the _p_jar attribute is set to a data manager.

      There is, currently, no official way to detect whether an object
      is in the sticky state.

    - Changed

      The object has been changed.

      In this state, the _p_changed attribute is true
      and the _p_jar attribute is set to a data manager.

    - Ghost

      the object is in memory but its state has not been loaded from
      the database (or has been unloaded).  In this state, the object
      doesn't contain any data.

    The following state transactions are possible:

    - Unsaved -> Saved

      This transition occurs when an object is saved in the
      database. This usually happens when an unsaved object is added
      to (e.g. as an attribute ot item of) a saved (or changed) object
      and the transaction is committed.

    - Saved  -> Changed
      Sticky -> Changed

      This transition occurs when someone sets an attribute or sets
      _p_changed to a true value on an up-to-date or sticky
      object. When the transition occurs, the persistent object is
      required to call the register method on its data manager,
      passing itself as the only argument.

    - Saved -> Sticky

      This transition occurs when C code marks the object as sticky to
      prevent its deactivation and transition to the ghost state.

    - Saved -> Ghost

      This transition occurs when an saved object is deactivated, by:
      calling _p_deactivate, setting _p_changed to None, or deleting
      _p_changed.

    - Sticky -> Saved

      This transition occurs when C code unmarks the object as sticky to
      allow its deactivation and transition to the ghost state.

    - Changed -> Saved

      This transition occurs when a transaction is committed.
      The data manager affects the transaction by setting _p_changed
      to a true value.

    - Changed -> Ghost

      This transition occurs when a transaction is aborted.
      The data manager affects the transaction by deleting _p_changed.

    - Ghost -> Saved

      This transition occurs when an attribute or operation of a ghost
      is accessed and the object's state is loaded from the database.

    Note that there is a separate C API that is not included here.
    The C API requires a specific data layout and defines the sticky
    state that is used to pevent object deactivation while in C
    routines.

    """

    _p_jar=Attribute(
        """The data manager for the object

        The data manager implements the IPersistentDataManager interface.
        If there is no data manager, then this is None.
        """)

    _p_oid=Attribute(
        """The object id

        It is up to the data manager to assign this.
        The special value None is resrved to indicate that an object
        id has not been assigned.
        """)

    _p_changed=Attribute(
        """The persistence state of the object

        This is one of:

        None -- The object is a ghost. It is not active.

        false -- The object is saved (or has never been saved).

        true -- The object has been modified.

        The object state may be changed by assigning this attribute,
        however, assigning None is ignored if the object is not in the
        up-to-date state.

        Note that an object can change to the modified state only if
        it has a data manager. When such a state change occurs, the
        'register' method of the data manager is called, passing the
        persistent object.

        Deleting this attribute forces deactivation independent of
        existing state.

        Note that an attribute is used for this to allow optimized
        cache implementations.
        """)

    _p_serial=Attribute(
        """The object serial number

        This is an arbitrary object.
        """)

    _p_atime=Attribute(
        """The integer object access time, in seconds, modulus one day.

        XXX When does a day start, the current implementation appears
        to use gmtime, but this hasn't be explicitly specified.

        XXX Why just one day?
        """)

    def __getstate__():
        """Get the object state data.

        The state should not include peristent attributes ("_p_name")
        """

    def __setstate__(state):
        """Set the object state data

        Note that this does not affect the object's persistence state.
        """

    def _p_activate():
        """Activate the object.

        Change the object to the up-to-date state if it is a ghost.
        """
    
    def _p_deactivate():
        """Deactivate the object

        Change the object to the ghost state is it is in the
        up-to-date state.
        """

    def _p_independent():
        """Hook for subclasses to prevent read conflict errors.

        A specific peristent object type can defined this method and
        have it return true if the data manager should ignore read
        conflicts for this object.
        """
