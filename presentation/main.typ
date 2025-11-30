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
    institution: [],
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


= Weitführende Inhalte

== Wo kann ich mehr dazu finden?
- Einstiegsthema: Lineare Kontrolltheorie / linear control
- Youtube Video Serie *Control Systems in Practice*, Mathworks: https://youtu.be/ApMz1-MK9IQ?si=CdSrJPCsdLwsGXnT
- Podcast *inControl*, Roberto Padoan, Interviews mit führenden Experten über deren jeweiliges Spezialgebiet: https://www.incontrolpodcast.com/

== Quellen
Bibliographie
