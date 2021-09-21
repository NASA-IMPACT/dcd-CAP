class CAP():
    def __init__(self, master_list):
        if master_list:
            self.master_list = master_list
        else:
            raise Exception("Please provide a master list")

    def ingest(self):
        pass

    def run_qa(self):
        pass

    def run_tag_check(self):
        pass

    def run_dataset_check(self):
        pass

    def export(self):
        # return a dictionary with all required metrics
        return
    
    def say_hi(self):
        print("Hi!")
