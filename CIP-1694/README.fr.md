---
CIP: 1694
Source: https://github.com/cardano-foundation/CIPs/blob/master/CIP-1694/README.md
Title: Un premier pas vers une gouvernance décentralisée on-chain
Revision: 5a2fc66
Translators:
    - Mike Hornan <mike.hornan@able-pool.io>
    - Alexandre Lafleur <alexandre.lafleur@able-pool.io>
Language: fr
---

## Résumé

Nous proposons une révision du système de gouvernance on-chain de Cardano pour répondre aux nouvelles exigences de Voltaire.
La prise en charge de gouvernance spécialisée existante pour les mises à jour des paramètres de protocole et les certificats MIR sera supprimée,
et deux nouveaux champs seront ajoutés aux corps de transaction normaux pour:

1. Actions de gouvernance
2. Votes

**Tout utilisateur Cardano** sera autorisé à soumettre une **action de gouvernance**.
Nous introduisons également trois organes de gouvernance distincts qui ont des fonctions spécifiques dans ce nouveau cadre de gouvernance :

1. Un comité constitutionnel
2. un groupe de représentants délégués (ci-après dénommé **DReps**)
3. les opérateurs de pool de participation (ci-après appelés **SPO**)

Chaque mesure de gouvernance doit être ratifiée par au moins deux de ces trois organes de gouvernance en utilisant leurs **votes** en chaîne.
Le type d’action et l’état du système de gouvernance déterminent quels organes doivent le ratifier.

Les actions ratifiées sont ensuite **promulguées** sur la chaîne, suivant un ensemble de règles bien définies.

Comme pour les pools de participations, tout détenteur d’Ada peut s’inscrire pour être un DRep et donc choisir de
se représenter soi-même et/ou représenter les autres. En outre, comme pour les pools de participations, les détenteurs d’Ada peuvent, à la place, déléguer leur
droits de vote à tout autre DRep.
Les droits de vote seront basés sur l’Ada totale qui est déléguée, comme un nombre entier de Lovelace.

L’aspect le plus crucial de cette proposition est donc la notion de **«un Lovelace = une voix»**.

Pour les nombreux contributeurs à cette proposition, voir [Remerciements](#remerciements).
## Motivation : pourquoi ce CIP est-il nécessaire ?

+ [Objectif](#objectif)
+ [Conception actuelle](#conception-actuelle-du-mécanisme-de-gouvernance)
+ [Lacunes de la conception de la gouvernance Shelley](#lacunes-de-la-conception-de-la-gouvernance-shelley)
+ [Hors champ d’application](#hors-champ-dapplication)

### Objectif

Nous entrons dans l’ère de Voltaire, jetant les bases d’une prise de décision décentralisée.
Ce CIP décrit un mécanisme de gouvernance on-chain qui sous-tendra la phase Voltaire de Cardano.
Le CIP s’appuie sur le schéma de gouvernance Cardano original qui reposait sur un nombre fixe de clés de gouvernance et l’étend.
Il vise à fournir une **première étape** qui est à la fois précieuse et, surtout, techniquement réalisable
à **court terme** dans le cadre du système de gouvernance Voltaire proposé.

Il vise également à servir de point de départ pour la participation continue de la communauté,
y compris sur les paramètres de seuil appropriés et d’autres paramètres on-chain.

Les propositions subséquentes pourraient adapter et élargir cette proposition pour répondre aux nouveaux besoins en matière de gouvernance.

### Conception actuelle du mécanisme de gouvernance

Le mécanisme de gouvernance Cardano en chaîne qui a été introduit à l’ère du grand livre Shelley est capable de:

1. Modifier les valeurs des paramètres du protocole (y compris lancer des « hard forks »)
2. transférer Ada hors des réserves et du trésor (et également déplacer Ada entre les réserves et le trésor)

Dans le schéma actuel, les mesures de gouvernance sont initiées par des transactions spéciales qui nécessitent des autorisations de  `Quorum-Many`
à partir des clés de gouvernance (5 sur 7 sur le réseau principal Cardano)[^1].
Les champs de l’organisme de transaction fournissent des détails sur la mesure de gouvernance proposée :
soit i) les changements de paramètres du protocole; ou ii) initier des transferts de fonds.
Chaque transaction peut déclencher les deux types d’actions de gouvernance, et une seule action peut avoir plus d’un effet (par exemple, la modification de deux paramètres de protocole ou plus).

- Les mises à jour des paramètres de protocole utilisent le [champ de transaction nº6](https://github.com/input-output-hk/cardano-ledger/blob/8884d921c8c3c6e216a659fca46caf729282058b/eras/babbage/test-suite/cddl-files/babbage.cddl#L56) du corps de la transaction.
- Les mouvements de la trésorerie et des réserves utilisent [Déplacer les certificats de récompenses instantanées(abrégé MIR)](https://github.com/input-output-hk/cardano-ledger/blob/8884d921c8c3c6e216a659fca46caf729282058b/eras/babbage/test-suite/cddl-files/babbage.cddl#L180).

Les mesures de gouvernance dûment autorisées sont appliquées à une limite d’époque (elles sont **adoptées**).

#### Hard Forks

L’un des paramètres du protocole est suffisamment important pour mériter une attention particulière :
La modification de la version majeure du protocole permet à Cardano d’adopter des hard forks contrôlés.
Ce type de mise à jour des paramètres de protocole a donc un statut particulier, puisque les pools de mise
doivent mettre à niveau leurs nœuds afin de pouvoir prendre en charge la nouvelle version du protocole une fois le hard fork adopté.

### Lacunes de la conception de la gouvernance Shelley

La conception de la gouvernance Shelley visait à fournir une approche simple et transitoire de la gouvernance.
La présente proposition vise à remédier à un certain nombre de lacunes de cette conception.
qui sont apparents lorsque nous entrons dans Voltaire.

1. La conception de la gouvernance Shelley ne laisse aucune place à la participation active des détenteurs d’Ada sur la chaîne.
Bien que les modifications apportées au protocole soient généralement le résultat de discussions avec des acteurs communautaires sélectionnés,
Le processus est actuellement mené principalement par les entités fondatrices.
S’assurer que tout le monde peut exprimer ses préoccupations est fastidieux et peut parfois être perçu comme arbitraire.

2. Les mouvements du Trésor constituent un sujet critique et sensible.
Cependant, ils peuvent être difficiles à suivre. Il est important d’avoir plus de transparence
et plus de couches de contrôle sur ces mouvements.

3. Bien qu’ils doivent être traités spécialement par les SPO, les hard forks ne sont pas différenciés des autres changements de paramètres de protocole.

4. Enfin, bien qu’il existe actuellement une vision quelque peu commune pour _Cardano_ qui est partagée par ses entités fondatrices ainsi que par de nombreux membres de la communauté,
Il n’y a pas de document clairement défini où ces principes directeurs sont consignés.
Il est logique de tirer parti de la blockchain Cardano pour enregistrer la philosophie Cardano partagée de manière immuable, en tant que constitution Cardano formelle.

### Hors champ d’application

Les sujets suivants sont considérés comme ne relevant pas de la portée de ce CIP.

#### Le contenu de la constitution

Ce CIP se concentre uniquement sur les mécanismes en chaîne. Les dispositions de la constitution initiale sont extrêmement importantes, de même que tous les processus qui
permettra de le modifier. Ceux-ci méritent leur propre discussion séparée et ciblée.

#### La composition du comité constitutionnel

Il s’agit d’un problème hors chaîne.

#### Questions juridiques

Toute application légale potentielle du protocole Cardano ou de la Constitution Cardano est complètement hors de portée de ce CIP.


#### Normes hors chaîne pour les actions de gouvernance

La communauté Cardano doit réfléchir profondément aux normes et processus appropriés pour gérer la création des actions de gouvernance spécifiées dans ce CIP.
En particulier, le rôle du projet Catalyst dans la création d’actions de retrait de trésorerie est complètement en dehors du champ d’application de ce CIP.


#### Ada holdings et délégation

Comment les entreprises privées, les institutions publiques ou privées, les particuliers, etc. choisir de détenir ou de déléguer leur Ada, y compris la délégation aux pools de participation ou DReps, n’entre pas dans le champ d’application de ce CIP.

## Spécification

+ [La Constitution Cardano](#la-constitution-cardano)
+ [Le comité constitutionnel](#le-comité-constitutionnel)
  - [État de non-confiance](#état-de-non-confiance)
  - [Clés du comité constitutionnel](#clés-du-comité-constitutionnel)
  - [Remplacement du comité constitutionnel](#remplacement-du-comité-constitutionnel)
  - [Taille du comité constitutionnel](#taille-du-comité-constitutionnel)
  - [Mandat](#mandat)
  - [Script de rambardes](#script-de-rambardes)
+ [Représentants délégués (DReps)](#représentants-délégués-dreps)
  - [Options de vote prédéfinies](#options-de-vote-prédéfinies)
  - [DReps enregistrés](#dreps-enregistrés)
  - [Nouvelle distribution de la mise pour DReps](#nouvelle-distribution-de-la-mise-pour-dreps)
  - [Incitatifs pour les détenteurs d’Ada à déléguer une mise de vote](#incitatifs-pour-les-détenteurs-dada-à-déléguer-une-mise-de-vote)
  - [Incitatifs DRep](#incitatifs-drep)
+ [Actions de gouvernance](#actions-de-gouvernance)
  - [Ratification](#ratification)
    * [Exigences](#exigences)
    * [Restrictions](#restrictions)
  - [Promulgation](#promulgation)
  - [Cycle de vie](#cycle-de-vie)
  - [Contenu](#contenu)
  - [Groupes de paramètres de protocole](#groupes-de-paramètres-de-protocole)
+ [Votes](#votes)
  - [État de gouvernance](#état-de-gouvernance)
  - [Modifications apportées à l'instantané de mise](#modifications-apportées-à-linstantané-de-mise)
  - [Définitions relatives à la participation de vote](#définitions-relatives-à-la-participation-de-vote)

### La Constitution Cardano

La Constitution de Cardano est un document texte qui définit les valeurs communes et les principes directeurs de Cardano.
À ce stade, la Constitution est un document d’information qui capture sans ambiguïté les valeurs fondamentales de Cardano
et agit pour assurer sa viabilité à long terme.
À un stade ultérieur, nous pouvons imaginer que la Constitution évolue peut-être vers un ensemble de règles basées sur des contrats intelligents qui régissent l’ensemble du cadre de gouvernance.
Pour l’instant, cependant, la Constitution restera un document hors chaîne dont la valeur de condensation de hachage sera enregistrée sur la chaîne.
Comme nous l’avons vu plus haut, la Constitution n’est pas encore définie et son contenu n’entre pas dans le champ d’application de ce CIP.

<!--------------------------- Comité constitutionnel ------------------------>

### Le comité constitutionnel

Nous définissons un _comité constitutionnel_ qui représente un ensemble d’individus ou d’entités
(chacun associé à un identifiant Ed25519 ou un identifiant de script natif ou Plutus) qui sont collectivement responsables de **veiller à ce que la Constitution soit respectée**.

Bien qu’il **ne puisse pas être appliqué en chaîne**, le comité constitutionnel est **seulement** censé voter
sur la constitutionnalité des actions de gouvernance (qui devraient ainsi assurer la viabilité à long terme de la blockchain) et devraient être remplacées
(via l’action **non-confiance**) s’ils dépassent cette limite.
Autrement dit, il existe un contrat social entre le comité constitutionnel et les acteurs du réseau.
Bien que le comité constitutionnel puisse rejeter certaines actions de gouvernance (en votant « non »),
ils ne devraient le faire que lorsque ces mesures de gouvernance sont contraires à la Constitution.

Par exemple, si nous considérons la règle hypothétique de la Constitution « Le réseau Cardano doit toujours être capable de produire de nouveaux blocs »,
Ensuite, une mesure de gouvernance qui réduirait la taille maximale du bloc à `0` serait, en fait,
inconstitutionnelle et pourrait donc ne pas être ratifiée par le Comité constitutionnel. La règle
Cependant, ne pas spécifier la plus petite taille maximale acceptable de bloc, de sorte que le Comité constitutionnel devrait déterminer ce nombre
et votez en conséquence.

#### État de non-confiance

Le comité constitutionnel est considéré comme se trouvant à tout moment dans l’un des deux États suivants:

1. un état normal (c’est-à-dire un état de confiance)
2. un état de non-confiance

Dans un _état de non-confiance_, le comité actuel n’est plus en mesure de participer aux mesures de gouvernance
et doivent être remplacés avant que toute mesure de gouvernance puisse être ratifiée (voir ci-dessous).

#### Clés du comité constitutionnel

Le comité constitutionnel utilisera une configuration de clé chaude et froide, similaire au mécanisme existant de « certificat de délégation genesis ».

#### Remplacement du comité constitutionnel

Le comité constitutionnel peut être remplacé via une action de gouvernance spécifique
("Mise à jour du comité", décrit ci-dessous) qui requiert l'approbation à la fois
des **SPOs** et des **DReps**
Le seuil de ratification peut être différent dépendamment de si la gouvernance est
dans un état normal ou dans un état de non-confiance.

Le nouveau comité constitutionnel pourrait, en principe, être identique ou partiellement chevaucher le comité sortant tant que l’action est dûment ratifiée.
Cela pourrait se produire, par exemple, si les électeurs ont une confiance collective dans tout ou une partie du comité et souhaitent prolonger son mandat.


#### Taille du comité constitutionnel

Contrairement à la conception de la gouvernance Shelley, la taille du comité constitutionnel n’est pas fixe et peut être n’importe quel nombre non négatif.
Il peut être modifié chaque fois qu’un nouveau comité est élu (« Mise à jour du comité »).
De même, le seuil du comité (la fraction des votes `Yes` du comité qui sont nécessaires pour ratifier les mesures de gouvernance) n’est pas fixe et
peut également varier en fonction de la mesure de gouvernance.
Cela donne beaucoup de flexibilité à la composition du comité.
En particulier, il est possible d’élire un comité vide si la communauté souhaite supprimer entièrement le comité constitutionnel. Notez que cela est différent d’un état de non-confiance et constitue toujours un système de gouvernance capable de mettre en oeuvre des propositions.

Il y aura un nouveau paramètre du protocole pour la taille minimale du comité,
lui-même un nombre non négatif appelé `committeeMinSize`.

#### Mandat

Chaque comité constitutionnel nouvellement élu aura un mandat.
Les mandats par membre permettent un système de rotation, par exemple un tiers du comité
expirant chaque année.
Les membres expirés ne peuvent plus voter.
Le membre peut également volontairement démissionner plus tôt, ce qui sera marqué sur la chaîne comme un membre expiré.

Si le nombre de membres non expirés du comité tombe en dessous de la taille minimale
du comité, le comité constitutionnel ne pourra pas ratifier 
les actions de gouvernance. Cela signifie que seules les actions de gouvernance 
qui ne nécessitent pas le vote du comité constitutionnel peuvent toujours 
être ratifiées.

Par exemple, un comité de cinq membres avec un seuil de 60%, une taille minimale 
de trois et deux membres expirés peut toujours
adopter des mesures de gouvernance si deux membres non expirés votent `Yes`.
Cependant, si un autre membre expire alors le comité constitutionnel devient
incapable de ratifier d’autres actions de gouvernance.

La durée maximale du mandat est un paramètre du protocole de gouvernance, spécifié en nombre d'époques.
Pendant un état de non-confiance, aucune action ne peut être ratifiée,
le comité devrait donc prévoir son propre remplacement s'il souhaite éviter les perturbations.

#### Script de rambardes

Bien que la constitution soit un document informel hors chaîne, il y aura
également un script facultatif qui pourra appliquer certaines directives. Ce scénario
agit pour compléter le comité constitutionnel en restreignant certains
types de propositions. Par exemple, si la communauté souhaite avoir des règles
strictes pour la trésorerie qui ne peuvent être violées, un script qui applique
ces règles peut être voté en tant que script de rambardes.

Le script de rambardes s'applique uniquement aux propositions de mise à jour des paramètres du protocole et 
de retrait de trésorerie.

<!---------------------------           DReps          -------------------------->

### Représentants délégués (DReps)

> **Warning**
> CIP-1694 DReps **ne doit pas être confondu** avec Project Catalyst DReps.

#### Options de vote prédéfinies

Afin de participer à la gouvernance, un justificatif d’identité de mise doit être délégué à un DRep.
Les détenteurs d’Ada délégueront généralement leurs droits de vote à un DRep enregistré
qui voteront en leur nom. De plus, deux options de vote prédéfinies sont disponibles :

* `Abstain`

  Si un détenteur d’Ada délègue à `Abstain`, alors sa mise est activement marquée
  comme ne participant pas à la gouvernance.

  L’effet de la délégation de `Abstain` sur la chaîne est que la participation déléguée *ne sera pas* considérée comme
  une partie de la participation active de vote. Toutefois, la participation *sera* considérée comme enregistrée pour
  l’objectif des incitations décrites dans [Incitations pour les détenteurs d’Ada à déléguer une mise de vote](#incitatifs-pour-les-détenteurs-dada-à-déléguer-une-mise-de-vote).

* `No Confidence`

  Si un détenteur d’Ada délègue à `No Confidence`, sa participation est comptée comme
  un vote `Yes` pour chaque action de `No Confidence` et un vote `No` pour toute autre action.
  La participation déléguée *sera* considérée comme faisant partie de la participation au vote actif.
  Il sert également de mesure directement vérifiable de la confiance des détenteurs d’Ada envers le comité
  constitutionel.


> **Note**
> Les options de vote prédéfinis ne votent pas à l'intérieur des transactions, leur comportement est pris en compte au niveau du protocole.
> L'option `Abstain` peut être choisi pour diverses raisons, y compris le désir de ne pas
> participer au système de gouvernance.

> **Note**
> Tout détenteur d'Ada peut s'inscrire en tant que DRep et se déléguer s'il souhaite participer activement à
> vote.

> **Note**
> Tout portefeuille servant de portefeuille de récompenses enregistré pour un pool de participation peut être délégué à l'une de ces options de vote prédéfinies et servira ainsi d'option de vote par défaut sélectionnée par le SPO pour tous les votes d'action de gouvernance, à l'exception des actions de gouvernance de hard fork. En raison de la nécessité d'un consensus robuste autour des initiations de hard fork, ces votes doivent être respectés en pourcentage de la participation détenue par tous les pools de participation.

#### DReps enregistrés

Dans Voltaire, les références de mise existantes seront
en mesure de déléguer leur participation à des DReps à des fins de vote,
en plus de la délégation actuelle aux pools de participation pour la production de blocs.
La délégation DRep imitera les mécanismes de délégation de mise existants (via des certificats on-chain).
De même, l’enregistrement des DReps imitera les mécanismes existants d’enregistrement des mise.
De plus, les DReps inscrits devront voter régulièrement pour être toujours considérés comme actifs.
Plus précisément, si un DRep ne soumet aucun vote pour `drepActivity` - plusieurs époques, le DRep est considéré comme inactif,
où `drepActivity` est un nouveau paramètre de protocole.
Les DReps inactifs ne comptent plus dans la participation active des votes, et peut redevenir actif durant un nombre 
`drepActivity` d'époques en votant sur n’importe quel actions de gouvernance ou en soumettant une de mise à jour du certificat de DRep.
La raison pour laquelle les DReps sont marqués comme inactifs est que les DReps qui cessent de participer mais qui ont encore
la mise qui leur est déléguée ne laisse finalement pas le système dans un état où aucune action de
gouvernance peut passer.

Les DReps enregistrés sont identifiés par un justificatif d’identité qui peut être :

* Une clé de vérification (Ed25519)
* Un script natif ou Plutus

Le condensé de hachage blake2b-224 d’une informations d’identification DRep sérialisées est appelé _DRep ID_.

Les nouveaux types de certificats suivants seront ajoutés pour les DReps :
les certificats d’inscription DRep, les certificats de retraite DRep, et
certificats de délégation de vote.

##### Certificats d’enregistrement DRep

Les certificats d’inscription DRep comprennent :

* un ID DRep
* un dépôt
* une ancre en option

Une **ancre** est une paire de :

* une URL vers une charge utile JSON de métadonnées
* un hachage du contenu de l’URL des métadonnées

La structure et le format de ces métadonnées sont délibérément laissés ouverts dans ce CIP.
Les règles on-chain ne vérifieront ni l’URL ni le hachage.
Les applications clientes doivent toutefois effectuer les vérifications d’intégrité habituelles lors de la récupération de contenu à partir de l’URL fournie.


##### Certificats de retraite DRep

Les certificats de retraite DRep comprennent :

* un ID DRep

Notez qu'un DRep est mis à la retraite dès que la chaîne accepte un certificat de retraite,
et le dépôt est restitué dans le cadre de la transaction qui soumet le certificat de retrait
(de la même manière que les dépôts d'enregistrement du justificatif de participation sont retournés).

##### Certificats de délégation de vote

Les certificats de délégation de vote comprennent :

* l’ID DRep auquel la participation doit être déléguée
* les informations d’identification de mise pour le délégant

> **Note**
>
> La délégation DRep mappe toujours un justificatif d'identité de mise à un justificatif d'identité DRep.
> Cela signifie qu'un DRep ne peut pas déléguer une mise de vote à un autre DRep.

##### Schémas d’autorisation de certificat

Le système d’autorisation (c’est-à-dire quelles signatures sont requises pour l’enregistrement, le retrait ou la délégation) imite le système existant d’autorisation de délégation de mise.

<!-- TODO: Fournir la spécification CBOR dans l’annexe pour ces nouveaux certificats. -->


#### Nouvelle distribution de la mise pour DReps

En plus de la distribution existante par délégation de mise et de la
distribution par pool de participation, le grand livre déterminera désormais également la distribution de la mise par DRep.
Cette répartition déterminera le montant de la mise par laquelle chaque vote d'un DRep
est soutenu.

> **Warning**
>
> **Contrairement à** la distribution utilisée pour la production de blocs, nous utiliserons toujours la plus
> récente version de la distribution de mise par DRep telle qu’elle est donnée sur la limite d’époque.
>
> Cela signifie que **pour tout sujet qui intéresse profondément les électeurs,
> ils ont le temps de déléguer à eux-mêmes comme DRep et de voter directement**.
> Cependant, cela signifie qu’il peut y avoir une différence entre la mise utilisé pour la production
> de bloc et la mise utilisée pour voter à une époque donnée.


#### Incitatifs pour les détenteurs d’Ada à déléguer une mise de vote

Il y aura une courte [phase d’amorçage] (#bootstrapping-phase) au cours de laquelle des récompenses seront gagnées
pour la délégation de mise, etc. et peut être retiré à tout moment.
Après cette phase, bien que des récompenses continueront d’être gagnées pour la délégation de blocs, etc., les comptes de récompense seront
**empêché de retirer des récompenses** à moins que leurs informations d’identification de mise associées ne soient également déléguées à un DRep ou à une option de vote prédéfinie.
Cela contribue à assurer une participation élevée et, par conséquent, une légitimité.

> **Note**
>
> Même si les récompenses ne peuvent pas être retirées, elles ne sont pas perdues. Dès qu’un justificatif de mise est délégué
> (y compris à une option de vote prédéfinie), les récompenses peuvent être retirées.

#### Incitatifs DRep

Les DReps ont sans doute besoin d’être rémunérés pour leur travail. La recherche sur les modèles incitatifs est toujours en cours,
et nous ne souhaitons pas retarder la mise en oeuvre de ce CIP pendant que ce problème est résolu.

Notre proposition provisoire est donc l'entiercement de Lovelace de la trésorerie Cardano existante jusqu’à ce
qu'une décision extrêmement importante peut être convenue par la communauté, à travers le mécanisme de gouvernance en chaîne
en cours d’élaboration.

Alternativement, les DReps pourraient se payer par le biais d’instances de l’action de gouvernance « retrait du Trésor ».
Une telle action serait vérifiable sur la chaîne et devrait refléter un accord hors chaîne entre DReps et les délégants.

<!---------------------------           DReps          ------------------------>
<!--------------------------- Mesures de gouvernance -------------------------->

### Actions de gouvernance

Nous définissons sept types différents d'**actions de gouvernance**.
Une action de gouvernance est un événement en chaîne qui est déclenché par une transaction et a une date limite après lequel il ne peut être promulgué.

- Une action est dite **ratifiée** lorsqu’elle recueille suffisamment de votes en sa faveur (grâce aux règles et paramètres détaillés ci-dessous).
- Une action qui ne parvient pas à être ratifiée avant sa date limite est dite **expirée**.
- Une action qui a été ratifiée est dite **promulguée** une fois qu’elle a été activée sur le réseau.


| Action                                                | Description                                                                                                                                                   |
| :-----------------------------------------------------| :-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1. Motion de censure                                  | Une motion pour créer un _état de non-confiance_ au sein du comité constitutionnel actuel                                                                     |
| 2. Nouveau comité constitutionnel et/ou nouveau seuil | Modification des membres du comité constitutionnel et/ou de son seuil de signature et/ou limites de mandat                                                    |
| 3. Mises à jour de la Constitution                    | Une modification de la Constitution off-chain, enregistrée en tant que hachage on-chain du document texte                                                     |
| 4. Hard-Fork[^2] Initiation                           | Déclenche une mise à niveau non rétrocompatible du réseau ; Nécessite une mise à niveau logicielle préalable                                                  |
| 5. Modifications des paramètres du protocole          | Tout changement **d’un ou de plus** paramètres de protocole pouvant être mis à jour, excluant les changements aux versions majeures du protocole (hard forks) |
| 6. Retraits de trésorerie                             | Retraits de la trésorerie                                                                                                                                     |
| 7. Infos                                              | Action qui n’a aucun effet sur la chaîne, autre qu’un enregistrement sur la chaîne.                                                                           |

**Tout détenteur d’Ada** peut soumettre une action de gouvernance à la chaîne.
Ils doivent fournir un dépôt de `govActionDeposit` Lovelace, qui sera retourné lorsque l’action sera finalisée
(s’il est **ratifié** ou **a expiré**).
Le montant du dépôt sera ajouté au _pot de dépôt_, similaire aux dépôts clés de mise.
Il sera également pris en compte dans la mise de l’adresse de récompense à laquelle il sera remboursé, afin de ne pas réduire le pouvoir de vote du déposant pour voter sur ses propres actions (et concurrentes).

Si un script de rambardes est présente, la transaction doit inclure ce
script dans le témoin soit directement, soit via des entrées de référence,
et toutes les autres exigences imposées par le script de rambardes doivent être
satisfaites.

Notez qu’une motion de non-confiance est une mesure extrême qui permet aux détenteurs d’Ada de révoquer le pouvoir
qui a été accordé à l’actuel Comité constitutionnel.

> **Note**
> Une **seule** action de gouvernance peut contenir **plusieurs** mises à jour des paramètres de protocole. De nombreux paramètres sont interconnectés et peuvent nécessiter d'être déplacés en synchronisme.

#### Ratification

Les mesures de gouvernance sont **ratifiées** par le biais d’actions de vote en chaîne.
Différents types d'action de gouvernance ont des exigences de ratification différentes, mais impliquent toujours **deux des trois** organes de gouvernance,
à l’exception d’une initiative de hard fork et paramètres de protocole liés à la sécurité, qui nécessite la ratification de tous les organes de gouvernance.
Selon le type d’action de gouvernance, une action sera donc ratifiée lorsqu’une combinaison des éléments suivants se produit :

* le comité constitutionnel approuve l’action (le nombre de membres qui votent `Yes` atteint le seuil du comité constitutionnel)
* les DReps approuvent l’action (la participation contrôlée par les DReps qui votent `Yes` atteint un certain seuil de la mise totale active des votes)
* les SPO approuvent l'action (la participation contrôlée par les SPO qui votent « Oui » atteint un certain seuil de la participation totale de vote active, à l'exception des actions de gouvernance Hard Fork)

> **Warning**
> Comme expliqué ci-dessus, différentes distributions de mise s’appliquent aux DReps et aux SPO.

Une motion de non-confiance réussie, la mise à jour du comité constitutionnel,
un changement constitutionnel, ou un hard fork, retarde
la ratification de toutes les autres mesures de gouvernance jusqu’à la première époque suivant leur promulgation. Cela donne
à un comité constitutionnel mis à jour suffisamment de temps pour voter sur les propositions actuelles, réévaluer les propositions existantes
à l’égard d’une nouvelle constitution, et veille à ce que les changements sémantiques arbitraires de principe entraîné
en adoptant un hard-fork n’ont pas de conséquences imprévues en combinaison avec d’autres actions.

##### Exigences

Le tableau suivant détaille les exigences de ratification pour chaque scénario d’action de gouvernance. Les colonnes représentent :

* **Type d’action de gouvernance**<br/>
 Type de mesure de gouvernance. Notez que les mises à jour des paramètres de protocole sont regroupées en quatre catégories.

* **Comité constitutionnel (abréviation CC)**<br/>
 Une valeur de ✓ indique que le comité constitutionnel doit approuver cette action.<br/>
 Une valeur de - signifie que les votes du comité constitutionnel ne s’appliquent pas.

* **DReps**<br/>
 Le seuil de vote DRep qui doit être atteint en pourcentage de la *participation de vote active*.

* **SPO**<br/>
 Le seuil de vote SPO doit être atteint en tant que certain seuil de la participation totale active au vote, à l'exception des actions de gouvernance Hard Fork. En raison de la nécessité d'un consensus solide autour des initiations Hard Fork, ces votes doivent être atteints en tant que pourcentage de la participation détenue par tous les pools de participation.<br/>
 Une valeur de - signifie que les votes SPO ne s’appliquent pas.

| Type d’action de gouvernance                                                    | CC  | DReps    | SPOs     |
|:--------------------------------------------------------------------------------|:----|:---------|:---------|
| 1. Motion de non-confiance                                                      | \-  | $P_1$    | $Q_1$    |
| 2<sub>a</sub>. Mise à jour du comité/seuil (_état normal_)                      | \-  | $P_{2a}$ | $Q_{2b}$ |
| 2<sub>b</sub>. Mise à jour du comité/seuil (_état de non-confiance_)            | \-  | $P_{2b}$ | $Q_{2b}$ |
| 3. Nouvelle Constitution ou script de rambardes                                 | ✓   | $P_3$    | \-       |
| 4. Initiation du hard fork                                                      | ✓   | $P_4$    | $Q_4$    |
| 5<sub>a</sub>. Modifications des paramètres de protocole, groupe réseau         | ✓   | $P_{5a}$ | \-       |
| 5<sub>b</sub>. Modifications des paramètres du protocole, groupe économique     | ✓   | $P_{5b}$ | \-       |
| 5<sub>c</sub>. Modifications des paramètres de protocole, groupe technique      | ✓   | $P_{5c}$ | \-       |
| 5<sub>d</sub>. Modifications des paramètres de protocole, groupe de gouvernance | ✓   | $P_{5d}$ | \-       |
| 6. Retrait du Trésor                                                            | ✓   | $P_6$    | \-       |
| 7. Infos                                                                        | ✓   | $100$    | $100$    |

Chacun de ces seuils est un paramètre de gouvernance. Il y a un 
seuil supplémentaire, « Q5 », lié aux paramètres de protocole pertinents pour la sécurité, 
qui est expliqué ci-dessous.
Les seuils initiaux devraient être choisis par la communauté Cardano dans son ensemble.
Tous les seuils de l'action Info sont définis à 100 % car le fixer plus bas
entraînerait l'impossibilité de sonder au-dessus du seuil.

Certains paramètres sont pertinents pour les propriétés de sécurité du système. Toute
proposition tentant de modifier un tel paramètre nécessite un vote supplémentaire 
des SPOs, avec le seuil `Q5`.

Les paramètres de protocole pertinents pour la sécurité sont :
* `maxBlockBodySize`
* `maxTxSize`
* `maxBlockHeaderSize`
* `maxValueSize`
* `maxBlockExecutionUnits`
* `txFeePerByte`
* `txFeeFixed`
* `utxoCostPerByte`
* `govActionDeposit`
* `minFeeRefScriptCostPerByte`

> **Note**
> Il peut être logique que certains ou tous les seuils s’adaptent en ce qui concerne le Lovelace qui est activement inscrit pour voter.
> Par exemple, un seuil pourrait varier entre 51 % pour un niveau élevé d’enregistrement et 75 % pour un niveau d’enregistrement faible.
> En outre, le seuil de trésorerie pourrait également être adaptatif, en fonction du Lovelace total qui est retiré,
> ou différents seuils pourraient être fixés pour différents niveaux de retrait.

> **Note**
> Pour atteindre la légitimité, le seuil minimum acceptable ne devrait pas être inférieur à 50% de la mise déléguée.


##### Restrictions

Outre _Retrait du trésor_ et _Infos_, nous incluons un mécanisme pour assurer que les actions de gouvernance
du même type ne se heurtent pas accidentellement de manière inattendue.

Chaque action de gouvernance doit inclure l’ID de l’action de gouvernance de l’action la plus récente adoptée de son type donné.
Cela signifie que deux actions du même type peuvent être promulguées en même temps,
Mais ils doivent être *délibérément* conçus pour le faire.


#### Promulgation

Les actions qui ont été ratifiées à l’époque actuelle sont classées par ordre de priorité comme suit pour la promulgation :

1. Motion de non-confiance
2. Mise à jour du comité/seuil
3. Nouvelle Constitution ou script de rambardes
4. Initiation du hard fork
5. Modifications des paramètres du protocole
6. Retraits du Trésor
7. Infos

> **Note** La promulgation des actions _Info_ est une action nulle, car elles n’ont aucun effet sur le protocole.

##### Ordre de promulgation

Les actions de gouvernance sont mises en oeuvre par ordre d’acceptation dans la chaîne.
Cela résout les conflits où, par exemple, il y a deux changements de paramètres concurrents.

#### Cycle de vie

Les actions de gouvernance ne sont vérifiées pour ratification que sur une limite d’époque.
Une fois ratifiée, des actions sont organisées en vue de leur promulgation.

Toutes les actions de gouvernance soumises seront donc soit :

1. **ratifié**, puis **promulgué**
2. ou **expirée** après un certain nombre d’époques

Dans tous ces cas, les dépôts sont retournés immédiatement.

Toutes les actions de gouvernance sont adoptées à la frontière de l'époque après leur ratification.

#### Contenu

Chaque mesure de gouvernance comprendra les éléments suivants :

* un montant de dépôt (enregistré puisque le montant du dépôt est un paramètre de protocole pouvant être mis à jour)
* une adresse de récompense pour recevoir le dépôt lorsqu’il est remboursé
* une ancre pour toutes les métadonnées nécessaires pour justifier l’action
* une valeur de condensé de hachage pour éviter les collisions avec des actions concurrentes du même type (comme décrit précédemment)

<!-- TODO: Fournir une spécification CBOR dans l’annexe pour ces nouvelles entités sur la chaîne -->

De plus, chaque action comprendra certains éléments spécifiques à son type :

| Type d’action de gouvernance                                  | Données supplémentaires                                                                                                                            |
|:--------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------|
| 1. Motion de non-confiance                                    | Aucune                                                                                                                                             |
| 2. Mise à jour du comité/seuil                                | L’ensemble des résumés de hachage de clé de vérification (membres à supprimer), une carte des résumés de hachage de clé de vérification aux numéros d'époque (nouveaux membres et leur limite de mandat) et une fraction (nouveau seuil)                                                                                                                               |
| 3. Nouvelle Constitution ou script de rambardes               | Un condensé de hachage du document constitutionnel                                                                                                 |
| 4. Initiation du hard fork                                    | La nouvelle version majeure du protocole                                                                                                           |
| 5. Modifications des paramètres du protocole                  | Les paramètres modifiés                                                                                                                            |
| 6. Retrait du Trésor                                          | Une carte d’identification de mise à un nombre positif de Lovelace                                                                                 |
| 7. Infos                                                      | Aucune                                                                                                                                             |

> **Note**
> La nouvelle version majeure du protocole doit être précisément supérieure d’une à la version actuelle du protocole.
> Deux époques consécutives quelconques auront donc soit la même version de protocole majeure, soit le
> plus tard, on aura une version de protocole majeure qui est une plus grande.

> **Note**
> Il ne peut y avoir de doublons entre les membres d’un comité - chaque paire de clé de références dans un comité doit être unique.

Chaque action de gouvernance acceptée sur la chaîne se verra attribuer un identifiant unique (alias l'**ID de l’action de gouvernance**),
composé du hachage de transaction qui l’a créé et de l’index dans le corps de la transaction qui pointe vers lui.

#### Groupes de paramètres de protocole

Nous avons regroupé les changements de paramètres de protocole par type,
permettant de fixer différents seuils pour chaque groupe.

Toutefois, nous ne limitons pas chaque action de gouvernance des paramètres de protocole à un seul groupe.
Dans le cas où une action de gouvernance contient des mises à jour pour plusieurs paramètres de différents groupes,
le seuil maximal de tous les groupes concernés s’appliquera à toute mesure de gouvernance donnée.

Les groupes de paramètres _réseaux_, _économique_ et _technique_ collectent les paramètres de protocole existants qui ont été introduits pendant les ères Shelley, Alonzo et Babbage.
De plus, nous introduisons un nouveau groupe _gouvernance_ qui est spécifique aux nouveaux paramètres de gouvernance qui seront introduits par le CIP-1694.

Le **groupe de réseaux** se compose de :
* taille maximale du corps du bloc (`maxBlockBodySize`)
* taille maximale de la transaction (`maxTxSize`)
* taille maximale de l’en-tête de bloc (`maxBlockHeaderSize`)
* taille maximale d’une valeur de ressource sérialisée (`maxValueSize`)
* nombre maximal d’unités d’exécution de script dans une seule transaction (`maxTxExecutionUnits`)
* nombre maximal d’unités d’exécution de script dans un seul bloc (`maxBlockExecutionUnits`)
* nombre maximal d’entrées collatérales (`maxCollateralInputs`)

Le **groupe économique** comprend :
* coefficient de redevance minimal (`txFeePerByte`)
* constante de frais minimum (`txFeeFixed`)
* clé de délégation Lovelace dépôt (`stakeAddressDeposit`)
* inscription à la piscine Dépôt Lovelace (`stakePoolDeposit`)
* expansion monétaire (`monetaryExpansion`)
* expansion de la trésorerie (`treasuryCut`)
* réduction des primes fixes minimales pour les pools (`minPoolCost`)
* dépôt minimum de Lovelace par octet d’UTxO sérialisé (`utxoCostPerByte`)
* prix des unités d’exécution de Plutus (`executionUnitPrices`)

Le **groupe technique** est composé de :
* l'influence du pool pledge (`poolPledgeInfluence`)
* époque maximale du retrait du pool (`poolRetireMaxEpoch`)
* nombre souhaité de pools (`stakePoolTargetNum`)
* modèles de coûts d’exécution de Plutus (`costModels`)
* proportion de collatéral nécessaire pour les scripts (`collateralPercentage`)

Le **groupe de gouvernance** comprend tous les nouveaux paramètres de protocole introduits dans ce CIP :
* seuils de vote de gouvernance ($P_1$, $P_{2a}$, $P_{2b}$, $P_3$, $P_4$, $P_{5a}$, $P_{5b}$, $P_{5c}$, $P_{5d}$, $P_6$, $Q_1$, $Q_{2a}$, $Q_{2b}$, $Q_4$, $Q_5$)
* durée de vie maximale de l'action de gouvernance en époques (`govActionLifetime`)
* dépôt d'action de gouvernance (`govActionDeposit`)
* montant du dépôt DRep (`dRepDeposit`)
* période d’activité DRep en époques (`dRepActivity`)
* taille minimale du comité constitutionnel (`committeeMinSize`)
* durée maximale du mandat (en époques) des membres du comité constitutionnel (`committeeMaxTermLength`)

<!-- À faire :
 - Décider des valeurs initiales des nouveaux paramètres de gouvernance
 
 - Décider des conditions de cohérence des seuils de vote.
 Par exemple, le seuil d’une motion de censure devrait sans doute être plus élevé que celui d’un retrait mineur du Trésor.
-->

<!--------------------------- Actions de Gouvernance -------------------------->

<!---------------------------          Votes           ------------------------>

### Votes

Chaque transaction de vote comprend les éléments suivants :

* un ID d’action de gouvernance
* un rôle - membre du comité constitutionnel, DRep ou SPO
* un témoin d’informations d’identification de gouvernance pour le rôle
* une ancre en option (tel que défini ci-dessus) pour les renseignements pertinents au vote;
* un vote 'Oui'/'Non'/'Abstention'

Pour les SPO et les DReps, le nombre de votes exprimés (que ce soit 'Oui', 'Non' ou 'Abstention') est proportionnel au Lovelace qui leur est déléguée au moment où
l’action est vérifiée pour ratification. Pour les membres du comité constitutionnel, chaque membre actuel du comité dispose d’un vote.

> **Warning** Les votes 'Abstention' ne sont pas inclus dans la « participation active ».
>
> Notez qu’un vote explicite pour s’abstenir diffère de l’abstention de voter.
> La mise non enregistré qui n’a pas voté se comporte comme un vote 'Abstention',
> alors que la mise enregistré qui n’a pas voté se comporte comme un vote 'non'.
> Pour éviter toute confusion, nous n’utiliserons le mot 'Abstention' qu’à partir de maintenant pour signifier un vote en chaîne pour s’abstenir.

Le témoin d’informations d’identification de gouvernance déclenchera les vérifications appropriées dans le registre conformément à la règle de registre « UTxOW » existante
(c’est-à-dire une vérification de signature pour les clés de vérification, et une exécution de validateur avec un rédempteur de vote spécifique et un nouvel objectif de script Plutus pour les scripts).

Les votes peuvent être exprimés plusieurs fois pour chaque action de gouvernance par un seul témoin d’informations d’identification.
Les votes correctement soumis remplacent tous les votes plus anciens pour les mêmes informations d’identification et le même rôle.
C’est-à-dire que l’électeur peut changer sa position sur n’importe quelle action s’il le souhaite.
Dès qu’une mesure de gouvernance est ratifiée, le vote prend fin et les transactions contenant d’autres votes sont invalides.

#### État de gouvernance

Lorsqu’une action de gouvernance est soumise avec succès à la chaîne, sa progression sera suivie par l’état du grand livre.
En particulier, les éléments suivants seront suivi :

* l’ID de l’action de gouvernance
* l’époque à laquelle l’action expire
* le montant du dépôt
* l’adresse des récompenses qui recevra le dépôt lorsqu’il sera retourné
* le total des votes 'Oui'/'Non'/'Abstention' du comité constitutionnel pour cette action
* le total des votes 'Oui'/'Non'/'Abstention' des DReps pour cette action
* le total des votes 'Oui'/'Non'/'Abstention' des SPO pour cette action


#### Modifications apportées à l’instantané de mise

Étant donné que l’instantané de mise change à chaque limite d’époque, un nouveau décompte doit être calculé lorsque chaque mesure de gouvernance non ratifiée
est vérifié pour la ratification. Cela signifie qu’une action pourrait être promulguée même si les votes DRep ou SPO n’ont pas changé
(puisque la délégation de vote aurait pu changer).

#### Définitions relatives à la participation de vote

Nous définissons un certain nombre de nouveaux termes liés à la participation de vote :

* Lovelace contenu dans une sortie de transaction est considéré comme **actif pour le vote** (c’est-à-dire qu’il forme la « participation de vote active ») :
  * Il contient une identification de mise enregistrée.
  * L’accréditation de mise enregistrée a délégué ses droits de vote à un DRep.
* Par rapport à un certain pourcentage `P`, un seuil de vote DRep (SPO) **a été atteint** si la somme de la mise relative qui a été déléguée aux DReps (SPO)
 qui votent `Yes` à une mesure de gouvernance
 est au moins `P`.

## Raison d’être

+ [Rôle du comité constitutionnel](#rôle-du-comité-constitutionnel)
+ [Omission intentionnelle de la vérification de l’identité](#omission-intentionnelle-de-la-vérification-didentité)
+ [Réduire le pouvoir des entités avec de grandes quantités d’Ada](#réduire-la-puissance-des-entités-avec-de-grandes-quantités-dada)
+ [Greffage sur la distribution des mises du pool de participation](#greffage-sur-la-distribution-des-mises-du-pool-de-participation)
+ [Séparation de l’initiation du hard-fork des modifications des paramètres de protocole standard](#séparation-de-linitiation-du-hard-fork-des-modifications-des-paramètres-du-protocole-standard)
+ [Le but des DReps](#le-but-des-dreps)
+ [Tableau des exigences de ratification](#tableau-des-exigences-de-ratification)
+ [Motion de non-confiance](#motion-de-non-confiance)
+ [Mise à jour du comité/seuil (état de non-confiance)](#mide-à-jours-du-comitéseuil-état-de-non-confiance)
+ [La polyvalence de l’action de gouvernance de l'information](#la-polyvalence-de-laction-de-gouvernance-de-linformation)
+ [Initiation hard-fork](#initiation-hard-fork)
+ [Nouvelles structures de métadonnées](#nouvelles-structures-de-métadonnées)
+ [Contrôle du nombre d’actions de gouvernance actives](#contrôle-du-nombre-dactions-de-gouvernance-actives)
+ [Pas d’AVST](#pas-davst)

### Rôle du comité constitutionnel

À première vue, le comité constitutionnel peut sembler être un comité spécial qui s’est vu accorder un pouvoir supplémentaire sur les DReps.
Cependant, étant donné que DReps peut remplacer le comité constitutionnel à tout moment et que les votes DRep sont également nécessaires pour ratifier chaque action de gouvernance,
le comité constitutionnel n’a pas plus (et peut, en fait, avoir moins) de pouvoir que le DReps.
Dans ce contexte, quel rôle le comité joue-t-il et pourquoi n’est-il pas superflu?
La réponse est que le comité résout le problème d’amorçage du nouveau cadre de gouvernance.
En effet, dès que nous appuyons sur la gâchette et permettons à ce cadre de devenir actif sur la chaîne, alors sans comité constitutionnel,
il faudrait rapidement qu’il y ait suffisamment de DReps, afin que le système ne repose pas uniquement sur les votes SPO.
Nous ne pouvons pas encore prédire à quel point la communauté sera active dans l’inscription en tant que DReps, ni dans quelle mesure les autres détenteurs d’Ada seront réactifs en ce qui concerne la délégation de votes.

Ainsi, le comité constitutionnel entre en jeu pour s’assurer que le système peut passer de
son état actuel dans une gouvernance entièrement décentralisée en temps voulu.
De plus, à long terme, le comité peut jouer un rôle de mentorat et de conseil dans les décisions de gouvernance
en étant un ensemble de représentants élus qui sont mis sous les projecteurs pour leur jugement et leur orientation dans les décisions de gouvernance.
Par-dessus tout, le comité est tenu à tout moment de respecter la Constitution et de ratifier les propositions conformément aux dispositions de la Constitution.

### Omission intentionnelle de la vérification d’identité

Notez que ce CIP ne mentionne aucun type de validation ou de vérification d’identité pour les membres du comité constitutionnel ou du DReps.

C’est intentionnel.

Nous espérons que la communauté envisagera fortement de ne voter que pour et de déléguer aux DReps qui fournissent quelque chose comme un DID pour s’identifier.
Cependant, l’application de la vérification d’identité est très difficile sans un oracle centralisé, que nous considérons comme un pas dans la mauvaise direction.

### Réduire la puissance des entités avec de grandes quantités d’Ada

Divers mécanismes, tels que le vote quadratique, ont été proposés pour se prémunir contre les entités ayant une grande influence.
Dans un système basé sur « 1 Lovelace, 1 vote », cependant, il est trivialement facile de diviser la mise en petits montants et d’annuler les protections.
Sans un système de vérification d’identité en chaîne, nous ne pouvons pas adopter de telles mesures.

### Greffage sur la distribution des mises du pool de participation

Le protocole Cardano est basé sur un mécanisme de consensus Proof-of-Stake, il est donc judicieux d’utiliser une approche de gouvernance basée sur les enjeux.
Cependant, il existe de nombreuses façons de définir comment enregistrer la répartition des mises entre les participants.
Pour rappel, les adresses réseau peuvent actuellement contenir deux ensembles d’informations d’identification : une pour identifier qui peut débloquer des fonds à une adresse
(alias informations d’identification de paiement) et qui peut être délégué à un pool de participations (alias informations d’identification de délégation).

Plutôt que de définir un troisième ensemble d’informations d’identification, nous proposons plutôt de réutiliser les informations d’identification de délégation existantes,
Utilisation d’un nouveau certificat on-chain pour déterminer la répartition des mise de gouvernance. Cela implique que l’ensemble des DReps peut (et sera probablement) différent de l’ensemble des SPO,
créant ainsi un équilibre. D’un autre côté, cela signifie que la répartition des mise de gouvernance souffre des mêmes lacunes que celle de la production en blocs :
par exemple, les fournisseurs de logiciels de portefeuille doivent prendre en charge les systèmes de multidélégation et doivent faciliter le partitionnement de la mise en sous-comptes si un détenteur d’Ada souhaite déléguer à plusieurs DReps,
ou un détenteur d’Ada doit diviser manuellement sa mise si son portefeuille ne le prend pas en charge.

Cependant, ce choix limite également les efforts futurs de mise en oeuvre pour les fournisseurs de portefeuilles et minimise l’effort nécessaire pour que les utilisateurs finaux participent au protocole de gouvernance.
Cette dernière préoccupation est suffisamment importante pour justifier la décision. En se greffant sur la structure existante,
Le système reste familier aux utilisateurs et raisonnablement facile à configurer. Cela maximise à la fois les chances de succès et le taux de participation au cadre de gouvernance.

### Séparation de l’initiation du hard fork des modifications des paramètres du protocole standard

Contrairement aux autres mises à jour des paramètres de protocole, les hard forks (ou, plus exactement, les modifications apportées au numéro de version majeure du protocole) nécessitent beaucoup plus d’attention.
En effet, alors que d’autres modifications des paramètres de protocole peuvent être effectuées sans modifications logicielles significatives,
un hard fork suppose qu’une super-majorité du réseau a mis à niveau le noeud Cardano pour prendre en charge le nouvel ensemble de fonctionnalités introduites par la mise à niveau.
Cela signifie que le calendrier d’un événement hard fork doit être communiqué bien à l’avance à tous les utilisateurs de Cardano et nécessite une coordination entre les opérateurs de pool de participations, les fournisseurs de portefeuille, les développeurs DApp et l’équipe de libération des noeuds.

Par conséquent, cette proposition, contrairement au schéma Shelley, encourage les initiations de hard fork en tant qu’action de gouvernance autonome, distincte des mises à jour des paramètres de protocole.

### Le but des DReps

Rien dans cette proposition n’empêche les SPO de devenir des DReps.
Pourquoi avons-nous des DReps?
La réponse est que les SPO sont choisis uniquement pour la production de blocs et que tous les SPO ne voudront pas devenir DReps.
Les électeurs peuvent choisir de déléguer leur vote aux DReps sans avoir à se demander s’ils sont
également un bon producteur de blocs, et les SPO peuvent choisir de représenter les détenteurs d’Ada ou non.

### Tableau des exigences de ratification

Les conditions énoncées dans le [tableau des conditions de ratification](#exigences) sont expliquées ici.
La plupart des actions de gouvernance ont le même type d’exigences :
le comité constitutionnel et le DReps doivent atteindre un nombre suffisant de
Votes 'Oui'.
Cela inclut les actions suivantes :
* Mise à jour du comité/seuil (état normal)
* Nouvelle Constitution
* Modifications des paramètres de protocole
* Retrait du Trésor

### Motion de non-confiance

Une motion de censure représente un manque de confiance de la part de la communauté de Cardano à l’égard de la
Le Comité constitutionnel actuel et, par conséquent, le Comité constitutionnel ne devraient pas
être inclus dans ce type de mesure de gouvernance.
Dans cette situation, les SPOs et les DReps sont laissés à représenter la volonté de la communauté.

### Mise à jour du comité/seuil (état de non-confiance)

Semblable à la motion de non-confiance, l’élection d’un comité constitutionnel
dépend à la fois des SPOs et des DReps pour représenter la volonté de la communauté.

### La polyvalence de l’action de gouvernance de l’information

Bien qu’elle ne soit pas contraignante pour la chaîne, l’action de gouvernance de l’information pourrait être utile dans un certain nombre de
Situations. Il s’agit notamment des éléments suivants :

* ratifier un CIP
* Décider du fichier Genesis pour une nouvelle ère de grand livre
* consigner les commentaires initiaux pour les futures mesures de gouvernance

### Initiation Hard-Fork

Indépendamment de tout mécanisme de gouvernance, la participation des SPO est nécessaire pour tout hard fork car ils doivent mettre à niveau leur logiciel de noeud.
Pour cette raison, nous rendons leur coopération explicite dans l’action de gouvernance d’initiation hard fork,
en exigeant toujours leur vote.
Le comité constitutionnel vote également, signalant la constitutionnalité d’un hard fork.
Les DReps votent également, pour représenter la volonté de chaque partie prenante.

### Nouvelles structures de métadonnées

Les actions de gouvernance, les votes et les certificats et la Constitution utilisent de nouveaux champs de métadonnées,
sous forme d’URL et de hachages d’intégrité
(reflétant la structure des métadonnées pour l’enregistrement du pool de participation).
Les métadonnées sont utilisées pour fournir un contexte.
Les actions de gouvernance doivent expliquer pourquoi elles sont nécessaires,
quels experts ont été consultés, etc.
Étant donné que les contraintes de taille des transactions ne devraient pas limiter ces données explicatives,
nous utilisons plutôt des URL.

Cela introduit toutefois de nouveaux problèmes.
Si une URL ne se résout pas, à quoi faut-il s’attendre pour voter sur cette action ?
Devrions-nous nous attendre à ce que tout le monde vote 'non'?
S’agit-il d’un vecteur d’attaque contre le système de gouvernance ?
Dans un tel scénario, la pré-image de hachage pourrait être communiquée d’autres manières, mais nous devrions être
préparé à la situation.
Devrait-il y avoir un résumé de la justification sur la chaîne?

#### Alternative : Utilisation des métadonnées de transaction

Au lieu de champs dédiés spécifiques au format transactionnel, nous pourrions utiliser le champ de métadonnées de transaction existant.

Les métadonnées liées à la gouvernance peuvent être clairement identifiées en enregistrant une étiquette de métadonnées CIP-10.
Dans ce cadre, la structure des métadonnées peut être déterminée par ce CIP (format exact à déterminer), à l’aide d’un index pour mapper l’ID de vote ou d’action de gouvernance à l’URL et au hachage des métadonnées correspondants.

Cela évite d’avoir à ajouter des champs supplémentaires au corps de la transaction, au risque de faciliter l’ignorance des déposants.
Toutefois, étant donné que les métadonnées requises peuvent être vides (ou peuvent pointer vers une URL non résolue),
Il est déjà facile pour les auteurs de fournir des métadonnées, et il n’est donc pas clair si cela aggrave la situation.

Notez que les métadonnées de transaction ne sont jamais stockées dans l’état du grand livre, de sorte que ce serait aux clients de décider.
pour coupler les métadonnées avec les actions et les votes dans cette alternative, et ne serait pas disponible
en tant que requête d’état du grand livre.

### Contrôle du nombre d’actions de gouvernance actives

Étant donné que les actions de gouvernance peuvent être soumises par tous, nous avons besoin d’un mécanisme pour empêcher
les personnes responsables du vote de ne pas être submergées par un flot de propositions.
Un dépôt important est l’un de ces mécanismes, mais cela se fait au prix malheureux d’être un obstacle
pour certaines personnes qui souhaiteraient soumettent une action.
Notez cependant que le crowd-sourcing avec un script Plutus est toujours une option pour collecter le dépôt.

Nous pourrions, alternativement, accepter la possibilité d’un grand nombre d’actions actives à un temps donné
et plutôt dépendre de la socialisation hors chaîne pour guider l’attention des électeurs vers ceux qui le méritent.
Dans ce scénario, le comité constitutionnel pourrait choisir de n’examiner que les propositions qui ont
a déjà recueilli suffisamment de votes de la part des DReps.

### Pas d’AVST

Une version antérieure de ce CIP incluait la notion d’un « seuil de mise active » ou AVST.
Le but de l’AVST était d’assurer la légitimité de chaque vote, en éliminant la possibilité que, par exemple,
9 Lovelace sur 10 pourraient décider du sort de millions d’entités sur Cardano.
Il y a vraiment deux préoccupations ici, qui méritent d’être séparées.

La première préoccupation est celle de l’amorçage du système, c’est-à-dire d’atteindre le moment initial où
Une participation suffisante est enregistrée pour voter.
La deuxième préoccupation est que le système pourrait perdre sa participation au fil du temps.
L’un des problèmes de l’AVST est qu’elle incite les SPOs à souhaiter un faible taux d’enregistrement au vote.
(puisque leurs votes ont alors plus de poids).
Ce n’est absolument pas un affront aux SPOs existants, mais un problème avec de mauvaises incitations.

Nous avons donc choisi de résoudre les deux préoccupations différemment.
Nous résolvons le problème d’amorçage comme décrit dans la section sur l’amorçage.
Nous résolvons le problème de la participation à long terme en n’autorisant pas les retraits de récompenses
(après la phase bootstrap) sauf si la participation est déléguée à un DRep
(y compris les deux cas particuliers, à savoir 'Abstention' et 'Non-confiance').

### Journal des modifications

#### Modifications après l'atelier Longmont (Mars 2023)

* Remerciez les participants à l'atelier.
* Nous avons ajouté les termes du Comité constitutionnel.
* Deux nouvelles options de vote « prédéfinies » : abstention et non-confiance.
* Nouvelle action de gouvernance « Info ».
* Utilisez la distribution de participation DRep la plus récente pour la ratification.
  Cela signifie que si jamais votre DRep vote comme vous ne l'aimez pas,
  vous pouvez immédiatement vous faire un DRep et voter comme vous le souhaitez.
* Récupérez une partie de l'ADA de la trésorerie actuelle pour d'éventuelles
  incitations DRep futures.
* Supprimez les actions de trésorerie à plusieurs niveaux au profit de quelque chose d'adaptatif
  (le seuil du « Yes » dépendrait donc de :
      1) combien d'ada,
      2) quel est le montant de la mise de participation enregistrée, et peut-être
      3) combien d'ada est libéré à chaque époque
* Divisez les mises à jour des paramètres de protocole en quatre groupes :
  réseau, économique, technique et gouvernemental.
* La plupart des actions de gouvernance peuvent être promulguées (après ratification)
  immédiatement. Tout sauf : les paramètres de protocole et les hard forks.
* Supprimez la restriction « une action par type et par époque » en faveur du
  suivi du dernier ID d'action de chaque type, et de son inclusion
  dans l'action.
* Pas d'AVST.
* Phase d'amorçage : jusqu'à ce que X % des ADA soient inscrits pour voter ou que Y époques se
  soient écoulées, seuls les changements de paramètres et les hard forks peuvent se produire.
  Les changements du PP ont juste besoin du seuil du CC, les HF ont besoin du CC et des SPOs.
  Après la phase de bootstrap, nous mettons en place l'incitation à maintenir des
  DReps bas, mais ce mécanisme se détend **automatiquement**.
* Nouvel objectif de script plutus pour DReps.
* Retraits multiples du Trésor en une seule époque.
* Une section sur le problème récursif du "comment ratifier ce CIP".
* Modifications apportées au protocole local de requête d'état.
* Nouvelles idées, si le temps le permet :
  * Pesez d'une manière ou d'une autre le vote des enjeux SPO par par le « pledge ».
  * Les DReps peuvent spécifier quel autre DRep recevra ses délégants
    au cas ou ils se retire.
* Dépôt réduit pour action gouvernementale si un membre du CC
  l'approuve (ce qui signifie probablement qu'il a suivi un certain processus).
* Inclure le hachage de (future) configuration Genesis dans la proposition de HF.

#### Modifications après l'atelier d'Édimbourg (Juillet 2023)

* Ajoutez un script de rambardes, qui peut contrôler quels retraits de trésorerie et
  modifications des paramètres de protocole sont autorisés.
* Supprimer l'abandon des actions de gouvernance. Le seul effet que cela a est que si
  une mesure de censure est adoptée, les actions restent
  en place. Cependant, seules les nouvelles propositions du comité
  conçues pour s’appuyer sur cette mesure de censure peuvent être
  adoptées. Si un nouveau comité est élu alors que certaines de ces actions
  n'ont pas expiré, ces actions peuvent être ratifiées mais le nouveau comité
  doit les approuver.
* All governance actions are enacted one epoch after they are ratified.
* Déplacez les restrictions post-bootstrapping vers « Autres idées ».
* Ajoutez une section sur les différents montants de dépôt à « Autres idées ».
* Ajoutez une section pour un AVS minimum à « Autres idées ».
* Renommez certains paramètres de protocole.
* Renommez `TALLY` en `GOV`.
* Transformez la Constitution en une ancre.
* Retravaillez quelles ancres sont requises et lesquelles sont facultatives.
* Nettoyez diverses incohérences et restes des anciennes versions.

#### Modifications liées à la sécurité et autres correctifs (Janvier 2024)

* Protégez les modifications liées à la sécurité derrière les votes SPO.
* Le système n’entre pas dans un état de non-confiance avec un nombre insuffisant
  de membres actifs du CC, le CC devient tout simplement incapable d’agir.
* Précisez que les membres du CC peuvent utiliser n’importe quel type d’identifiant.

#### Mai 2024

* Mise à jour de la section sur la période d'amorçage.
* Mention du paramètre `Q_5` manquant.
* Diverses petites corrections/changements de cohérence.
  
## Chemin vers Actif

### Critères d’acceptation

- [x] Une nouvelle ère du grand livre est activée sur le réseau principal Cardano, qui implémente la spécification ci-dessus.
- Gouvernance de la phase d'amorçage via le hardfork Chang #1
- Gouvernance complète via le hardfork Plomin

### Plan de mise en oeuvre

Les fonctionnalités de ce CIP nécessitent un hard fork.

Ce document décrit un changement ambitieux dans la gouvernance de Cardano.
Nous proposons de mettre en œuvre les changements via deux hard forks : le premier
contenant toutes les nouvelles fonctionnalités mais certaines étant désactivées pendant une période de démarrage
et le second permettant toutes les fonctionnalités.

Dans les sections suivantes, nous donnons plus de détails sur les différents éléments de travail de mise en œuvre qui ont déjà été identifiés.
En outre, la dernière section expose quelques questions ouvertes qui devront être finalisées.
Nous espérons que ces questions pourront être abordées dans le cadre d’ateliers et de discussions communautaires.

#### Ratification de cette proposition

La ratification de cette proposition est en quelque sorte un problème circulaire: nous avons besoin d’une forme de cadre de gouvernance afin de nous mettre d’accord sur ce que devrait être le cadre de gouvernance final.
Comme on l’a dit à maintes reprises, les CIP ne font pas autorité et ne constituent pas un mécanisme de gouvernance.
Ils décrivent plutôt des solutions techniques qui ont été jugées saines (d’un point de vue technique) par la communauté d’experts.

Le CIP-1694 va sans doute au-delà de la portée habituelle du processus de CIP et il y a un fort désir de ratifier ce CIP par le biais de _un processus_.
Toutefois, ce processus n’a pas encore été défini et reste une question ouverte.
Le processus de ratification finale sera probablement un mélange de diverses idées, telles que:

- [x] Recueillir les opinions des ateliers communautaires, semblables à l’atelier du Colorado de février-mars 2023.
- [ ] Exercer des actions de vote sur un réseau de test public, avec une participation suffisante.
- [ ] Interrogez les fournisseurs de services établis.
- [ ] Tirer parti de Project Catalyst pour recueillir les contributions de la communauté électorale existante (bien que petite en termes de participation active).

#### Modifications apportées au corps de la transaction

- [x] De nouveaux éléments seront ajoutés au corps de la transaction, et les fonctionnalités de mise à jour et MIR existantes seront supprimées. En particulier

 Les actions de gouvernance et les votes comprendront deux nouveaux champs d’organe de transaction.

- [x] Trois nouveaux types de certificats seront ajoutés en plus des certificats existants :

  * Inscription DRep
  * Désinscription DRep
  * Délégation de vote

 De même, les certificats MIR et genesis actuels seront supprimés.

- [x] Un nouvel objectif `Voting` sera ajouté aux contextes de script Plutus.
 Cela prévoira, en particulier, le vote aux scripts on-chain.

> **Warning** Comme d’habitude, nous fournirons une spécification CDDL pour chacune de ces modifications.

#### Modifications apportées aux règles existantes du grand livre

* La règle de transition `PPUP` sera réécrite et déplacée de la règle `UTxO` vers la règle `LEDGER` en tant que nouvelle règle `GOV`.

 Il traitera et enregistrera les actions de gouvernance et les votes.

* La règle de transition `NEWEPOCH` sera modifiée.
* La sous-règle `MIR` sera supprimée.
* Une nouvelle règle `RATIFY` sera introduite pour mettre en scène les actions de gouvernance en vue de leur promulgation.

 Il ratifiera les mesures de gouvernance et les mettra en oeuvre en vue de leur promulgation à l’époque actuelle ou à l’époque suivante, selon le cas.

* Une nouvelle règle de `ENACTMENT` sera appelée immédiatement après la règle `EPOCH` . Cette règle édictera des mesures de gouvernance qui ont déjà été ratifiées.
* La règle `EPOCH` n’appellera plus la sous-règle `NEWPP` ni ne calculera si le quorum est atteint sur l’état PPUP.

#### Modifications apportées au protocole de requête d’état local

La charge de travail de gouvernance sur la chaîne est importante, mais la charge de travail hors chaîne pour les outils et les applications sera sans doute encore plus importante.
Pour construire un écosystème de gouvernance efficace, le grand livre devra fournir des interfaces avec divers éléments de gouvernance.

Alors que les votes et les (dé)inscriptions DReps sont directement visibles dans les blocs et seront donc accessibles via les protocoles de synchronisation de la chaîne locale existants; Nous devrons mettre à niveau le protocole de requête d’état local pour fournir des informations supplémentaires sur les informations qui sont plus difficiles à déduire des blocs (c’est-à-dire celles qui nécessitent le maintien d’un état de grand livre). Les nouvelles requêtes d’état doivent couvrir (au moins) :

- Les actions de gouvernance actuellement mises en œuvre
- Les actions de gouvernance en cours de ratification, avec le total et le pourcentage de mise « oui », de mise « non » et de mise « abstention »
- Le comité constitutionnel actuel et le condensé de hachage de la constitution

#### Phase d’amorçage

Nous devrons faire attention à la façon dont nous amorcerons ce gouvernement naissant. Toutes les parties
qui sont impliqués auront besoin de suffisamment de temps pour s’inscrire et se familiariser avec le processus.

Des dispositions spéciales s’appliqueront dans la phase initiale de bootstrap.
Tout d’abord, pendant la phase d’amorçage, un vote du comité constitutionnel
est suffisant pour modifier les paramètres du protocole.
Deuxièmement, pendant la phase d’amorçage, un vote du comité constitutionnel,
avec un vote SPO suffisant, est suffisant pour initier un hard fork.
Troisièmement, des actions d'information seront disponibles.
Aucune autre action autre que celles mentionnées dans ce paragraphe n’est possible pendant la phase d’amorçage.

La phase d'amorçage se termine lorsque le Comité constitutionnel et les SPOs
ratifieront un hard fork ultérieur, permettant les actions de 
de gouvernance restantes et la participation des DReps.
Cela se produira probablement plusieurs mois après le hard fork de Chang.
Bien que toutes les fonctionnalités soient techniquement disponibles à ce stade, des exigences
supplémentaires pour l'utilisation de chaque fonctionnalité peuvent être spécifiées dans la constitution.

De plus, il y aura un comité constitutionnel intérimaire pour une durée déterminée,
également spécifié dans le fichier de configuration de la prochaine ère du "ledger".
Le calendrier de rotation du premier comité non intérimaire pourrait être inclus dans la constitution elle-même.
Notez toutefois que, puisque le comité constitutionnelle ne vote jamais sur de nouveaux comités,
il ne peut pas réellement imposer la rotation.

#### Autres idées / Questions ouvertes

##### Vote des SPO pondérés par les engagements

Le vote du SPO pourrait en outre être pondéré par l’engagement de chaque SPO.
Cela fournirait un mécanisme permettant à ceux qui ont un intérêt littéral dans le jeu d’avoir un vote plus fort.
La pondération doit être choisie avec soin.

##### Redélégation automatique des DReps

Un DRep pourrait éventuellement indiquer un autre identifiant DRep dans son certificat d’enregistrement.
À la retraite, toutes les délégations du DRep seraient automatiquement transférées vers
les informations d’identification DRep choisi. Si ce DRep avait déjà pris sa retraite, la délégation serait transférée
à l'option de vote 'Abstention'.

##### Pas d’inscription DRep

Étant donné que l’enregistrement DRep ne remplit aucune fonction nécessaire,
les certificats pour (dés)enregistrer DReps pourraient être supprimés. Ceci
rend la démocratie plus liquide puisqu’elle supprime une partie de la bureaucratie et
élimine également le besoin du dépôt DRep, au détriment du déplacement de l’ancre qui fait partie du
certificat d’enregistrement DRep dans les métadonnées de transaction.

##### Réduction des dépôts pour certaines actions gouvernementales

Le dépôt qui est attaché aux actions de gouvernance existe pour prévenir un flot d'actions de gouvernance non sérieuse,
dont chacune nécessiterait du temps et de l’attention de la part de la communauté de Cardano.
Nous pourrions réduire ce dépôt pour les propositions qui passent par un processus convenu hors chaîne.
Cela serait marqué sur la chaîne par l’approbation d’au moins un membre du comité constitutionnel.
L’inconvénient de cette idée est qu’elle donne plus de pouvoir au comité constitutionnel.

##### Différents montants de dépôt pour différentes actions de gouvernance

Plusieurs ateliers de ce CIP ont proposé d'introduire un montant de dépôt différent
pour chaque type d'action de gouvernance. Il n’est pas clair
si une majorité est favorable à cette idée, mais elle pourrait être
envisagée s’il apparaît clairement que cela est nécessaire.

##### Participation minimale de vote actif

Comme garantie supplémentaire pour garantir que les actions de gouvernance ne peuvent pas être proposées
juste avant un hard fork, être votées par un DRep avec une grande quantité
de participation et être adoptées immédiatement, il pourrait y avoir une exigence
supplémentaire selon laquelle un certain montant absolu fixe de participation
doit voter « oui » sur l'action à adopter.

Cela ne semble pas nécessaire dans la conception actuelle, puisque la participation de
tous les DReps enregistrés se comporte comme un vote « non » jusqu'à ce qu'ils aient effectivement
voté. Cela signifie que pour que ce scénario se produise, l’acteur malveillant
doit au moins contrôler la fraction de la participation du DRep
correspondant au seuil pertinent, auquel cas cela pourrait tout aussi bien être 
considéré comme une action légitime.

##### Inclure le hachage de la (future) configuration de la genèse dans la proposition de hard-fork

Certains hard-forks nécessitent de nouvelles configurations de genèse.
Cela a été le cas pour les hard forks Shelley et Alonzo (mais pas Allegra, Mary, Vasil ou Valentine), ce sera peut-être le cas à l’avenir.
Pour le moment, cette proposition ne dit rien sur une telle configuration de genèse :
Il est implicitement supposé qu’il s’agit d’un accord hors chaîne.
Nous pourrions cependant faire en sorte que (le hachage) d’une configuration de genèse spécifique soit également capturé dans une action de gouvernance hard-fork.

##### Seuils adaptatifs

Comme nous l’avons vu plus haut, il peut être logique que certains ou tous les seuils s’adaptent à l’égard du Lovelace qui est activement inscrit pour voter,
afin que le système offre une plus grande légitimité lorsqu’il n’y a qu’un faible niveau de participation active des votes.
Le mécanisme d’amorçage proposé ci-dessus peut toutefois englober cela en veillant à ce que le système de gouvernance soit activé
uniquement lorsqu’un niveau minimum de mise a été délégué à DReps.


##### Renommer DReps / état de non-confiance ?

Il a été dit à plusieurs reprises que « DReps » tel que présenté ici, pourrait être confondu avec Project Catalyst DReps.
De même, certaines personnes ont exprimé une confusion entre l’état de non-confiance, la motion de non-confiance et l'option de vote non-confiance.

Nous pourrions imaginer trouver de meilleurs termes pour ces concepts.

##### Mouvements de trésorerie limitant les taux

Rien n’empêche de retirer de l’argent du Trésor autre que les votes proposés et les seuils de vote. Étant donné que le Trésor Cardano est une composante tout à fait fondamentale de sa politique monétaire, nous pourrions imaginer appliquer (au niveau du protocole) le montant maximum qui peut être retiré du Trésor sur une période donnée.

##### Mesure de sécurité finale, post-bootstrapping

De nombreuses personnes ont déclaré qu'elles pensaient que le taux de participation réel ne serait pas si important
qu'il constituerait une pression sur le débit du système.
Nous pensons également que cela sera probablement le cas, mais lorsque la phase d'amorçage se terminera, nous pourrions
mettre en place une dernière mesure de sécurité temporaire (cela nous permettra également de justifier un faible montant de dépôt DRep).

Pour les valeurs de $X$ et $Y$ qui restent à déterminer,
dès la fin de la phase bootstrapping,
lorsque nous calculerons la distribution des enjeux DReps pour la prochaine limite d'époque,
nous considérerons _uniquement_ les DReps qui sont _soit_ dans le les meilleurs $X$ - de nombreux DReps classés par montant de mise,
ou les DReps qui ont au moins $Y$ Lovelace.
À chaque époque, la valeur de $X$ _augmentera_ et la valeur de $Y$ diminuera,
de sorte qu'à terme $X$ sera effectivement infini et $Y$ sera nul.
Notez qu'il ne s'agit que d'une incitation et que rien n'empêche réellement un DRep d'exprimer
son vote (même s'il ne sera pas pris en compte s'il ne répond pas aux exigences).

Si la communauté décide à un moment donné qu’il y a effectivement un problème de congestion,
alors un hard fork pourrait être adopté pour limiter le nombre de DReps de manière plus restrictive.

Des chiffres raisonnables pour la valeur initiale de X$ sont probablement compris entre 5 000 et 10 000.
Les nombres raisonnables pour la valeur initiale de $Y$ sont probablement le nombre total de Lovelace
divisé par la valeur initiale de $X$.

Le mécanisme devrait être assoupli à un rythme où la restriction serait complètement supprimée
après une période de six mois à un an.

## Remerciements

<details>
 <summary><strong>Première ébauche</strong></summary>

De nombreuses personnes ont commenté et contribué à la première ébauche de ce document, qui a été publiée en novembre 2022.
Nous tenons particulièrement à remercier les personnes suivantes pour leur sagesse et leurs idées :

 * Jack Briggs
 * Tim Harrison
 * Philippe Lazos
 * Michael Madoff
 * Evangelos Markakis
 * Joël Telpner
 * Thomas Upfield

Nous tenons également à remercier ceux qui ont commenté via Github et d’autres canaux.
</details>

<details>
 <summary><strong>2023 Atelier du Colorado (28/02 → 01/03)</strong></summary>

De plus, nous tenons à remercier tous les participants à l’atelier qui s’est tenu à Longmont, Colorado, les 28 février et 1er mars 2023 pour leurs précieuses contributions
à ce CIP, et pour leur défense active de la vision de Cardano pour une gouvernance minimale viable. Cela inclue:

* Adam Rusch, ADAO & Summon
* Addie Girouard
* Andrew Westberg
* Darlington Wleh, LidoNation
* Eystein Hansen
* James Dunseith, Gimbalabs
* Juana Attieh
* Kenric Nelson
* Lloyd Duhon, DripDropz
* Marcus Jay Allen
* Marek Mahut, 5 binaires
* Markus Gufler
* Matthieu Capps
* Miséricorde, Wada
* Michael Dogali
* Michael Madoff
* Patrick Tobler, NMKR
* Philippe Lazos
* π Lanningham, SundaeSwap
* Rick McCracken
* Romain Pellerin
* Sergio Sanchez Ferreros
* Tim Harrison
* Tsz Wai Wu
</details>

<details>
  <summary><strong>2023 Mexico, Atelier du Mexique (20/05)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Mexico, au Mexique, le 20 mai 2023 pour leurs précieuses contributions
à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Donovan Riaño
* Cristian Jair Rojas
* Victor Hernández
* Ramón Aceves
* Sergio Andrés Cortés
* Isaías Alejandro Galván
* Abigail Guzmán
* Jorge Fernando Murguía
* Luis Guillermo Santana

</details>

<details>
  <summary><strong>2023 Buenos Aires, Atelier de l'Argentine (20/05)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Buenos Aires, Argentine le 20 mai 2023 pour leurs précieuses contributions
à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Lucas Macchiavelli
* Alejando Pestchanker
* Juan Manuel Castro Pippo
* Federico Weill
* Jose Otegui
* Mercedes Ruggeri
* Mauro Andreoli
* Elias Aires
* Jorge Nasanovsky
* Ulises Barreiro
* Martin Ochoa
* Facundo Lopez
* Vanina Estrugo
* Luca Pestchanker
</details>

<details>
  <summary><strong>2023 Johannesburg, Atelier d'Afrique du Sud(25/05)</strong></summary>

En outre, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Johannesburg, en Afrique du Sud, le 25 mai 2023, pour leurs précieuses contributions à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Celiwe Ngwenya
* Bernard Sibanda
* Dumo Mbobo
* Shaolyn Dzwedere
* Kunoshe Muchemwa
* Siphiwe Mbobo
* Lucas Sibindi
* DayTapoya
* Mdu Ngwenya
* Lucky Khumalo
* Skhangele Malinga
* Joyce Ncube
* Costa Katenhe
* Bramwell Kasanga
* Precious Abimbola
* Ethel Q Tshuma
* Panashe Sibanda
* Radebe Tefo
* Kaelo Lentsoe
* Richmond Oppong
* Israel Ncube
* Sikhangele Malinga
* Nana Safo
* Ndaba Delsie
* Collen Tshepang
* Dzvedere Shaolyn
* Thandazile Sibanda
* Ncube Joyce
* Lucas Sibindi
* Pinky Ferro
* Ishmael Ntuta
* Khumalo Lucky
* Fhulufelo
* Thwasile Ngwenya
* Kunashe Muchemwa
* Dube Bekezela
* Tinyiko Baloi
* Dada Nomathemba
</details>


<details>
  <summary><strong>2023 Bogota, Atelier de Colombie (27/05)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Bogota, en Colombie, le 27 mai 2023 pour leurs précieuses contributions
à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Alvaro Moncada
* Jaime Andres Posada Castro
* Jose Miguel De Gamboa
* Nicolas Gomez
* Luis Restrepo (Moxie)
* Juanita Jaramillo R.
* Daniel Vanegas
* Ernesto Rafael Pabon Moreno
* Carlos Eduardo Escobar
* Manuel Fernando Briceño
* Sebastian Pabon
</details>

<details>
  <summary><strong>2023 Caracas, Atelier du Venezuela (27/05)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Caracas, Venezuela le 27 mai 2023 pour leurs précieuses contributions
à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Jean Carlo Aguilar
* Wilmer Varón
* José Erasmo Colmenares
* David Jaén
* Félix Dávila
* Yaneth Duarte
* Nando Vitti
* Wilmer Rojas
* Andreina García
* Carmen Galban
* Osmarlina Agüero
* Ender Linares
* Carlos A. Palacios R
* Dewar Rodríguez
* Lennys Blanco
* Francys García
* Davidson Arenas
</details>

<details>
  <summary><strong>2023 Manizales, Atelier de Colombie (27/05)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Manizales, en Colombie, le 27 mai 2023 pour leurs précieuses contributions
à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Yaris Cruz
* Yaneth Duarte
* Ciro Gelvez
* Kevin Chacon
* Juan Sierra
* Caue Chianca
* Sonia Malagon
* Facundo Ramirez
* Hope R.
</details>

<details>
  <summary><strong>2023 Addis-Abeba, Atelier d'Éthiopie (27/05 & 28/5)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Addis-Abeba, en Éthiopie, les 27 et 28 mai 2023 pour leurs précieuses contributions.
à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Kaleb Dori
* Eyassu Birru
* Matthew Thornton
* Tamir Kifle
* Kirubel Tabu
* Bisrat Miherete
* Emmanuel Khatchadourian
* Tinsae Teka
* Yoseph Ephrem
* Yonas Eshetu
* Hanna Kaleab
* Tinsae Teka
* Robee Meseret
* Matias Tekeste
* Eyasu Birhanu
* yonatan berihun
* Nasrallah Hassan
* Andinet Assefa
* Tewodros Sintayehu
* KIDUS MENGISTEAB
* Djibril Konate
* Nahom Mekonnen
* Eyasu Birhanu
* Eyob Aschenaki
* Tinsae Demissie
* Yeabsira Tsegaye
* Tihitna Miroche
* Mearaf Tadewos
* Yab Mitiku
* Habtamu Asefa
* Dawit Mengistu
* Nebiyu Barsula
* Nebiyu Sultan
* Nathan Samson
</details>

<details>
  <summary><strong>2023 Kyoto et Fukuoka, Atelier du Japon (27/05 & 10/06 )</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Kyoto et à Fukuoka, au Japon, les 27 mai et 10 juin 2023 pour leurs précieuses contributions à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Arimura
* Hidemi
* Nagamaru(SASApool)
* shiodome47(SODMpool)
* Wakuda(AID1pool)
* Yuta(Yuki Oishi)
* Andrew
* BANCpool
* Miyatake
* Muen
* Riekousagi
* SMAN8(SA8pool)
* Tatsuya
* カッシー
* 松
* ポンタ
* リサ
* Mako
* Ririco
* ながまる
* Baku
* マリア
* たりふん
* JUNO
* Kinoko
* Chikara
* ET
* Akira555
* Kent
* Ppp
* Shiodome47
* Sam
* ポール
* Concon
* Sogame
* ハンド
* Demi
* Nonnon
* banC
* SMAN8(SA8pool)
* りんむ
* Kensin
* りえこうさぎ
* アダマンタイト
* の/ゆすけ
* MUEN
* いちごだいふく
* Ranket
* A.yy
* N S
* Kazuya
* Daikon
</details>

<details>
  <summary><strong>2023 Monterey, Atelier de Californie (28/05)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Monterey, en Californie, le 28 mai 2023, pour leurs précieuses contributions à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Shane Powser
* Rodrigo Gomez
* Adam K. Dean
* John C. Valdez
* Kyle Solomon
* Erick "Mag" Magnana
* Bryant Austin
* John Huthmaker
* Ayori Selassie
* Josh Noriega
* Matthias Sieber
</details>

<details>
  <summary><strong>2023 Tlaxcala, Atelier du Mexique (01/06)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Tlaxcala, au Mexique, le 1er juin 2023, pour leurs précieuses contributions à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Victor Hernández
* Cristian Jair Rojas
* Miriam Mejia
* Josmar Cabañas
* Lizbet Delgado
* José Alberto Sánchez
* Fátima Valeria Zamora
* Julio César Montiel
* Jesús Pérez
* José Adrián López
* Lizbeth Calderón
* Zayra Molina
* Nayelhi Pérez
* Josué Armas
* Diego Talavera
* Darían Gutiérrez
</details>

<details>
  <summary><strong>2023 Atelier virtuel LATAM (03/06)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier virtuel LATAM le 3 juin 2023 pour leurs précieuses contributions à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Juan Sierra
* @CaueChianca
* Ernesto Rafael
* Pabon Moreno
* Sonia Malagon
* Facundo Ramírez
* Mercedes Ruggeri
* Hope R.
* Yaris Cruz
* Yaneth Duarte
* Ciro Gélvez
* Kevin Chacon
* Juanita Jaramillo
* Sebastian Pabon
</details>

<details>
  <summary><strong>2023 Worcester, Atelier du Massachusetts (08/06)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Worcester, Massachusetts le 8 juin 2023 pour leurs précieuses contributions à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* CardanoSharp
* Kenric Nelson
* Matthias Sieber
* Roberto Mayen
* Ian Burzynski
* omdesign
* Chris Gianelloni
</details>

<details>
  <summary><strong>2023 Chicago, Atelier d'Illinois (10/06)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Chicago, Illinois le 10 juin 2023 pour leurs précieuses contributions à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Adam Rusch
* Jose Martinez
* Michael McNulty
* Vanessa Villanueva Collao
* Maaz Jedh
</details>

<details>
  <summary><strong>2023 Atelier virtuel (12/06)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu virtuellement le 12 juin 2023 pour leurs précieuses contributions à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Rojo Kaboti
* Tommy Frey
* Tevo Saks
* Slate
* UBIO OBU
</details>

<details>
  <summary><strong>2023 Toronto, Atelier du Canada (15/06)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Toronto, au Canada, le 15 juin 2023, pour leurs précieuses contributions à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* John MacPherson
* Lawrence Ley
</details>

<details>
  <summary><strong>2023 Philadelphie, Atelier de Pennsylvanie (17/06)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Philadelphie, en Pennsylvanie, le 17 juin 2023, pour leurs précieuses contributions à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* NOODZ
* Jarhead
* Jenny Brito
* Shepard
* BONE Pool
* type_biggie
* FLAWWD
* A.I. Scholars
* Eddie
* Joker
* Lex
* Jerome
* Joey
* SwayZ
* Cara Mia
* PHILLY 1694
</details>

<details>
  <summary><strong>2023 Atelier de Santiago du Chili (17/06)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Santiago du Chili le 17 juin 2023 pour leurs précieuses contributions
à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Rodrigo Oyarsun
* Sebastián Aravena
* Musashi Fujio
* Geo Gavo
* Lucía Escobar
* Juan Cruz Franco
* Natalia Rosa
* Cristian M. García
* Alejandro Montalvo
</details>

<details>
  <summary><strong>2023 Atelier virtuel (17/06)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu virtuellement le 17 juin 2023 pour leurs précieuses contributions
à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Juana Attieh
* Nadim Karam
* Amir Azem
* Rami Hanania
* LALUL Stake Pool
* HAWAK Stake Pool
</details>

<details>
  <summary><strong>2023 Taipai, Atelier de Taïwan (18/06)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Taipai, Taiwan le 18 juin 2023 pour leurs précieuses contributions
à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Michael Rogero
* Ted Chen
* Mic
* Jeremy Firster 
* Eric Tsai
* Dylan Chiang
* JohnsonCai
* DavidCHIEN
* Zach Gu
* Jimmy WANG
* JackTsai
* Katherine Hung
* Will Huang
* Kwicil
</details>

<details>
  <summary><strong>2023 Midgard Vikingcenter Horten, Atelier de Norvège (19/06)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Midgard Vikingcenter Horten, en Norvège, le 19 juin 2023 pour leurs précieuses contributions.
à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Daniel D. Johnsen
* Thomas Lindseth
* Eystein Hansen
* Gudbrand Tokerud 
* Lally McClay
* $trym
* Arne Rasmussen
* Lise WesselTVVIN
* Bjarne 
* Jostein Aanderaa
* Ken-Erik Ølmheim
* DimSum
</details>

<details>
  <summary><strong>2023 Atelier Virtuel (19/06)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu virtuellement le 19 juin 2023 pour leurs précieuses contributions
à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Nicolas Cerny
* Nils Peuser
* Riley Kilgore
* Alejandro Almanza
* Jenny Brito
* John C. Valdez
* Rhys
* Thyme
* Adam Rusch
* Devryn
</details>

<details>
  <summary><strong>2023 New York, Atelier de New York (20/06)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu dans la ville de New York, le 20 juin 2023 pour leurs précieuses contributions
à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* John Shearing
* Geoff Shearing
* Daniela Balaniuc
* SDuffy
* Garry Golden
* Newman
* Emmanuel Batse
* Ebae
* Mojira
</details>

<details>
  <summary><strong>2023 La Cumbre, Atelier d'Argentine (23/06)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à La Cumbre, Argentine le 23 juin 2023 pour leurs précieuses contributions
à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Ulises Barreiro
* Daniel F. Rodriguez
* Dominique Gromez
* Leandro Chialvo
* Claudia Vogel
* Guillermo Lucero
* Funes, Brian Carrasco
* Melisa Carrasco
* Carlos Carrasco
</details>

<details>
  <summary><strong>2023 Minneapolis, Atelier du Minnesota (23/06)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Minneapolis, Minnesota le 23 juin 2023 pour leurs précieuses contributions à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Stephanie King
* Darlington Wleh
</details>

<details>
  <summary><strong>2023 La Plata, Atelier d'Argentine (23/06)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à La Plata, Argentine le 23 juin 2023 pour leurs précieuses contributions
à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Mauro Andreoli
* Rodolfo Miranda
* Agustin Francella
* Federico Sting
* Elias Aires
* Lucas Macchiavelli
* Pablo Hernán Mazzitelli
</details>

<details>
  <summary><strong>2023 Puerto Madryn, Atelier d'Argentine (23/06)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Puerto Madryn, en Argentine, le 23 juin 2023, pour leurs précieuses contributions à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Andres Torres Borda
* Federico Ledesma Calatayud
* Maximiliano Torres
* Federico Prado
* Domingo Torres
* Floriana Pérez Barria
* Martin Real
* Florencia García
* Roberto Neme
</details>

<details>
  <summary><strong>2023 Accra,  Atelier du Ghana (24/06)</strong></summary>

En outre, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Accra, au Ghana, le 24 juin 2023, pour leurs précieuses contributions à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Wada
* Laurentine
* Christopher A.
* Nathaniel D.
* Edufua
* Michael
* Augusta
* Jeremiah
* Boaz
* Mohammed
* Richmond O.
* Ezekiel
* Megan
* Josue
* Michel T.
* Bineta
* Afia O.
* Mercy
* Enoch
* Kofi
* Awura
* Emelia
* Richmond S.
* Solomon
* Phillip
* Faakor
* Manfo
* Josh
* Daniel
* Mermose
</details>

<details>
  <summary><strong>2023 Atelier Virtuel (24/06)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu virtuellement le 24 juin 2023 pour leurs précieuses contributions à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Jonas Riise
* Thomas Lindseth
* André "Eilert" Eilertsen
* Eystein Hansen
</details>

<details>
  <summary><strong>2023 Séoul, Atelier de la Corée du Sud (24/06)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Séoul, en Corée du Sud, le 24 juin 2023, pour leurs précieuses contributions à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Oscar Hong (JUNGI HONG)
* SPO_COOL (Kevin Kordano)
* SPO_KTOP (KT OH)
* WANG JAE LEE
* JAE HYUN AN
* INYOUNG MOON (Penny)
* HOJIN JEON
* SEUNG KYU BAEK
* SA SEONG MAENG
* JUNG MYEONG HAN
* BRIAN KIM
* JUNG HOON KIM
* SEUNG WOOK JUNG (Peter)
* HYUNG WOO PARK
* EUN JAE CHOI
* NA GYEONG KIM
* JADEN CHOI
</details>

<details>
  <summary><strong>2023 Abu Dhabi, UAE Workshop (25/06)</strong></summary>

En outre, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Abu Dhabi, Émirats arabes unis le 25 juin 2023 pour leurs précieuses contributions à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Amir Azem
* Ian Arden
* Madina Abdibayeva
* BTBF (Yu Kagaya)
* محمد الظاهري
* Tegegne Tefera
* Rami Hanania
* Tania Debs
* Khalil Jad
* Mohamed Jamal
* Ruslan Yakubov
* OUSHEK Mohamed eisa
* Shehryar
* Wael Ben Younes
* Santosh Ray
* Juana Attieh
* Nadim Karam
* DubaistakePool
* HAWAK Pool
* LALKUL Stake Pools
</details>

<details>
  <summary><strong>2023 Williamsburg, Atelier de New York (25/06)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Williamsburg, New York le 25 juin 2023 pour leurs précieuses contributions à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Pi
* Joseph
* Skyler
* Forrest
* Gabriel
* Newman
</details>

<details>
  <summary><strong>2023 Lagos, Atelier de Nigéria (28/06)</strong></summary>

En outre, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Lagos, au Nigeria, le 28 juin 2023, pour leurs précieuses contributions à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Jonah Benson
* Augusta
* Ubio Obu
* Olumide Hrosuosegbe
* Veralyn Chinenye
* Ona Ohimer
* William Ese
* Ruth Usoro
* William P
* Esther Simi
* Daniel Effiom
* Akinkurai Toluwalase
</details>

<details>
  <summary><strong>2023 Sao Paulo, Atelier du Brésil (01/07)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu à Sao Paulo, au Brésil, le 1er juillet 2023, pour leurs précieuses contributions à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Otávio Lima
* Rodrigo Pacini
* Maria Carmo
* Cauê Chianca
* Daniela Alves
* Jose Lins Dias
* Felipe Barcelos
* Rosana Melo
* Johnny Oliveira
* Lucas Ravacci
* Cristofer Ramos
* Weslei Menck
* Leandro Tsutsumi
* Izaias Pessoa
* Gabriel Melo
* Yuri Nabeshima
* Alexandre Fernandes
* Vinicius Ferreiro
* Lucas Fernandes
* Alessandro Benicio
* Mario Cielho
* Lory Fernandes Lima
* Larissa Nogueira
* Latam Cardano Community
</details>

<details>
  <summary><strong>2023 Atelier virtuel du Brésil (04/07)</strong></summary>

De plus, nous tenons à remercier tous les participants à l'atelier qui s'est tenu au Brésil le 4 juillet 2023 pour leurs précieuses contributions
à ce CIP et pour s'être fait champion actif de la vision de Cardano pour une gouvernance minimale viable. Ceux-ci inclus:

* Lincon Vidal
* Thiago da Silva Nunes
* Rodrigo Pacini
* Livia Corcino de Albuquerque
* Cauê Chianca
* Otávio Lima
</details>

## Droit d’auteur

Ce CIP est sous licence [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)

[^1]: Une description formelle des règles actuelles pour les actions de gouvernance est donnée dans la [spécification du registre Shelley](https://github.com/input-output-hk/cardano-ledger/releases/latest/download/shelley-ledger.pdf).

    - Pour les modifications des paramètres de protocole (y compris les hard forks), la règle de transition `PPUP` (Figure 13) décrit comment les mises à jour des paramètres de protocole sont traitées, et la règle de transition `NEWPP` (Figure 43) décrit comment les modifications apportées aux paramètres de protocole sont mises en œuvre.

    - Pour les transferts de fonds, la règle de transition `DELEG` (figure 24) décrit la manière dont les certificats MIR sont traités, et la règle de transition `MIR` (figure 55) décrit comment les mouvements de trésorerie et de réserves sont promulgués.

    > **Note**
    > Les capacités de la règle de transition `MIR` ont été étendues dans la [spécification du registre Alonzo](https://github.com/input-output-hk/cardano-ledger/releases/latest/download/alonzo-ledger.pdf)


[^2]: Il existe de nombreuses définitions différentes du terme « hard fork » dans l’industrie de la blockchain. Les hard forks font généralement référence à des mises à jour non rétrocompatibles d’un réseau. Dans Cardano, nous formalisons un peu plus la définition en appelant toute mise à niveau qui conduirait à la validation de _more blocks_ un « hard fork » et forçons les noeuds à se conformer à la nouvelle version du protocole, obsolant ainsi les noeuds incapables de gérer la mise à niveau.

[^3]: Il s’agit de la définition utilisée dans « participation active » pour la délégation de participation aux pools de participations, voir Section 17.1, Calcul de la mise totale, de la [spécification du grand livre Shelley](https://github.com/input-output-hk/cardano-ledger/releases/latest/download/shelley-ledger.pdf).
