#!/usr/bin/env python3

import argparse
import os
import time
import math
import jenkins
import tabulate
import re
from servers import servers, init_servers

def job_queue(server, show_why=False):
    queue = []
    for j in reversed(server.get_queue_info()):
        detail      = server.get_queue_item(j['id'], depth=1)
        name        = detail['task']['name']
        queued_time = j['inQueueSince'] / 1000.0
        now_time    = time.mktime(time.localtime())
        time_diff   = now_time - queued_time
        if time_diff > 86400:
            start_time = f"{math.floor(time_diff / 86400.0)} days"
            if time_diff < 2*86400:
                start_time = start_time[:-1]
        else:
            start_time = time.strftime('%l:%M%p', time.localtime(queued_time))
        if show_why:
            why = j['why']
            if len(why) > 80:
                why = why[0:79] + '....'
            queue.append([j['url'][11:-1], start_time, name, why])
        else:
            queue.append([j['url'][11:-1], start_time, name])
#        print(f"{j['url'][11:-1]} ({start_time}): {j['why']}")
    return queue

# nodes which have all the given labels
def nodes_with_labels(server, labels):
    idle = []
    offline = []
    running = []
    for n in server.get_nodes(depth=1):
        name = n['name']
        try:
            info = server.get_node_info(name, depth=2)
        except jenkins.JenkinsException:
            continue
        node_labels = [x['name'] for x in info['assignedLabels'] if x['name'] != name]
        second = None
        if 'all' in labels or all([l in node_labels for l in labels]):
            arch = [l for l in node_labels if re.match('^gfx', l)]
            if arch:
                arch = arch[0]
                node_labels.remove(arch)
                node_labels.insert(0, arch)
            name = f"{name} ({arch})"
            if info['offline']:
                if info['offlineCauseReason'] == 'Offline because computer was idle; it will be relaunched when needed.':
                    idle.append([name, 'idle (and offline)'])
                elif info['offlineCauseReason']:
                    offline.append([name, info['offlineCauseReason']])
                else:
                    offline.append([name, 'offline but no reason reported'])
            elif info['idle']:
                idle.append([name, 'idle'])
            else:
                ex = info['executors'][0]
                ce = ex['currentExecutable']
                if ce:
                    running.append([name, ce['displayName']])
                else:
                    running.append([name, '[running something unknown]'])
    return running + idle + offline

def run(labels, show_queue=True, show_why=False):
    for server in init_servers(servers):
        conn = server['connection']
        print(f"On {server['host']}:")
        print(tabulate.tabulate(nodes_with_labels(conn, labels), tablefmt='plain'))
        if show_queue:
            print('')
            print(tabulate.tabulate(job_queue(conn, show_why), tablefmt='plain'))
        print('')

parser = argparse.ArgumentParser()
parser.add_argument('--queue', action='store_true',
                    help="show the job queue")
parser.add_argument('--why', action='store_true',
                    help="also show the reason the job is queued")
parser.add_argument('--labels', default='mlir', type=str,
                    help='comma-separated list of labels, or "all" to match any label')
args = parser.parse_args()

if __name__ == '__main__':
    try:
        run(labels=args.labels.split(','), show_queue=args.queue, show_why=args.why)
    except Exception as err:
        print(f"Error: {err}")
