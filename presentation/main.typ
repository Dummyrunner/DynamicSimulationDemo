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
    author: [Daniel],
    date: wissen_ist_nacht_datum,
    institution: [Finsterberg Akademie, Zamonien],
    // Disable automatic insertion of the outline slide before each section
    outline: false,
  ),
)

#title-slide()
= Einleitung
== Fancy Bilder
Inhalt der fancy bilder folie



#outline-slide()

= Dynamische Systeme

== Was ist ein dynamisches System?
Schlauer Satz
- Beispiel 1
- Beispiel 2

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
#pause
#leftmessage[hi lol]
#pause
#rightmessage[was geht ab?]
#pause
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
- KI Algorithmen sind oft sehr *unrobust* gegenüber Störungen @ilyas2019adversarialexamplesbugsfeatures
  #align(center)[#figure(
    image("images/adversarial_example_dog_to_cat.png", width: 30%),
    caption: [Kleine Störung, große Wirkung, von: https://gradientscience.org/adv/],
  )]
- KI integrität / sicherheit oft schwer zu garantieren (_"Dieser Flug wird mit einer wahrscheinlichkeit von 98% nicht abstürzen"_)

  == Also doch Kontrolltheorie
  - Kontrolltheorie über vernetzte Systeme kann zu robustem KI Design beitragen
  -





== Zukunftsvisionen: John Doyle
- Systemarchitekturen auf vielen Ebenen
- Robustheit fehlt in heutigen Systemen oft



= Weitführende Inhalte
== Wo kann ich mehr dazu finden?
- Einstiegsthema: Lineare Kontrolltheorie / linear control
- Youtube Video Serie *Control Systems in Practice*, Mathworks: https://youtu.be/ApMz1-MK9IQ?si=CdSrJPCsdLwsGXnT
- Podcast *inControl*, Roberto Padoan, Interviews mit führenden Experten über deren jeweiliges Spezialgebiet: https://www.incontrolpodcast.com/

== Quellen
#bibliography("sources.bib")
