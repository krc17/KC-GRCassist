# KC-GRCassist
Build out a Python code that scrapes today's news articles based on keyword, saves to excel. Eventually creating a kiosk info board.

First code would run the script and append the current days data onto the end of the grcdata file - keeping a running logs of news stories. I attempted to have the code sort by severity using AI to dial in what the qualifiers would be for the different tiers of 'severity' and display the top 10 in a running Powerpoint presentation.

Massive failure!

Since grcdata is a log of months and months of stories, the top ten are unlikely to change in a day or a week or a month. Nothing dynamic happening there.
Presenting this data in Powerpoint is its own conversion hurdle. Tried this by having the script launch the grcdata urls in a browser's full screen mode with an extension to cycle tabs ever x seconds. Works.

Currently looking at focusing on daily news update kiosk setup. Eliminate the 'severity' portion for now and have the grcassist python code clear grcdata and write only the current day's news. Then, separately, open to browser tabs to cycle.

Once this is tested I might look at combining all the elements. Until then, make a script to run the separate functions and a Windows task to run the script in the morning.
