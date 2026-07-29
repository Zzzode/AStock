# Full-Chain Taxonomy

**Coverage pack:** `workspace/templates/industry-coverage-packs/aidc.md`.

```mermaid
flowchart LR
  A["Ascend 950DT and HiZQ memory"] --> B["Atlas 950 compute and communication cabinets"]
  P["Power, UPS, busway and backup"] --> B
  T["CDU, cold plate, pipework, coolant and facility cooling"] --> B
  N["UnifiedBus, optical/OCS, NIC, switch and copper interconnect"] --> B
  C["PCB, CCL, substrate, connector and cable"] --> B
  S["Storage, SSD and data pipeline"] --> B
  B --> D["Huawei Cloud and operator intelligent-compute centers"]
  D --> M["Model training, inference and agent applications"]
  M --> U["Enterprise and public-sector workloads"]
```

The architecture creates scale-up demand across eight AIDC blocks, but Huawei retains the system, accelerator, memory-subsystem and interconnect control points. Public evidence does not disclose enough subsystem suppliers to convert the product launch directly into an A-share revenue list.
