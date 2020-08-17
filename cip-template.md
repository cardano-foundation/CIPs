---
CIP: <CIP number, or "?" before being assigned>  
Title: <CIP title; maximum 44 characters>  
Authors: <list of authors' real names and email address>  
Discussions-To: <URL or email address>  
Comments-Summary: <summary tone>  
Comments-URI: <links to wiki page for comments>  
Status: <Draft | Proposed | On Hold | Rejected | Active | Obsolete>  
Type: <Standards Track | Informational | Process>  
Created: <date created on, in ISO 8601 (yyyy-mm-dd) format>  
* License: <abbreviation for approved license(s)>  
* License-Code: <abbreviation for code under different approved license(s)>  
* Post-History: <dates of postings to Cardano Dev Forum, or link to thread>  
* Requires: <CIP number(s)>  
* Replaces: <CIP number>  
Superseded-By: <CIP number>
---
This is the suggested template for new CIPs.
  
Note that a CIP number will be assigned by an editor. When opening a pull request to submit your CIP, please use an abbreviated title in the filename, cip-johndoe-banktheunbanked.md.

The title should be 44 characters or less.

## Preamble

RFC 822 style headers containing metadata about the CIP, including the CIP number, a short descriptive title (limited to a maximum of 44 characters), the names, and optionally the contact info for each author, etc.

## Simple Summary

If you can't explain it simply, you don't understand it well enough." Provide a simplified and layman-accessible explanation of the CIP.

## Abstract

A short (~200 word) description of the technical issue being addressed.

## Motivation

The motivation is critical for CIPs that want to change the Cardano protocol. It should clearly explain why the existing protocol specification is inadequate to address the problem that the CIP solves. CIP submissions without sufficient motivation may be rejected outright.

## Specification

The technical specification should describe the syntax and semantics of any new feature. The specification should be detailed enough to allow competing, interoperable implementations.

## Rationale

The rationale fleshes out the specification by describing what motivated the design and why particular design decisions were made. It should describe alternate designs that were considered and related work, e.g. how the feature is supported in other languages. The rationale may also provide evidence of consensus within the community, and should discuss important objections or concerns raised during the discussion.

  

## Backward Compatibility

All CIPs that introduce backward incompatibilities must include a section describing these incompatibilities and their severity. The GIP must explain how the author proposes to deal with these incompatibilities. GIP submissions without a sufficient backward compatibility treatise may be rejected outright.

## Test Cases

Test cases for implementation are mandatory for CIPs that are affecting consensus changes. Other CIPs can choose to include links to test cases if applicable.

## Implementations

The implementations must be completed before any CIP is given status “Active”, but it need not be completed before the CIP is accepted. While there is merit to the approach of reaching consensus on the specification and rationale before writing code, the principle of “rough consensus and running code” is still useful when it comes to resolving many discussions of API details.

## Copyright

  

This CIP is licensed under Apache-2.0
