#!/usr/bin/env python3
# runner.py
# Lee config.json, itera muestras y algoritmos, ejecuta compresión/descompresión y monitoriza recursos.
import os
import sys
import json
import csv
import shlex
import subprocess
import time
import psutil
from datetime import datetime
from dateutil import tz
import argparse
from pathlib import Path

def load_config(path):
    with open(path, "r") as f:
        return json.load(f)

def run_and_monitor(cmd, timeout, sample_interval):
    # start subprocess (shell=True for complex commands)
    proc = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)
    p = psutil.Process(proc.pid)
    start = time.time()
    peak_rss = 0
    cpu_time = 0.0
    io_read = 0
    io_write = 0
    try:
        while True:
            if proc.poll() is not None:
                break
            try:
                mem = p.memory_info().rss
                if mem > peak_rss: peak_rss = mem
                ctimes = p.cpu_times()
                cpu_time = ctimes.user + ctimes.system
                io = p.io_counters()
                io_read = io.read_bytes
                io_write = io.write_bytes
            except (psutil.NoSuchProcess, psutil.ZombieProcess):
                break
            if time.time() - start > timeout:
                proc.kill()
                return {"status":"timeout","elapsed":time.time()-start,"peak_rss":peak_rss,"cpu_time":cpu_time,"io_read":io_read,"io_write":io_write}
            time.sleep(sample_interval)
        end = time.time()
        # final sample
        try:
            mem = p.memory_info().rss
            if mem > peak_rss: peak_rss = mem
            ctimes = p.cpu_times()
            cpu_time = ctimes.user + ctimes.system
            io = p.io_counters()
            io_read = io.read_bytes
            io_write = io.write_bytes
        except Exception:
            pass
        return {"status":"finished","elapsed":end-start,"peak_rss":peak_rss,"cpu_time":cpu_time,"io_read":io_read,"io_write":io_write, "returncode": proc.returncode}
    except Exception as e:
        proc.kill()
        return {"status":"error","error":str(e)}

def safe_cmd(cmd):
    # Replace placeholders; caller must format with infile/outfile etc.
    return cmd

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--samples-dir", default="samples")
    parser.add_argument("--work-dir", default="work")
    parser.add_argument("--out-csv", default="results.csv")
    args = parser.parse_args()

    cfg = load_config(args.config)
    os.makedirs(args.work_dir, exist_ok=True)

    sample_files = sorted(Path(args.samples_dir).glob("*"))
    if not sample_files:
        print("No sample files in", args.samples_dir, "— ejecuta generator.py primero.")
        sys.exit(1)

    # CSV header
    header = ["timestamp","sample","algorithm","level","phase","command","status","elapsed_s","peak_rss_bytes","cpu_time_s","io_read_bytes","io_write_bytes","infile_size_bytes","outfile_size_bytes","notes"]
    with open(args.out_csv, "w", newline="") as csvf:
        writer = csv.writer(csvf)
        writer.writerow(header)

        for sample in sample_files:
            infile = str(sample)
            infile_size = sample.stat().st_size
            for algo in cfg["algorithms"]:
                name = algo["name"]
                for level in algo.get("levels", [None]):
                    level_str = str(level) if level is not None else ""
                    # compress cmd
                    comp_cmd = algo["compress_cmd"].format(level=level_str, infile=infile, outfile=infile + ".out")
                    # some compress commands produce predictable extension; we'll glob later
                    print(f"[{datetime.now().isoformat()}] {sample.name} -> {name} level {level_str}")
                    comp_res = run_and_monitor(comp_cmd, cfg.get("timeout_seconds",300), cfg.get("sample_interval_seconds",0.1))
                    # find compressed file (best-effort)
                    outfile_candidates = list(Path(".").glob(infile + "*"))
                    compressed_path = None
                    # prefer file larger than 0 and different from infile
                    for c in outfile_candidates:
                        try:
                            if c.exists() and c.stat().st_size > 0 and str(c) != infile:
                                if str(c).endswith(tuple(algo.get("extensions",[]))):
                                    compressed_path = str(c)
                                    break
                                elif compressed_path is None:
                                    compressed_path = str(c)
                        except Exception:
                            pass
                    outfile_size = os.path.getsize(compressed_path) if compressed_path and os.path.exists(compressed_path) else ""
                    writer.writerow([datetime.now().isoformat(), sample.name, name, level_str, "compress", comp_cmd, comp_res.get("status"), comp_res.get("elapsed"), comp_res.get("peak_rss"), comp_res.get("cpu_time"), comp_res.get("io_read"), comp_res.get("io_write"), infile_size, outfile_size, ""])
                    csvf.flush()

                    if comp_res.get("status") != "finished":
                        # cleanup partial artifacts and continue
                        print("Compression failed/timeout; skipping decompression.")
                        continue

                    # decompression command
                    # choose infile for decompression (compressed_path) or pattern
                    if compressed_path is None:
                        print("No compressed file found for", comp_cmd)
                        continue
                    dec_cmd = algo["decompress_cmd"].format(infile=compressed_path, outfile=os.path.join(args.work_dir, f"decompressed_{sample.name}_{name}_{level_str}"))
                    dec_res = run_and_monitor(dec_cmd, cfg.get("timeout_seconds",300), cfg.get("sample_interval_seconds",0.1))
                    dec_outfile = dec_cmd.split(">")[-1].strip() if ">" in dec_cmd else ""
                    dec_out_size = os.path.getsize(dec_outfile) if dec_outfile and os.path.exists(dec_outfile) else ""
                    writer.writerow([datetime.now().isoformat(), sample.name, name, level_str, "decompress", dec_cmd, dec_res.get("status"), dec_res.get("elapsed"), dec_res.get("peak_rss"), dec_res.get("cpu_time"), dec_res.get("io_read"), dec_res.get("io_write"), infile_size, dec_out_size, ""])
                    csvf.flush()

                    # cleanup generated compressed + decompressed files to avoid filling disk (optional)
                    try:
                        if compressed_path and os.path.exists(compressed_path):
                            os.remove(compressed_path)
                        if dec_outfile and os.path.exists(dec_outfile):
                            os.remove(dec_outfile)
                    except Exception:
                        pass

    print("Experimento finalizado. Resultados en", args.out_csv)

if __name__ == "__main__":
    main()
