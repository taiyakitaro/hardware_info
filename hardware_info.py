import tkinter as tk
from tkinter import ttk
import psutil
import GPUtil
from cpuinfo import get_cpu_info
import time
import math

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
    mem = psutil.virtual_memory()
    return {
        "Total Memory (GB)": round(mem.total / (1024**3), 2),
        "Used Memory (%)": mem.percent
    }

def get_gpu_info():#gpu 詳細表示(現在はNVIDIAGPUのみ)
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

def simple_cpu_benchmark(duration=1.0):
    """指定秒数だけCPUに負荷をかけて回数をスコアに変換(任意に変更可)"""
    start_time = time.time()
    count = 0
    while time.time() - start_time < duration:
        for i in range(1, 1000):#計算量の調整(いじりすぎるとスコアが意味をなさなくなるので注意)
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
        self.geometry("500x700")
        self.resizable(False, False)

        # 言語設定（初期値は日本語）
        self.language = "ja"

        self.label_frame = ttk.LabelFrame(self, text=self.get_text("System Information"), padding=10)
        self.label_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.labels = {}

        # ラベル初期化
        all_info = {}
        all_info.update(get_cpu_info_details())
        all_info.update(get_memory_info())
        all_info.update(get_gpu_info())

        for key in all_info:
            lbl = ttk.Label(self.label_frame, text=f"{key}: ")
            lbl.pack(anchor="w", padx=5, pady=2)
            self.labels[key] = lbl

        # ベンチマークボタン
        self.benchmark_btn = ttk.Button(self, text=self.get_text("Start CPU Benchmark"), command=self.run_benchmark)
        self.benchmark_btn.pack(pady=10)

        self.benchmark_result = ttk.Label(self, text=self.get_text("Score: ---"))
        self.benchmark_result.pack(pady=5)

        # 言語変更ボタン
        self.language_btn = ttk.Button(self, text=self.get_text("Change Language"), command=self.toggle_language)
        self.language_btn.pack(pady=10)

        # 更新ループ開始
        self.update_info()

    def get_text(self, text):
        """指定されたテキストを現在の言語に基づいて翻訳"""
        translations = {
            "System Information": {"ja": "システム情報", "en": "System Information"},
            "Start CPU Benchmark": {"ja": "CPUベンチマーク開始", "en": "Start CPU Benchmark"},
            "Score: ---": {"ja": "スコア: ---", "en": "Score: ---"},
            "Benchmarking...": {"ja": "ベンチマーク中...", "en": "Benchmarking..."},
            "Score: {score} (iterations per second)": {
                "ja": "スコア: {score}（1秒間に処理した回数）",
                "en": "Score: {score} (iterations per second)"
            },
            "Change Language": {"ja": "言語を変更", "en": "Change Language"}
        }
        return translations.get(text, {}).get(self.language, text)

    def toggle_language(self):
        """言語を切り替える"""
        self.language = "en" if self.language == "ja" else "ja"
        self.update_language()

    def update_language(self):
        """UIのテキストを現在の言語に基づいて更新"""
        self.label_frame.config(text=self.get_text("System Information"))
        self.benchmark_btn.config(text=self.get_text("Start CPU Benchmark"))
        self.benchmark_result.config(text=self.get_text("Score: ---"))
        self.language_btn.config(text=self.get_text("Change Language"))

    def update_info(self):
        all_info = {}
        all_info.update(get_cpu_info_details())
        all_info.update(get_memory_info())
        all_info.update(get_gpu_info())

        for key, label in self.labels.items():
            label.config(text=f"{key}: {all_info.get(key, 'N/A')}")

        self.after(1000, self.update_info)

    def run_benchmark(self):
        self.benchmark_result.config(text=self.get_text("Benchmarking..."))
        self.update_idletasks()
        score = simple_cpu_benchmark()
        self.benchmark_result.config(text=self.get_text("Score: {score} (iterations per second)").format(score=score))


if __name__ == "__main__":
    app = HardwareMonitorApp()
    app.mainloop()
