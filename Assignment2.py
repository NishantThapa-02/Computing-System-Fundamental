import random

R = 2  # restore time in hours


def next_gap(mean):
    # random time until the next failure (whole hours, at least 1)
    return max(1, round(random.expovariate(1 / mean)))


def simulate(means, show=False):
    n = len(means)
    up = [True] * n
    fail_at = [next_gap(m) for m in means]   # when each UP server will fail
    back_at = [0] * n                        # when each DOWN server comes back
    uptime = [0] * n
    downtime = [0] * n
    failures = [0] * n

    if show:
        print("   t |", " | ".join(f"S{i:02d} " for i in range(n)))
        print(f"{0:4d} |", " | ".join(f"{'UP':>4}" for _ in range(n)))

    t = 0
    while True:
        t += 1
        # count this hour for each server (state before any change at time t)
        for i in range(n):
            if up[i]:
                uptime[i] += 1
            else:
                downtime[i] += 1

        # servers finishing their restore come back up
        for i in range(n):
            if not up[i] and back_at[i] == t:
                up[i] = True
                fail_at[i] = t + next_gap(means[i])

        # servers failing now
        dead = False
        for i in range(n):
            if up[i] and fail_at[i] == t:
                failures[i] += 1
                if any(up[j] for j in range(n) if j != i):
                    up[i] = False
                    back_at[i] = t + R
                else:
                    up[i] = False   # nobody else is up -> system is dead
                    dead = True
                    break

        if show and (dead or t in back_at or any(fail_at[i] == t for i in range(n))):
            print(f"{t:4d} |", " | ".join(f"{'UP' if s else 'DOWN':>4}" for s in up))
        if dead:
            return t, uptime, downtime, failures


def main():
    N = int(input("Number of servers (2-5): "))
    means = [random.randint(10, 20) for _ in range(N)]
    print()
    for i, m in enumerate(means):
        print(f"S{i:02d} | {m} |")

    runs = 5
    total_up = [0] * N
    total_down = [0] * N
    total_fail = [0] * N
    for r in range(1, runs + 1):
        print(f"\nRun {r}")
        end, up, down, fails = simulate(means, show=True)
        for i in range(N):
            total_up[i] += up[i]
            total_down[i] += down[i]
            total_fail[i] += fails[i]

    print("\nServer | Avg Uptime | Avg Downtime | Availability | MTBF")
    for i in range(N):
        avg_up = total_up[i] / runs
        avg_down = total_down[i] / runs
        avail = 100 * avg_up / (avg_up + avg_down)
        mtbf = total_up[i] / total_fail[i]
        print(f"S{i:02d}    | {avg_up:10.1f} | {avg_down:12.1f} | {avail:10.2f}% | {mtbf:.2f}")

    # average time till total failure vs number of servers
    print("\nN | Avg time till total failure")
    xs, ys = [], []
    for n in range(2, 6):
        ms = [random.randint(10, 20) for _ in range(n)]
        avg = sum(simulate(ms)[0] for _ in range(1000)) / 1000
        xs.append(n)
        ys.append(avg)
        print(f"{n} | {avg:.1f}")

    try:
        import matplotlib.pyplot as plt
        plt.plot(xs, ys, marker="o")
        plt.yscale("log")
        plt.xlabel("Number of servers")
        plt.ylabel("Avg time till total failure (hours)")
        plt.show()
    except ImportError:
        pass


main()
