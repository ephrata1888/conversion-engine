\# Kill Switch — Tenacious Outbound Gate



\## Flag



`TENACIOUS\_OUTBOUND\_ENABLED` in `.env`



\*\*Default: unset.\*\* When unset, all outbound routes to the staff sink.



\## Behavior



| Flag value | Email | SMS | Cal.com booking |

|------------|-------|-----|-----------------|

| unset | Routed to sink (ephratawolde990@gmail.com) | Blocked | Blocked |

| `false` | Routed to sink | Blocked | Blocked |

| `true` | Sent to real prospect | Sent to real prospect | Real booking |



\## Staff sink



`ephratawolde990@gmail.com` — all outbound during challenge week routes here.



\## Code location



`agent/outbound\_gate.py` — every outbound call passes through `gate\_outbound()`.



\## How to enable for pilot (post-challenge only)



1\. Get written approval from program staff and Tenacious executive

2\. Set `TENACIOUS\_OUTBOUND\_ENABLED=true` in `.env`

3\. Run `bash infra/smoke\_test.sh` to confirm gate is in place

4\. Monitor first 10 sends manually before batch run

