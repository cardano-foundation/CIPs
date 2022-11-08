---
CIP: 60
Title: Music Token Metadata
Authors: Andrew Westberg <awestberg@projectnewm.io>, Ryan Jones <rjones@projectnewm.io>, Justin Morgan <jusemorgan@gmail.com>, Ian Singer <tcl@fre5hmusic.com>, Anthony Eizmendiz <aeizmendiz@icloud.com>, Session Cruz <session@demu.pro>, Jimmy Londo <SickCityCleveland@gmail.com>, Gudbrand Tokerud <Gudbrand.tokerud@gmail.com>, Kevin St.Clair <kos1777@gmail.com>
Comments-URI: no comments yet
Status: Active
Type: Process
Created: 2022-07-26
License: CC-BY-4.0
---

# Abstract

This proposal defines an extension to CIP-25 for token metadata specific to music tokens.

# Motivation

Music tokens on Cardano can be either NFTs or FTs and contain links to audio files. In order for players, indexers, and wallets to be able to properly search and categorize a user's music collection, we need to define a common schema for creating music on Cardano. If all parties creating these music tokens follow similar patterns, apps can consume this information and make proper use of it. The existing CIP-25 is a good base to build upon, but for a good music experience, we need to standardize additional fields that will be required specifically for music tokens.

# Specification

This CIP divides the additional metadata parameters into two categories of `Required` and `Optional`. When minting a music token on Cardano, you are expected to include ALL of the required fields. If you choose to include one or more of the optional fields, they must be named exactly as defined in this CIP. This will properly allow indexing apps and music players to utilize as much of your token metadata as possible without issues.

[CDDL Spec Version 1](cddl/version-1.cddl)

## Required Fields ###
| Field | Type | Example(s) | Notes |
| -------- | -------- | -------- | -------- |
| artists     | Array\<Artist\>     | "artists": [<br/>  { "name": "Stevie Nicks" },<br/>{ "name": "Tom Petty" }<br/>] | |
| album_title| String | "album_title": "Mr. Bad Guy" | |
| track_number | Integer | "track_number": 1 | |
| song_title | String \| Array\<String\> | "song_title": "Let's Turn it On" | |
| song_duration | String | "song_duration": "PT3M21S"  | ISO8601 Duration Format |
| genres | Array\<String\> | "genres": ["Rock","Classic Rock"] | Limited to 3 genres total. Players should ignore extra genres. |
| copyright | String | "copyright": "℗ 1985 Sony Records" | |
| release_type | Enum\<String\> | "release_type": "Single" | Must be one of "Single" or "Multiple". Multiple includes anything that will have multiple tracks: Album, EP, Compilation, etc...|
| music_metadata_version | Integer | "music_metadata_version" : 1 | Players should look for the presence of this field to determine if the token is a Music Token |

### Optional Fields ###
| Field | Type | Example(s) | Notes |
| -------- | -------- | -------- | -------- |
| contributing_artists | Array\<Artist\> | "contributing_artists": ["Dolly Parton"]<br/>*or*<br/>"contributing_artists": [<br/>"Brad Paisley",<br/>"Keith Urban"<br/>] | |
| series | string | "series": "That's What I call Music" | |
| collection | string | "collection": "Now Dance" | |
| set | string | "set": "86 - 20 Smash Dance Hits of the Year" | |
| mood | String | "mood": "Empowered" | |
| lyrics | URL | "lyrics": "ipfs://QmSmadTEhB9bJQ1WHq58yN1YZaJo4jv5BwVNGaePvEj4Fy"<br/>*or*<br/>"Lyrics": "https://website.com/song_lyrics.txt" |  |
| lyricists | Array\<String\> | "lyricists": ["Paul McCartney", "John Lennon"] | |
| special_thanks | Array\<String\> | "special_thanks": ["Your mom","Your grandma"] | |
| visual_artist | String | "visual_artist": "beeple" | |
| distributor | String | "distributor": "https://newm.io" | |
| release_date | String | "release_date": "2022-07-27" | ISO8601 Date Format |
| publication_date | String | "publication_date": "2022-07-27" | ISO8601 Date Format |
| catalog_number | Integer | "catalog_number": 2 | | 
| bitrate | String | "bitrate": "256 kbit/s" | |
| mix_engineer | String | "mix_engineer": "Robert Smith II" | |
| mastering_engineer | String | "mastering_engineer": "Michael Tyson" | |
| producer | String | "producer": "Simon Cowell" | |
| co_producer | String | "co_producer": "Shavaun Dempsey" | |
| featured_artist | Artist | "featured_artist": {"name": "The Temptations"} | |
| recording_engineer | String | "recording_engineer": "Sharon Liston" | |
| release_version | Integer | "release_version": 2 | |
| parental_advisory | String | "parental_advisory": "Explicit" | Explicit/Censored/Non-Explicit
| explicit | Boolean | "explicit": true | |
| isrc | String | "isrc": "US-SKG-22-12345" | |
| iswc | String | "iswc": "T-123456789-Z" | |
| ipi | Array\<String\> | "ipi": ["595014347","342287075","550983139"] | |
| ipn | Array\<String\> | "ipn": ["38474593","2734040"] | |
| isni | Array\<String\> | "isni": ["000000038578365X","0000000037234532X"] | |
| metadata_language | String | "metadata_language": "en-US" | https://tools.ietf.org/search/bcp47 |
| country_of_origin | String | "country_of_origin": "United States" | |
| language | String | "language": "en-US" | https://tools.ietf.org/search/bcp47 |
| derived_from | String | "derived_from" : "Some other work" | |
| links | Map\<String,String\> | "links" : {<br/>"website": "https://website.com",<br/>"twitter": "https://twitter.com/username",<br/>"discord_invite": "https://discord.gg/TEzXxjsN",<br/>"TikTok": "https://www.tiktok.com/@knucklebumpfarms",<br/>"discord_username": "MusicianPerson#8537",<br/>"instagram":"...",<br/>"facebook":"...",<br/>"soundcloud": "...",<br/>"bandcamp": "...",<br/>"spotify": "...",<br/>"apple_music": "...",<br/>...<br/>...<br/>} | |

## Examples ##

### Single ###
```
{
    "721":
    {
        "123da5e4ef337161779c6729d2acd765f7a33a833b2a21a063ef65a5":
        {
            "SickCity354":
            {
                "name": "SickCity354-Phil z'viel",
                "image": "ipfs://QmQ13Cv9Wouf4rcwtNsuFhEeJVK9bEYjCYo6AN986takiu",
                "music_metadata_version": 1,
                "release_type": "Single",
                "album_title": "C.H.I.L.L.",
                "song_title": "C.H.I.L.L.",
                "song_duration": "PT3M6S",
                "track_number": 1,
                "mood": "chillout",
                "artists":
                [
                    { "name": "Phil z'viel" }
                ],
                "collection": "C.H.I.L.L.",
                "genres":
                [
                    "Guitar Live Looping",
                    "Progressive Ambient"
                ],
                "copyright": "℗ 2022 Phil z'viel",
                "distributor": "https://sickcity.xyz",
                "files":
                [
                    {
                        "name": "C.H.I.L.L.",
                        "mediaType": "audio/mp3",
                        "src": "ipfs://QmfY4ugNdYYJxpbn5BnN8yt5EmiUCznexQoQi6RTEu9SuC"
                    }
                ],
                "links":
                {
                    "discord_user": "Phil z'viel#4711",
                    "twitter": "@Phil_zviel_CNFT",
                    "website": "www.philzvielcnft.com"
                }
            }
        }
    }
}
```

### Album ###

```
{
    "fb818dd32539209755211ab01cde517b044a742f1bc52e5cc57b25d9":
    {
        "JamisonDanielStudioLife83":
        {
            "name": "Jamison Daniel-Studio Life",
            "image": "ipfs://QmUBLXPgJM6oSeybv7FB15kQzbZtzPXifk9fJhLVcbCjVh",
            "mediaType": "image/webp",
            "version": 1,
            "music_metadata_version": 1,
            "release_type": "Multiple",
            "attributes":
            {
                "Collection": "Basic",
                "Number": "83/500"
            },
            "files":
            [
                {
                    "name": "hi-res",
                    "mediaType": "image/webp",
                    "src": "ipfs://QmbU2Xm7swgYBQvN8cWXWVZJ1a2fMFmtFkymUu6fRogQwj"
                },
                {
                    "name": "Finally (Master 2021)",
                    "mediaType": "audio/flac",
                    "src": "ipfs://QmduC7pkR14K3mhmvEazoyzGsMWVF4ji45HZ1XfEracKLv",
                    "artists": [{"name": "Jamison Daniel"}],
                    "album_title": "Studio Life",
                    "track_number": 1,
                    "song_title": "Finally (Master 2021)",
                    "song_duration": "PT6M36S",
                    "genres": ["electronic", "house"],
                    "copyright": "Jamison Daniel © 2021",
                    "visual_artist": "Jamison Daniel",
                    "producer": "Jamison Daniel",
                    "publisher": "Jamison Daniel Music",
                    "links": {
                      "twitter": "@JamisonDMusic",
                      "website": "jamisondaniel.com"
                    }
                },
                {
                    "name": "Funky Squirrel (Master 2021)",
                    "mediaType": "audio/flac",
                    "src": "ipfs://QmW9sHugSArzf29JPuEC2MqjtbsNkDjd9xNUxZFLDXSDUY",
                    "artists": [{"name": "Jamison Daniel"}],
                    "album_title": "Studio Life",
                    "track_number": 2,
                    "song_title": "Funky Squirrel (Master 2021)",
                    "song_duration": "PT6M47S",
                    "genres": ["electronic", "house"],
                    "copyright": "Jamison Daniel © 2021",
                    "visual_artist": "Jamison Daniel",
                    "producer": "Jamison Daniel",
                    "publisher": "Jamison Daniel Music",
                    "links": {
                      "twitter": "@JamisonDMusic",
                      "website": "jamisondaniel.com"
                    }
                },
                {
                    "name": "Weekend Ride (Master 2021)",
                    "mediaType": "audio/flac",
                    "src": "ipfs://Qmb8fm7CkzscjjoJGVp3p7qjSVMknsk27d3cwjqM26ELVB",
                    "artists": [{"name": "Jamison Daniel"}],
                    "album_title": "Studio Life",
                    "track_number": 3,
                    "song_title": "Weekend Ride (Master 2021)",
                    "song_duration": "PT6M39S",
                    "genres": ["electronic", "house"],
                    "copyright": "Jamison Daniel © 2021",
                    "visual_artist": "Jamison Daniel",
                    "producer": "Jamison Daniel",
                    "publisher": "Jamison Daniel Music",
                    "links": {
                      "twitter": "@JamisonDMusic",
                      "website": "jamisondaniel.com"
                    }
                },
                {
                    "name": "Rave Culture (Master 2021)",
                    "mediaType": "audio/flac",
                    "src": "ipfs://QmTwvwpgE9Fx6QZsjbXe5STHb3WVmaDuxFzafqCPueCmqc",
                    "artists": [{"name": "Jamison Daniel"}],
                    "album_title": "Studio Life",
                    "track_number": 4,
                    "song_title": "Rave Culture (Master 2021)",
                    "song_duration": "PT6M39S",
                    "genres": ["electronic", "house"],
                    "copyright": "Jamison Daniel © 2021",
                    "visual_artist": "Jamison Daniel",
                    "producer": "Jamison Daniel",
                    "publisher": "Jamison Daniel Music",
                    "links": {
                      "twitter": "@JamisonDMusic",
                      "website": "jamisondaniel.com"
                    }
                },
                {
                    "name": "Vibrate (Master 2021)",
                    "mediaType": "audio/flac",
                    "src": "ipfs://QmTETraR8WvExCaanc5aGT8EAUgCojyN8YSZYbGgmzVfja",
                    "artists": [{"name": "Jamison Daniel"}],
                    "album_title": "Studio Life",
                    "track_number": 5,
                    "song_title": "Vibrate (Master 2021)",
                    "song_duration": "PT6M51S",
                    "genres": ["electronic", "house"],
                    "copyright": "Jamison Daniel © 2021",
                    "visual_artist": "Jamison Daniel",
                    "producer": "Jamison Daniel",
                    "publisher": "Jamison Daniel Music",
                    "links": {
                      "twitter": "@JamisonDMusic",
                      "website": "jamisondaniel.com"
                    }
                },
                {
                    "name": "Top 40's (Master 2021)",
                    "mediaType": "audio/flac",
                    "src": "ipfs://Qmdfr4PvuiZhi3a6EaDupGN6R33PKSy5kntwgFEzLQnPLR",
                    "artists": [{"name": "Jamison Daniel"}],
                    "album_title": "Studio Life",
                    "track_number": 6,
                    "song_title": "Top 40's (Master 2021)",
                    "song_duration": "PT6M33S",
                    "genres": ["electronic", "house"],
                    "copyright": "Jamison Daniel © 2021",
                    "visual_artist": "Jamison Daniel",
                    "producer": "Jamison Daniel",
                    "publisher": "Jamison Daniel Music",
                    "links": {
                      "twitter": "@JamisonDMusic",
                      "website": "jamisondaniel.com"
                    }
                },
                {
                    "name": "Acid Trip (Master 2021)",
                    "mediaType": "audio/flac",
                    "src": "ipfs://QmSp4Cn7qrhLTovezS1ii7ct1VAPK6Gotd2GnxnBc6ngSv",
                    "artists": [{"name": "Jamison Daniel"}],
                    "album_title": "Studio Life",
                    "track_number": 7,
                    "song_title": "Acid Trip (Master 2021)",
                    "song_duration": "PT6M7S",
                    "genres": ["electronic", "house"],
                    "copyright": "Jamison Daniel © 2021",
                    "visual_artist": "Jamison Daniel",
                    "producer": "Jamison Daniel",
                    "publisher": "Jamison Daniel Music",
                    "links": {
                      "twitter": "@JamisonDMusic",
                      "website": "jamisondaniel.com"
                    }
                },
                {
                    "name": "For The Win (Master 2021)",
                    "mediaType": "audio/flac",
                    "src": "ipfs://QmV8ihv8R6cCKsFJyFP8fhnnQjeKjS7HAAjmxMgUPftmw6",
                    "artists": [{"name": "Jamison Daniel"}],
                    "album_title": "Studio Life",
                    "track_number": 8,
                    "song_title": "For The Win (Master 2021)",
                    "song_duration": "PT6M36S",
                    "genres": ["electronic", "house"],
                    "copyright": "Jamison Daniel © 2021",
                    "visual_artist": "Jamison Daniel",
                    "producer": "Jamison Daniel",
                    "publisher": "Jamison Daniel Music",
                    "links": {
                      "twitter": "@JamisonDMusic",
                      "website": "jamisondaniel.com"
                    }
                },
                {
                    "name": "Sunday Sermon (Master 2021)",
                    "mediaType": "audio/flac",
                    "src": "ipfs://QmWux5UpX6BtYQ7pjugqRh6ySa2vVJN12iSC2AB1cAQynU",
                    "artists": [{"name": "Jamison Daniel"}],
                    "album_title": "Studio Life",
                    "track_number": 9,
                    "song_title": "Sunday Sermon (Master 2021)",
                    "song_duration": "PT5M13S",
                    "genres": ["electronic", "house"],
                    "copyright": "Jamison Daniel © 2021",
                    "visual_artist": "Jamison Daniel",
                    "producer": "Jamison Daniel",
                    "publisher": "Jamison Daniel Music",
                    "links": {
                      "twitter": "@JamisonDMusic",
                      "website": "jamisondaniel.com"
                    }
                }
            ]
        }
    }
}
```

# Rationale

Implementing this simplifies and commonizes the process for creating music tokens on Cardano. It greatly simplifies the work that apps have to make when consuming such tokens.

This CIP is the result of several online meetings between many different companies building music-related projects on top of Cardano. These meetings were organized as many in the community started to see fragmentation in the way music NFTs were being minted on Cardano. These meetings gave the opportunity for a bit of a reset and will allow a much brighter future for music on Cardano. As long as all projects agree on some of these basic fields, there is great flexibility in this CIP to do application-specific unique things on top of the music NFT itself. The CIP is intentionally open-ended and can be updated in future versions if there are additional fields that the wider group could benefit from.

## Path to Active

This proposal is now considered in an Active state and has been implemented by a number of parties.

- [x] SickCityNFT - sickcity.xyz
- [x] NEWM - newm.io
- [x] SoundRig - soundrig.io

# Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
