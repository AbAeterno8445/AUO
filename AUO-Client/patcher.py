import os, errno

class Patcher(object):
    def __init__(self, conn):
        self.conn = conn

        self.filedl_list = {}

    # Delete a file silently
    def silentremove(self, filename):
        try:
            os.remove(filename)
        except OSError as e:  # this would be "except OSError, e:" before Python 2.6
            if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
                raise  # re-raise exception if a different error occurred

    def check_uptodate(self):
        self.conn.send("filedl_check")
        uptodate = False
        while not uptodate:
            sv_data = self.conn.receive(True)
            if sv_data:
                sv_data = sv_data.split('|')
                if sv_data[0] == "filedl_begin": # Check if file is up to date
                    dl = False
                    try:
                        if not os.path.getsize(sv_data[1]) == int(sv_data[2]):
                            dl = True
                        else:
                            print("File [" + sv_data[1] + "] up to date.")
                            self.conn.send("filedl_uptodate|" + sv_data[1])
                            self.conn.send("filedl_check")

                    except os.error:
                        dl = True

                    if dl: # Start downloading if not
                        print("Downloading file [" + sv_data[1] + "]...")
                        self.silentremove(sv_data[1])
                        self.filedl_list[sv_data[1]] = open(sv_data[1], "a")
                        self.conn.send("filedl_ok|" + sv_data[1])
                        self.conn.send("filedl_next|" + sv_data[1])

                elif sv_data[0] == "filedl": # Write data into file
                    self.filedl_list[sv_data[1]].write(sv_data[2])
                    self.conn.send("filedl_next|" + sv_data[1])

                elif sv_data[0] == "filedl_done": # Close file when done and keep checking
                    self.filedl_list[sv_data[1]].close()
                    self.filedl_list.pop(sv_data[1], None)
                    self.conn.send("filedl_check")

                elif sv_data[0] == "filedl_end":
                    uptodate = True