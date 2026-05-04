#!/usr/bin/env python3
"""Batch doc generator - picks next pending small plugin from index."""
import json
import sys
import os
import time
from datetime import datetime

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(_BASE, 'plugins-index.json')
DOCS_BASE = os.path.join(_BASE, 'docs')
TIMING_LOG = os.path.join(_BASE, 'scripts', 'timing.log')

def load_index():
    with open(INDEX) as f:
        return json.load(f)

def save_index(data):
    with open(INDEX, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_next_batch(size='small', count=2):
    data = load_index()
    pending = [p for p in data if p['size'] == size and p['status'] == 'pending']
    return pending[:count]

def mark_done(name, duration_sec=None):
    data = load_index()
    for p in data:
        if p['name'] == name:
            p['status'] = 'done'
            break
    save_index(data)
    
    # Log timing
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    src_files = '?'
    for p in data:
        if p['name'] == name:
            src_files = p.get('src_files', '?')
            break
    
    if duration_sec is not None:
        mins = duration_sec / 60
        log_line = f"[{ts}] {name} ({src_files}f) completed in {mins:.1f}min"
    else:
        log_line = f"[{ts}] {name} ({src_files}f) completed"
    
    with open(TIMING_LOG, 'a') as f:
        f.write(log_line + '\n')

def get_progress():
    data = load_index()
    from collections import Counter
    size_status = {}
    for p in data:
        key = p['size']
        if key not in size_status:
            size_status[key] = {'done': 0, 'pending': 0}
        size_status[key][p['status']] += 1
    return size_status

def show_timing():
    if not os.path.exists(TIMING_LOG):
        print("No timing data yet.")
        return
    
    with open(TIMING_LOG) as f:
        lines = f.readlines()
    
    if not lines:
        print("No timing data yet.")
        return
    
    # Parse and show stats
    durations = []
    for line in lines:
        line = line.strip()
        if 'completed in' in line:
            try:
                mins = float(line.split('completed in ')[1].replace('min', ''))
                durations.append(mins)
            except:
                pass
    
    if durations:
        avg = sum(durations) / len(durations)
        total = sum(durations)
        print(f"已记录 {len(durations)} 个 plugin 的耗时:")
        print(f"  平均: {avg:.1f} min/plugin")
        print(f"  总计: {total:.0f} min")
        print(f"  最快: {min(durations):.1f} min")
        print(f"  最慢: {max(durations):.1f} min")
    
    print(f"\n最近 10 条:")
    for line in lines[-10:]:
        print(f"  {line.strip()}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 batch_doc.py next [size] [count]")
        print("       python3 batch_doc.py done <plugin_name> [duration_sec]")
        print("       python3 batch_doc.py progress")
        print("       python3 batch_doc.py timing")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'next':
        size = sys.argv[2] if len(sys.argv) > 2 else 'small'
        count = int(sys.argv[3]) if len(sys.argv) > 3 else 2
        batch = get_next_batch(size, count)
        print(json.dumps(batch, indent=2, ensure_ascii=False))
    
    elif cmd == 'done':
        name = sys.argv[2]
        duration = float(sys.argv[3]) if len(sys.argv) > 3 else None
        mark_done(name, duration)
        if duration:
            print(f"Marked {name} as done ({duration/60:.1f}min)")
        else:
            print(f"Marked {name} as done")
    
    elif cmd == 'progress':
        prog = get_progress()
        total_done = sum(v['done'] for v in prog.values())
        total_pending = sum(v['pending'] for v in prog.values())
        print(f"总计: {total_done} done / {total_pending} pending")
        for s in ['small', 'medium', 'large', 'xlarge']:
            if s in prog:
                print(f"  {s:8s}: {prog[s]['done']:3d} done / {prog[s]['pending']:3d} pending")
    
    elif cmd == 'timing':
        show_timing()
