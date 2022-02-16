---
title: Tableau Server (Flow web authoring) Installation Instructions Template
---

1. Download the Connector file (.taco).
2. Move the .taco file to: `[Tableau_Server_Installation_Directory]/data/tabsvc/flowqueryservice/Connectors`
3. Start Tableau and under **Connect**, select the `[Connector Name]` connector. (**Note**: You will be prompted if the driver is not yet installed.)
4. Go to the [Driver Download](https://www.driverdownloadlinkhere.com) page.
5. Download the `[Connector Name]` Driver .jar file.
6. Install following the instructions in the readme provided with the client installation. Ensure the 64-bit client version is installed.
7. Relaunch Tableau and connect using the `[Connector Name]` connector.