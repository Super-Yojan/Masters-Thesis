# Control-loop stability analysis (thesis Chapter 7)

Models Terra's control loops as written in Rust (Terra main, 2026-10-28), fits the motor
plant to logged step responses, and computes margins, describing-function limit cycles,
hold/windup behaviour and L3 heading response.

| File | What it is |
| --- | --- |
| `terra_loop.py` | Ports of the speed/yaw PI (`terra-control`), turning limiter, pursuit law; 100 Hz loop simulator; frequency-response helpers |
| `analysis.py` | Plant fit, margin cases, delay budget, holds, terra-mini deadband, yaw and L3. Writes `thesis/figures/ctl_*.pdf` and `results.json` |
| `results.json` | Every number quoted in the chapter |
| `data/step_boot*_*.csv` | Two 0.3 m/s steps (phone speed, mean wheel effort), phone journal of 2026-10-26, about 10 Hz |
| `data/gate_hold_boot12.csv` | A run where the mount check held the motors while the controller integrated |

Run: `pip install numpy matplotlib && python3 analysis.py` (about 30 s).

Caveats: the plant is fitted from two steps at one speed, logged at 8-10 Hz, so the lag and
dead time are only resolved as a sum (about 0.2 s). The yaw plant gain is not measured.
terra-mini's plant is assumed, not fitted.
