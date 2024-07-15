---
CIP: 60
Title: Music Token Metadata
Status: Active
Category: Metadata
Authors:
  - Andrew Westberg <awestberg@projectnewm.io>
  - Ryan Jones <rjones@projectnewm.io>
  - Justin Morgan <jusemorgan@gmail.com>
  - Ian Singer <tcl@fre5hmusic.com>
  - Anthony Eizmendiz <aeizmendiz@icloud.com>
  - Session Cruz <session@demu.pro>
  - Jimmy Londo <SickCityCleveland@gmail.com>
  - Gudbrand Tokerud <Gudbrand.tokerud@gmail.com>
  - Kevin St.Clair <kos1777@gmail.com>
  - Brandon Loyche <dsqise@gmail.com>
  - Andrew Donovan <adonovan23@gmail.com>
Implementors:
  - NEWM <newm.io>
  - SoundRig <soundrig.io>
  - SickCityNFT <sickcity.xyz>
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/307
  - https://github.com/cardano-foundation/CIPs/pull/367
  - https://github.com/cardano-foundation/CIPs/pull/502
Created: 2022-07-26
License: CC-BY-4.0
---

## Abstract

This proposal defines an extension to CIP-25 and CIP-68 for token metadata specific to music tokens.

## Motivation: why is this CIP necessary?

Music tokens on Cardano can be either NFTs or FTs and contain links to audio files. In order for players, indexers, and wallets to be able to properly search and categorize a user's music collection, we need to define a common schema for creating music on Cardano. If all parties creating these music tokens follow similar patterns, apps can consume this information and make proper use of it. The existing CIP-25 is a good base to build upon, but for a good music experience, we need to standardize additional fields that will be required specifically for music tokens.

## Specification

This CIP divides the additional metadata parameters into two categories of `Required` and `Optional`. When minting a music token on Cardano, you are expected to include ALL of the required fields. If you choose to include one or more of the optional fields, they must be named exactly as defined in this CIP. This will properly allow indexing apps and music players to utilize as much of your token metadata as possible without issues.

[CDDL Spec Version 3 (proposal)](./cddl/version-3.cddl)<br/>
[CDDL Spec Version 2](./cddl/version-2.cddl)<br/>
[CDDL Spec Version 1 (deprecated)](./cddl/version-1.cddl)

### Summary of v2 Changes ###
In version 2 of the CIP-60 spec, `album_title` has been renamed to `release_title`. `release` is a more generic name that covers all types of releases from Albums, EPs, LPs, Singles, and Compilations. At the top level, we are grouping those metadata items that relate to the release under a new key `release`. At the file for each song, there is a new `song` key that holds the metadata specific to the individual song. These changes separate the music-specific metadata from the general CIP-25/CIP-68 NFT metadata. A music player can look at just the information necessary instead of having to ignore extra NFT-related fields. CIP-68 NFTs are officially supported and an example specific to CIP-68 has been added below.

### Summary of v3  Proposed Changes ###
Version 3 reorders identifiers like IPN, ISNI, etc into objects tied with the entities they are associated with. `contributing_artists`, `artists`, and `featured_artists` fields are explicitly defined to reduce interpretation.  `ipi` array replaced with `author` array, which includes `ipi` key.  Removed the `parental_advisory` field, as it was redundant (`explicit` is all players need to look for). `lyricist` is removed and merged into `contributing_artist`, under `role`.  Copyright is moved to optional fields, as many situations, including AI generated content, bring forth conditions where copyright is not applicable.

### Required Fields ##s#
| Field | Type | Example(s) | Notes |
| -------- | -------- | -------- | -------- |
| artists     | Array\<Artist\>   | "artists": [<br/>  { "name": "Stevie Nicks" },<br/>{ "name": "Tom Petty", "isni":"xxxxxxxxxxxxxxx" }<br/>] | Players should use these values to determine the song's artist, and should be kept minimal. |
| release_title| String | "release_title": "Mr. Bad Guy" | |
| track_number | Integer | "track_number": 1 | |
| song_title | String \| Array\<String\> | "song_title": "Let's Turn it On" | |
| song_duration | String | "song_duration": "PT3M21S"  | ISO8601 Duration Format |
| genres | Array\<String\> | "genres": ["Rock","Classic Rock"] | Limited to 3 genres total. Players should ignore extra genres. |
| release_type | Enum\<String\> | "release_type": "Single" | Must be one of "Single" or "Multiple". Multiple includes anything that will have multiple tracks: Album, EP, Compilation, etc...|
| music_metadata_version | Integer | "music_metadata_version" : 1 | Players should look for the presence of this field to determine if the token is a Music Token.  Use integers only. |

#### Optional Fields ###
| Field | Type | Example(s) | Notes |
| -------- | -------- | -------- | -------- |
| copyright | String | "copyright": "℗ 1985 Sony Records" | |
| ai_generated | Boolean| "ai_generated": "true"  | Used to distinguish works that are significantly AI generated, as they may not qualify as copyrighted material |
| contributing_artists |  Array\<Artist\> | "contributing_artists": [{"name":"Dolly Parton"}]<br/>*or*<br/>"contributing_artists": [<br/>{"name":"Brad Paisley"},{"name":"Keith Urban", "ipn":"xxxxxxxxxxx"}<br/>] | Contributing artist are defined as any creative contributor who is not necessarily identified as an author, but will receive performance royalties when applicable.  eg, a band would place the band name in `artists`, while the band members would be listing individually here.  Should not pass to players, but readable within metadata.  Can optionally contain `role` key, replacing `lyricist` |
| role | string | "contributing_artists": [{"name":"Jimmy Londo", "ipn":"xxxxxxxxxxxxxxxx", "role": "guitars/vocals"}] | This optionally clarifies the contribution made by the contributor in question. |
| ipn | Array\<String\> | "contributing_artists": [{"name":"Contributor", "ipn": "xxxxxxxxxxx", "role: "synths/programming/vocals"}] | Included within `contributing_artists` array, associating the IPN with a specific performer |
| series | string | "series": "That's What I call Music" | |
| collection | string | "collection": "Now Dance" | |
| set | string | "set": "86 - 20 Smash Dance Hits of the Year" | |
| mood | String | "mood": "Empowered" | |
| lyrics | URL | "lyrics": "ipfs://QmSmadTEhB9bJQ1WHq58yN1YZaJo4jv5BwVNGaePvEj4Fy"<br/>*or*<br/>"lyrics": "https://website.com/song_lyrics.txt" |  |
| special_thanks | Array\<String\> | "special_thanks": ["Your mom","Your grandma"] | |
| visual_artist | String | "visual_artist": "beeple" | |
| distributor | String | "distributor": "https://newm.io" | |
| release_date | String | "release_date": "2022-07-27" | ISO8601 Date Format |
| publication_date | String | "publication_date": "2022-07-27" | ISO8601 Date Format |
| catalog_number | Integer | "catalog_number": 2 | | 
| bitrate | String | "bitrate": "256 kbit/s" | |
| bpm | String | "bpm": "120 BPM" | |
| mix_engineer | String | "mix_engineer": "Robert Smith II" | |
| mastering_engineer | String | "mastering_engineer": "Michael Tyson" | |
| producer | String | "producer": "Simon Cowell" | |
| co_producer | String | "co_producer": "Shavaun Dempsey" | |
| featured_artists | Array\<Artist\> | "featured_artists": {"name": "The Temptations"} | `feautured_artists` should be passed to players along with the `artists`, and should be expected to appear as "artistName(s) ft. featuredArtist(s)" .  Also may include ISNI identifier and `links` within the object.  Should be kept minimal. |
| recording_engineer | String | "recording_engineer": "Sharon Liston" | |
| release_version | Integer | "release_version": 2 | |
| explicit | Boolean | "explicit": true | | *
| isrc | String | "isrc": "US-SKG-22-12345" | |
| iswc | String | "iswc": "T-123456789-Z" | |
| authors | Array\<Author\> | "authors": [{"name": "Author Name", "ipi":"595014347"},{"name":"Author Name2", "ipi":"342287075"},{"ipi":"550983139"}] | `ipi` array changed to "authors", allowing searching and indexing by songwriter.  `name` key optional, should psuedo-anonimity be desired.|

| isni | Array\<String\> | "artists": [{"name":"Awesome Artist", "isni":"xxxx-xxxx-xxxx-xxxx"}] | Included within the `artists` array within an object so players can distinguish between similar named entities|
| metadata_language | String | "metadata_language": "en-US" | https://tools.ietf.org/search/bcp47 |
| country_of_origin | String | "country_of_origin": "United States" | |
| language | String | "language": "en-US" | https://tools.ietf.org/search/bcp47 |
| derived_from | String | "derived_from" : "Some other work" | |
| links | Map\<String,String\> | "artists": [<br/>"name":"Andrew Donovan", "links":{"website": "https://website.com",<br/>"twitter": "https://twitter.com/username",<br/>"discord_invite": "https://discord.gg/TEzXxjsN",<br/>"TikTok": "https://www.tiktok.com/@knucklebumpfarms",<br/>"discord_username": "MusicianPerson#8537",<br/>"instagram":"...",<br/>"facebook":"...",<br/>"soundcloud": "...",<br/>"bandcamp": "...",<br/>"spotify": "...",<br/>"apple_music": "..."}}] | included within `artists` and `featured_artists` arrays|

### Examples ##

```
{
    "721":
    {
        "<policyId>":
        {
            "<assetName>":
            {
                "name": "<releaseName>",
                "image": "<mediaURL>",
                "music_metadata_version": 3,
                "release": {
                    "release_type": "<Single/Multiple>",
                    "release_title": "<releaseTitle>",
                    "distributor": "<distributor>"
                },
                "files":
                [
                    {
                        "name": "<fileName>",
                        "mediaType": "<mimeType>",
                        "src": "<mediaURL>",
                        "song": {
                            "song_title": "<songName>",
                            "song_duration": "PT<minutes>M<seconds>S",
                            "track_number": "<track#>",
                            "mood": "<mood>",
                            "artists":
                            [
                                { "name": "<artistName>", "isni":"xxxxxxxxxxxxxxxxx", "links":
                            {
                                "<linkName>": "<url>",
                                "<link2Name>": "<url>",
                                "<link3Name>": "<url>"
                            } }
                            ],
                            "featured_artists":
                                [
                                {"name":"<artistName>", "isni":"xxxxxxxxxxxxxxxxx", "links":{
                                "<linkName>": "<url>",
                                "<link2Name>": "<url>",
                                "<link3Name>": "<url>"
                                }}
                                ],
                            "contributing_artists":[
                                {
                                    "name":"<artistName>", "ipn":"xxxxxxxxxxxx", "role":"roleDescription"
                                },
                                {
                                    "name":"<artistName>", "ipn":"xxxxxxxxxxxx", "role":"roleDescription"
                                },
                                {
                                    "name":"<artistName>", "ipn":"xxxxxxxxxxxx", "role":"roleDescription"
                                }
                            ],
                            "collection": "<collectionName>",
                            "genres":
                            [
                                "<genre>",
                                "<genre>",
                                "<genre>"
                            ],
                            "copyright": "℗ <year/CopyrightHolder>"
                            
                        }
                    },
                    {
                        "name": "<fileName>",
                        "mediaType": "<mimeType>",
                        "src": "<mediaURL>",
                        "song": {
                            "song_title": "<songName>",
                            "song_duration": "PT<minutes>M<seconds>S",
                            "track_number": "<track#>",
                            "mood": "<mood>",
                            "artists":
                            [
                            { "name": "<artistName>",
                               "isni":"xxxxxxxxxxxxxxxxx",
                                 "links":
                                        {
                                        "<linkName>": "<url>",
                                        "<link2Name>": "<url>",
                                        "<link3Name>": "<url>"
                                        }
                                }
                            ],
                            "featured_artists":
                                [
                                {"name":"<artistName>",
                                 "isni":"xxxxxxxxxxxxxxxxx",
                                 "links":{
                                        "<linkName>": "<url>",
                                        "<link2Name>": "<url>",
                                        "<link3Name>": "<url>"
                                        }
                                }
                                ],
                            "contributing_artists":[
                                {
                                    "name":"<artistName>",
                                    "ipn":"xxxxxxxxxxxx",
                                    "role":"roleDescription"
                                },
                                {
                                    "name":"<artistName>",
                                    "ipn":"xxxxxxxxxxxx",
                                    "role":"roleDescription"
                                },
                                {
                                    "name":"<artistName>",
                                    "ipn":"xxxxxxxxxxxx",
                                    "role":"roleDescription"
                                }
                            ],
                            "collection": "<collectionName>",
                            "genres":
                            [
                                "<genre>",
                                "<genre>",
                                "<genre>"
                            ],
                            "copyright": "℗ <year/CopyrightHolder>"
                            
                        }
                    },
                    {
                        "name": "<fileName>",
                        "mediaType": "<mimeType>",
                        "src": "<mediaURL>",
                        "song": {
                            "song_title": "<songName>",
                            "song_duration": "PT<minutes>M<seconds>S",
                            "track_number": "<track#>",
                            "mood": "<mood>",
                            "artists":
                            [
                                { "name": "<artistName>",
                                  "isni":"xxxxxxxxxxxxxxxxx",
                                  "links":
                                        {
                                            "<linkName>": "<url>",
                                            "<link2Name>": "<url>",
                                            "<link3Name>": "<url>"
                                        }
                                }
                            ],
                            "featured_artists":
                                [
                                {"name":"<artistName>",
                                 "isni":"xxxxxxxxxxxxxxxxx",
                                 "links":{
                                          "<linkName>": "<url>",
                                          "<link2Name>": "<url>",
                                          "<link3Name>": "<url>"
                                          }
                                }
                                ],
                            "contributing_artists":[
                                {
                                    "name":"<artistName>",
                                    "ipn":"xxxxxxxxxxxx",
                                    "role":"roleDescription"
                                },
                                {
                                    "name":"<artistName>",
                                    "ipn":"xxxxxxxxxxxx",
                                    "role":"roleDescription"
                                },
                                {
                                    "name":"<artistName>",
                                    "ipn":"xxxxxxxxxxxx",
                                    "role":"roleDescription"
                                }
                            ],
                            "collection": "<collectionName>",
                            "genres":
                            [
                                "<genre>",
                                "<genre>",
                                "<genre>"
                            ],
                            "copyright": "℗ <year/CopyrightHolder>"
                            
                        }
                    }
                    
                ]
            }
        }
    }
}
```


#### CIP-68 ###

```
{
    "constructor": 0,
    "fields": [
        {
            "map": [
                {"k": {"bytes": "6E616D65"}, "v": {"bytes": "<encoded releaseName>"}},
                {"k": {"bytes": "696D616765"}, "v": {"bytes": "<encoded mediaURL>"}},
                {"k": {"bytes": "6D757369635F6D657461646174615F76657273696F6E"}, "v": {"int": 3}},
                {"k": {"bytes": "72656C65617365"}, "v": 
                    {
                        "map": [
                            {"k": {"bytes": "72656C656173655F74797065"}, "v": {"bytes": "<encoded Single/Multiple>"}},
                            {"k": {"bytes": "72656C656173655F7469746C65"}, "v": {"bytes": "<encoded releaseTitle>"}},
                            {"k": {"bytes": "6469737472696275746F72"}, "v": {"bytes": "<encoded distributor>"}}
                        ]
                    }
                },
                {"k": {"bytes": "66696C6573"}, "v": 
                    {
                        "array": [
                            {
                                "map": [
                                    {"k": {"bytes": "6E616D65"}, "v": {"bytes": "<encoded fileName>"}},
                                    {"k": {"bytes": "6D6564696154797065"}, "v": {"bytes": "<encoded mimeType>"}},
                                    {"k": {"bytes": "737263"}, "v": {"bytes": "<encoded mediaURL>"}},
                                    {"k": {"bytes": "736F6E67"}, "v": 
                                        {
                                            "map": [
                                                {"k": {"bytes": "736F6E675F7469746C65"}, "v": {"bytes": "<encoded songName>"}},
                                                {"k": {"bytes": "736F6E675F6475726174696F6E"}, "v": {"bytes": "<encoded PT<minutes>M<seconds>S>"}},
                                                {"k": {"bytes": "747261636B5F6E756D626572"}, "v": {"int": "<track#>"}},
                                                {"k": {"bytes": "6D6F6F64"}, "v": {"bytes": "<encoded mood>"}},
                                                {"k": {"bytes": "61727469737473"}, "v": 
                                                    {
                                                        "array": [
                                                            { 
                                                                "map": [
                                                                    {"k": {"bytes": "6E616D65"}, "v": {"bytes": "<encoded artistName>"}},
                                                                    {"k": {"bytes": "69736E69"}, "v": {"bytes": "<encoded ISNI>"}},
                                                                    {"k": {"bytes": "6C696E6B73"}, "v": 
                                                                        {
                                                                            "map": [
                                                                                {"k": {"bytes": "<encoded linkName>"}, "v": {"bytes": "<encoded url>"}},
                                                                                {"k": {"bytes": "<encoded link2Name>"}, "v": {"bytes": "<encoded url>"}},
                                                                                {"k": {"bytes": "<encoded link3Name>"}, "v": {"bytes": "<encoded url>"}}
                                                                            ]
                                                                        }
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                },
                                                {"k": {"bytes": "6665617475726564_61727469737473"}, "v": 
                                                    {
                                                        "array": [
                                                            { 
                                                                "map": [
                                                                    {"k": {"bytes": "6E616D65"}, "v": {"bytes": "<encoded artistName>"}},
                                                                    {"k": {"bytes": "69736E69"}, "v": {"bytes": "<encoded ISNI>"}},
                                                                    {"k": {"bytes": "6C696E6B73"}, "v": 
                                                                        {
                                                                            "map": [
                                                                                {"k": {"bytes": "<encoded linkName>"}, "v": {"bytes": "<encoded url>"}},
                                                                                {"k": {"bytes": "<encoded link2Name>"}, "v": {"bytes": "<encoded url>"}},
                                                                                {"k": {"bytes": "<encoded link3Name>"}, "v": {"bytes": "<encoded url>"}}
                                                                            ]
                                                                        }
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                },
                                                {"k": {"bytes": "636F6E747269627574696E675F61727469737473"}, "v": 
                                                    {
                                                        "array": [
                                                            {
                                                                "map": [
                                                                    {"k": {"bytes": "6E616D65"}, "v": {"bytes": "<encoded artistName>"}},
                                                                    {"k": {"bytes": "69706E"}, "v": {"bytes": "<encoded IPN>"}},
                                                                    {"k": {"bytes": "726F6C65"}, "v": {"bytes": "<encoded roleDescription>"}}
                                                                ]
                                                            },
                                                            {
                                                                "map": [
                                                                    {"k": {"bytes": "6E616D65"}, "v": {"bytes": "<encoded artistName>"}},
                                                                    {"k": {"bytes": "69706E"}, "v": {"bytes": "<encoded IPN>"}},
                                                                    {"k": {"bytes": "726F6C65"}, "v": {"bytes": "<encoded roleDescription>"}}
                                                                ]
                                                            },
                                                            {
                                                                "map": [
                                                                    {"k": {"bytes": "6E616D65"}, "v": {"bytes": "<encoded artistName>"}},
                                                                    {"k": {"bytes": "69706E"}, "v": {"bytes": "<encoded IPN>"}},
                                                                    {"k": {"bytes": "726F6C65"}, "v": {"bytes": "<encoded roleDescription>"}}
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                },
                                                {"k": {"bytes": "636F6C6C656374696F6E"}, "v": {"bytes": "<encoded collectionName>"}},
                                                {"k": {"bytes": "67656E726573"}, "v": 
                                                    {
                                                        "array": [
                                                            {"bytes": "<encoded genre1>"},
                                                            {"bytes": "<encoded genre2>"},
                                                            {"bytes": "<encoded genre3>"}
                                                        ]
                                                    }
                                                },
                                                {"k": {"bytes": "636F707972696768"}, "v": {"bytes": "<encoded copyright>"}}
                                            ]
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        },
        {
            "int": 1
        }
    ]
}
```

## Rationale: how does this CIP achieve its goals?

Implementing this simplifies and commonizes the process for creating music tokens on Cardano. It greatly simplifies the work that apps have to make when consuming such tokens.

This CIP is the result of several online meetings between many different companies building music-related projects on top of Cardano. These meetings were organized as many in the community started to see fragmentation in the way music NFTs were being minted on Cardano. These meetings gave the opportunity for a bit of a reset and will allow a much brighter future for music on Cardano. As long as all projects agree on some of these basic fields, there is great flexibility in this CIP to do application-specific unique things on top of the music NFT itself. The CIP is intentionally open-ended and can be updated in future versions if there are additional fields that the wider group could benefit from.

## Path to Active

### Acceptance Criteria

- [x] Has been implemented by a number of parties, including:
  - [x] SickCityNFT - sickcity.xyz
  - [x] NEWM - newm.io
  - [x] SoundRig - soundrig.io

### Implementation Plan

- [x] Consensus of companies building music-related Cardano projects to develop a mutually beneficial metadata vocabulary.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
