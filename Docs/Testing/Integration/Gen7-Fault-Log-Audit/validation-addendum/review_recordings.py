"""Read-only analysis of original recordings; exports derived review evidence."""
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import bisect
import csv
import json
import re

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'validation'
FAULT = re.compile(r'^v=1 seq=(\d+) boot=(\d+) ms=(\d+) source=(\S+) reason=(\d+):(.*?) '
                   r'severity=(\d+) exception=(\d+) bdtr=([\da-fA-F]+) ccer=([\da-fA-F]+) '
                   r'gate=([\da-fA-F]+) kind=(\d+) fields=(\S+) values=(\S+)$')
FLOAT_KINDS = {2,3,4,5,6,7,8,13,14}
STATE_KEYS = {'control_state','main_fault_names','main_fault_flags_hex',
              'coprocessor_fault_names','coprocessor_safety_state','fw_graph_hash','boot_state'}
NUMERIC_EVENTS = {'control_outputs_enabled','main_outputs_enabled','gate_power_enabled',
                  'gate_reset_asserted','pwm_moe','gate_ready','gate_fault',
                  'cg_sample_valid','enc_rejects','fault_log_count',
                  'cg_dclink_valid',
                  'coprocessor_report_generation','coprocessor_trip_reason','coprocessor_trip_inputs'}
transfer = json.loads((ROOT/'transfer-checksums.json').read_text())
expected = {e['file']:e for e in transfer['files']}
results = []
for source in sorted(ROOT.glob('*.jsonl')):
    v = json.loads((OUT/(source.stem+'.validation.json')).read_text())
    history, raw_failures, events, current = {}, [], [], {}
    boot_first = boot_last = None
    initial_definitions = 0
    first_frame = last_frame = None
    jumps = []
    window = defaultdict(list)
    before = {}
    with source.open() as stream:
        for raw in stream:
            e=json.loads(raw)
            t,kind=e['t'],e['type']
            if kind=='signal_definition' and t==0: initial_definitions+=1
            if 'frame_sequence' in e:
                frame=(e['frame_sequence'],e['device_time_us'])
                if frame!=last_frame:
                    if first_frame is None:first_frame={'t':t,'sequence':frame[0],'device_time_us':frame[1]}
                    if last_frame is not None:
                        delta=(frame[0]-last_frame[0])&0xFFFFFFFF
                        if 1<delta<0x80000000:
                            jumps.append({'t':t,'unrepresented_frames':delta-1,
                                          'device_gap_s':((frame[1]-last_frame[1])&0xFFFFFFFF)/1e6})
                    last_frame=frame
            if kind in ('console','command','recording_gap','g4_legacy_status'):
                events.append(e)
            if kind=='state':
                key,value=e['signal'],e['value']
                if key in STATE_KEYS and current.get(key)!=value:
                    events.append(e);current[key]=value
                if key in ('fault_log_latest','fault_log_record'):
                    m=FAULT.fullmatch(value)
                    if not m:
                        if value!='none' and len(raw_failures)<10:raw_failures.append({'t':t,'raw':value})
                    else:
                        g=m.groups()
                        identity=g[1]+':'+g[0]
                        if identity not in history:
                            names=g[12].split(',');values=g[13].split(',');fk=int(g[11])
                            decoded=[float(a) if fk in FLOAT_KINDS else int(a,16) for a in values]
                            history[identity]={'sequence':int(g[0]),'boot':int(g[1]),'uptime_ms':int(g[2]),
                                'source':g[3],'reason':int(g[4]),'reason_text':g[5],'severity':int(g[6]),
                                'exception':int(g[7]),'pwm_bdtr':int(g[8],16),'pwm_ccer':int(g[9],16),
                                'gate_inputs':int(g[10],16),'kind':fk,'evidence':dict(zip(names,decoded)),
                                'raw':value,'first_t':t,'last_t':t,'publications':0}
                        h=history[identity];h['last_t']=t;h['publications']+=1
                        if h['raw']!=value:raise RuntimeError('Fault identity changed: '+identity)
            if kind=='telemetry':
                for key,value in e['values'].items():
                    if key=='boot_uptime_ms':
                        point={'t':t,'uptime_ms':value}
                        if boot_first is None:boot_first=point
                        boot_last=point
                    if key in NUMERIC_EVENTS and current.get(key)!=value:
                        events.append({'type':'numeric_change','t':t,'signal':key,'value':value,
                                       'device_time_us':e.get('device_time_us'),'frame_sequence':e.get('frame_sequence')})
                        current[key]=value
                    if '10-44-50' in source.name:
                        if t<104:before[key]=[t,value]
                        elif t<=112:window[key].append([t,value,e.get('device_time_us'),e.get('frame_sequence')])
    start=datetime.fromisoformat(v['session_start']['started_at_utc'].replace('Z','+00:00'))
    end=start+timedelta(seconds=v['duration_s'])
    result={'file':source.name,'started_at_utc':start.isoformat(),'ended_at_utc':end.isoformat(),
            'started_local':start.astimezone(ZoneInfo('America/Los_Angeles')).isoformat(),
            'duration_s':v['duration_s'],'sha256_matches_transfer':v['sha256']==expected[source.name]['sha256'],
            'initial_cached_definition_records':initial_definitions,'first_frame':first_frame,
            'last_frame':last_frame,'first_boot_uptime':boot_first,'last_boot_uptime':boot_last,
            'frame_jumps':jumps,'fault_history':sorted(history.values(),key=lambda h:h['sequence']),
            'unparsed_fault_text':raw_failures,'event_changes':events}
    (OUT/(source.stem+'.review.json')).write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    if window:
        (OUT/'fault-window-104-112s.json').write_text(json.dumps({'source':source.name,'previous_values':before,'series':window},allow_nan=False))
        with (OUT/'fault-window-104-112s.csv').open('w') as output:
            w=csv.writer(output);w.writerow(['time_s','device_time_us','frame_sequence','signal','value'])
            combined=sorted((t,us,seq,k,value) for k,series in window.items() for t,value,us,seq in series)
            w.writerows(combined)
    results.append(result)
    print(json.dumps({'file':source.name,'unique_fault_history_records':len(history),
                      'unparsed_fault_text':len(raw_failures),'initial_definitions':initial_definitions,
                      'sequence_gaps_after_first_second':sum(j['unrepresented_frames'] for j in jumps if j['t']>1),
                      'new_fault_sequences':[h['sequence'] for h in history.values() if h['uptime_ms']>=boot_first['uptime_ms'] and h['boot']==12]}),flush=True)
boundaries=[]
for previous,nxt in zip(results,results[1:]):
    gap=(datetime.fromisoformat(nxt['started_at_utc'])-datetime.fromisoformat(previous['ended_at_utc'])).total_seconds()
    boundaries.append({'previous':previous['file'],'next':nxt['file'],'wall_time_gap_s':gap,
                       'previous_last_frame':previous['last_frame'],'next_first_frame':nxt['first_frame']})
(OUT/'recording-boundaries.json').write_text(json.dumps(boundaries,indent=2)+'\n')
print('Boundaries:',json.dumps(boundaries),flush=True)
