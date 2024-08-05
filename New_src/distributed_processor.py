import zmq
import dill
from pathlib import Path
from pdf_processor import PDFProcessor
from Config import load_config

class DistributedProcessor:
    def __init__(self, is_master, master_address='localhost', port='5555'):
        self.is_master = is_master
        self.context = zmq.Context()
        if is_master:
            self.socket = self.context.socket(zmq.REP)
            self.socket.bind(f"tcp://*:{port}")
        else:
            self.socket = self.context.socket(zmq.REQ)
            self.socket.connect(f"tcp://{master_address}:{port}")

    def run(self):
        config = load_config('config.yaml')
        processor = PDFProcessor(config)

        if self.is_master:
            pdf_files = list(Path(config['input_dir']).glob('**/*.pdf'))
            total_files = len(pdf_files)
            files_processed = 0

            while files_processed < total_files:
                # Wait for a worker to request a file
                message = self.socket.recv()
                if message == b"READY":
                    if files_processed < total_files:
                        # Send the next file to process
                        file_to_process = str(pdf_files[files_processed])
                        self.socket.send(dill.dumps(file_to_process))
                        files_processed += 1
                    else:
                        # No more files to process
                        self.socket.send(b"DONE")
            print("All files processed.")
        else:
            while True:
                # Tell the master we're ready for work
                self.socket.send(b"READY")
                # Get a response from the master
                response = self.socket.recv()
                if response == b"DONE":
                    break
                # Process the file
                file_to_process = dill.loads(response)
                try:
                    processor.process_single_file(Path(file_to_process))
                    print(f"Processed: {file_to_process}")
                except Exception as e:
                    print(f"Error processing {file_to_process}: {str(e)}")
