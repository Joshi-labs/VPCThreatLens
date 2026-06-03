import json
import random
from pathlib import Path

INPUT_DIR = Path("data/uncompressed")

# -----------------------------
# CONFIG
# -----------------------------

MIN_TIME_OFFSET = 0
MAX_TIME_OFFSET = 60

# -----------------------------
# RANDOM IP GENERATOR
# -----------------------------

def random_ip():
    return ".".join(
        str(random.randint(1, 255))
        for _ in range(4)
    )

# -----------------------------
# REALISTIC ATTACK SIZE
# -----------------------------

def random_attack_size():

    # Gaussian distribution
    count = int(abs(random.gauss(12, 6)))

    # Clamp values
    count = max(3, min(count, 30))

    return count

# -----------------------------
# PROCESS FILES
# -----------------------------

for file in INPUT_DIR.glob("*.jsonl"):

    print(f"\nInjecting into {file.name}")

    logs = []

    with open(file, "r") as f:

        for line in f:

            try:
                logs.append(json.loads(line))
            except:
                pass

    if len(logs) == 0:
        continue

    # -----------------------------
    # RANDOM ATTACK SIZE
    # -----------------------------

    injection_count = random_attack_size()

    print(f"Attack Size: {injection_count}")

    # -----------------------------
    # PICK RANDOM BASE LOG
    # -----------------------------

    base_log = random.choice(logs)

    try:

        base_start = int(base_log["start"])
        base_end = int(base_log["end"])

    except:
        continue

    injected_logs = []

    # -----------------------------
    # GENERATE SSH ATTACK FLOWS
    # -----------------------------

    for _ in range(injection_count):

        start_offset = random.randint(
            MIN_TIME_OFFSET,
            MAX_TIME_OFFSET
        )

        end_offset = random.randint(
            MIN_TIME_OFFSET,
            MAX_TIME_OFFSET
        )

        fake_log = {

            "version": "2",

            "account_id": base_log["account_id"],

            "interface_id": base_log["interface_id"],

            # Random attacking IP
            "srcaddr": random_ip(),

            # Same target
            "dstaddr": base_log["dstaddr"],

            # Random source port
            "srcport": str(
                random.randint(30000, 65000)
            ),

            # SSH target
            "dstport": "22",

            # TCP
            "protocol": "6",

            "packets": str(
                random.randint(1, 5)
            ),

            "bytes": str(
                random.randint(40, 300)
            ),

            # Similar time window
            "start": str(
                base_start + start_offset
            ),

            "end": str(
                base_end + end_offset
            ),

            "action": random.choice([
                "ACCEPT",
                "REJECT"
            ]),

            "log_status": "OK",

            # Metadata
            "injected": True,

            "attack_type": "coordinated_ssh_scan"
        }

        injected_logs.append(fake_log)

    # -----------------------------
    # APPEND TO FILE
    # -----------------------------

    with open(file, "a") as f:

        for log in injected_logs:

            json.dump(log, f)

            f.write("\n")

    print(
        f"Injected {len(injected_logs)} synthetic SSH logs."
    )

print("\nSSH injection completed.")