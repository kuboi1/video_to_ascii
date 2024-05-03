import cv2
import os
import threading
from string import digits
from random import choice as rand_choice

class VideoFramesExtractor:
    def __init__(self, output_path: str) -> None:
        self._output_path = output_path

        self._vidcap = None

        self._extracting = False
        self._extracted_frames = 0
        self._frame_count = 0
        self._output_dir = ''
        
    def extract(self, video_path: str) -> str:
        self._vidcap = cv2.VideoCapture(video_path)

        self._create_output_dir()

        self._frame_count = int(self._vidcap.get(cv2.CAP_PROP_FRAME_COUNT))

        self._extracting = True

        extract_thread = threading.Thread(target=self._extract_frames)
        pp_thread = threading.Thread(target=self._print_progress)

        extract_thread.start()
        pp_thread.start()

        extract_thread.join()
        pp_thread.join()

        return self._output_dir
    
    def get_vidcap_fps(self) -> float:
        return self._vidcap.get(cv2.CAP_PROP_FPS)

    def _extract_frames(self) -> None:
        while self._extracting:
            self._extracted_frames += 1
            self._extracting, image = self._vidcap.read()
            try:
                cv2.imwrite(os.path.join(self._output_dir, f'frame_{self._extracted_frames}.jpg'), image)
            except:
                self._extracting = False
                break
            if cv2.waitKey(10) == 27:
                break
    
    def _print_progress(self) -> None:
        print('\r')
        while self._extracting and self._extracted_frames < self._frame_count:
            print(f'Extracting frames from video [{self._extracted_frames}/{self._frame_count}]', end='\r')
        print('                                                                                    ')
    
    def _create_output_dir(self) -> None:
        temp_id = ''.join([rand_choice(digits) for _ in range(10)])
        self._output_dir = os.path.join(self._output_path, temp_id)
        os.mkdir(self._output_dir)