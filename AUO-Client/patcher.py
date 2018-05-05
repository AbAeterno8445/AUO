import os

class Patcher(object):
    def __init__(self, conn):
        self.conn = conn

        self.filedl_list = {}
        self.tmp_queue = []

    def check_uptodate(self):
        self.conn.send_data("filedl_check")
        uptodate = False
        while not uptodate:
            sv_data = self.conn.get_data(True)
            if sv_data:
                sv_data = sv_data.split('|')
                if sv_data[0] == "filedl_begin": # Check if file is up to date
                    dl = False
                    try:
                        if not os.path.getsize(sv_data[1]) == int(sv_data[2]):
                            dl = True
                        else:
                            print("File [" + sv_data[1] + "] up to date.")
                            self.conn.send_data("filedl_uptodate|" + sv_data[1])
                            self.conn.send_data("filedl_check")

                    except os.error:
                        dl = True

                    if dl: # Start downloading if not
                        print("Downloading file [" + sv_data[1] + "]...")
                        self.filedl_list[sv_data[1]] = []
                        self.conn.send_data("filedl_ok|" + sv_data[1])

                elif sv_data[0] == "filedl": # Download file line into dict
                    self.filedl_list[sv_data[1]].append(sv_data[2])

                elif sv_data[0] == "filedl_done": # Write dictionary entry for file into new updated file
                    with open(sv_data[1], "w") as f:
                        for l in self.filedl_list[sv_data[1]]:
                            f.write(l)
                    self.conn.send_data("filedl_check")

                elif sv_data[0] == "filedl_end":
                    uptodate = True
                    for i in self.tmp_queue:
                        self.conn.rec_queue.put(i)

                else: # Add unrelated messages to temporary list to process later
                    self.tmp_queue.append(''.join(sv_data))