---
title: Tableau Server Installation Instructions Template
---

1. Download the Connector file (.taco).
2. Move the .taco file here: 
   -  Tableau Prep Conductor: `[Tableau_Server_Installation_Directory]/data/tabsvc/flowprocessor/Connectors`
   -  Tableau Flow Web Authoring: `[Tableau_Server_Installation_Directory]/data/tabsvc/flowqueryservice/Connectors`
   > **Important**: For a multi-node Tableau server, place the Connector file in the correct folder for each server node.
3. Start Tableau and under **Connect**, select the `[Connector Name]` connector. (**Note**: You will be prompted if the driver is not yet installed.)
4. Go to the [Driver Download](https://www.driver-download-link-here.com) page.
5. Download the `[Connector Name]` Driver .jar file.
6. Install following the instructions in the readme provided with the client installation. Ensure the 64-bit client version is installed.
7. Relaunch Tableau and connect using the `[Connector Name]` connector.