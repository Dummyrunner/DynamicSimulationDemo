#import "@preview/touying:0.5.2": *
#import "@preview/touying-buaa:0.2.0": *

#let wissen_ist_nacht_datum = datetime(
  year: 2025,
  month: 12,
  day: 27,
)
// Specify `lang` and `font` for the theme if needed.
#show: buaa-theme.with(
  config-info(
    title: [Kybernetik: Was ist das und was soll das?],
    // Alternativ: Ein Tick Kybernetik
    subtitle: [Dynamische Systeme beeinflussen],
    author: [Dani],
    date: wissen_ist_nacht_datum,
    institution: [Finsterberg Akademie, Zamonien],
    // Disable automatic insertion of the outline slide before each section
    outline: false,
  ),
)

#title-slide()
#outline-slide()

= Um was geht es?
== Was ist Kybernetik?
Was ist Kybernetik? Einfach mal googeln:
#pause
#grid(
  columns: (2fr, 2fr),
  gutter: 15pt,
  figure(
    image("images/CyberneticsSearch/SystemFamilie.png", width: 100%),
    caption: [https://o.quizlet.com/HPMRT3dpudKi1Ua3AOXmaw.png],
  ),
  figure(
    image("images/CyberneticsSearch/Kybernetik-definition-datascientest-orange-robot.jpg", width: 100%),
    caption: [https://datascientest.com/de/kybernetik-alles-wissen],
  ),

  figure(
    image("images/CyberneticsSearch/KybUniStuttgart.jpg", width: 100%),
    caption: [https://studieren.de/technische-kybernetik-uni-stuttgart.studienprofil.t-0.a-456.c-34710.html],
  ),
  figure(
    image("images/CyberneticsSearch/KunstKybernetik.jpg", width: 100%),
    caption: [https://pictures.abebooks.com/inventory/30771070339.jpg],
  ),

  figure(
    image("images/CyberneticsSearch/kybhand.jpg", width: 60%),
    caption: [https://www.gkm.uni-stuttgart.de/techkyb/.content/img/kybhand.jpg?__scale=w:220,h:220,cx:0,cy:0,cw:2000,ch:2000],
  ),
  text[Ok das war noch nicht sehr hilfreich!],
)

== Kybernetik: Definition
_Die Kybernetik ist die Wissenschaft von Kontrolle und Information, gleichgültig, ob es
sich über lebendige Wesen oder Maschinen handelt_
-- Norbert Wiener


== Dieser Vortrag
Schwerpunkt des heutigen Vortrags:
- Steuerung und Regelung technischer Systeme
- Ausblick zu verschiedenen Methoden und Herausforderungen in der Kybernetik


- Kybernetik ist eine sehr Mathematiklastige Disziplin:\
  Versuch, hier ohne Formeln Fachwissen auszukommen
- Für Fans und Experten: Manchmal Formel-Areal auf der rechten Seite

= Dynamische Systeme
== Was ist ein dynamisches System?
Schlauer Satz
- Beispiel 1
- Beispiel 2

= Systemanalyse
== Linearität
#tblock(title: "Definition")[
  Ein System ist *linear*, wenn es die folgenden 2 Eigenschaften erfüllt:
  + *Superposition*
  + *Homogenität*
]

== Linearität
*Superposition:*
_2 Signale addieren und in das System einspeisen = Beide signale jeweils einzeln ins System einspeisen und die Ergebnisse addieren_
#image("images/superposition.png", height: 60%)
== Linearität
*Homogenität:*
_Ein Signal mit einem Faktor multiplizieren und in das System einspeisen = Das Ergebnis des aus dem System mit dem Faktor multiplizieren_
#image("images/homogenity.png", height: 60%)

== Stabilität
- Gleichgewichtszustände (engl. _Equilibria_)
  - Stabil (System verbleibt in der Nähe / Strebt zurück wenn abglenkt)
  - Nicht Stabil (System entfernt sich weiter, wenn abgelenkt)
  - Grenzstabil (System bleibt in der Nähe, zB auf periodischer Bahn)

== Steuerbarkeit / Beobachtbarkeit
- Welche System Zustände können durch Eingänge beeinflusst werden?
- Welche System Zustände können durch Ausgänge gemessen werden?

Für *Lineare Systeme*: Kriterien, die (für Computer) leicht zu überprüfen sind (Kalman Matrix Rang kriterien)

= Beobachter
== Größen nicht zu messen: Was tun?
Beispiele:
- Brenntemperatur in Motor / Raketendüse
- Aktuelle nicht modellierte Störungen (zB. turbulente Luftströmungen)
- Lastmassen (zB. Passagiere in Flugzeug, Roboterarm mit Greifer)

== Beobachter: Idee
+ Rate Anfangszustand
+ Rechne simulierte systemdynamik "nebenher"
+ Berechne, was der Ausgang des simulierten Systems sein müsste
+ Vergleiche mit gemessenem Ausgang
+ Korrigiere Zustandsschätzung basierend auf Differenz

== Beobachter: Anschauliche Erklärung als Dialog
#let leftmessage(body) = align(left)[
  #block(
    width: 60%,
    inset: 10pt,
    fill: gray.lighten(80%),
    body,
  )
]

#let rightmessage(body) = align(right)[
  #block(
    width: 60%,
    inset: 10pt,
    fill: blue.lighten(80%),
    body,
  )
]
#leftmessage[hi lol]
#rightmessage[was geht ab?]
#leftmessage[I bims]

= Relevanz / Zukunft
== Jetzt haben wir KI: Brauchen wir noch Kontrolltheorie?
- *Vorteile von KI Methoden*:
  - Lernen aus großen mengen von Daten. Mechanismen / Modelle müssen nicht mehr von Menschen verstanden werden
  - Computertechnologie hat potentielle Anwendungsgebiete stark ausgeweitet --> "Probleme mit Rechenpower erschlagen"
  - Kontrolltheoretische Methoden wurden in manchen Bereichen durch KI abgelöst
    - Computer Vision
    - Autonomes Fahren _"End to End"_

== Jetzt haben wir KI: Brauchen wir noch Kontrolltheorie?
- Machine Learning / LLM Modelle sind oft "Black Boxen"
- KI Algorithmen sind oft sehr *unrobust* gegenüber Störungen. Beispiel: Bilderkennung @ilyas2019adversarialexamplesbugsfeatures
  #align(center)[#figure(
    image("images/adversarial_example_dog_to_cat.png", width: 30%),
    caption: [Kleine Störung, große Wirkung, von: https://gradientscience.org/adv/],
  )]
- KI integrität / Sicherheit oft schwer zu garantieren (_"Dieser Flug wird mit einer wahrscheinlichkeit von 98% nicht abstürzen"_)

== Also doch Kontrolltheorie
- Kontrolltheorie über vernetzte Systeme kann zu robustem KI Design beitragen
- KI braucht riesige Datenmengen für Training, Kontrolltheorie kann helfen, Daten effizienter zu nutzen (Bsp. Individuelle Krebsbehandlung @rantzeretalconvexcancer)
  - Medikation muss individuell auf jeden Patienten angepasst werden
  - Unmöglich, für jeden Patienten riesige Datenmengen zu sammeln
  - Kontrolltheoretische Methoden der Konvexen Optimierung können helfen, verbesserte Behandlungsstrategien zu finden

= Weitführende Inhalte
== Wo kann ich mehr dazu finden?
- Einstiegsthema: Lineare Kontrolltheorie / linear control
- Vorlesung Uni Washington: *Linear Systems (UW ME 547)*,  https://faculty.washington.edu/chx/teaching/me547/
- Youtube Video Serie *Control Systems in Practice*, Mathworks: https://youtu.be/ApMz1-MK9IQ?si=CdSrJPCsdLwsGXnT
- Podcast *inControl*, Roberto Padoan, Interviews mit führenden Experten über deren jeweiliges Spezialgebiet: https://www.incontrolpodcast.com/

= Playground
== Two-Column Slide (2/3 - 1/3 split)

#slide(composer: (2fr, 1fr))[
  == Left Column (2/3 width)

  This is the main content area that takes up approximately 66% of the slide width.

  #image("images/CyberneticsSearch/KunstKybernetik.jpg", width: 80%)

  You can include detailed explanations, code examples, or large images here.
][
  == Right Column (1/3 width)

  #text(fill: gray)[

    Linear System: \
    $dot(x) = A x + B u \ y = C x$
  ]
]

== Quellen
#bibliography("sources.bib")
== Software
- python
- pymunk
- pygame
- python.control
- Präsentation: typst

- programmcode: github.....
