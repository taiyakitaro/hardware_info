import tkinter as tk
from tkinter import ttk
import psutil
import GPUtil
from cpuinfo import get_cpu_info
import time
import math
import wmi

def get_cpu_info_details():
    cpu_info = get_cpu_info()
    return {
        "Processor": cpu_info.get("brand_raw", "Unknown"),
        "Physical Cores": psutil.cpu_count(logical=False),
        "Total Cores": psutil.cpu_count(logical=True),
        "Max Frequency (MHz)": psutil.cpu_freq().max,
        "Current Frequency (MHz)": psutil.cpu_freq().current,
        "CPU Usage (%)": psutil.cpu_percent(interval=0.5)
    }

def get_memory_info():
    MEMORY_TYPE_MAP = {
        0: "Unknown",
        1: "Other",
        2: "DRAM",
        3: "Synchronous DRAM",
        4: "Cache DRAM",
        5: "EDO",
        6: "EDRAM",
        7: "VRAM",
        8: "SRAM",
        9: "RAM",
        10: "ROM",
        11: "Flash",
        12: "EEPROM",
        13: "FEPROM",
        14: "EPROM",
        15: "CDRAM",
        16: "3DRAM",
        17: "SDRAM",
        18: "SGRAM",
        19: "RDRAM",
        20: "DDR",
        21: "DDR2",
        22: "DDR2 FB-DIMM",
        24: "DDR3",
        26: "DDR4"
    }

    mem = psutil.virtual_memory()
    memory_info = {
        "Total Memory (GB)": round(mem.total / (1024**3), 2),
        "Used Memory (%)": mem.percent,
        "Used Memory (GB)": round(mem.used / (1024**3), 2)
    }

    try:
        c = wmi.WMI()
        physical_memories = c.Win32_PhysicalMemory()
        if len(physical_memories) > 0:
            # 最初のモジュールの情報を取得
            memory = physical_memories[0]
            memory_type = MEMORY_TYPE_MAP.get(memory.MemoryType, "Unknown")
            memory_info["Memory Module 0"] = {
                "Manufacturer": memory.Manufacturer.strip() if memory.Manufacturer else "Unknown",#メモリモジュール製造メーカー
                "Type": memory_type,#DDR規格(DDR5・LPDDR5・LPDDR5X・LPDDR4・LPDDR4Xは非対応 ※unknownと表示(DDR5系はWMIの対応待ち・LPDDR4系は検証できず))

                #"Capacity (GB)": round(int(memory.Capacity) / (1024**3), 2),#モジュールの容量
                #"Speed (MHz)": memory.Speed if memory.Speed else "Unknown",#モジュールの速度
                #"Serial Number": memory.SerialNumber.strip() if memory.SerialNumber else "Unknown",#シリアルナンバー
                #"Part Number": memory.PartNumber.strip() if memory.PartNumber else "Unknown"#部品番号
            }

            # 2枚目のモジュールがあり、メーカーが異なる場合に追加
            if len(physical_memories) > 1:
                second_memory = physical_memories[1]
                if second_memory.Manufacturer.strip() != memory.Manufacturer.strip():
                    second_memory_type = MEMORY_TYPE_MAP.get(second_memory.MemoryType, "Unknown")
                    memory_info["Memory Module 1"] = {
                        "Manufacturer": second_memory.Manufacturer.strip() if second_memory.Manufacturer else "Unknown",#メモリモジュール製造メーカー
                        "Type": second_memory_type,#DDR規格(DDR5・LPDDR5・LPDDR5X 非対応 ※unknownと表示)

                        #"Capacity (GB)": round(int(second_memory.Capacity) / (1024**3), 2),
                        #"Speed (MHz)": second_memory.Speed if second_memory.Speed else "Unknown",
                        #"Serial Number": second_memory.SerialNumber.strip() if second_memory.SerialNumber else "Unknown",
                        #"Part Number": second_memory.PartNumber.strip() if second_memory.PartNumber else "Unknown"
                    }
    except Exception as e:
        memory_info["Memory Info Error"] = f"Error: {str(e)}"

    return memory_info

def get_gpu_info():
    info = {}
    try:
        gpus = GPUtil.getGPUs()
        if not gpus:
            info["NVIDIA GPU Error"] = "No NVIDIA GPUs detected."
        else:
            for i, gpu in enumerate(gpus):
                info[f"NVIDIA GPU {i} Name"] = gpu.name
                info[f"NVIDIA GPU {i} Load (%)"] = f"{gpu.load * 100:.1f}%"
                info[f"NVIDIA GPU {i} Memory Total (MB)"] = gpu.memoryTotal
                info[f"NVIDIA GPU {i} Memory Free (MB)"] = gpu.memoryFree
                info[f"NVIDIA GPU {i} Memory Used (MB)"] = gpu.memoryUsed
    except Exception as e:
        info["NVIDIA GPU Error"] = f"Error: {str(e)}"
    return info

def get_storage_info():
    info = {}
    try:
        c = wmi.WMI()
        for i, disk in enumerate(c.Win32_DiskDrive()):
            info[f"Storage {i} Model"] = disk.Model
            info[f"Storage {i} Interface"] = disk.InterfaceType
            info[f"Storage {i} Size (GB)"] = round(int(disk.Size) / (1024**3), 2)
            # NVMeバージョン(PCIE vr.)等はWMIでは困難=> 今後の実装に期待
    except Exception as e:
        info["Storage Error"] = f"Error: {str(e)}"
    return info

def simple_cpu_benchmark(duration=1.0):
    start_time = time.time()
    count = 0
    while time.time() - start_time < duration:
        for i in range(1, 1000):
            _ = i * i
            _ = math.sqrt(i)
            _ = math.sin(i)
            _ = math.log(i)
        count += 1
    return count

class HardwareMonitorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hardware Monitor + Benchmark")
        self.geometry("500x750")
        self.resizable(False, False)

        self.language = "ja"
        self.labels = {}

        self.cpu_frame = ttk.LabelFrame(self, text="CPU", padding=10)
        self.cpu_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.mem_frame = ttk.LabelFrame(self, text="Memory", padding=10)
        self.mem_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.gpu_frame = ttk.LabelFrame(self, text="GPU", padding=10)
        self.gpu_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.storage_frame = ttk.LabelFrame(self, text="Storage", padding=10)
        self.storage_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 初期表示
        self.build_labels()

        self.benchmark_btn = ttk.Button(self, text=self.get_text("Start CPU Benchmark"), command=self.run_benchmark)
        self.benchmark_btn.pack(pady=10)

        self.benchmark_result = ttk.Label(self, text=self.get_text("Score: ---"))
        self.benchmark_result.pack(pady=5)

        self.language_btn = ttk.Button(self, text=self.get_text("Change Language"), command=self.toggle_language)
        self.language_btn.pack(pady=10)

        self.update_info()

    # GUI　ラベル
    def build_labels(self):
        for frame, data in [
            (self.cpu_frame, get_cpu_info_details()),
            (self.mem_frame, get_memory_info()),
            (self.gpu_frame, get_gpu_info()),
            (self.storage_frame, get_storage_info())
        ]:
            for key in data:
                lbl = ttk.Label(frame, text=f"{key}: {data[key]}")
                lbl.pack(anchor="w", padx=5, pady=2)
                self.labels[key] = lbl

    # 言語切り替えのための場所
    def get_text(self, text):
        translations = {
            "Start CPU Benchmark": {"ja": "CPUベンチマーク開始", "en": "Start CPU Benchmark"},
            "Score: ---": {"ja": "スコア: ---", "en": "Score: ---"},
            "Benchmarking...": {"ja": "ベンチマーク中...", "en": "Benchmarking..."},
            "Score: {score} (iterations per second)": {
                "ja": "スコア: {score}（1秒間に処理した回数）",
                "en": "Score: {score} (iterations per second)"
            },
            #プロセッサー
            "Change Language": {"ja": "言語を変更", "en": "Change Language"},
            "Processor": {"ja": "プロセッサ", "en": "Processor"},
            "Physical Cores": {"ja": "物理コア数", "en": "Physical Cores"},
            "Total Cores": {"ja": "総コア数", "en": "Total Cores"},
            "Max Frequency (MHz)": {"ja": "最大周波数 (MHz)", "en": "Max Frequency (MHz)"},
            "Current Frequency (MHz)": {"ja": "現在の周波数 (MHz)", "en": "Current Frequency (MHz)"},
            "CPU Usage (%)": {"ja": "CPU使用率 (%)", "en": "CPU Usage (%)"},
            
            #メモリー
            "Total Memory (GB)": {"ja": "総メモリ (GB)", "en": "Total Memory (GB)"},
            "Used Memory (%)": {"ja": "使用メモリ率 (%)", "en": "Used Memory (%)"},
            "Used Memory (GB)": {"ja": "使用メモリ (GB)", "en": "Used Memory (GB)"},
            "Manufacturer":{"ja":"モジュールメーカー", "en": "module manufacturer"},
            "Type": {"ja": "DRAMタイプ","TYPE":"DRAM Type"},
            
            #NVIDIA GPU
            "NVIDIA GPU Error": {"ja": "NVIDIA GPUエラー", "en": "NVIDIA GPU Error"},

            #ストレージ
            "Storage Error": {"ja": "ストレージエラー", "en": "Storage Error"},
            "Storage {i} Model": {"ja": "ストレージ {i} モデル", "en": "Storage {i} Model"},
            "Storage {i} Interface": {"ja": "ストレージ {i} インターフェース", "en": "Storage {i} Interface"},
            "Storage {i} Size (GB)": {"ja": "ストレージ {i} サイズ (GB)", "en": "Storage {i} Size (GB)"}
        }
        return translations.get(text, {}).get(self.language, text)

    def toggle_language(self):
        self.language = "en" if self.language == "ja" else "ja"
        self.update_language()

    def update_language(self):
        self.benchmark_btn.config(text=self.get_text("Start CPU Benchmark"))
        self.benchmark_result.config(text=self.get_text("Score: ---"))
        self.language_btn.config(text=self.get_text("Change Language"))

    def update_info(self):
        sources = {
            **get_cpu_info_details(),
            **get_memory_info(),
            **get_gpu_info(),
            **get_storage_info()
        }

        for key, label in self.labels.items():
            if key in sources:
                translated_key = self.get_text(key)
                label.config(text=f"{translated_key}: {sources[key]}")
        self.after(1000, self.update_info)

    def run_benchmark(self):
        self.benchmark_result.config(text=self.get_text("Benchmarking..."))
        self.update_idletasks()
        score = simple_cpu_benchmark()
        self.benchmark_result.config(
            text=self.get_text("Score: {score} (iterations per second)").format(score=score)
        )

if __name__ == "__main__":
    try:
        app = HardwareMonitorApp()
        app.mainloop()
    except Exception as e:
        with open("error_log.txt", "w", encoding="utf-8") as f:
            f.write(str(e))
        raise
