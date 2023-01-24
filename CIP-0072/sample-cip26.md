### **Offchain Metadata Storage**

There are multiple options to store metadata offchain. The most common options are:
- IPFS
- CIP-26 

#### `CIP-26 Example`

CIP-26 offers a API that stores properties regarding a particular subject. This isn't directly JSON compliant as it would only support writing flat JSON objects into a CIP-26 server. Although we can make use of encoding mechanisms to store nested JSON properties in a CIP-26 server.

The following example shows how we can store a JSON object into CIP-26. The nested JSON object is encoded into a string and stored into CIP-26 in a single property.

Even though CIP-26 does not support nested JSON objects and hierarchies, we can still store them by encoding them into a string. Giving us the ability to take advantage of it's versioning, historical data, auditability and signature attestations at the property level.

Sample JSON 
```json
  {
  	"subject": "9SYAJPNN",
  	"projectName": "My Project",
  	"link": "https://myProject.app",
  	"twitter": "https://twitter.com/MyProject",
  	"category": "GAMING",
  	"subCategory": "RPG",
  	"description": {
  		"short": "A story rich game where choices matter"
  	},

  	"releases": [{
  		"releaseNumber": 1,
  		"releaseName": "V1",
  		"auditId": "z5L90f",
  		"scripts": [{
  			"id": "PmNd6w",
  			"version": 1
  		}]
  	}],
  	"scripts": [{
  		"id": "PmNd6w",
  		"name": "Marketplace",
  		"purpose": "SPEND",
  		"type": "PLUTUS",
  		"versions": [{
  			"version": 1,
  			"plutusVersion": 1,
  			"fullScriptHash": "711dcb4e80d7cd0ed384da5375661cb1e074e7feebd73eea236cd68192",
  			"scriptHash": "1dcb4e80d7cd0ed384da5375661cb1e074e7feebd73eea236cd68192",
  			"contractAddress": "addr1wywukn5q6lxsa5uymffh2esuk8s8fel7a0tna63rdntgrysv0f3ms"
  		}],
  		"audits": [{
  			"auditId": "z5L90f",
  			"auditor": "Canonical LLC.",
  			"auditLink": "https://github.com/somlinkToAessment",
  			"auditType": "MANUAL",
  			"signature": "0x1234567890abcdef",
  			"publicKey": "0x1234567890abcdef"
  		}]
  	}]
  }
```

