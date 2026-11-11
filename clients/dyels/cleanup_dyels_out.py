#!/usr/bin/env python3
import os

keep = {"Analytics_MinimalProxy.csv", "Analytics_IsDiamondProxy.csv", "Analytics_TransientReentrancyGuardUpgradable.csv",
        "Analytics_ReentrancyGuardUpgradable.csv", "Analytics_Initializable.csv", "Analytics_IsOZProxy.csv", 
        "Analytics_Is1822Proxy.csv", "Analytics_Is1967Beacon.csv", "Analytics_Is1967Proxy.csv", "Analytics_ReentrancyGuard.csv"}

for name in os.listdir("."):
    if name.endswith(".csv") and name not in keep:
        os.remove(name)