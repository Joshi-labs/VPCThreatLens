import json
from pathlib import Path
from collections import defaultdict

INPUT_DIR = Path("data/uncompressed")
OUTPUT_FILE = Path("data/datasets/window_events.jsonl")

OUTPUT_FILE.parent.mkdir(exist_ok=True)

# -----------------------------
# CONFIG
# -----------------------------

WINDOW_SIZE = 60
SSH_UNIQUE_IP_THRESHOLD = 15
PORTSCAN_THRESHOLD = 10
HIGH_PACKET_THRESHOLD = 100

# -----------------------------
# STORAGE
# -----------------------------

windows = defaultdict(list)

# SSH tracking PER WINDOW
ssh_tracker = defaultdict(set)

# -----------------------------
# LOAD LOGS
# -----------------------------

for file in INPUT_DIR.glob("*.jsonl"):

    print(f"Processing {file.name}")

    with open(file, "r") as f:

        for line in f:

            try:
                log = json.loads(line)

                if log["dstport"] == "dstport":
                    continue

                src_ip = log["srcaddr"]
                dst_port = int(log["dstport"])
                timestamp = int(log["start"])

                window_id = timestamp // WINDOW_SIZE

                # SSH tracking per window
                if dst_port == 22:
                    ssh_tracker[window_id].add(src_ip)

                window_key = (
                    src_ip,
                    window_id
                )

                windows[window_key].append(log)

            except Exception as e:
                print(e)

# -----------------------------
# ANALYZE WINDOWS
# -----------------------------

with open(OUTPUT_FILE, "w") as out:

    for (src_ip, window_id), logs in windows.items():

        ports = set()
        total_packets = 0
        reject_count = 0

        start_times = []
        end_times = []

        events = []

        for log in logs:

            dst_port = int(log["dstport"])
            packets = int(log["packets"])
            action = log["action"]

            ports.add(dst_port)
            total_packets += packets

            if action == "REJECT":
                reject_count += 1

            start_times.append(
                int(log["start"])
            )

            end_times.append(
                int(log["end"])
            )

        event_time_start = min(start_times)
        event_time_end = max(end_times)

        # -----------------------------
        # Coordinated SSH Activity
        # -----------------------------

        unique_ssh_ips = len(
            ssh_tracker[window_id]
        )

        if unique_ssh_ips >= SSH_UNIQUE_IP_THRESHOLD:

            events.append({

                "event_type":
                "coordinated_ssh_activity",

                "severity":
                "high",

                "src_ip":
                src_ip,

                "window":
                window_id,

                "event_time_start":
                event_time_start,

                "event_time_end":
                event_time_end,

                "unique_ssh_ips":
                unique_ssh_ips,

                "description":
                "Multiple unique IPs targeted SSH within same time window"

            })

        # -----------------------------
        # Port Scan Detection
        # -----------------------------

        if len(ports) >= PORTSCAN_THRESHOLD:

            events.append({

                "event_type":
                "port_scan",

                "severity":
                "high",

                "src_ip":
                src_ip,

                "window":
                window_id,

                "event_time_start":
                event_time_start,

                "event_time_end":
                event_time_end,

                "unique_ports":
                list(ports),

                "description":
                "Multiple destination ports targeted within time window"

            })

        # -----------------------------
        # Traffic Spike Detection
        # -----------------------------

        if total_packets >= HIGH_PACKET_THRESHOLD:

            events.append({

                "event_type":
                "traffic_spike",

                "severity":
                "medium",

                "src_ip":
                src_ip,

                "window":
                window_id,

                "event_time_start":
                event_time_start,

                "event_time_end":
                event_time_end,

                "packets":
                total_packets,

                "description":
                "High traffic volume detected"

            })

        # -----------------------------
        # Rejected Traffic Detection
        # -----------------------------

        if reject_count > 0:

            events.append({

                "event_type":
                "rejected_activity",

                "severity":
                "medium",

                "src_ip":
                src_ip,

                "window":
                window_id,

                "event_time_start":
                event_time_start,

                "event_time_end":
                event_time_end,

                "reject_count":
                reject_count,

                "description":
                "Rejected traffic detected"

            })

        # -----------------------------
        # Normal Activity
        # -----------------------------

        if len(events) == 0:

            events.append({

                "event_type":
                "normal_activity",

                "severity":
                "low",

                "src_ip":
                src_ip,

                "window":
                window_id,

                "event_time_start":
                event_time_start,

                "event_time_end":
                event_time_end,

                "description":
                "Normal network activity observed"

            })

        # -----------------------------
        # SAVE EVENTS
        # -----------------------------

        for event in events:

            json.dump(event, out)

            out.write("\n")

print("Window analysis completed.")