"""Test event sources and threads"""
from __future__ import generators
from unittest import TestCase, makeSuite, TestSuite
from peak.api import *
from peak.tests import testRoot

class BasicTests(TestCase,object):

    kind = "stream"
    sourceType = events.Distributor
    requiredInterface = events.IEventSource

    def setUp(self):
        self.source = self.sourceType()
        self.log = []

    def sink(self,source,event):
        self.log.append((source,event))
        return True

    def reject(self,source,event):
        self.log.append((source,event))

    def doPut(self,value,force=False):
        self.source.send(value)

    def reenter(self,source,event):
        source.addCallback(self.sink)


    def testSuspend(self):
        # Verify that source always suspends
        self.failUnless( self.source.nextAction() is None )

    def testCallback(self):
        # Verify simple callback
        self.source.addCallback(self.sink)
        self.doPut(1)
        self.assertEqual(self.log,[(self.source,1)])


    def testProvides(self):
        adapt(self.source, self.requiredInterface)


    def testMultiCallback(self):

        for i in range(10):
            self.source.addCallback(self.sink)

        if self.kind=="stream":
            # Verify stream for stream types
            for i in range(10):
                self.doPut(i)
            self.assertEqual(self.log,
                [(self.source,i) for i in range(10)]
            )
        else:
            # Verify broadcast for broadcast types
            self.doPut(42)
            self.assertEqual(self.log,
                [(self.source,42) for i in range(10)]
            )


    def testNoReentrance(self):

        self.source.addCallback(self.reenter)

        self.doPut(1,True)
        self.assertEqual(self.log, [])

        self.doPut(2,True)
        self.assertEqual(self.log, [(self.source, 2)])








    def testRejection(self):

        # This test is a little tricky.  If we are using a stream source,
        # we are verifying that it doesn't throw away an event that was
        # rejected by the callback.  If we're using a broadcast source, we're
        # verifying that it sends everything to everybody whether they accept
        # it or reject it.  :)

        self.source.addCallback(self.reject)
        self.source.addCallback(self.sink)
        self.doPut(1)
        self.assertEqual(self.log,[(self.source,1),(self.source,1)])





























class ValueTests(BasicTests):

    sourceType = events.Value
    kind = "broadcast"
    requiredInterface = events.IWritableSource

    def doPut(self,value,force=False):
        self.source.set(value, force)


class ConditionTests(ValueTests):

    sourceType = events.Condition
    requiredInterface = events.IConditional

    def reenter(self,source,event):
        self.doPut(False)
        source.addCallback(self.sink)

    def testSuspend(self):
        # Verify that source suspends when value is true

        for f in False, '', 0:
            self.doPut(f,True)
            self.failUnless( self.source.nextAction() is None, self.source())

        for t in True, 'xx', 27:
            self.doPut(t,True)
            self.failIf( self.source.nextAction() is None)












class DerivedValueTests(BasicTests):

    sourceType = events.DerivedValue
    kind = "broadcast"

    requiredInterface = events.IReadableSource

    def setUp(self):
        self.base = events.Value(False)
        self.source = self.sourceType(lambda: self.base() * 2, self.base)
        self.log = []

    def doPut(self,value,force=False):
        try:
            v = value/2.0
        except TypeError:
            v = value[:len(value)/2]
        self.base.set(v, force)


class DerivedConditionTests(DerivedValueTests):

    sourceType = events.DerivedCondition
    requiredInterface = events.IConditional

    reenter = ConditionTests.reenter.im_func
    testSuspend = ConditionTests.testSuspend.im_func














class SemaphoreTests(ConditionTests):

    sourceType = events.Semaphore
    kind = "stream"
    requiredInterface = events.ISemaphore

    def reenter(self,source,event):
        source.take()
        source.addCallback(self.sink)


    def testMultiCallback(self):
        # Verify put/take operations
        def take(source,event):
            source.take()
            self.sink(source,event)
            return True
        src = events.Semaphore(3)
        for i in range(10):
            src.addCallback(take)
        self.assertEqual(self.log, [(src,3),(src,2),(src,1)])


    def testNoReentrance(self):
        # Ensure semaphore is reset before starting
        self.source.set(0)
        ConditionTests.testNoReentrance(self)














class AnyOfTests(TestCase):

    def testAnyOfOne(self):
        # Verify that AnyOf(x) is x
        c = events.Condition()
        self.failUnless(events.AnyOf(c) is c)

    def testAnyOfNone(self):
        # Verify that AnyOf() raises ValueError
        self.assertRaises(ValueError, events.AnyOf)

    def testOnlyOnce(self):
        # Verify that AnyOf calls only once per addCallback

        values = [events.Value(v) for v in range(10)]
        any = events.AnyOf(*tuple(values))
        def sink(source,event):
            log.append((source,event))

        for i in range(10):
            # For each possible value, fire that one first, then all the others
            log = []
            any.addCallback(sink)
            values[i].set(-i,True)   # fire the chosen one
            for j in range(10):
                values[j].set(j*2,True)  # fire all the others
            self.assertEqual(log, [(any,(values[i],-i))])

    def testAnySuspend(self):
        c1, c2, c3 = events.Condition(), events.Condition(), events.Condition()
        any = events.AnyOf(c1,c2,c3)
        for i in range(8):
            c1.set(i & 4); c2.set(i & 2); c3.set(i & 1)
            self.assertEqual(
                (any.nextAction() is None), not c1() and not c2() and not c3()
            )

    def testNonEvent(self):
        # Verify that AnyOf(nonevent) raises NotImplementedError
        self.assertRaises(NotImplementedError, events.AnyOf, 42)

    def testRejection(self):
        # Verify that an AnyOf-callback rejects events rejected by its
        # downstream callbacks, or that arrive after the first relevant event
        # for that callback.

        log = []

        def sink(source,event):
            log.append(("sink",source,event))
            return True

        def reject(source,event):
            log.append(("reject",source,event))

        d1, d2 = events.Distributor(), events.Distributor()
        any = events.AnyOf(d1,d2)

        any.addCallback(reject)
        d1.addCallback(sink)
        d1.send(1)
        self.assertEqual(log, [("reject",any,(d1,1)), ("sink",d1,1)])

        log = []
        d2.send(2)  # nothing should happen, since 'reject' already fired
        self.assertEqual(log, [])

        any.addCallback(sink)
        d2.addCallback(sink)
        d2.send(3)
        self.assertEqual(log, [("sink",any,(d2,3))])

        d2.send(4)
        self.assertEqual(log, [("sink",any,(d2,3)),("sink",d2,4)])








class TestThreads(TestCase):

    def spawn(self, iterator):
        return events.Thread(iterator)

    def tick(self):
        pass

    def simpleGen(self, log, guard, sentinel):
        while True:
            yield guard; value = events.resume()
            if value == sentinel:
                break
            log.append(value)


    def testSimple(self):
        # Test running a single-generator thread, receiving values
        # from an event source, verifying its 'isFinished' condition

        v = events.Value()
        log = []
        testData = [1,2,3,5,8,13]

        thread = self.spawn( self.simpleGen(log,v,None) )
        self.failIf( thread.isFinished() )

        for i in testData:
            v.set(i); self.tick()
            self.failIf( thread.isFinished() )

        v.set(None); self.tick()
        self.failUnless( thread.isFinished() )
        self.assertEqual(log, testData)







    def testAnySuspend(self):

        testdata = []; log = []
        v1, v2, v3 = events.Value(), events.Value(), events.Value()

        any = events.AnyOf(v1,v2,v3)
        thread = self.spawn( self.simpleGen(log, any, (v3,None)) )

        for i in range(5):
            v3.set(i); self.tick();
            testdata.append((v3,i))

        v1.set(True); self.tick()
        v2.set(True); self.tick()
        v1.set(False); self.tick()
        v1.set(True); self.tick()
        v3.set(None); self.tick()

        testdata += [(v1,True),(v2,True),(v1,False),(v1,True)]

        self.failUnless( thread.isFinished() )
        self.assertEqual(log, testdata)



















    def testSemaphores(self):

        sem1 = events.Semaphore(5)
        sem2 = events.Semaphore(0)
        log = []

        def gen(me):
            yield sem1; v = events.resume()
            sem1.take()
            log.append((me,v))

            yield sem2; events.resume()
            sem2.take()
            sem1.put()

        threads = []

        # In the first phase, the first 5 threads take from sem1, and its
        # available count decreases

        part1 = [(0,5), (1,4), (2,3), (3,2), (4,1)]
        for n in range(10):
            threads.append( self.spawn( gen(n) ) )

        self.assertEqual(log, part1)

        # In the second phase, the first 5 threads release their hold on sem1,
        # and the second 5 threads get to take it, seeing each count as it
        # becomes available.

        part2 = [(5,1),(6,1),(7,1),(8,1),(9,1)]

        for i in range(10):
            sem2.put(); self.tick()
            self.failUnless(threads[i].isFinished(), i)

        self.assertEqual(log, part1+part2)
        self.assertEqual(sem1(), 5)
        self.assertEqual(sem2(), 0)


    def testSimpleError(self):

        def gen():
            try:
                yield gen1(); events.resume()
            except ValueError:
                log.append("caught")
            else:
                log.append("nocatch")

            # this shouldn't throw an error; i.e.,
            # resuming after catching an error shouldn't reraise the error.
            yield None; events.resume()

        def gen1():
            # We yield first, to ensure that we aren't raising the error
            # while still being called from the first generator (which would
            # be handled by normal Python error trapping)
            yield events.Condition(1); events.resume()

            # Okay, now we're being run by the thread itself, so hit it...
            raise ValueError

        log = []
        self.spawn(gen())
        self.assertEqual(log, ["caught"])















    def testUncaughtError(self):

        def gen():
            yield gen1(); events.resume()

        def gen1():
            yield events.Condition(1); events.resume()
            raise ValueError

        self.assertRaises(ValueError, self.spawn, gen())































class ScheduledThreadsTest(TestThreads):

    def setUp(self):
        self.scheduler = events.Scheduler()

    def spawn(self,iterator):
        return self.scheduler.spawn(iterator)

    def tick(self):
        self.scheduler.tick()

    def testUncaughtError(self):

        # This also verifies task-switch on sleep, and aborted/not isFinished
        # state of an aborted scheduled thread.

        def gen(c):
            yield c; events.resume()
            yield gen1(); events.resume()

        def gen1():
            yield events.Condition(1); events.resume()
            raise ValueError

        c = events.Condition()
        thread = self.spawn(gen(c))
        c.set(True) # enable proceeding
        self.assertRaises(ValueError, self.scheduler.tick)

        self.scheduler.tick()   # give the error handler a chance to clean up

        self.assertEqual(thread.isFinished(), False)
        self.assertEqual(thread.aborted(), True)








class SchedulerTests(TestCase):

    def setUp(self):
        self.time = events.Value(0)
        self.sched = events.Scheduler(self.time)

    def testAvailableTime(self):
        self.assertEqual(self.sched.time_available(), None)

        minDelay = 9999
        for t in 5,15,71,3,2:
            minDelay = min(t,minDelay)
            u = self.sched.until(t)
            self.assertEqual(self.sched.time_available(), minDelay)

        self.time.set(1)
        self.assertEqual(self.sched.time_available(), minDelay-1)
        self.time.set(2)
        self.assertEqual(self.sched.time_available(), minDelay-2)
        self.time.set(3)
        self.sched.tick()   # Clear out the 2 and 3, should now be @5
        self.assertEqual(self.sched.time_available(), 2)    # and delay==2

    def testUntil(self):
        self.verifyAppts(self.sched.until)

    def testTimeouts(self):
        self.time.set(27)   # any old time
        self.verifyAppts(self.sched.timeout)

    def verifyAppts(self,mkAppt):
        offset = self.time()
        appts = 1,2,3,5,8,13
        conds = [mkAppt(t) for t in appts]
        for i in range(20):
            self.time.set(i+offset)
            self.sched.tick()
            for a,c in zip(appts,conds):
                self.assertEqual(a<=i, c())     # Condition met if time expired


    def testSleep(self):

        delays = 2,3,5,7
        sleeps = [self.sched.sleep(t) for t in delays]
        log = []

        def callback(s,e):
            log.append((delays[sleeps.index(s)],e))
            s.addCallback(callback)

        for s in sleeps:
            s.addCallback(callback)

        for i in range(20):
            self.time.set(i)
            self.sched.tick()


        # Notice that this ordering may seem counterintuitive for paired-prime
        # products such as '6': one might expect '(2,6)' to come before
        # '(3,6)', for example.  However, the callback occurring at '(3,6)' was
        # registered at time '3', and the callback occurring at '(2,6)' was
        # registered at time '4'.  So, the callbacks are actually being called
        # in the desired, order-preserving fashion, despite the apparently
        # "wrong" order of the data.

        self.assertEqual(log,
            [   (2,2), (3,3), (2,4), (5,5), (3,6), (2,6), (7,7),
                (2,8), (3,9), (5,10), (2,10), (3,12), (2,12),
                (7,14), (2,14), (5,15), (3,15), (2,16), (3,18),
                (2,18),
            ]
        )








class AdviceTests(TestCase):

    def testAdvice(self):

        class MyClass(binding.Component):

            def aThread(self):
                yield events.Condition(True); events.resume()

            aThread = binding.Make( events.threaded(aThread) )

            def threadedMethod(self):
                yield events.Condition(True); events.resume()

            threadedMethod = events.threaded(threadedMethod)

        ob = MyClass()
        self.failIf(adapt(ob.aThread, events.IThread,None) is None)
        self.failIf(adapt(ob.threadedMethod(), events.IThread,None) is None)






















TestClasses = (
    BasicTests, ValueTests, ConditionTests, SemaphoreTests, AnyOfTests,
    TestThreads, ScheduledThreadsTest, SchedulerTests, AdviceTests,
    DerivedValueTests, DerivedConditionTests
)

def test_suite():
    s = []
    for t in TestClasses:
        s.append(makeSuite(t,'test'))

    return TestSuite(s)






























