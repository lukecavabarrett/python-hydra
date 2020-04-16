import json
import os

if os.path.exists('/tmp/__hydra_control_pipe_out'):
    comm_pipe_out = open('/tmp/__hydra_control_pipe_out', 'w')
else:
    comm_pipe_out = None


def is_available():
    return comm_pipe_out is not None


class checkpoint:
    def __init__(self):
        self._linked_files = []

    def save_to_server(self):
        self._request_type = 'save_checkpoint'
        comm_pipe_out.write(json.dumps(self, default=lambda o: o.__dict__, sort_keys=True))
        comm_pipe_out.write('\0')
        comm_pipe_out.flush()

    def link_file(self, path):
        self._linked_files.append(os.path.abspath(path))

    def linked_files(self):
        return self._linked_files

    def retrieve_file(self, k):
        for f in self._linked_files:
            if os.path.basename(f) == os.path.basename(k):
                return f
        return None


def restore_checkpoint():
    if not os.path.exists('/tmp/__hydra_checkpoint.json'):
        return None
    with open('/tmp/__hydra_checkpoint.json') as json_file:
        ck = checkpoint()
        for key, value in json.load(json_file).items():
            setattr(ck, key, value)
        return ck


def set_eta(eta):
    comm_pipe_out.write(json.dumps({'_request_type': 'set_eta', 'millisec': int(eta * 1000)}))
    comm_pipe_out.write('\0')
    comm_pipe_out.flush()