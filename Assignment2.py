"""Mirror Server Simulation (PA02)

N mirrored servers, each with mean time between failures T_i (integer, 10..20).
Failure gaps are exponentially distributed with mean T_i, rounded to whole hours.
A failed server needs R = 2 hours to restore. The simulation ends the moment the
last remaining UP server fails (all servers DOWN together).
"""
import random

R = 2            # restore time (hours)
NUM_RUNS = 5     # runs printed in detail
T_MIN, T_MAX = 10, 20


def gap(mean):
    """Integer time until next failure, exponential with the given mean (>= 1)."""
    return max(1, round(random.expovariate(1.0 / mean)))


def simulate(means, r=R):
    """Run one simulation. Returns (end_time, log, up_time, down_time, failures)."""
    n = len(means)
    up = [True] * n
    next_fail = [gap(m) for m in means]
    recover = [None] * n
    up_time = [0] * n
    down_time = [0] * n
    failures = [0] * n
    log = [(0, up[:])]
    t = 0

    while True:
        # next event: a failure (if UP) or a restoration (if DOWN)
        nt = min(next_fail[i] if up[i] else recover[i] for i in range(n))
        for i in range(n):
            if up[i]:
                up_time[i] += nt - t
            else:
                down_time[i] += nt - t
        t = nt

        # 1) restorations first (a server that recovers at t is UP at t)
        for i in range(n):
            if not up[i] and recover[i] == t:
                up[i] = True
                next_fail[i] = t + gap(means[i])

        # 2) failures
        ended = False
        for i in range(n):
            if up[i] and next_fail[i] == t:
                failures[i] += 1
                if any(up[j] for j in range(n) if j != i):
                    up[i] = False
                    recover[i] = t + r
                else:               # last UP server fails -> system dead
                    up[i] = False
                    ended = True
                    break

        if not log or log[-1][1] != up or log[-1][0] != t:
            log.append((t, up[:]))
        if ended:
            return t, log, up_time, down_time, failures


def print_log(log, n):
    print("      | " + " | ".join(f"S{i:02d} " for i in range(n)) + " |")
    print("-" * (8 + 7 * n))
    for t, states in log:
        cells = " | ".join(f"{'UP' if s else 'DOWN':>4}" for s in states)
        print(f"{t:5d}| {cells} |")


def run_experiment(n, runs=NUM_RUNS, verbose=True):
    means = [random.randint(T_MIN, T_MAX) for _ in range(n)]
    if verbose:
        print(f"\n===== N = {n} servers =====")
        for i, m in enumerate(means):
            print(f"S{i:02d} | {m} |")

    tot_up = [0] * n
    tot_down = [0] * n
    tot_fail = [0] * n
    end_times = []

    for k in range(1, runs + 1):
        end, log, up_t, down_t, fails = simulate(means)
        end_times.append(end)
        for i in range(n):
            tot_up[i] += up_t[i]
            tot_down[i] += down_t[i]
            tot_fail[i] += fails[i]
        if verbose:
            print(f"\n--- Run {k} (system failed at hour {end}) ---")
            print_log(log, n)

    if verbose:
        print("\nServer | Avg Uptime | Avg Downtime | Availability | MTBF")
        print("-" * 58)
        for i in range(n):
            au, ad = tot_up[i] / runs, tot_down[i] / runs
            avail = 100.0 * au / (au + ad) if au + ad else 0.0
            mtbf = tot_up[i] / tot_fail[i] if tot_fail[i] else float("inf")
            print(f"S{i:02d}    | {au:10.2f} | {ad:12.2f} | {avail:11.2f}% | {mtbf:.2f}")
        print(f"\nAverage time till total failure: {sum(end_times)/runs:.2f} hours")
    return sum(end_times) / runs


def plot_vs_servers(max_n=5, runs=2000):
    """Average time till total failure vs. number of servers."""
    ns = list(range(2, max_n + 1))
    avgs = [run_experiment(n, runs=runs, verbose=False) for n in ns]
    print("\nN | Avg time till total system failure")
    for n, a in zip(ns, avgs):
        print(f"{n} | {a:.2f}")
    try:
        import matplotlib.pyplot as plt
        plt.plot(ns, avgs, marker="o")
        plt.xticks(ns)
        plt.xlabel("Number of servers (N)")
        plt.ylabel("Avg time till total failure (hours)")
        plt.title("Mirror server system lifetime")
        plt.grid(True)
        plt.savefig("avg_time_vs_servers.png", dpi=150)
        plt.show()
    except ImportError:
        print("(install matplotlib to see the plot)")


if __name__ == "__main__":
    N = int(input("Enter number of servers N (2-5): ") or 2)
    assert 2 <= N <= 5, "N must be between 2 and 5"
    run_experiment(N)
    plot_vs_servers()
