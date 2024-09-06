from qai_appbuilder import (QNNContext, QNNContextProc, QNNShareMemory, Runtime, LogLevel, ProfilingLevel, PerfProfile, QNNConfig, timer)
from PySide2.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QFileDialog, QLabel, QWidget, QListWidget, QListWidgetItem
from PySide2.QtCore import QThread, QTimer, Signal, Qt
from PySide2.QtGui import QPixmap, QPainter, QPen, QColor, QBrush
from PySide2 import QtCore, QtGui
from preprocess import tokenize as tokenizer, convert as converter
from clip_search_images_ui import Ui_MainWindow
import cv2, torch, numpy as np
import os, sys, time, threading
from typing import Union, List
import concurrent.futures

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
# QNN_SDK_PATH = "C:\\Qualcomm\\AIStack\\QAIRT\\2.23.0.240531\\lib\\arm64x-windows-msvc"
QNN_SDK_PATH = "C:\\Qualcomm\\AIStack\\QAIRT\\2.24.0.240626\\lib\\arm64x-windows-msvc"
IMAGE_ENCODER_MODEL = ROOT_DIR + "\\models\\export_openai_clip_CLIPImageEncoder.bin"
TEXT_ENCODER_MODEL  = ROOT_DIR + "\\models\\export_openai_clip_CLIPTextEncoder.bin"
IMAGE_FILE_NAME_LIST_LOCK    = threading.Lock()
IMAGE_FILE_NAME_LIST         = []
IMAGE_FILE_NAME_LIST_RIDX    = 0
IMAGE_FILE_FEATURES_MAP_LOCK = threading.Lock()
IMAGE_FILE_FEATURES_MAP      = {}
CONCURRENT_PROCESS_COUNT     = 4
SET_PERF_PROFILE_BURST_LOCK  = threading.Lock()
SET_PERF_PROFILE_BURST       = False
QNN_CONTEXT_PROC_USED        = False


class TextEncoder1(QNNContext):
    def Inference(self, 
        texts: List[str], perf_profile: PerfProfile = PerfProfile.DEFAULT):
        result = []
        for text in texts:
            input_datas = [text]
            output_data = super().Inference(input_datas, perf_profile)[0]
            output_data = torch.from_numpy(output_data)
            result.append(output_data)
        return result


class TextEncoder2(QNNContextProc):
    def Inference(self, shared_memory, 
        texts: List[str], perf_profile: PerfProfile = PerfProfile.DEFAULT):
        result = []
        for text in texts:
            input_datas = [text]
            output_data = super().Inference(shared_memory, input_datas, perf_profile)[0]
            output_data = torch.from_numpy(output_data)
            result.append(output_data)
        return result


class ImageEncoder1(QNNContext):
    def Inference(self, 
        images: Union[List[torch.Tensor], torch.Tensor], perf_profile: PerfProfile = PerfProfile.DEFAULT):
        result = []
        for i in range(len(images)):
            input_datas = [images[i]]
            output_data = super().Inference(input_datas, perf_profile)[0]
            output_data = torch.from_numpy(output_data)
            result.append(output_data)
        return result


class ImageEncoder2(QNNContextProc):
    def Inference(self, shared_memory, 
        images: Union[List[torch.Tensor], torch.Tensor], perf_profile: PerfProfile = PerfProfile.DEFAULT):
        result = []
        for i in range(len(images)):
            input_datas = [images[i]]
            output_data = super().Inference(shared_memory, input_datas, perf_profile)[0]
            output_data = torch.from_numpy(output_data)
            result.append(output_data)
        return result


class ImageScanner(QThread):
    update_process_info_signal, update_image_count_signal = Signal(str), Signal(str)
    def __init__(self, path):
        global IMAGE_FILE_NAME_LIST_LOCK, IMAGE_FILE_NAME_LIST, IMAGE_FILE_NAME_LIST_RIDX
        super().__init__()
        self.exited = False
        self.path = path
        with IMAGE_FILE_NAME_LIST_LOCK: 
            IMAGE_FILE_NAME_LIST, IMAGE_FILE_NAME_LIST_RIDX = [], 0

    def run(self):
        global IMAGE_FILE_NAME_LIST_LOCK, IMAGE_FILE_NAME_LIST
        time.sleep(1)
        print(f'ImageScanner STARTED')
        self.update_process_info_signal.emit(f'图片扫描中...{len(IMAGE_FILE_NAME_LIST)}')
        self.update_image_count_signal.emit(f'图片数量：{len(IMAGE_FILE_NAME_LIST)}')
        start_time = time.perf_counter()
        self.get_image_files(self.path)
        delta = (time.perf_counter() - start_time) * 1000
        self.update_process_info_signal.emit(f'图片扫描结束，耗时{delta:.0f}ms')
        self.update_image_count_signal.emit(f'图片数量：{len(IMAGE_FILE_NAME_LIST)}')
        print(f'ImageScanner EXITED')
        self.exited = True

    def get_image_files(self, path: str):
        global IMAGE_FILE_NAME_LIST_LOCK, IMAGE_FILE_NAME_LIST
        if not os.path.exists(path):
            print(f'Error: path {path} is not existed')
            return
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path):
                if os.path.splitext(file_path)[-1].lower() not in [".jpg", ".jpeg", ".png"]: 
                    continue
                with IMAGE_FILE_NAME_LIST_LOCK:
                    IMAGE_FILE_NAME_LIST.append(file_path)
                self.update_process_info_signal.emit(f'图片扫描中...{len(IMAGE_FILE_NAME_LIST)}')
                self.update_image_count_signal.emit(f'图片数量：{len(IMAGE_FILE_NAME_LIST)}')
                time.sleep(0.005)
            elif os.path.isdir(file_path):
                self.get_image_files(file_path)

    def stop(self):
        self.terminate()
        self.wait()


def processImages(scanner, id):
    global IMAGE_FILE_NAME_LIST_LOCK, IMAGE_FILE_NAME_LIST, IMAGE_FILE_NAME_LIST_RIDX
    global IMAGE_FILE_FEATURES_MAP_LOCK, IMAGE_FILE_FEATURES_MAP, IMAGE_ENCODER_MODEL
    global SET_PERF_PROFILE_BURST_LOCK, SET_PERF_PROFILE_BURST, QNN_CONTEXT_PROC_USED
    if QNN_CONTEXT_PROC_USED:
        image_encoder = ImageEncoder2(f'image_encoder_{id}', f'image_encoder_{id}', IMAGE_ENCODER_MODEL)
        shared_memory = QNNShareMemory(f'image_encoder_{id}', 1024 * 1024 * 16)
    else:
        image_encoder = ImageEncoder1(f'image_encoder_{id}', IMAGE_ENCODER_MODEL)
        shared_memory = None
    with SET_PERF_PROFILE_BURST_LOCK:
        if not QNN_CONTEXT_PROC_USED and not SET_PERF_PROFILE_BURST:
            SET_PERF_PROFILE_BURST = True
            PerfProfile.SetPerfProfileGlobal(PerfProfile.BURST)
    print(f'processImages {id} STARTED')
    start_time, count = time.perf_counter() * 1000, 0
    while True:
        index, image_file = 0, None
        with IMAGE_FILE_NAME_LIST_LOCK:
            if IMAGE_FILE_NAME_LIST_RIDX < len(IMAGE_FILE_NAME_LIST):
                index = IMAGE_FILE_NAME_LIST_RIDX
                image_file = IMAGE_FILE_NAME_LIST[index]
                IMAGE_FILE_NAME_LIST_RIDX = index + 1
        if image_file is None:
            if scanner.exited: break
            time.sleep(1)
            continue
        images = converter(image_file)
        if QNN_CONTEXT_PROC_USED:
            image_features_list = image_encoder.Inference(shared_memory, images, PerfProfile.BURST)
        else:
            image_features_list = image_encoder.Inference(images, PerfProfile.DEFAULT)
        with IMAGE_FILE_FEATURES_MAP_LOCK:
            IMAGE_FILE_FEATURES_MAP[image_file] = image_features_list[0]
        count = count + 1
        # print(f'{id} GET --> {count} {index} {image_file} --> ok({len(IMAGE_FILE_FEATURES_MAP)})')
    end_time = time.perf_counter() * 1000
    print(f'processImages {id} EXITED')
    if image_encoder is not None: del(image_encoder)
    if shared_memory is not None: del(shared_memory)
    return start_time, end_time


def processText(input_texts):
    global IMAGE_FILE_FEATURES_MAP_LOCK, IMAGE_FILE_FEATURES_MAP, TEXT_ENCODER_MODEL
    global SET_PERF_PROFILE_BURST_LOCK, SET_PERF_PROFILE_BURST, QNN_CONTEXT_PROC_USED
    if QNN_CONTEXT_PROC_USED:
        text_encoder = TextEncoder2(f'text_encoder', f'text_encoder', TEXT_ENCODER_MODEL)
        shared_memory = QNNShareMemory(f'text_encoder', 1024 * 1024 * 16)
    else:
        text_encoder = TextEncoder1(f'text_encoder', TEXT_ENCODER_MODEL)
        shared_memory = None
    with SET_PERF_PROFILE_BURST_LOCK:
        if not QNN_CONTEXT_PROC_USED and not SET_PERF_PROFILE_BURST:
            SET_PERF_PROFILE_BURST = True
            PerfProfile.SetPerfProfileGlobal(PerfProfile.BURST)
    print(f'processText STARTED')
    start_time, count = time.perf_counter() * 1000, 0
    texts = [tokenizer(text) for text in input_texts]
    if QNN_CONTEXT_PROC_USED:
        text_features_list = text_encoder.Inference(shared_memory, texts, PerfProfile.BURST)
    else:
        text_features_list = text_encoder.Inference(texts, PerfProfile.DEFAULT)
    with IMAGE_FILE_FEATURES_MAP_LOCK:
        for i in range(len(text_features_list)):
            result, text_features = [], text_features_list[i]
            for image_file, image_features in IMAGE_FILE_FEATURES_MAP.items():
                logits_per_image = image_features @ text_features.t()
                result.append(logits_per_image.numpy().item())
            max_index = np.argmax(np.array(result))
            similarity = (torch.tensor(result)).softmax(dim=-1).numpy() * 100.0
            values, indices = (torch.tensor(similarity)).topk(5)
            print(f"{input_texts[i]}: ")
            j = 0
            for image_file, image_features in IMAGE_FILE_FEATURES_MAP.items():
                ch = '\033[92m' + ('√' if j == max_index else '-') + '\033[0m'
                print(f"  [{ch}] {similarity[j]:>5.2f}% {result[j]:5.2f} <-- {image_file}")
                j = j + 1
    matched_indexs = [(indices.tolist()[i],values.tolist()[i]) for i in range(len(values.tolist())) if values.tolist()[i] > 5]
    end_time = time.perf_counter() * 1000
    print(f'processText EXITED')
    return start_time, end_time, matched_indexs


class CustomListWidgetItem(QWidget):
    def __init__(self, filepath, prob, parent=None):
        super(CustomListWidgetItem, self).__init__(parent)
        layout = QVBoxLayout()
        self.imageL = QLabel()
        self.imageL.setFixedWidth(400)
        self.imageL.setFixedHeight(350)
        self.imageL.setStyleSheet("QLabel { border: 1px solid black; }")
        self.imageL.mouseDoubleClickEvent = self.on_double_clicked
        layout.addWidget(self.imageL)
        self.filepath = filepath
        filename = os.path.basename(filepath)
        self.filenameL = QLabel(f'{filename}, [{prob:>5.2f}%]')
        self.filenameL.setFixedWidth(400)
        self.filenameL.setFixedHeight(30)
        layout.addWidget(self.filenameL)
        self.setLayout(layout)
        image = cv2.imread(self.filepath)
        self.update_image(image)
    
    def update_image(self, image):
        self.image = np.ascontiguousarray(image) if image is not None else None
        if self.image is None or self.image.size == 0: return
        qimage = QtGui.QImage (self.image.data, self.image.shape[1], self.image.shape[0], self.image.strides[0], 
            QtGui.QImage.Format_BGR888)
        self.pixmap = QPixmap(QPixmap.fromImage(qimage))
        self.imageL.setPixmap(self.pixmap.scaled(self.imageL.width(), self.imageL.height(), Qt.KeepAspectRatio))

    def on_double_clicked(self, event):
        cv2.namedWindow(self.filepath, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
        cv2.imshow(self.filepath, self.image)
        print(f"on_double_clicked({self.image.shape})")


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        global IMAGE_FILE_NAME_LIST, IMAGE_FILE_FEATURES_MAP
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.selectDirectoryButton.clicked.connect(self.select_images_directory)
        self.searchImagesButton.clicked.connect(self.search_matched_images)
        self.processInfomation = QLabel('未在扫描图片')
        self.processInfomation.setFixedWidth(250)
        self.imageFileCount = QLabel(f'图片数量：{len(IMAGE_FILE_NAME_LIST)}')
        self.imageFileCount.setFixedWidth(150)
        self.inferenceInformation = QLabel('未在推理图片')
        self.inferenceInformation.setFixedWidth(250)
        self.imageFeatureCount = QLabel(f'图片特征数：{len(IMAGE_FILE_FEATURES_MAP)}')
        self.imageFeatureCount.setFixedWidth(150)
        self.imageMatchedCount = QLabel(f'搜索结果：0')
        self.imageMatchedCount.setFixedWidth(200)
        self.imageListWidget.setFlow(QListWidget.LeftToRight)
        self.statusbar.addWidget(self.processInfomation, 1)
        self.statusbar.addWidget(self.imageFileCount, 2)
        self.statusbar.addWidget(self.inferenceInformation, 3)
        self.statusbar.addWidget(self.imageFeatureCount, 4)
        self.statusbar.addWidget(self.imageMatchedCount, 5)
        self.selectDirectoryButton.setFocus()
        self.image_futures = []
        self.text_futures = []
        self.scanner = None

    def select_images_directory(self):
        global IMAGE_FILE_NAME_LIST_LOCK, IMAGE_FILE_NAME_LIST, CONCURRENT_PROCESS_COUNT
        global IMAGE_FILE_FEATURES_MAP_LOCK, IMAGE_FILE_FEATURES_MAP
        directory = QFileDialog.getExistingDirectory(None, "选择图片目录")
        if directory is None or directory == "": return
        self.directoryLineEdit.setText(directory)
        self.processInfomation.setText(f'图片扫描中...{len(IMAGE_FILE_NAME_LIST)}')
        self.imageFileCount.setText(f'图片数量：{len(IMAGE_FILE_NAME_LIST)}')
        self.inferenceInformation.setText(f'图片推理中...{len(IMAGE_FILE_FEATURES_MAP)}')
        self.imageFeatureCount.setText(f'图片特征数：{len(IMAGE_FILE_FEATURES_MAP)}')
        self.scanner = ImageScanner(directory)
        self.scanner.update_process_info_signal.connect(self.update_process_info)
        self.scanner.update_image_count_signal.connect(self.update_image_count)
        self.scanner.start()
        executor = concurrent.futures.ThreadPoolExecutor()
        for i in range(CONCURRENT_PROCESS_COUNT):
            self.image_futures.append(executor.submit(processImages, self.scanner, i))
        self.timer_0 = QTimer(self)
        self.timer_0.timeout.connect(self.on_timer_timeout_0)
        self.timer_0.start()

    def search_matched_images(self):
        input_texts = self.textDescriptionTextEdit.toPlainText().strip()
        if input_texts == "": return
        executor = concurrent.futures.ThreadPoolExecutor()
        self.text_futures.append(executor.submit(processText, [input_texts]))
        self.imageListWidget.clear()
        self.timer_1 = QTimer(self)
        self.timer_1.timeout.connect(self.on_timer_timeout_1)
        self.timer_1.start()

    def update_process_info(self, text):
        self.processInfomation.setText(text)

    def update_image_count(self, text):
        self.imageFileCount.setText(text)

    def on_timer_timeout_0(self):
        global IMAGE_FILE_FEATURES_MAP, QNN_CONTEXT_PROC_USED, SET_PERF_PROFILE_BURST_LOCK, SET_PERF_PROFILE_BURST
        self.inferenceInformation.setText(f'图片推理中...{len(IMAGE_FILE_FEATURES_MAP)}')
        self.imageFeatureCount.setText(f'图片特征数：{len(IMAGE_FILE_FEATURES_MAP)}')
        done, start_times, end_times = True, [], []
        for future in self.image_futures:
            if not future.done():
                done = False
                break
            start_time, end_time = future.result()
            start_times.append(start_time)
            end_times.append(end_time)
        if not done: return
        # with SET_PERF_PROFILE_BURST_LOCK:
        #     if not QNN_CONTEXT_PROC_USED and SET_PERF_PROFILE_BURST:
        #         PerfProfile.RelPerfProfileGlobal()
        #         SET_PERF_PROFILE_BURST = False
        delta = max(end_times) - min(start_times)
        self.timer_0.stop()
        self.inferenceInformation.setText(f'图片推理结束，耗时{delta:.0f}ms')
        if self.scanner is not None:
            self.scanner.stop()
            self.scanner = None
        self.image_futures = []

    def on_timer_timeout_1(self):
        done, start_times, end_times, matched_indexs = True, [], [], []
        for future in self.text_futures:
            if not future.done():
                done = False
                break
            start_time, end_time, top5_matched_indexs = future.result()
            start_times.append(start_time)
            end_times.append(end_time)
            matched_indexs.append(top5_matched_indexs)
        if not done: return
        delta = max(end_times) - min(start_times)
        self.timer_1.stop()
        self.imageMatchedCount.setText(f'搜索结果：{len(matched_indexs[0])}')
        with IMAGE_FILE_FEATURES_MAP_LOCK:
            image_files = list(IMAGE_FILE_FEATURES_MAP.keys())
            for index, prob in matched_indexs[0]:
                item = QListWidgetItem(self.imageListWidget)
                widget = CustomListWidgetItem(image_files[index], prob)
                item.setSizeHint(widget.sizeHint())
                self.imageListWidget.addItem(item)
                self.imageListWidget.setItemWidget(item, widget)
        self.text_futures = []


if __name__ == '__main__':
    QNNConfig.Config(QNN_SDK_PATH, Runtime.HTP, LogLevel.WARN, ProfilingLevel.OFF)
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exec_()