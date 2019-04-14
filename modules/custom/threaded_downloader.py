try:
    from Queue import Queue
except ImportError:
    from queue import Queue
from threading import Thread
from modules.custom import ACOWD_mod as fnku
from time import sleep


# A first attempt at making a dowload session manager that runs in a separate thread.
# My goal is to relay progress and log communications from the downloading threads to the gui from here.
# When the user adjusts the download rate limiter, it is communicated from the gui to this manager, which
# will be running the actual rate limiter and communicating back to the threads how long they need to sleep
# before downloading their next chunk of data.

class DownloadSession(Thread):
    def __init__(self, jobQ, resultQ, abortQ, threadcount, gui):
        Thread.__init__(self)
        self.setDaemon(True)
        self.threads = []
        self.jobQ = jobQ
        self.guiresultQ = resultQ
        self.progressQ = Queue()
        self.finishedQ = Queue()
        self.ratelimitQ = Queue()
        self.threadcount = threadcount
        self.total_progress = 0

        for i in range(1, threadcount + 1):
            self.threads.append(DownloadWorker(jobQ, resultQ, abortQ, self.progressQ, self.finishedQ, self.ratelimitQ, str(i), gui))

    def start_session(self):
        for i in self.threads:
            i.start()

    def populate_job(self, joblist):
        for i in joblist:
            for job in i:
                self.jobQ.put(job)

    def poison_threads(self):
        for i in range(self.threadcount):
            self.jobQ.put(None)  # A poison pill to kill each thread

    def run(self):
        self.start_session()
        prog = []
        log = []

        while True: # Only run while at least 1 thread is alive
            sleep(.00000001)
            if not self.progressQ.empty():
                for i in range(self.progressQ.qsize()):
                    x =(self.progressQ.get())
                    if x[0] == 'progress':
                        prog.append(x)
                    else:
                        log.append(x)
                                    
                # Trying to structure the communications to keep progressbar moving
                # instead of freezing to process several log requests at once.
                req = []

                for i in range(int(len(prog)/5) + 10):
                    if prog:
                        req.append(prog.pop())
                        try:
                            req.append(prog.pop())
                        except:
                            pass
                    if log:
                        req.append(log.pop())
                    
                for i in req:
                    self.guiresultQ.put(i)
                #prog = []
                #log = []
                    
                # Monitor how many threads have died and reduce the threadcount
                # The thread will terminate when all download threads have died
            if not self.finishedQ.empty():
                for i in range(self.finishedQ.qsize()): 
                    _ = self.finishedQ.get()
                    self.threadcount -= 1
                                   
            if not self.threadcount:
                return
                
                


# A Multithread download 'worker'. Using threads should improve download speeds but may
# cause servers to drop the connection with an 'Error 104, Connection reset by peer'
# when too many threads are downloading at once. More testing is needed to determine an
# optimum number of concurrent downloads.
class DownloadWorker(Thread):
    def __init__(self, jobQ, resultQ, abortQ, progressQ, finishedQ, ratelimitQ, thread_id, gui):
        Thread.__init__(self)
        self.jobQ = jobQ
        self.resultQ = resultQ
        self.abortQ = abortQ
        self.progressQ = progressQ
        self.finishedQ = finishedQ
        self.ratelimitQ = ratelimitQ
        self.setDaemon(True)
        self.thread_id = thread_id
        self.lang = gui.get_gui_language()
        self.gui = gui
        

    def run(self):
        lang = self.lang
        while True:
            if not self.abortQ.empty():
                #self.resultQ.put(('log', lang['Thread {} has been stopped by the user'].format(self.thread_id)))
                self.resultQ.put(('aborted', job))
                self.resultQ.put(('fail', '', title_id))
                self.resultQ.put(('thread died',))
                self.finishedQ.put(self.thread_id)
                return
            if not self.jobQ.empty():
                job = self.jobQ.get()
                if not job:
                    self.resultQ.put(('status', self.thread_id, lang['Finished']))
                    self.resultQ.put(('log', lang['Thread {} has terminated'].format(self.thread_id)))
                    self.resultQ.put(('thread died',))
                    self.finishedQ.put(self.thread_id)
                    break

                else:
                    title_id = job[0][4]
                    if job[0][4] in self.gui.failed_downloads:
                        self.progressQ.put(job[0][3])
                        continue
    
                    app = job[0]
                    h3 = job[1]


                    # Attempt to download .app file
                    
                    rslt = fnku.download_file(app[0], app[1], app[2], expected_size=app[3], resultsq=self.resultQ, abortq=self.abortQ,
                                              progressq=self.progressQ, ratelimitq=self.ratelimitQ, titleid=title_id, threadid=self.thread_id)
                    if not rslt:
                        self.resultQ.put(('fail', '{}.app'.format(app[0].split('/')[6]), title_id))
                        self.resultQ.put(
                            ('log', lang['DOWNLOAD ERROR:']+' '+lang['Thread {} failed to download {}.app for title {}'].format(
                                self.thread_id, app[0].split('/')[6], title_id)))
                        
                    elif rslt == 'aborted':                      
                        self.resultQ.put(('aborted', job))
                        self.resultQ.put(('fail', '', title_id))
                        self.resultQ.put(('thread died',))
                        self.finishedQ.put(self.thread_id)

                    elif rslt == 'skipped':
                        pass # ignore for now.

                    else:
                        self.resultQ.put(
                            ('log', lang['Thread {} finished downloading {}.app for title {}'].format(self.thread_id,
                                                                                                app[0].split('/')[6],
                                                                                                title_id)))

                    # Attempt to download .h3 file
                    if not fnku.download_file(h3[0], h3[1], h3[2], ignore_404=h3[3], resultsq=self.resultQ, abortq=self.abortQ,
                                              progressq=self.progressQ, ratelimitq=self.ratelimitQ, titleid=title_id, threadid=self.thread_id):
                        self.resultQ.put(('fail', '{}'.format(h3[0].split('/')[6]), title_id))
                        self.resultQ.put(('log', lang['DOWNLOAD ERROR:']+' '+lang['Thread {} failed to download {} for title {}'].format(
                            self.thread_id, h3[0].split('/')[6], title_id)))
                    #else:
                        #self.resultQ.put(
                            #('log', lang['Thread {} finished downloading {} for title {}'].format(self.thread_id,
                                                                                            #h3[0].split('/')[6],
                                                                                            #title_id)))
