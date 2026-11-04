# Synopsis for the team

Version 3, 3 Nov 2026. The full plan is in [overview.md](overview.md); the build details are in [build-spec.md](build-spec.md).

**Dancing with the SARS: The Hidden Steps**

On 27 Sep 2026 the Gandak River in Bihar hit a record level. Two nights later its embankments broke in several places, and about 2 lakh people were affected. The flood maps responders use come from Sentinel-1, a C-band radar, and C-band mostly bounces off leaves. Water sitting under trees or tall crops shows up as dry land.

NISAR, the new NASA-ISRO satellite, uses L-band. Its longer wave gets through the canopy and bounces off the water underneath. NISAR passed over the Gandak on 28 Sep, and Sentinel-1 passed eleven hours later. Two radars seeing the same record flood on the same day is rare, and it's the core of our project.

We're building a web app that shows anyone what that difference looks like.

The heart of it is one slider. You start on Sentinel-1's flood map. Drag the slider and NISAR's map comes in, and water appears under the trees where Sentinel-1 showed dry ground. The rest of the app is there to make that moment land and to prove it's real:

- **The dance.** NISAR images the same spot every 12 days, so we animate the river from July to October as it rises and spreads.
- **Listen to the flood.** Tap any field and hear its radar signal change over time. Open water goes low and quiet; flooded forest gets louder.
- **Why it works.** Two short visuals: open water acts like a mirror, while water under trees bounces the signal off the trunks and straight back. This answers the challenge's question about which polarizations show the change.
- **How we know.** We check both radars against optical satellite maps from 8 hours before and 16 hours after. We also show the pixels we don't trust, like the gaps between NISAR's swaths, instead of hiding them.

The video runs on two numbers: how many km² of flooding NISAR found where Sentinel-1 said dry, and whether NISAR keeps up with Sentinel-1 on open water.

What changed from the last plan: the trust model and the ranked "check first" list are now stretch goals. The science stays, but the app comes first. Local judges are mostly not radar people, and the challenge asks for something a broad audience can use.

Roles: Radar processes the NISAR data, Truth produces the two numbers, App builds the site, and Story owns the video and project page. Story also tries to get a quote from someone in Bihar.

One thing we don't know yet: how strong the hidden water will be. The prelim tests only check that the flood shows up at all; the km² number gets computed during the event. If it comes out small, the app still works, and the story becomes where L-band helps and where it doesn't.
