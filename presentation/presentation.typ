#import "@preview/touying:0.5.2": *
#import "@preview/touying-buaa:0.2.0": *

#let wissen_ist_nacht_datum = datetime(
  year: 2025,
  month: 12,
  day: 27,
)

#let todo = block(
  width: 80%,
  inset: 10pt,
  fill: red.lighten(50%),
  text(size: 1.2em)[
    TODO
  ],
)


#let two-column-slide(
  left-content: [],
  right-content: [],
  right-text-color: black.lighten(30%),
  separator-color: black,
  separator-width: 1pt,
) = {
  slide(composer: (2fr, 1fr))[
    #box(width: 100%, height: 90%, stroke: (right: separator-width + separator-color))[
      #left-content
    ]
  ][
    #meanwhile
    #text(fill: right-text-color)[
      #right-content
    ]
  ]
}

#let linear_state_space_system(A, B, C) = {
  $dot(x) = A x + B u \ y = C x$
}


// Specify `lang` and `font` for the theme if needed.
#show: buaa-theme.with(
  // config-common(handout: true),
  config-info(
    title: [Kybernetisches Denken],
    subtitle: [ Eine Einführung ohne mathematisches Bla Bla],
    author: [Dani],
    date: wissen_ist_nacht_datum,
    institution: [Finsterberg Akademie, Zamonien],
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
    caption: [https://www.gkm.uni-stuttgart.de/techkyb/.content/img/kybhand.jpg],
  ),
  text[*Ok das war noch nicht sehr hilfreich!*],
)

== Kybernetik: Definition
_Die Kybernetik ist die Wissenschaft von Kontrolle und Information, gleichgültig, ob es
sich über lebendige Wesen oder Maschinen handelt_
-- Norbert Wiener


== Dieser Vortrag: Thema
Schwerpunkt des heutigen Vortrags:
- Regelung technischer Systeme
- Ausblick zu verschiedenen Methoden und Herausforderungen in der Kybernetik

== Dieser Vortrag: Darreichungsform
#two-column-slide(
  left-content: [
    - Kybernetik ist eine sehr mathematiklastige Disziplin
      - Um die gezeigten Zusammenhänge mathematisch präzise darzustellen, ist viel Vorwissen nötig
      - Hier werden die Zusammenhänge und Ideen intuitiv, ohne mathematische Grundvorraussetzungen dargestellt
      - _Rechte Spalte: Mathematische Darstellungen für Fans, *nicht* nötig fürs Verständnis_
  ],
  right-content: [Beispiel:\
    $cal(L){f(t)} = integral_0^infinity f(t) e^(-s t) dif t$ \
    Unnötige mathematische Ausführungen für unangenehme Besserwisser],
)


= Dynamische Systeme
== Was ist ein dynamisches System?
#todo

= Beispiel: U-Boot Tiefenregelung
== U-Boot Tiefenregelung: Problemstellung
- U-Boot Tiefe soll vorgegebener Linie folgenden
- Vertikale Kraft kann beeinflusst werden
*Demo*: _Simulation mit manueller Steuerung (Pfeiltasten)_

== U-Boot Tiefenregelung: Regelung via Feedback
- Ziel: Automatische Regelung der Tiefe
- Anwendung:* PID Regler*
  - *Proportionaler Anteil (P)*: Reagiert auf aktuellen Fehler
  - *Integraler Anteil (I)*: Reagiert auf aufsummierten Fehler über Zeit
  - *Differentieller Anteil (D)*: Reagiert auf Änderungsrate des Fehlers
  Verstärkungen der einzelnen Anteile *P, I, D* müssen gewählt werden!

*Demo*: _Simulation mit geregelter Steuerung (PID Regler)_
- Feedback: Aktuelle Tiefe wird gemessen und mit gewünschter Tiefe verglichen
- Regler berechnet Steuerungskraft basierend auf Differenz (Fehler)

= Weitere Konzepte
== Warum nicht Feierabend?
#tblock(
  title: "Kritische Selbsthinterfragung",
)[Das war ja sehr einfach? Warum soll man dann eine ganze Wissenschaft draus machen?]
Gute Gründe:
- Betrachtet wurde ein sehr, sehr einfaches Beispiel
- In der Praxis sind Systeme oft viel komplexer
- Störungen, Unsicherheiten, Verzögerungen sind in der Praxis unvermeidbar


== U-Boot Tiefenregelung: Darstellung im Blockdiagramm
#[
  #grid(
    columns: (1fr, 1fr),
    rows: (1fr, 1fr),
    gutter: 10pt,
    figure(
      image("images/block_diagram_openloop_submarine.png", width: 95%),
      caption: [Submarine: Open Loop],
    ),
    [],

    figure(
      image("images/block_submarine_closed_loop.png", width: 95%),
      caption: [Submarine: Closed Loop],
    ),
    [],
  )
]
#[
  #grid(
    columns: (1fr, 1fr),
    rows: (1fr, 1fr),
    gutter: 10pt,
    figure(
      image("images/block_diagram_openloop_submarine.png", width: 95%),
      caption: [Submarine: Open Loop],
    ),
    figure(
      image("images/block_diagram_open_loop_general.png", width: 95%),
      caption: [General: Open Loop],
    ),

    figure(
      image("images/block_submarine_closed_loop.png", width: 95%),
      caption: [Submarine: Closed Loop],
    ),
    [],
  )
]
== U-Boot Tiefenregelung: Darstellung im Blockdiagrammdback
#grid(
  columns: (1fr, 1fr),
  rows: (1fr, 1fr),
  gutter: 10pt,
  figure(
    image("images/block_diagram_openloop_submarine.png", width: 95%),
    caption: [Submarine: Open Loop],
  ),
  figure(
    image("images/block_diagram_open_loop_general.png", width: 95%),
    caption: [General: Open Loop],
  ),

  figure(
    image("images/block_submarine_closed_loop.png", width: 95%),
    caption: [Submarine: Closed Loop],
  ),
  figure(
    image("images/block_diagram_closed_loop_general.png", width: 95%),
    caption: [General: Closed Loop],
  ),
)
== Gefahr: Instabilität!

*Demo*: _Simulation mit instabilem Regler (hohe P Anteile)_
= Abstraktion
== Warum Abstraktion?
- Systeme können durch mathematische Modelle abstrahiert werden
- Erlaubt große Vielfalt von Anwendungsgebieten
  - Tatsächlich U-Boot Steuerung @Slotine_Lohmiller_1998_ContractionAnalysisNonlinearSystems
  - Flugzeug / Raketensteuerung
  - Chemische Reaktoren @Slotine_Lohmiller_1998_ContractionAnalysisNonlinearSystems
  - Wirtschaftssysteme
  - Verkehrswesen (zB. Verkehrsflussregelung)
  - Biologische Systeme (zB. Medizintechnik, Erhalt von Ökosystemen @Lotka_Elements_1926
  - Soziale Systeme (zB. Epidemiekontrolle: Analyse von Covid-Ausbreitung via Model Predictive Control, Uni Stuttgart @KOHLER2021525)

== Warum Abstraktion?
- Sobald die Modellierung steht, können Kybernetisch bewanderte Personen alle diese Systeme regeln, ohne Detailwissen auf den einzelnen Gebieten
- Kybernetik als "Universalwerkzeugkasten" für viele Anwendungsgebiete

== Modellbasierte Regelung
- Finde ausreichend akkurates Modell des Systems
- _"Alle Modelle sind falsch, aber manche sind nützlich"_ -- George Box, Statistiker
- Modellierung:
  - Was muss modelliert werden (Physikalische zusammenhänge, Logische implikationen, etc. )
  - Welcher Detailgrad ist nötig?
  - Was kann/muss vernachlässigt werden?
  - Was muss berücksichtigt werden (Störungen, Unsicherheiten, etc.)

== Regelkreis mit Störungen
#image("images/block_diagram_general_closed_loop_distorted.png", width: 100%)

= Systemanalyse
== Systemidentifikation

- Wie finde ich ein Modell für ein reales System?
- Was berücksichtige ich, was nicht?
- Gibt es Unsicherheiten:
  - Parameter Unsicherheiten (zB. Masse des U-Boots variiert je nach Beladung)
  - Modell Unsicherheiten (zB. Nicht modellierte Effekte wie Strömungswiderstand)
  - Messrauschen (zB. Sensoren haben begrenzte Genauigkeit)
  - ...


== Linearität
#tblock(title: "Definition")[
  Ein System ist *linear*, wenn es die folgenden 2 Eigenschaften erfüllt:
  + *Superposition*
  + *Homogenität*
]

== Linearität
#two-column-slide(
  left-content: [
    *Superposition:*
    _2 Signale addieren und in das System einspeisen = Beide Signale jeweils einzeln ins System einspeisen und die Ergebnisse addieren_
    #image("images/superposition.png", height: 60%)
  ],
  right-content: [
    $G(x + y) = G(x) + G(y) \ #text("für alle input signale ") x,y$
  ],
)

== Linearität
#two-column-slide(
  left-content: [
    *Homogenität:*
    _Ein Signal mit einem Faktor multiplizieren und in das System einspeisen = Das Signal ins System einspeisen und das Ergebnis mit dem Faktor multiplizieren_
    #image("images/homogenity.png", width: 80%)],
  right-content: [
    $G(alpha dot x) = alpha dot G(x) \ #text("für alle input signale") x \ #text("und Skalare") a$
  ],
)

== Stabilität
- Gleichgewichtszustände (engl. _Equilibria_)
  - Stabil (System verbleibt in der Nähe / Strebt zurück wenn abglenkt)
  - Nicht Stabil (System entfernt sich weiter, wenn abgelenkt)
  - Grenzstabil (System bleibt in der Nähe, zB auf periodischer Bahn)

== Steuerbarkeit / Beobachtbarkeit
- Welche System Zustände können durch Eingänge beeinflusst werden?
- Welche System Zustände können durch Ausgänge gemessen werden?

Für *Lineare Systeme*: Kriterien, die (für Computer) leicht zu überprüfen sind (Kalman Matrix Rang kriterien)

*Beobachtbare* größen können manchmal nicht direkt gemessen werden, aber dennoch rekonstruiert: Beobachter

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
    width: 65%,
    inset: 5pt,
    fill: gray.lighten(80%),
    text(size: 0.75em, body),
  )
]
#let rightmessage(body) = align(right)[
  #block(
    width: 65%,
    inset: 5pt,
    fill: blue.lighten(80%),
    text(size: 0.75em, body),
  )
]

#two-column-slide(
  left-content: [
    #pause
    #leftmessage[Hi, ich bin der Beobachter!]
    #pause
    #rightmessage[Moin, ich bin das System!]
    #pause
    #rightmessage[Was ist die Düsentemperatour?]
    #pause
    #leftmessage[Ich rate mal: 1500 °C]
    #pause
    #rightmessage[Angenommen, das würde Stimmen, was wäre dann der Ausgangswert des Systems?]
    #pause
    #leftmessage[Das wäre dann 500 000 N]

  ],
  right-content: [Lineares System:\ $dot(x) = A x + B u \ y = C x + D u$ \
    Beobachter-Simulator:
    $dot(hat(x)) = A hat(x) + B u \ hat(y) = C hat(x) + D u$ \
    Abgleich, wie gut die Schätzung ist:
    $abs(hat(y) - y) = 0?$ \
    Führe Korrektur ein: \
    $dot(hat(x)) = A hat(x) + B u + L (y - hat(y))$ \ Mit L so gewählt, dass die Fehlerdynamik  $dot(e) = dot(y) - dot(hat(y))$ stabile Eigenwerte hat],
)

#two-column-slide(
  left-content: [
    #pause
    #rightmessage[Der Echte Ausgangswert ist aber nur 450 000 N]
    #pause
    #leftmessage[Ok, aus dem Unterschied (50 000N) berechne ich eine Korrektur]
    #pause
    #leftmessage[Wenn ich berechne, was mittlerweile passiert sein muss, komme ich auf eine Düsentemperatur von 1450 °C. Das würde einen Ausgangswert von 473 000 N ergeben]
    #pause
    #rightmessage[Der echte Ausgangswert liegt momentan bei 460 000 N. Deine Schätzung wurde also schon besser]
    #pause
    #leftmessage[Ok, ich passe die Schätzung die Schätzung durch eine weitere Korrektur an]
    #pause
    #align(center)[... usw ...]
  ],
  right-content: [Lineares System:\ $dot(x) = A x + B u \ y = C x + D u$ \
    Beobachter-Simulator:
    $dot(hat(x)) = A hat(x) + B u \ hat(y) = C hat(x) + D u$ \
    Abgleich, wie gut die Schätzung ist:
    $abs(hat(y) - y) = 0?$ \
    Führe Korrektur ein: \
    $dot(hat(x)) = A hat(x) + B u + L (y - hat(y))$ \ Mit L so gewählt, dass die Fehlerdynamik  $dot(e) = dot(y) - dot(hat(y))$ stabile Eigenwerte hat],
)

= Relevanz / Zukunft
== Jetzt haben wir KI: Brauchen wir noch Kontrolltheorie?
- *Vorteile von KI Methoden*:
  - Lernen aus großen Mengen von Daten. Mechanismen / Modelle müssen nicht mehr von Menschen verstanden werden
  - Computertechnologie hat potentielle Anwendungsgebiete stark ausgeweitet --> "Probleme mit Rechenpower erschlagen"
  - Kontrolltheoretische Methoden wurden in manchen Bereichen durch KI abgelöst
    - Computer Vision
    - Autonomes Fahren _"End to End"_

== Jetzt haben wir KI: Brauchen wir noch Kontrolltheorie?
- Machine Learning / LLM Modelle sind meistens "Black Boxen"
- KI Algorithmen sind oft sehr *unrobust* gegenüber Störungen. Beispiel: Bilderkennung @ilyas2019adversarialexamplesbugsfeatures
  #align(center)[#figure(
    image("images/adversarial_example_dog_to_cat.png", width: 30%),
    caption: [Kleine Störung, große Wirkung, von: https://gradientscience.org/adv/],
  )]
- Schwächen der KI Algorithmen oft schwer vorrauszusagen
- KI integrität / Sicherheit oft schwer zu garantieren (_"Dieser Flug wird mit einer Wahrscheinlichkeit von 98% nicht abstürzen"_)

== Also doch Kontrolltheorie
- Kontrolltheorie über vernetzte Systeme kann zu robustem KI Design beitragen
- KI braucht riesige Datenmengen für Training, Kontrolltheorie kann helfen, Daten effizienter zu nutzen (Bsp. Individuelle Krebsbehandlung @rantzeretalconvexcancer)
  - Medikation muss individuell auf jeden Patienten angepasst werden
  - Unmöglich, für jeden Patienten riesige Datenmengen zu sammeln
  - Kontrolltheoretische Methoden der Konvexen Optimierung @Boyd_Vandenberghe_2004_ConvexOptimization können helfen, verbesserte Behandlungsstrategien zu finden

= Weitführende Inhalte
== Wo kann ich mehr dazu finden?
- Einstiegsthema: Lineare Kontrolltheorie / linear control
- Vorlesung Uni Washington: *Linear Systems (UW ME 547)*,  https://faculty.washington.edu/chx/teaching/me547/
- Youtube Video Serie *Control Systems in Practice*, Mathworks: https://youtu.be/ApMz1-MK9IQ?si=CdSrJPCsdLwsGXnT
- Podcast *inControl*, Roberto Padoan, Interviews mit führenden Experten über deren jeweiliges Spezialgebiet: https://www.incontrolpodcast.com/

== Quellen
#bibliography("sources.bib")
== Software
- python
- pymunk
- pygame
- python.control
- Präsentation: typst

- Programmcode für Simulationen:
  https://github.com/Dummyrunner/DynamicSimulationDemo
