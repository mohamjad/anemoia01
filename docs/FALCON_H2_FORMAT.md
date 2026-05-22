# FALCON H2 Format

The pass-2 parser uses the NWB/HDF5 paths exercised by the public FALCON H2
demo:

- `acquisition/binned_spikes/data`
- `acquisition/binned_spikes/timestamps`
- `acquisition/eval_mask/data`
- `intervals/trials/cue`
- `intervals/trials/start_time`
- `intervals/trials/stop_time`
- `intervals/trials/id`
- `intervals/trials/block_num` when available

Cue strings use `>` as a space marker and `~` as a period marker. Weak target
construction treats these as declared prompt proxies, not direct observations of
intent.

