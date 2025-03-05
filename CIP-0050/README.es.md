---
CIP: 50
Source: https://github.com/cardano-foundation/CIPs/blob/master/CIP-0050/README.md
Title: Recompensas de participación basadas en el apalancamiento de promesas
Revision: 2022-05-29
Translators:
  - Juan Montano DOT5
Language: es
---

# Lista de Potenciales Revisores:

- Aggelos Kiayias
- Aikaterini-Panagiota Stouka
- Charles Hoskinson
- Christia Ovezik
- Colin Edwards
- Duncan Coutts
- Elias Koutsoupias
- Francisco Landino
- Lars Brünjes
- Mark Stopka
- Philipp Kant
- Shawn McMurdo
- Tobias Francee
- Tom Stafford

# Extracto

Mejorar la descentralización es absolutamente necesario para la salud y crecimiento del ecosistema de Cardano a largo plazo. La fórmula actual de recompensas ha resultado en un estable pero estancado nivel de descentralización. Con el beneficio de retrospección durante el último año, la intención de (a0, k) no ha resultado en la descentralizada secuela esperado. Este CIP provee las justificaciones, métricas, los métodos y calendario de implementación de un programa mejorado para incrementar la descentralización de la red de Cardano.

La ecuación de recompensas propuesta retiene la función de k de recompensas disminuyentes basada en “stake”, pero reutiliza el parámetro a0 para imponer las recompensas disminuyentes basadas en la ventaja por pledge. La ecuación propuesta impone una serie de principios para asegurar que todos los accionistas de tamaños dramáticamente diferentes alcancen el mismo rendimiento máximo.La característica del tope en el rendimiento previene la formación de dos clases de accionistas y remueve algunos de los beneficios de la centralización.  Las motivaciones económicas de los accionistas más grandes se alinearían con la descentralización, diversificación de recompensas, tolerancia a fallos, y aseguraría la protección sibila de la comunidad entera.


# Motivación

Mejorar la descentralización es absolutamente necesario para la salud y crecimiento del ecosistema de Cardano a largo plazo. La fórmula actual de recompensas ha resultado en un estable pero estancado nivel de descentralización. La motivación es proveer las justificaciones, métricas, los métodos y calendario de implementación de un programa mejorado para incrementar la descentralización de la red de Cardano.


K y a0 son parámetros introducidos a la formulación de recompensa diseñada para promover la descentralización. La intención original del parámetro k era que estableciera un ‘soft-cap’ en el tamaño de una pool y por consecuencia fomentar al sistema a que convergiera hacia k pools del mismo tamaño, entregando un retorno equitativo por unidad de stake a todos los delegadores. En el mundo ideal, esto significaría que k pools que son casi igualmente saturados producirían una proporción aproximadamente igual de bloques. Una suposición subyacente era que una entidad correría solamente una pool, y discusiones de diseño sobre estos parámetros han descrito correr múltiples pools como una forma de ataque sibilo. [2].

Sin embargo, los parámetros introducidos no han logrado estas metas. Actualmente hay entidades únicas que corren 10,20,30 o hasta 100 pools separadas. Se ha propuesto que el “resultado promedio de descentralización” sea calculado a base de stake sostenido por cada entidad/grupo. “K-efectivo” es por eso utilizado para medir el “resultado promedio de descentralización” y es computado usando Ecuación 1. El Coeficiente Nakamoto es aproximadamente la mitad de k-efectivo redondeado al entero más cercano. K-efectivo provee una resolución cuantificada más alta de descentralización de la red comparada al Coeficiente Nakamoto.


La red de Cardano actualmente produce ~21,600 bloques por epoch con ~2,400 grupos produciendo entre 0 a ~3,600 bloques por grupo. Si se promedia, 41 grupos del mismo tamaño crearían cada uno ~527 bloques por epoch. La historia de la descentralización de la red enseñada en Figura 1 ha mejorado de 30.0 en epoch 245 a entre 39.0 y 43.0 después del epoch 260. Esta “descentralización efectiva” o “k-efectivo” no está para nada cerca a la figura de 500 que tiene el actual parámetro k=500 como blanco.  Un ejemplo parcial de la tabla usada para computar k-efectivo es enseñado en Figura 2.

(1) https://iohk.io/en/blog/posts/2020/11/05/parameters-and-decentralization-the-way-ahead/

(2) https://iohk.io/en/blog/posts/2018/10/29/preventing-sybil-attacks/

<img src="equation1.png" width="400"> (1)

![Figure 1](k-effective.png)
Figure 1. Historial del k-efectivo desde epoch 245 al presente.

![Figure 2](k-effective-table.png)
Figure 2. Tabla de cálculo del k-efectivo

## La intención del (a0,k)

Citando Aggelos Kiayias, Chief Scientist de IOG:

> “Central to the mechanism’s behavior are two parameters: k and a0. The k-parameter caps the rewards of pools to 1/k of the total available. The a0 parameter creates a benefit for pledging more stake into a single pool; adding X amount of pledge to a pool increases its rewards additively by up to a0*X. This is not to the detriment of other pools; **any rewards left unclaimed due to insufficient pledging will be returned to the Cardano’s reserves and allocated in the future**.” [3]
 
> “Paired with the assessment of stake pools performed by the delegates, **this mechanism provides the right set of constraints for the system to converge to a configuration of k equal size pools with the maximum amount of pledge possible**.” [3]
 
El análisis de la fórmula de recompensas actual en [4] igualaba 1 pool a 1 entidad. En el mundo real 1 entidad puede escoger delegar a otra entidad, operar un pool, u operar múltiples pools. Este desprevenido error en el análisis original contribuyó a la proliferación de múltiples pools en contra de incrementos en el parámetro k.

(3) https://iohk.io/en/blog/posts/2020/11/13/the-general-perspective-on-staking-in-cardano/

(4) https://arxiv.org/ftp/arxiv/papers/1807/1807.11218.pdf

## La Fórmula de Recompensas Actual

Desde “4.1 Our RSS construction” de “Reward Sharing Schemes for Stake Pools” [5]   la ecuación de recompensas actual es:

<img src="equation2.png" width="600"> (2)

donde:

λ’ = min{λ,β}, σ’ = min{σ,β} and β,α son parámetros fijos.

Una elección natural β = 1/k, donde k es el deseado número de pools.

y los siguientes son parámetros actuales del protocolo:

k = 500

α = a0 = 0.3
 
El parámetro a0 representa la fracción de las recompensas (R/(1+a0)) que no son pagadas a menos que todo el stake esté en pledge. Un a0 de 0.3 asegura que 1.0-1.0/(1.0+0.3) = 23% de las recompensas totales R serán retenidas de la fracción de pools con bajo pledge y regresadas a la reserva. El efecto de esta fórmula es que el pledge incrementado resulta en retener más de las recompensas disponibles R. Sin embargo, este beneficio no es lineal, sino que es drásticamente perjudicial hacia el límite de saturación. El término σ’ = min{σ,β} impone un limite en recompensas basado en k. Es necesario visualizar el campo de resultados concluyentes de diferentes cantidades de pledges desde 0.00% a 100.0%. La línea de puntos roja “Recompensa Máxima” representa el rendimiento máximo disponible del R con el tamaño actual de la red de stake.

<img src="a0 0.3 minfee 340.png">

## Si el cobro mínimo es 30

<img src="a0 0.3 minfee 30.png">

## Si el cobro mínimo es 0

<img src="a0 0.3 minfee 0.png">

## Si a0 se incrementa a 0.5

<img src="a0 0.5 minfee 340.png">

## Si a0 se incrementa a 1.0

<img src="a0 1.0 minfee 340.png">

## Si a0 se incrementa a 10.0

<img src="a0 10.0 minfee 340.png">

## Si a0 se disminuye a 0.2

<img src="a0 0.2 minfee 340.png">

## Si a0 se disminuye a 0.1

<img src="a0 0.1 minfee 340.png">

## Si a0 se disminuye a 0.0

<img src="a0 0.0 minfee 340.png">

## Si a0 se disminuye a 0.0 y mínimo cobro = 0

<img src="a0 0.0 minfee 0.png">

## La Realidad de (a0,k)

La intención de los parámetros (a0, k) no se ha realizado. La gráfica de k-efectivo demuestra que incrementando k de 150 a 500 no resultó en un incremento proporcional de la descentralización. El parámetro k actualmente es 500/41 = 12.2 veces más grande que el efectivo descentralizado k-efectivo. En Epoch 333, 46% del stake total estaba controlado por operadores de multi-pools que no son exchanges. 

Otro determinante importante de la habilidad para que pools pequeños puedan competir con pools más grandes es el cobro mínimo mandatorio el cual es actualmente 340₳. Este cobro mínimo es un porcentaje más alto de las recompensas totales para un pool pequeño que para un pool grande. Esto significa que las ganancias de delegadores para un pool pequeño no exceden 4.0% hasta que la pool tenga al menos 10.0% de saturación (actualmente ~6.8M₳). Esta es una barrera de entrada significante para pools pequeños.

Billones de ADA están actualmente staked en pools con casi 0 pledge y pledges extremadamente altos. También, un billón de ADA están actualmente como pledge en pools privadas al borde de saturación que están cerradas a delegación de la comunidad. Hay muy pocos pools públicos aceptando delegación de la comunidad con pledge de montos entre 5M₳ a 60M₳ y la gran mayoría de pools públicas tienen menos de 1M₳ en pledge. La siguiente tabla demuestra la distribución de stake como función de ventaja, o “leverage” en inglés, en una escala log(Stake) vs log(Leverage). El mecanismo de incentivo actual del pledge solo se vuelve relevante en un pequeño segmento de esta tabla debajo de un leverage de 10 y encima de un pledge de 10M₳. La Alianza “Single Pool Operator Alliance” (SPA) es un colectivo de ~2,250 pools individuales y operadores de pools con un stake colectivo de 5B₳ con un factor leverage promedio de solo 22. La SPA es el ancla de descentralización en Cardano.

<img src="stake vs leverage current.png">

En el diseño original, el parámetro a0 representó la influencia que el pledge del operador tenía en la atractividad de la pool. En otras palabras, más pledge significa que la pool es más atractiva para recibir delegación. Sin embargo, la fórmula de recompensas actual no ha producido este efecto. Ver Figura 2. Con pledge incrementando en proporción del stake total, hay muy poco efecto perceptible en recompensas hasta que vemos altos porcentajes de pledge. Estos altos porcentajes de pledge no son obtenibles excepto por accionistas extremadamente grandes. Además, teniendo un porcentaje de pledge tan alto derrotaría el propósito del staking de la comunidad, ya que la pool ya estaría saturada cuando el beneficio de pledge máximo se obtiene.

La realidad de los previos 18 meses es que operadores de pools han dividido su pledge por múltiples pools porque es más rentable (cobro mínimo + margen%) que incrementar el pledge en un solo pool. El pequeño incremento en ganancias para pools con menos de 10M₳ en pledge es mucho menos que la aleatoria certeza de recompensas cada epoch. El incentivo del pledge es actualmente un beneficio estadísticamente desapercibido usado solo por grandes inversionistas privados. La ecuación de recompensas actual ha sacrificado recompensas igualitarias justas por un incentivo que no está proveyendo protección sibila como se destinaba.

## El Efecto Sundaeswap

El SundaeSwap Initial Stake Offering (ISO) demostró que la participación del delegador de la comunidad puede ser muy móvil. Más de un par de billones en participación se centralizó en grupos de ISO. Después de darse cuenta que la popularidad de su ISO resultó en una centralización de la red, SundaeSwap lanzó un ISO 'Reverse' en beneficio de los grupos individuales. El RISO revirtió temporalmente la tendencia de centralización cuando se delegaron un billón de ADA a pequeños grupos. La red Cardano alcanzó un factor de descentralización de 43.22 en la epoch 321. Después de la RISO, estas ganancias de descentralización se revirtieron porque los incentivos subyacentes de la fórmula de recompensa no han cambiado. Esto demuestra que la comunidad está comprometida y que su participación es móvil, especialmente en cuanto a rendimiento y ganancias.

## a0: El parámetro del pledge que aumenta rendimiento

Un diseño intencional de la ecuación de recompensa actual es permitir deliberadamente que las grandes partes interesadas que suplican a los grupos privados obtengan los máximos rendimientos posibles mientras excluyen la delegación de la comunidad. La gran mayoría de los pools con compromiso <10% de saturación de participación tienen un rendimiento asintótico que actualmente se acerca a un rendimiento máximo de 4.25%. Una fracción de compromiso alto en un fondo privado puede obtener hasta el rendimiento máximo disponible del 5,5 %, un 30 % más de rendimiento que los fondos comunitarios de compromiso bajo. 

El término R/(1+a0) garantiza que los fondos comunes pequeños no ganarán la misma fracción de la reserva que los fondos grandes comprometidos. Actualmente, aproximadamente 1.25B₳ obtienen recompensas completas en 19 grupos. Si no se modifican a lo largo del tiempo, las empresas de gestión patrimonial de custodia podrán ofrecer rendimientos sustancialmente más altos que los particulares. Wave Financial es un ejemplo de una empresa que actualmente ofrece este modelo de negocio a los clientes. Eternl/ccvault está introduciendo funciones de firmas múltiples para permitir que muchas personas se comprometan colectivamente con los grupos. Con el tiempo, esta diferencia da como resultado dos clases diferentes de partes interesadas y erosiona el atractivo de auto custodia descentralizado de Cardano.

## El peligro de “solo incrementa k”

Obligar al parámetro k a ser radicalmente diferente de la descentralización efectiva, k-efectivo, de la red ha tenido consecuencias no deseadas. Cuando se incrementó k los grupos grandes crearon nuevas pools para retener a los delegadores. Si se aumenta el parámetro k sin actualizar la fórmula de recompensas, los inversionistas más grandes podrán obtener rendimientos completos comprometiéndose con fondos privados, excluyendo la delegación comunitaria.

Las grandes diferencias entre el parámetro k y el k-efectivo de la red representan un estrés en el estado actual de la red. Más pools bajo el control de un número menor de grupos no mejora la descentralización y de hecho toma más tiempo y recursos para propagar el blockchain a más nodos y relays. Un K-efectivo de >100.0 con un k-parámetro ajustable de ~3.0*k-efectivo es una meta a largo plazo numéricamente justificable. 



# Especificación

## Declaración de Principios

“Principles matter.” -CH

1. Todos en la comunidad deberían ser tratados justamente desde pequeños peces delegadores (1-2k₳) a ballenas (>100m₳) y exchanges.
2. Todos en la comunidad deberían tener la misma oportunidad de en promedio ganar el mismo rendimiento y no debería de existir dos clases de inversionistas.
3. Debería de haber una relación causa y efecto muy clara entre (a0,k) parámetros ingresados y la descentralización k-efectivo resultante.
4. El parámetro a0 ingresado debería requerir, no incentivar, a operadores de pools a tener pledge para apoyar los delegadores y protección sibila.
5. La descentralización resultada será cuantificada en términos de descentralización agrupada de producción de bloques, no saturación de stake relativo hacia pools.
6. La implementación debería ser fluida, sencilla, clara, y beneficiosa para todos los inversionistas y operadores.
7.Una ecuación de recompensas nueva debería ser computacionalmente simple y elegante.

## La Nueva Fórmula Propuesta

La propuesta ecuación de recompensas retiene la función de k para recompensas limitadas basadas en stake, pero le da un nuevo propósito al parámetro a0 para hacer cumplir recompensas limitadas basadas en la ventaja de pledge. La ecuación balancea equitativamente ambos parámetros de recompensas. En vez de a0 variando de 0.0 a infinito, el parámetro a0 es destinado a variar de 10,000.0 hasta 1.0. Un a0 con valor de 100 requeriría pools a hacer pledge 1% del stake, y un a0 de 1.0 requeriría todas las pools tener 100.0% pledge.

<img src="new equation.png" width="400">

R = ( reserva * rho + cobros )( 1.0 - tau )

r( sigma, lambda ) = R * min{ sigma, a0 * lambda, 1/k }


La nueva ecuación es computacionalmente simple y no usa logaritmos a propósito, exponentes, o curvas geométricas. En vez de un incentivo basado en costo-beneficios entre recompensas igualitarias y una resiliencia sibila percibida, la nueva ecuación hace cumplir las recompensas igualitarias y resiliencia sibila basada en pledge por igual. Un límite en rendimiento egalitario simple con aplicación de ventaja en pledge para defensa sibila tiene un profundo efecto psicológico: Stakeholders saben que no hay manera de jugar el sistema, ya sea individualmente o colectivamente con gubernatura, y pledge es absolutamente mandatorio. Sin alguna parcialidad artificial, la descentralización de Cardano se fusionaría a la diversidad de la comunidad, servicios, y distribución de stakeholders. Si esta propuesta se adopta eventualmente, cambios en la diversidad de la comunidad, no cambios en la fórmula o parámetros, cambiaría la descentralización.


# Razonamiento

## Reforma de a0

El parámetro a0 será redefinido para establecer un pledge máximo antes de limitar recompensas, similar al parámetro k de tamaño de pools. La ventaja de pledge establece un ‘punto de saturación’ diferente por cada pool basado en su pledge. La reforma del parámetro a0 hace cumplir el principio que pledge incrementando es absolutamente requerido para apoyar la delegación de la comunidad en crecimiento. Este cambio alinea el parámetro a0 para proteger la red de comportamientos sibilos. El factor de la ventaja de pledge provee un límite de enforzamiento en actores sibilos y su retorno máximo en capital invertido. Pledge no será un incentivo estadísticamente muy apenas reconocible usado solo por grandes inversionistas privados. El mecanismo preferido para constreñir comportamiento sibilo sería gobernanza de la comunidad para ajustar el factor de ventaja a0. 

El nuevo parámetro a0 va a variar de 1000.0 a 1.0. El valor inicial de la proporción a0 en pledge máximo debería inicialmente ser establecida conservativamente alto en (>=100.0) y opcionalmente disminuida conforme avanza el tiempo a un equilibrio saludable por gobernancia de la comunidad. En (a0=100, k=500) aproximadamente 680k₳ pledge sería requerido para apoyar un pool totalmente saturado. 

## La nueva ecuación de recompensas

La nueva fórmula propuesta debería ser visualizada en una escala (rendimiento)-lineal vs log(saturación) independiente de k. La Figura abajo demuestra el campo de posibles resultados en varios niveles de pledge y stake extendiéndose más de 3 órdenes de magnitud. El efecto de una reforma de a0 se hace obvia, la saturación de pool será limitado primero por pledge y eventualmente por k. Una característica muy importante de esta relación es que 0₳ pledge resultará siempre en 0₳ recompensas. En a0=100.0 para apoyar un stake pool 100% saturado, 1.0% pledge será siempre requerido.

<img src="a0 100 minfee 30.png">

## La nueva ecuación de recompensas sin el cobro mínimo

<img src="a0 100 minfee 0.png">

## La zona de ecuación de recompensas nueva

<img src="stake vs leverage proposed.png">

## El límite de rendimiento

La nueva ecuación es diseñada a propósito para que inversionistas de tamaños dramáticamente diferentes puedan todos alcanzar el mismo rendimiento máximo. La característica del límite de rendimiento previene la formación de dos clases de inversionistas y remueve el beneficio económico de la centralización. El límite de rendimiento es la “recompensa igualitaria” descrita pero no implementada por el documento original.

Con el cobro mínimo <30 ya que un pool crezca a >0.5% de saturación, las recompensas intermitentes van a, en promedio, proveer un rendimiento competitivo para delegadores en >5.0%. En k=500 y a0=100 esto corresponde a un tamaño de pool de 500k₳ con un pledge mínimo de solo 5k₳. El límite de rendimiento también es compatible para una implementación potencial en el futuro del concepto de un pool cónclave colectivo. Por el límite de rendimiento, stake pools colectivos grandes solo proveerán más retornos predecibles, no un rendimiento materialmente más grande, el cual competiría con pools pequeños independientes.

## Una ventaja de pools pequeños

Los ganadores de forks de bloques y batallas por slots son determinados por cual pool tiene un puntaje VRF más bajo. Sí operadores de multi-pools se consolidan para mejorar la eficiencia de la red y reducir costos de operación, se les daría una pequeña ventaja a favor de los pools pequeños. Los pools pequeños también tendrán una ligera ventaja ante futuros pools colectivos. Esta ventaja no es bien conocida pero le favorece a pools pequeños.

## La motivación económica de accionistas grandes y pools colectivos

La nueva fórmula no disminuirá los rendimientos de las grandes partes interesadas que se comprometan con los fondos privados. Los grandes inversionistas de ADA, como los exchanges, los fondos de liquidez o los contratos inteligentes, no estarían obligados a comprometer la gran mayoría de esas tenencias para obtener rendimientos que actualmente solo se pueden lograr con pools totalmente en pledge. Esta propiedad mejora la liquidez en general. La única motivación económica que queda para los grupos con una gran participación, incluidos los fundadores, las organizaciones fundadoras, los intercambios, el capital de inversión, los fideicomisos y el capital de riesgo, sería asegurar la diversificación y mejorar el valor de toda la red dividiendo la delegación para asegurar diversificación.

Los grandes inversionistas que pueden dividir su participación en docenas de pools también lograrán una mayor diversificación de recompensas y tolerancia a fallas que la auto operación de una pequeña cantidad de pools privados centralizados ofrecerían. Varias billeteras, incluidas Eternl/ccvault, ofrecen la habilidad de dividir la delegación de participación en muchos grupos. Esta decisión de diseño alinea el interés de las principales partes interesadas con los intereses de toda la comunidad.

## Propuestas CIP relevantes y borradores

1. https://cips.cardano.org/cips/cip7/
2. https://github.com/cardano-foundation/CIPs/pull/163
3. https://github.com/cardano-foundation/CIPs/pull/229 
4. https://forum.cardano.org/t/cip-leverage-based-saturation-and-pledge-benefit/95632
5. https://forum.cardano.org/t/cip-change-the-reward-formula/33615
6. https://forum.cardano.org/t/an-alternative-to-a0-and-k/42784

## Métodos y paradigmas para validación de ecuaciones

Para validar cualquier simulación de ecuación de recompensas, se debe considerar que una entidad pueda escoger delegar a otra entidad, operar una stake pool, u operar varias stake pools. Cualquier nueva ecuación debe ser comparada a la ecuación actual con a0=0.3 y la ecuación actual con minFee=0, a0=0.0. . Un gran número de entidades (>100000) debe simularse para cada ensayo de cada ecuación. Además, durante cada epoch de cada simulación para cada bloque de ecuación, la producción podría mostrarse a partir de una distribución normal. La producción de bloques y las recompensas tienen incertidumbre estadística.

```
Cada ecuación:
  Cada epoch:
    Producción de bloque de muestra (recompensas) por pool de una distribución normal
    Cada entidad puede decidir a:
      crear/retirar 1 o mas pools
      Ajustar la estructura del cobro/margen de (s)us pool(s)
      Delegar a la pool de una entidad diferente
```

Para cada ecuación en consideración, el promedio (y la variación) del coeficiente de nakamoto, el coeficiente k-efectivo (o un equivalente basado en una entidad/grupo) y un coeficiente de sibila debería ser calculada para cada época hasta la conclusión. El coeficiente sibilo cuantificaria la fracción de stake controlado por todas las entidades operando muti pools, excluyendo negocios regulados como los exchanges.

# Compatibilidad reversa

La implementación ocurrirá en dos fases distintas, siendo la primera fase solo cambios de parámetros que no requieren una bifurcación dura. Durante esta primera fase cualquier cambio será reversible. La segunda fase requerirá un hard fork.

# Camino a Activación

La implementación de esta propuesta debe ser fluida, escenificada, deliberada y bien comunicada a través de publicidad y educación. Cada cambio en el horario de implementación debe incluir una comunicación clara a la comunidad en expectativas. La educación transparente sobre cómo funcionarán los parámetros y el efecto sobre las recompensas es importante.

1. Conseguir declaraciones de apoyo de una gran parte de la comunidad de Cardano.

A pesar de aún no haber entrado a la era Voltaire, aun así deberíamos alcanzar consenso de la comunidad.

2. Reducir cobro mínimo de 340₳ a 0₳.

Reduciendo el cobro mínimo obligatorio a 0 permitirá a pools pequeños ser más competitivos mientras se deja a cada pool independiente seleccionar un cobro fijo apropiado.

3. Esperar 5 - 10 epochs, evaluar descentralización, recaudar comentarios de la comunidad.

4. Conseguir más declaraciones de apoyo de una gran parte de la comunidad de Cardano.

5. Reducir k de 500 a aproximadamente 3 veces K-efectivo y disminuir a0 de 0.3 a 0.1.

Esto mejorará rendimientos para la comunidad de delegadores y permitirá a multi pools tiempo para consolidar pledge, delegación, y retirar pools innecesarios.

6. Esperar 5 - 10 epochs, evaluar descentralización, recaudar comentarios de la comunidad.

7. Implementación HARDFORK de la nueva fórmula dando a cumplir retornos disminuyentes de la ventaja de pledge (a0 >= 100, k = 3.0*k-efectivo).

8. Evaluar descentralización, recaudar comentarios de la comunidad.

9. Ajustar a0 y k por aproximadamente 5% cada 10 epochs hasta el final de Voltaire.

10. Después de Voltaire, ajustar a0 y k anualmente/bi-anual por voto de la comunidad.

# Copyright

Copyright 2022 Michael Liesenfelt

Este CIP tiene licencia bajo [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/legalcode)

# Declaración de Conflicto de Interés 

El autor es empleado por tiempo completo como Profesor de Asistente en Investigación de Ingeniería Nuclear en la Universidad de Tennessee, recibe cero ganancias del ecosistema de Cardano, no opera ningún stake pool, y no busca apoyo de delegación de la Fundación de Cardano, tiene 23,000 ADA delegados a THOR stake pool.
