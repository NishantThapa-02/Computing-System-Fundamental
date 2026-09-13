#!/usr/bin/env python3
"""
CS 3360: Computing Systems Fundamentals
Programming Assignment 01: Synthetic Process Workload Generation and Simulation
"""

import math
import random

NUM_PROCESSES = 1000
LAMBDA_PER_MS = 2.0
T_MS = 1.0
OUTPUT_MD_PATH = "workload_report.md"

class Process:
    def __init__(self, pid, arrival_time, service_time):
        self.pid = pid
        self.arrival_time = arrival_time
        self.service_time = service_time
        self.state = "NEW"
        self.start_time = None
        self.end_time = None

    @property
    def turnaround_time(self):
        return self.end_time - self.arrival_time

    @property
    def waiting_time(self):
        return self.start_time - self.arrival_time

def _exp_inverse_transform(rate=None, mean=None):
    u = random.random()
    while u == 0:
        u = random.random()

    if rate is not None:
        return -math.log(u) / rate
    return -mean * math.log(u)

def generate_processes(num_processes=NUM_PROCESSES,
                        lambda_per_ms=LAMBDA_PER_MS,
                        t_ms=T_MS):
    processes = []
    arrival_time = 0

    for i in range(1, num_processes + 1):
        if i == 1:
            inter_arrival_ms = 0
        else:
            inter_arrival_ms = round(_exp_inverse_transform(rate=lambda_per_ms))

        arrival_time += inter_arrival_ms

        service_time_ms = round(_exp_inverse_transform(mean=t_ms))

        processes.append(Process(i, arrival_time, service_time_ms))

    return processes

def run_fifo_simulation(processes):
    current_time = 0
    for p in processes:
        p.state = "READY"
        start = max(current_time, p.arrival_time)
        p.start_time = start
        p.state = "RUNNING"
        p.end_time = start + p.service_time
        p.state = "TERMINATED"
        current_time = p.end_time
    return processes


def build_cpu_trace(processes):
    segments = []
    current_time = 0
    for p in processes:
        if current_time < p.start_time:
            segments.append((current_time, p.start_time, "IDLE", None))
            current_time = p.start_time
        segments.append((p.start_time, p.end_time, "BUSY", p.pid))
        current_time = p.end_time
    return segments

def compute_generation_stats(processes, lambda_per_ms, t_ms):
    n = len(processes)
    a_last = processes[-1].arrival_time

    lambda_a = (n / a_last) if a_last > 0 else float("inf")
    s_a = sum(p.service_time for p in processes) / n

    return {
        "n": n,
        "a_last": a_last,
        "lambda_a": lambda_a,
        "lambda_expected": lambda_per_ms,
        "s_a": s_a,
        "s_expected": t_ms,
    }


def compute_simulation_stats(processes):
    n = len(processes)
    total_complete_time = processes[-1].end_time
    total_service_time = sum(p.service_time for p in processes)

    avg_turnaround = sum(p.turnaround_time for p in processes) / n
    avg_waiting = sum(p.waiting_time for p in processes) / n
    cpu_utilization = (total_service_time / total_complete_time * 100
                        if total_complete_time else 0.0)
    throughput = (n / (total_complete_time / 1000.0)
                  if total_complete_time else 0.0)

    return {
        "Total Complete Time": f"{total_complete_time}ms",
        "Average Turnaround Time": f"{avg_turnaround:.2f}ms",
        "Average Waiting Time": f"{avg_waiting:.2f}ms",
        "Overall CPU utilization": f"{cpu_utilization:.2f}%",
        "Overall System Throughput": f"{throughput:.2f} processes/sec",
    }

def format_workload_table(processes):
    lines = ["process_id | arrival_time | requested_service_time",
             "-----------|--------------|-----------------------"]
    for p in processes:
        lines.append(f"{p.pid:<10} | {p.arrival_time:<12} | {p.service_time}")
    return lines


def format_trace_table(segments):
    lines = ["Time (in ms)      | CPU Status | PID",
             "------------------|------------|-----"]
    for start, end, status, pid in segments:
        pid_str = "" if pid is None else str(pid)
        lines.append(f"[{start:6d},{end:6d})   | {status:<10} | {pid_str}")
    return lines


def format_generation_stats(gstats):
    lines = [
        "Statistics                    | Results",
        "------------------------------|-----------------",
        f"Expected Average Arrival Rate | {gstats['lambda_expected']:.2f} processes per millisecond",
        f"Computed Average Arrival Rate | {gstats['lambda_a']:.2f} processes per millisecond",
        f"Expected Average Service Time | {gstats['s_expected']:.2f} milliseconds",
        f"Computed Average Service Time | {gstats['s_a']:.2f} milliseconds",
    ]
    return lines


def format_simulation_stats(sstats):
    lines = ["Statistics                    | Results",
              "------------------------------|-----------------"]
    for k, v in sstats.items():
        lines.append(f"{k:<30} | {v}")
    return lines


def build_report(processes, segments, gstats, sstats):
    report = []
    report.append("# CS 3360 -- Synthetic Process Workload Generation and Simulation\n")

    report.append("## Process Workload\n")
    report.append("```")
    report.extend(format_workload_table(processes))
    report.append("```\n")

    report.append("## CPU Simulation Trace\n")
    report.append("```")
    report.extend(format_trace_table(segments))
    report.append("```\n")

    report.append("## Generation Statistics\n")
    report.append("```")
    report.extend(format_generation_stats(gstats))
    report.append("```\n")

    report.append("## Simulation Statistics\n")
    report.append("```")
    report.extend(format_simulation_stats(sstats))
    report.append("```\n")

    return "\n".join(report)

def main():
    processes = generate_processes()
    run_fifo_simulation(processes)
    segments = build_cpu_trace(processes)

    gstats = compute_generation_stats(processes, LAMBDA_PER_MS, T_MS)
    sstats = compute_simulation_stats(processes)

    report_text = build_report(processes, segments, gstats, sstats)

    with open(OUTPUT_MD_PATH, "w") as f:
        f.write(report_text)

    # Console preview (full 1000-row table lives in the markdown file)
    print("**Process Workload (first 10 shown, full list in "
          f"{OUTPUT_MD_PATH})**\n")
    print("process_id | arrival_time | requested_service_time")
    for p in processes[:10]:
        print(f"{p.pid:<10} | {p.arrival_time:<12} | {p.service_time}")
    print("...\n")

    print("**Generation Statistics**\n")
    for line in format_generation_stats(gstats):
        print(line)
    print()

    print("**Simulation Statistics**\n")
    for line in format_simulation_stats(sstats):
        print(line)
    print(f"\nFull report (all {NUM_PROCESSES} processes + full CPU trace) "
          f"written to {OUTPUT_MD_PATH}")

if __name__ == "__main__":
    main()
