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
  - The Finest LLC (DBA So Litty Records) <solittyrecords@gmail.com>
  - Cristhian Escobar <escobarcristhian18@gmail.com>
  - Gabriel Stephan Talamantes <contact@psyencelab.media>
Implementors:
  - NEWM <newm.io>
  - SoundRig <soundrig.io>
  - SickCityNFT <sickcity.xyz>
Discussions:
  - https://github.com/cardano-foundation/CIPs/pull/307
  - https://github.com/cardano-foundation/CIPs/pull/367
  - https://github.com/cardano-foundation/CIPs/pull/502
  - https://github.com/cardano-foundation/CIPs/pull/868
Created: 2022-07-26
License: CC-BY-4.0
---

## Abstract

This proposal defines an extension to CIP-25 and CIP-68 for token metadata specific to music tokens.

## Motivation: Why is this CIP necessary?

Music tokens on Cardano can be either NFTs or FTs and contain links to audio files. In order for players, indexers, and wallets to be able to properly search and categorize a user's music collection, we need to define a common schema for creating music on Cardano. If all parties creating these music tokens follow similar patterns, apps can consume this information and make proper use of it. The existing CIP-25 is a good base to build upon, but for a good music experience, we need to standardize additional fields that will be required specifically for music tokens.

## Specification

This CIP divides the additional metadata parameters into two categories of `Required` and `Optional`. When minting a music token on Cardano, you are expected to include ALL of the required fields. If you choose to include one or more of the optional fields, they must be named exactly as defined in this CIP. This will properly allow indexing apps and music players to utilize as much of your token metadata as possible without issues.

[CDDL Spec Version 3 ](./cddl/version-3.cddl)<br/>
[CDDL Spec Version 2 (deprecated)](./cddl/version-2.cddl)<br/>
[CDDL Spec Version 1 (deprecated)](./cddl/version-1.cddl)

### Summary of v2 Changes ###
In version 2 of the CIP-60 spec, `album_title` has been renamed to `release_title`. `release` is a more generic name that covers all types of releases from Albums, EPs, LPs, Singles, and Compilations. At the top level, we are grouping those metadata items that relate to the release under a new key `release`. At the file for each song, there is a new `song` key that holds the metadata specific to the individual song. These changes separate the music-specific metadata from the general CIP-25/CIP-68 NFT metadata. A music player can look at just the information necessary instead of having to ignore extra NFT-related fields. CIP-68 NFTs are officially supported and an example specific to CIP-68 has been added below.

### Summary of v3  Proposed Changes ###
Version 3 reorders identifiers like IPN, ISNI, etc into objects tied with the entities they are associated with. `contributing_artists`, `artists`, and `featured_artists` fields are explicitly defined to reduce interpretation.  `ipi` array replaced with `author` array, which includes `ipi` key.  Removed the `parental_advisory` field, as it was redundant (`explicit` is all players need to look for). `lyricist` is removed and merged into `contributing_artist`, under `role`.  `copyright` adds `master` and `composition` to distinguish recording and composition copyright owners.  Certain fields may be included in `release` within "Album/EP" `release_type` if they are qualifying GRAM (Group Registration for Works on an Album of Music) publications. This is done in order to help conserve data in otherwise redundant entries.

### Required Fields ###
| Field | Type | Example(s) | Notes |
| -------- | -------- | -------- | -------- |
| artists     | Array\<Artist\>   | "artists": [{"name": "Sick City", "isni":"xxxxxxxxxxxxx", "links:{ "website":"https://sickcity.xyz"}}]  | Players should use these values to determine the song's artist, and should be kept minimal. `isni` and `links` are optional.  Included in `song` for "Single" and "Multiple" releases, and in `release` for "Album/EP" types. |
| release_title| String | "release_title": "Mr. Bad Guy" | Included in `release` |
| track_number | Integer | "track_number": 1 |  Included in `song` |
| song_title | String \| Array\<String\> | "song_title": "Let's Turn it On" |  Included in `song` |
| song_duration | String | "song_duration": "PT3M21S"  | ISO8601 Duration Format, included in `song`  https://www.iso.org/iso-8601-date-and-time-format.html |
| copyright | String | "copyright": {"master":"℗ 1985 Sony Records", "composition":"© 1985 Marvin Gaye"}  or <br/> "copyright": {"composition": "Public Domain", "master": "℗ 2024 Cool Guy"} | Included in `release` within "Album/EP" `release_type` (ONLY IF **ALL** compositions are owned by the same artist) , and in `song` within "Single" and "Multiple" releases. |
| genres | Array\<String\> | "genres": ["Rock","Classic Rock"] | Limited to 3 genres total. Players should ignore extra genres. Included in `song` within "Single" and "Multiple" releases, and in `release` for "Album/EP" releases should all songs share the same `genre` values. |
| release_type | Enum\<String\> | "release_type": "Single" | Must be "Single", "Album/EP" for GRAM (Group Registration for Works on an Album of Music- https://www.copyright.gov/rulemaking/gram/) publications, or "Multiple" (for all other cases"). "Multiple" and "Album/EP" releases need to be wary of txn size limits .  Included in `release`  |
| music_metadata_version | Integer | "music_metadata_version" : "3" | Players should look for the presence of this field to determine if the token is a Music Token.  Use integers only. |

#### Optional Fields ###
| Field | Type | Example(s) | Notes |
| -------- | -------- | -------- | -------- |
| isni | String | "artists": [{"name": "Sick City", "isni":"xxxxxxxxxxxxx", "links:{ "website":"https://sickcity.xyz"}}] |  Included in `song` with `artists` and `featured_artists` |
| links | Map | "artists": [{"name": "Sick City", "isni":"xxxxxxxxxxxxx", "links:{ "website":"https://sickcity.xyz"}}] | Included in `artists` and `featured_artist`, and in `release` where applicable, i.e. if a "Multiple" `release_type` is a single artist album and has recurring links |
| ai_generated | Boolean | "ai_generated": "true"  | Used to distinguish works that are entirely AI generated. |
| contributing_artists |  Array\<Artist\> | "contributing_artists": [{"name":"Jimmy Londo", "ipi":"158743685", "role":["guitars", "vocals"]}]  | Contributing artist are defined as any creative contributor who is not necessarily identified as an author, but will receive performance royalties when applicable.  eg, a band would place the band name in `artists`, while the band members would be listing individually here.  Should not pass to players, but readable within metadata.  May contain `ipn` or `ipi` (based on use/jurisdiction, i.e. `ipi` within the US; enables indexing of similarly named contributors) `links`, and `role`, all of which are optional |
| ipn | String | "contributing_artists": [{"name":"Jimmy Londo", "ipn":"158743685", "role":["guitars", "vocals"]}] |  Included in `song` within `contributing_artists` where used (typically outside US, though internationally recognized.)|
| role | string | "contributing_artists": [{"name":"Jimmy Londo", "ipi":"158743685", "role":["guitars", "vocals"]}] | Included in `song` within `contributing_artists` (declares a contributor's role/contribution to the work), as well as `authors` (establishing role in songwriting, following "Roles" from ASCAP)|
| series | string | "series": "That's What I call Music" | Included in `release` |
| collection | string | "collection": "Now Dance" | Included in `release` |
| set | string | "set": "86 - 20 Smash Dance Hits of the Year" | If the song is a part of a collection of songs, such as an album, EP, live performance, etc. that is separate from this release, it can be listed here.  Included in `song` |
| mood | String | "mood": "Empowered" | Included in `song` |
| lyrics | URL | "lyrics": "ipfs://QmSmadTEhB9bJQ1WHq58yN1YZaJo4jv5BwVNGaePvEj4Fy" | Included in `song` |
| special_thanks | Array\<String\> | "special_thanks": ["Your mom","Your grandma"] | Included in `song` |
| visual_artist | String | "visual_artist": "beeple" | Included in `release` |
| distributor | String | "distributor": "https://newm.io" | Included in `release` |
| release_date | String | "release_date": "2022-07-27" | ISO8601 Date Format, included in `release` |
| publication_date | String | "publication_date": "2022-07-27" | ISO8601 Date Format, included in `release` https://www.iso.org/iso-8601-date-and-time-format.html |
| catalog_number | Integer | "catalog_number": REC#4582 | Catalog numbers for digital releases should only be entered if the label or digital distributor has given a unique catalog number for the release. Included in `release` | 
| bitrate | String | "bitrate": "256 kbit/s" | Included in `song` |
| bpm | String | "bpm": "120 BPM" | Included in `song`|
| mix_engineer | String | "mix_engineer": "Robert Smith II" |  Included in `song` for "Single" and "Multiple" `release_type`, and in `release` for "Album/EP" types (if shared across the entire release, otherwise, in `song`). |
| mastering_engineer | String | "mastering_engineer": "Michael Tyson" | Included in `song` |
| producer | String | "producer": "Simon Cowell" |  Included in `song` for "Single" and "Multiple" `release_type`, and in `release` for "Album/EP" types (if shared across the entire release, otherwise, in `song`). |
| co_producer | String | "co_producer": "Shavaun Dempsey" |  Included in `song` for "Single" and "Multiple" `release_type`, and in `release` for "Album/EP" types (if shared across the entire release, otherwise, in `song`). |
| featured_artists | Array\<Artist\> | "featured_artists": [{"name":"Paul McCartney", isni":"xxxxxxxxx", "links"{"website":"www.paulmccartney.com"} }] | `feautured_artists` should be passed to players along with the `artists`, and should be expected to appear as "artistName(s) ft. featuredArtist(s)".  Contains `isni` and `links` keys, included in `song`  Should be kept minimal. |
| recording_engineer | String | "recording_engineer": "Sharon Liston" |  Included in `song` for "Single" and "Multiple" `release_type`, and in `release` for "Album/EP" types (if shared across the entire release, otherwise, in `song`). |
| explicit | Boolean | "explicit": true |  Included in `song` | 
| isrc | String | "isrc": "US-SKG-22-12345" |  Included in `song` |
| iswc | String | "iswc": "T-123456789-Z" |  Included in `song` |
| authors | Array\<Author\> | "authors": [{"name":"Mark Ronson", "ipi:"157896357", "share":"25%"}] | Publishers and authors will be listed here. May contain `ipi`, `role`, and `share`. Included in `song` |
| ipi | String | "authors": [{"name":"Mark Ronson", ipi:"157896357", "role":"Composer/Author", "share":"25%"}] |  Included in `song` within `authors` and `contributing_artists`|
| share | String | "authors": [{"name":"Mark Ronson", ipi:"157896357", "share":"25%"}] |  Included in `song` within `authors`.  Total percentage of all listed authors' shares MUST equal 100% |
| metadata_language | String | "metadata_language": "en-US" | https://tools.ietf.org/search/bcp47 | Included in `song` |
| country_of_origin | String | "country_of_origin": "United States" |  Included in `song` | 
| language | String | "language": "en-US" | https://tools.ietf.org/search/bcp47 | Included in `song` |
| derived_from | String | "derived_from" : "Some other work" |  Included in `song`|

### Examples ##

### Single Release ###

```
{
    "721": {
        "<policyId>": {
            "<assetName>": {
                "name": "<releaseName>",
                "image": "<mediaURL>",
                "music_metadata_version": 3,
                "release": {
                        "release_type": "<Single/Multiple>",
                        "release_title": "<releaseTitle>",
                        "distributor": "<distributor>"
                          },                
                "files": [
                    {
                        "name": "<fileName>",
                        "mediaType": "<mimeType>",
                        "src": "<mediaURL>",
                        "song": {
                            "song_title": "<songName>",
                            "song_duration": "PT<minutes>M<seconds>S",
                            "track_number": 1,
                            "mood": "<mood>",
                            "artists": [
                                {
                                    "name:": "<artistName>",
                                    "isni": "<isni>",
                                    "links": {
                                            "<linkName>": "<url>",
                                            "<link2Name>": "<url>",
                                            "<link3Name>": "<url>"
                                        }
                                    },
                                {
                                    "name:": "<artistName>",
                                    "isni": "<isni>",
                                    "links": {
                                            "<linkName>": "<url>",
                                            "<link2Name>": "<url>",
                                            "<link3Name>": "<url>"
                                        }
                                    }
                            ],
                            "featured_artists": [
                                {
                                    "name:": "<artistName>",
                                    "isni": "<isni>",
                                    "links": {
                                            "<linkName>": "<url>",
                                            "<link2Name>": "<url>",
                                            "<link3Name>": "<url>"
                                        }
                                    },
                               {
                                    "name:": "<artistName>",
                                    "isni": "<isni>",
                                    "links": {
                                            "<linkName>": "<url>",
                                            "<link2Name>": "<url>",
                                            "<link3Name>": "<url>"
                                        }
                                    }
                            ],
                            "authors": [
                                {
                                        "name": "<authorName>",
                                        "ipi": "<ipi>",
                                        "share": "<percentage>"
                                    },
                                    {
                                        "name": "<authorName>",
                                        "ipi": "<ipi>",
                                        "share": "<percentage>"
                                    },
                                    {
                                        "name": "<authorName>",
                                        "ipi": "<ipi>",
                                        "share": "<percentage>"
                                    }
                            ],
                            "contributing_artists": [
                                {
                                   "name": "<artistName>",
                                        "ipn": "<ipi>",
                                        "role": [
                                            "<roleDescription>",
                                            "<roleDescription>"
                                        ]
                                    
                                },
                                 {
                                   "name": "<artistName>",
                                        "ipi": "<ipi>",
                                        "role": [
                                            "<roleDescription>",
                                            "<roleDescription>"
                                        ]
                                    
                                },
                                 {
                                   "name": "<artistName>",
                                        "ipi": "<ipi>",
                                        "role": [
                                            "<roleDescription>",
                                            "<roleDescription>"
                                        ]
                                    
                                }
                            ],
                            "collection": "<collectionName>",
                            "genres": [
                                "<genre>",
                                "<genre>",
                                "<genre>"
                            ],
                            "copyright": {"master": "℗ <year, copyrightHolder>", "composition": "© <year, copyrightHolder>"}
                        }
                    }
                    
                ]
            }
        }
    }
}
```
### Album Release ###
```
{
    "721": {
        "c00d776a22ca5db986039420b2a9b3f880d593136a9e2262fabeeb58": {
            "ZiplineFromOuterspace": {
                "name": "Refraktal - Zipline From Outerspace",
                "image": "ipfs://QmeeHGqiRo8gvAfhG6MuHSTKv6rQpw2bxbnDkAPYvt9jD2",
                "music_metadata_version": 3,
                "release": {
                    "release_type": "Album/EP",
                    "release_title": "Zipline From Outerspace",
                    "copyright": {
                        "master": "℗ 2024 Refraktal",
                        "composition": "© 2024 Refraktal"
                    },
                    "artists": [
                        {
                            "name:": "Refraktal",
                            "isni": "0000000517483974",
                            "links": {
                                "website": "https://refraktal.com",
                                "exclusive_content": "https://refraktalnft.duckdns.org"
                            }
                        }
                    ],
                    "contributing_artists": [
                        {
                            "name": "Sudo Scientist",
                            "ipi": "1251891449",
                            "role": [
                                "guitar on VOID and Lullaby for My Demons",
                                "synth",
                                "programming"
                            ]
                        },
                        {
                            "name": "RX the Pharm Tech",
                            "ipi": "1251891057",
                            "role": [
                                "guitar on Bellywub",
                                "synth",
                                "programming"
                            ]
                        }
                    ],
                    "genre": [
                        "Electronic",
                        "Experimental",
                        "Psychedelic"
                    ]
                },
                "files": [
                    {
                        "name": "Void",
                        "mediaType": "audio/wav",
                        "src": "ipfs://QmeeHGqiRo8gvAfhG6MuHSTKv6rQpw2bxbnDkAPYvt9jD2",
                        "song": {
                            "song_title": "Void",
                            "song_duration": "PT4M21S",
                            "track_number": 1,
                            "isrc": "US-SKG-22-12345",
                            "iswc": "T-123456789-Z"
                        }
                    },
                    {
                        "name": "Bellywub",
                        "mediaType": "audio/wav",
                        "src": "ipfs://QmeeHGqiRo8gvAfhG6MuHSTKv6rQpw2bxbnDkAPYvt9jD2",
                        "song": {
                            "song_title": "Bellywub",
                            "song_duration": "PT5M31S",
                            "track_number": 2,
                            "isrc": "US-SKG-22-12345",
                            "iswc": "T-123456789-Z"
                        }
                    },
                    {
                        "name": "Lullaby for my Demons",
                        "mediaType": "audio/wav",
                        "src": "ipfs://QmeeHGqiRo8gvAfhG6MuHSTKv6rQpw2bxbnDkAPYvt9jD2",
                        "song": {
                            "song_title": "Lullaby for My Demons",
                            "song_duration": "PT3M11S",
                            "track_number": 3,
                            "isrc": "US-SKG-22-12345",
                            "iswc": "T-123456789-Z"
                        }
                    },
                    {
                        "name": "Meliorism",
                        "mediaType": "audio/wav",
                        "src": "ipfs://QmeeHGqiRo8gvAfhG6MuHSTKv6rQpw2bxbnDkAPYvt9jD2",
                        "song": {
                            "song_title": "Meliorism",
                            "song_duration": "PT4M21S",
                            "track_number": 4,
                            "isrc": "US-SKG-22-12345",
                            "iswc": "T-123456789-Z"
                        }
                    },
                    {
                        "name": "Zipline From Outerspace",
                        "mediaType": "audio/wav",
                        "src": "ipfs://QmeeHGqiRo8gvAfhG6MuHSTKv6rQpw2bxbnDkAPYvt9jD2",
                        "song": {
                            "song_title": "Zipline From Outerspace",
                            "song_duration": "PT3M36S",
                            "track_number": 5,
                            "isrc": "US-SKG-22-12345",
                            "iswc": "T-123456789-Z"
                        }
                    },
                    {
                        "name": "Another Cool Song",
                        "mediaType": "audio/wav",
                        "src": "ipfs://QmeeHGqiRo8gvAfhG6MuHSTKv6rQpw2bxbnDkAPYvt9jD2",
                        "song": {
                            "song_title": "Another Cool Song",
                            "song_duration": "PT2M12S",
                            "track_number": 6,
                            "isrc": "US-SKG-22-12345",
                            "iswc": "T-123456789-Z"
                        }
                    },
                    {
                        "name": "Another Cool Song",
                        "mediaType": "audio/wav",
                        "src": "ipfs://QmeeHGqiRo8gvAfhG6MuHSTKv6rQpw2bxbnDkAPYvt9jD2",
                        "song": {
                            "song_title": "Another Cool Song",
                            "song_duration": "PT3M36S",
                            "track_number": 7,
                            "isrc": "US-SKG-22-12345",
                            "iswc": "T-123456789-Z"
                        }
                    },
                    {
                        "name": "Another Cool Song",
                        "mediaType": "audio/wav",
                        "src": "ipfs://QmeeHGqiRo8gvAfhG6MuHSTKv6rQpw2bxbnDkAPYvt9jD2",
                        "song": {
                            "song_title": "Another Cool Song",
                            "song_duration": "PT3M36S",
                            "track_number": 8,
                            "isrc": "US-SKG-22-12345",
                            "iswc": "T-123456789-Z"
                        }
                    },
                    {
                        "name": "Another Cool Song",
                        "mediaType": "audio/wav",
                        "src": "ipfs://QmeeHGqiRo8gvAfhG6MuHSTKv6rQpw2bxbnDkAPYvt9jD2",
                        "song": {
                            "song_title": "Another Cool Song",
                            "song_duration": "PT3M36S",
                            "track_number": 9,
                            "isrc": "US-SKG-22-12345",
                            "iswc": "T-123456789-Z"
                        }
                    },
                    {
                        "name": "Another Cool Song",
                        "mediaType": "audio/wav",
                        "src": "ipfs://QmeeHGqiRo8gvAfhG6MuHSTKv6rQpw2bxbnDkAPYvt9jD2",
                        "song": {
                            "song_title": "Another Cool Song",
                            "song_duration": "PT3M36S",
                            "track_number": 10,
                            "isrc": "US-SKG-22-12345",
                            "iswc": "T-123456789-Z"
                        }
                    },
                    {
                        "name": "Another Cool Song",
                        "mediaType": "audio/wav",
                        "src": "ipfs://QmeeHGqiRo8gvAfhG6MuHSTKv6rQpw2bxbnDkAPYvt9jD2",
                        "song": {
                            "song_title": "Another Cool Song",
                            "song_duration": "PT3M36S",
                            "track_number": 11,
                            "isrc": "US-SKG-22-12345",
                            "iswc": "T-123456789-Z"
                        }
                    },
                    {
                        "name": "Another Cool Song",
                        "mediaType": "audio/wav",
                        "src": "ipfs://QmeeHGqiRo8gvAfhG6MuHSTKv6rQpw2bxbnDkAPYvt9jD2",
                        "song": {
                            "song_title": "Another Cool Song",
                            "song_duration": "PT3M36S",
                            "track_number": 12,
                            "isrc": "US-SKG-22-12345",
                            "iswc": "T-123456789-Z"
                        }
                    },
                    {
                        "name": "Another Cool Song",
                        "mediaType": "audio/wav",
                        "src": "ipfs://QmeeHGqiRo8gvAfhG6MuHSTKv6rQpw2bxbnDkAPYvt9jD2",
                        "song": {
                            "song_title": "Another Cool Song",
                            "song_duration": "PT3M36S",
                            "track_number": 13,
                            "isrc": "US-SKG-22-12345",
                            "iswc": "T-123456789-Z"
                        }
                    },
                    {
                        "name": "Another Cool Song",
                        "mediaType": "audio/wav",
                        "src": "ipfs://QmeeHGqiRo8gvAfhG6MuHSTKv6rQpw2bxbnDkAPYvt9jD2",
                        "song": {
                            "song_title": "Another Cool Song",
                            "song_duration": "PT3M36S",
                            "track_number": 14,
                            "isrc": "US-SKG-22-12345",
                            "iswc": "T-123456789-Z"
                        }
                    },
                    {
                        "name": "Another Cool Song",
                        "mediaType": "audio/wav",
                        "src": "ipfs://QmeeHGqiRo8gvAfhG6MuHSTKv6rQpw2bxbnDkAPYvt9jD2",
                        "song": {
                            "song_title": "Another Cool Song",
                            "song_duration": "PT3M36S",
                            "track_number": 15,
                            "isrc": "US-SKG-22-12345",
                            "iswc": "T-123456789-Z"
                        }
                    },
                    {
                        "name": "Another Cool Song",
                        "mediaType": "audio/wav",
                        "src": "ipfs://QmeeHGqiRo8gvAfhG6MuHSTKv6rQpw2bxbnDkAPYvt9jD2",
                        "song": {
                            "song_title": "Another Cool Song",
                            "song_duration": "PT3M36S",
                            "track_number": 16,
                            "isrc": "US-SKG-22-12345",
                            "iswc": "T-123456789-Z"
                        }
                    },
                    {
                        "name": "Another Cool Song",
                        "mediaType": "audio/wav",
                        "src": "ipfs://QmeeHGqiRo8gvAfhG6MuHSTKv6rQpw2bxbnDkAPYvt9jD2",
                        "song": {
                            "song_title": "Another Cool Song",
                            "song_duration": "PT3M36S",
                            "track_number": 17,
                            "isrc": "US-SKG-22-12345",
                            "iswc": "T-123456789-Z"
                        }
                    },
                    {
                        "name": "Another Cool Song",
                        "mediaType": "audio/wav",
                        "src": "ipfs://QmeeHGqiRo8gvAfhG6MuHSTKv6rQpw2bxbnDkAPYvt9jD2",
                        "song": {
                            "song_title": "Another Cool Song",
                            "song_duration": "PT3M36S",
                            "track_number": 18,
                            "isrc": "US-SKG-22-12345",
                            "iswc": "T-123456789-Z"
                        }
                    },
                    {
                        "name": "Another Cool Song",
                        "mediaType": "audio/wav",
                        "src": "ipfs://QmeeHGqiRo8gvAfhG6MuHSTKv6rQpw2bxbnDkAPYvt9jD2",
                        "song": {
                            "song_title": "Another Cool Song",
                            "song_duration": "PT3M36S",
                            "track_number": 19,
                            "isrc": "US-SKG-22-12345",
                            "iswc": "T-123456789-Z"
                        }
                    },
                    {
                        "name": "Another Cool Song",
                        "mediaType": "audio/wav",
                        "src": "ipfs://QmeeHGqiRo8gvAfhG6MuHSTKv6rQpw2bxbnDkAPYvt9jD2",
                        "song": {
                            "song_title": "Another Cool Song",
                            "song_duration": "PT3M36S",
                            "track_number": 20,
                            "isrc": "US-SKG-22-12345",
                            "iswc": "T-123456789-Z"
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
                {"k": {"bytes": "373231"}, "v": {
                    "map": [
                        {"k": {"bytes": "<encoded policyId>"}, "v": {
                            "map": [
                                {"k": {"bytes": "<encoded assetName>"}, "v": {
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
                                                                        {"k": {"bytes": "747261636B5F6E756D626572"}, "v": {"int": track#}},
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
                                                                        {"k": {"bytes": "617574686F7273"}, "v": 
                                                                            {
                                                                                "array": [
                                                                                    {
                                                                                        "map": [
                                                                                            {"k": {"bytes": "6E616D65"}, "v": {"bytes": "<encoded authorName>"}},
                                                                                            {"k": {"bytes": "697069"}, "v": {"bytes": "<encoded IPI>"}},
                                                                                            {"k": {"bytes": "7368617265"}, "v": {"bytes": "<encoded percentage>"}}
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
                                                                                            {"k": {"bytes": "697069"}, "v": {"bytes": "<encoded IPI>"}},
                                                                                            {"k": {"bytes": "726F6C65"}, "v": 
                                                                                                {
                                                                                                    "array": [
                                                                                                        {"bytes": "<encoded roleDescription>"},
                                                                                                        {"bytes": "<encoded roleDescription>"}
                                                                                                    ]
                                                                                                }
                                                                                            }
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
                                                                        {"k": {"bytes": "636F707972696768"}, "v": 
                                                                            {
                                                                                "map": [
                                                                                    {"k": {"bytes": "6D6173746572"}, "v": {"bytes": "<encoded ℗ <year, copyrightHolder>"}},
                                                                                    {"k": {"bytes": "636F6D706F736974696F6E"}, "v": {"bytes": "<encoded © <year, copyrightHolder>"}}
                                                                                ]
                                                                            }
                                                                        }
                                                                    ]
                                                                }
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        }
                                    ]
                                }}
                            ]
                        }}
                    ]
                }}
            ]
        },
        {
            "int": 1
        }
    ]
}
```

## Rationale: How does this CIP achieve its goals?

Implementing this simplifies and commonizes the process for creating music tokens on Cardano. It greatly simplifies the work that apps have to make when consuming such tokens.

This CIP is the result of several online meetings between many different companies building music-related projects on top of Cardano. These meetings were organized as many in the community started to see fragmentation in the way music NFTs were being minted on Cardano. These meetings gave the opportunity for a bit of a reset and will allow a much brighter future for music on Cardano. As long as all projects agree on some of these basic fields, there is great flexibility in this CIP to do application-specific unique things on top of the music NFT itself. The CIP is intentionally open-ended and can be updated in future versions if there are additional fields that the wider group could benefit from.

## Path to Active

### Acceptance Criteria

- [x] Has been implemented by a number of parties, including:
  - [x] SickCityNFT - sickcity.xyz
  - [x] NEWM - newm.io
  - [x] SoundRig - soundrig.io
  - [x] The Listening Room - https://thelr.io/
  - [x] Jukeboys
  - [x] So Litty Records
  - [x] Arp Radio - https://arpradio.media 

### Implementation Plan

- [x] Consensus of companies building music-related Cardano projects to develop a mutually beneficial metadata vocabulary.

## Copyright

This CIP is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)
