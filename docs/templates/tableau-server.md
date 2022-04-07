---
title: Tableau Server Installation Instructions Template
---

1. Download the Connector file (.taco).
2. Move the .taco file here:
    - Windows: `C:\Program Files\Tableau\Connectors`
    - Linux: `/opt/tableau/connectors`
1. For a multi-node Tableau server, copy the Connector file (.taco) in the correct folder for each server node.
3. Start Tableau and under **Connect**, select the `[Connector Name]` connector. (**Note**: You will be prompted if the driver is not yet installed.)
4. Go to the [Driver Download](https://www.driver-download-link-here.com) page.
5. Download the `[Connector Name]` Driver .jar file.
6. Install following the instructions in the readme provided with the client installation. Ensure the 64-bit client version is installed.
7. Restart Tableau Server and connect using the `[Connector Name]` connector.