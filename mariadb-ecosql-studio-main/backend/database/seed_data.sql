USE openflights;


INSERT INTO airports (AirportID, Name, Country, IATA)
VALUES (1, 'Gorakhpur Airport', 'India', 'GOP'),
       (2, 'Indira Gandhi Intl', 'India', 'DEL');


INSERT INTO routes (SourceAirportID, DestAirportID, Airline)
VALUES (1, 2, 'IndiGo');

