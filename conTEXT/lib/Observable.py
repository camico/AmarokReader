#!/usr/bin/env python

# Observer/Observable pattern for event delegation
# Manuel Amador (Rudd-O) written on 2005-11-28
# under the GPL
# but it someone proposes this for inclusion in the standard python library
# I'll gladly relicense it, damn!

__author__ = "Manuel Amador (Rudd-O) <dragonfear@gmail.com>"
__version__ = "0.1.0"

# This is an implementation of the Observer/Observable pattern.
#
# In software development literature, Observer/Observable is a software
# pattern.  From an Observer/Observable perspective, there are two kinds
# of objects:
#
# 	- objects which experience events or state changes (Observables)
# 	- objects which need to know about other objects' events (Observers)
#
# If you have any experience with event-based programming, such as with
# toolkits like GTK+ or Qt, you'll be familiar with the Observer/Observable
# pattern.  Observer objects register themselves with the Observable object
# of their interest, and when Observables experience events, these events
# are relayed to the Observers.
#
# Observer/Observable lets software developers build loosely coupled object
# meshes.  What this means to you: your software will be more stable and
# easier to refactor.
#
# This module has a complete Observer/Observable implementation.  To take
# advantage of this module, all you have to do is:
#
# 	- Make your Observable classes inherit from Observable
# 	  (don't forget to call Observable.__init__(self) in the constructor)
# 	- Make your Observer classes inherit from Observer
# 	  (don't forget to call Observer.__init__(self) in the constructor)
# 	- At runtime, for each object you want to observe, call
# 		self.observe(observable_object)
# 	  in a method of your Observer object.
# 	- In your Observable object, every time an event happens, call:
# 		...
# 		self.broadcastEvent("MyEventName",argument1,argument2...)
# 		...
# 	- In your Observer object, implement a method named:
# 		def processEvent(self,notifierObject,eventName,*args):
# 	  which will receive the notifier object, an event name, and a
# 	  variable number of arguments, every time broadcastEvent is
# 	  called in any of the Observable objects that have been observe'd()
#
# That's it.  Keep in mind that processEvent() will be invoked in the
# same thread context as the code which called broadcastEvent() in the
# Observable object.  Thus, processEvent() methods should return quickly and
# never do blocking operations (suggested technique for coping with blocking
# operations: run them in a separate thread, which sleeps until a flag is
# raised, and raise the flag in the processEvent() method as appropriate).
#
# Cute example:
#
# from Observable import Observable,Observed
#
# class Cat(Observable):
# 	def __init__(self):
# 		Observable.__init__(self)
# 	...
# 	def doMyLife(self):
# 		street = self.searchForFood()
# 		self.broadcastEvent("inNeighborhood",street)
# 	...
#
# class Dog(Observer):
# 	def __init__(self,neighborsCat):
# 		Observer.__init__(self)
# 		self.hatedCat = neighborsCat
# 		self.myStreet = "Fake Street"
# 		self.observe(neighborsCat)
# 	...
# 	def processEvent(self,notifierObject,eventName,*arguments):
# 		if notifierObject == self.hatedCat: # the cat I was observing
# 			if eventName == "inNeighborhood": # the event name
# 				if arguments[0] == self.myStreet: # my street
# 					self.chaseCat(self.hatedCat)
# 					# chaseCat should return quickly

import logging
logger = logging.getLogger("observable")
from threading import RLock


class Observer:
    """An object capable of observating an Observable
    To implement an Observer, you:
        - subclass your class from Observer
        - implement the processEvent() method, keeping in mind that
          processEvent() executes in the Observable's thread
          context.  Your processEvent() method implementation must
          never block, or else notifications to other objects will
          be delayed"""

    def __init__(self):
        pass

    def observe(self, obj):
        """Call this method with an Observable instance to let
        events happening within that instance be relayed to the
        processEvent() method here."""
        obj.register(self)

    def stopObserving(self, obj):
        """Call this method to stop observing an Observable instance"""
        obj.unregister(self)

    def processEvent(self, notifierObject, eventName, *args):
        """This is the default processEvent() implementation, it
        does nothing.  processEvent() receives the notifier object
        (the one emitting the notification), the event name (a
        string) and a variable number of positional arguments,
        which usually depend on the observable's policy.

        Implement this event to process received events.
        """
        pass


class Observable:
    """The Observable object.  Observable objects allow registration
    management of observers via the register() and unregister() events.

    To implement an Observable object:
        - subclass your class from Observable
        - whenever you want to notify observers of a relevant event
          use the broadcastEvent() method, passing an event name
          and a variable number of arguments.  These will be
          broadcast to all observing objects, in the Observable's
          thread context."""

    def __init__(self):
        self.__registeredObservers = []
        self.__registerLock = RLock()

    def register(self, observerObject):
        """This method is private and subject to modifications.
        Avoid calling or overriding it."""
        self.__registerLock.acquire()
        try:
            logger.debug("%s registering %s as observer", self, observerObject)
            if not observerObject in self.__registeredObservers:
                self.__registeredObservers.append(observerObject)
        finally:
            self.__registerLock.release()

    def unregister(self, observerObject):
        """This method is private and subject to modifications.
        Avoid calling or overriding it."""
        self.__registerLock.acquire()
        try:
            logger.debug("%s unregistering %s", self, observerObject)
            if observerObject in self.__registeredObservers:
                self.__registeredObservers.remove(observerObject)
        finally:
            self.__registerLock.release()

    def broadcastEvent(self, eventName, *args):
        """Call this method within your Observable instance to
        have all Observers be notified about the event.

        Pass an event name (usually a string) and a variable number
        of arguments.  They will be relayed to observing Observers.
        """
        logger.debug("%s broadcasting event %s,%s", self, eventName, args)
        for o in self.__registeredObservers[:]:
            try:
                o.processEvent(self, eventName, *args)
            except:
                logger.exception("Uncaught exception while relaying event %s%s from %s to %s.", eventName, args, self,
                                 o)
                logger.error("The event will still be relayed to the rest of observers")

# end observer/observable abstraction

__all__ = ["Observer", "Observable"]