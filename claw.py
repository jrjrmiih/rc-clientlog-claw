from source_folder import SourceFolder


class Claw:
    def __init__(self):
        self.source = SourceFolder()

    def start(self):
        self.source.get_source_log(self.log_parse, self.log_parse_error)

    def log_parse(self, json_obj_list):
        # print(len(json_obj_list))
        pass

    def log_parse_error(self, file, startline, index, info):
        print('\nlog parse error: {0} +{1}, {2}'.format(file, index, info))


claw = Claw()
claw.start()
