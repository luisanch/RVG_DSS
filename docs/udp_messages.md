# Received UDP Messages {#app:additional}

## AIS messages from Gunnerus

**Class A AIS Position Report (Messages 1, 2, and 3)**

1.  Message ID: Identifier for this message 1, 2 or 3

2.  Repeat indicator: Used by the repeater to indicate how many times a
    message has been repeated. See Section 4.6.1, Annex 2; 0-3; 0 =
    default; 3 = do not repeat any more.

3.  User ID: MMSI number

4.  Navigational status:

    1.  0 = under way using engine

    2.  1 = at anchor

    3.  2 = not under command

    4.  3 = restricted maneuverability

    5.  4 = constrained by her draught

    6.  5 = moored

    7.  6 = aground

    8.  7 = engaged in fishing

    9.  8 = under way sailing

    10. 9 = reserved for future amendment of navigational status for
        ships carrying DG, HS, or MP, or IMO hazard or pollutant
        category C, high speed craft (HSC)

    11. 10 = reserved for future amendment of navigational status for
        ships carrying dangerous goods (DG), harmful substances (HS) or
        marine pollutants (MP), or IMO hazard or pollutant category A,
        wing in ground (WIG)

    12. 11 = power-driven vessel towing astern (regional use)

    13. 12 = power-driven vessel pushing ahead or towing alongside
        (regional use)

    14. 13 = reserved for future use

    15. 14 = AIS-SART (active), MOB-AIS, EPIRB-AIS

    16. 15 = undefined = default (also used by AIS-SART, MOB-AIS and
        EPIRB-AIS under test)

5.  Rate of turn ROTAIS : 0 to +126 = turning right at up to 708 deg per
    min or higher 0 to -126 = turning left at up to 708 deg per min or
    higher Values between 0 and 708 deg per min coded by ROTAIS = 4.733
    SQRT(ROTsensor) degrees per min where ROTsensor is the Rate of Turn
    as input by an external Rate of Turn Indicator (TI). ROTAIS is
    rounded to the nearest integer value. +127 = turning right at more
    than 5 deg per 30 s (No TI available) -127 = turning left at more
    than 5 deg per 30 s (No TI available) -128 (80 hex) indicates no
    turn information available (default). ROT data should not be derived
    from COG information.

6.  SOG: Speed over ground in 1/10 knot steps (0-102.2 knots) 1 023 =
    not available, 1 022 = 102.2 knots or higher

7.  Position accuracy: The position accuracy (PA) flag should be
    determined in accordance with the table below: 1 = high (\<= 10 m) 0
    = low (\> 10 m) 0 = default

8.  Longitude: Longitude in 1/10 000 min (+/-180 deg, East = positive
    (as per 2's complement), West = negative (as per 2's complement).
    181= (6791AC0h) = not available = default)

9.  Latitude: Latitude in 1/10 000 min (+/-90 deg, North = positive (as
    per 2's complement), South = negative (as per 2's complement). 91deg
    (3412140h) = not available = default)

10. COG: Course over ground in 1/10 = (0-3599). 3600 (E10h) = not
    available = default. 3 601-4 095 should not be used

11. True heading: Degrees (0-359) (511 indicates not available =
    default)

12. Time stamp: UTC second when the report was generated by the
    electronic position system (EPFS) (0-59, or 60 if time stamp is not
    available, which should also be the default value, or 61 if
    positioning system is in manual input mode, or 62 if electronic
    position fixing system operates in estimated (dead reckoning) mode,
    or 63 if the positioning system is inoperative)

13. special maneuvre indicator: 0 = not available = default 1 = not
    engaged in special maneuver 2 = engaged in special maneuver (i.e.:
    regional passing arrangement on Inland Waterway)

14. Spare: Not used. Should be set to zero. Reserved for future use.

15. RAIM-flag: Receiver autonomous integrity monitoring (RAIM) flag of
    electronic position fixing device; 0 = RAIM not in use = default; 1
    = RAIM in use. See Table

16. Communication state:

    1.  Sync state: 0 UTC direct (sync from own integral GPS receiver) 1
        UTC indirect (own GPS unavailable - UTC sync from GPS receiver
        on nearby ship or base station) 2 Station is synchronized to a
        base station (base direct - GPS unavailable)

        3 Station is synchronized to another station based on the
        highest number of received stations or to another mobile
        station, which is directly synchronized to a base station (GPS
        unavailable)

    2.  Slot time-out: Specifies frames remaining until a new slot is
        selected 0 means that this was the last transmission in this
        slot 1-7 means that 1 to 7 frames respectively are left until
        slot change

    3.  Sub message: The sub message depends on the current value in
        slot time-out

17. Number of bits

## NMEA messages from Gunnerus {#appendix:nmea_msgs}

**YCMTW**: (YC) Transducer Temp. (MTW) Mean Temperature of Water\
**Format**: \$--MTW,x.x,C\*hh$<$CR$>$$<$LF$>$ Format Description:

1.  Temperature, degrees

2.  Unit of Measurement, Celsius

3.  Checksum

**SDDBT**: (SD) Depth Sounder. (DBT) Depth below transducer\
**Format**: \$--DBT,x.x,f,x.x,M,x.x,F\*hh$<$CR$>$$<$LF$>$ Format
Description:

1.  Water depth, feet

2.  f = feet

3.  Water depth, meters

4.  M = meters

5.  Water depth, Fathoms

6.  F = Fathoms

7.  Checksum

**SDDBS**: (SD) Depth Sounder. (DBS) Below Surface\
**Format**: \$--DBS,x.x,f,x.x,M,x.x,F\*hh$<$CR$>$$<$LF$>$ Format
Description:

1.  Water depth, feet

2.  f = feet

3.  Water depth, meters

4.  M = meters

5.  Water depth, Fathoms

6.  F = Fathoms

7.  Checksum

**SDDPT**: (SD) Depth Sounder. (DPT) Depth of Water\
**Format**: \$--DPT,x.x,x.x,x.x\*hh$<$CR$>$$<$LF$>$ Format Description:

1.  Water depth relative to transducer, meters

2.  Offset from transducer, meters positive means distance from
    transducer to water line negative means distance from transducer to
    keel

3.  Maximum range scale in use (NMEA 3.0 and above)

4.  Checksum

**PFEC**: Propietary sentence\
**Format**: \$PFEC,,xxxxx,x,x,x,x,x,x,x\*hh$<$CR$>$$<$LF$>$ Format
Description: unknown

**PSIMSSB**: Propietary sentence, SSB SSBL position\
**Format**:
\$PSIMSSB,hhmmss.ss,cc\_\_,A,cc\_,aa\_\_,aa\_\_,aa\_\_,x.x,x.x,x.x,x.x,\*hh$<$CR$>$$<$LF$>$
Format Description:

1.  = empty or time of reception

2.  cc\_\_ = Tp code (Examples: B01, B33, B47)

3.  A = Status, A for OK and V for not OK. When the measurement is not
    OK the Error code field contains the error code

4.  cc\_\_ = Error code. Empty or a three character error code

5.  aa\_\_ = Coordinate system. C for Cartesian, P for Polar and U for
    UTM

6.  aa\_\_ = Orientation. H for vessel head up, N for North and E for
    East

7.  aa\_\_ = SW filter. M for Measured, F for Filtered and P for
    Predicted

8.  x.x = X coordinate. The Coordinate system and Orientation fields
    should be used to decode the X and Y coordinate field

9.  x.x = Y coordinate. The Coordinate system and Orientation fields
    should be used to decode the X and Y coordinate fields

10. x.x =Depth in metres

11. x.x =Expected accuracy of the position

12. aa\_\_ = Additional information. N for None, C for Compass and I for
    Inclinometer

13. x.x = First additional value. Empty, Tp compass or Tp x inclination

14. x.x = First additional value. Empty or Tp y inclination

15. \* = checksum delimiter

16. hh = empty or checksum

**GPGBS**: (GP) Global Positioning System receiver. (GBS) GPS Satellite
Fault Detection\
**Format**:
\$--GBS,hhmmss.ss,x.x,x.x,x.x,x.x,x.x,x.x,x.x\*hh$<$CR$>$$<$LF$>$ Format
Description:

1.  UTC time of the GGA or GNS fix associated with this sentence. hh is
    hours, mm is minutes, ss.ss is seconds

2.  Expected 1-sigma error in latitude (meters)

3.  Expected 1-sigma error in longitude (meters)

4.  Expected 1-sigma error in altitude (meters)

5.  ID of most likely failed satellite (1 to 138)

6.  Probability of missed detection for most likely failed satellite

7.  Estimate of bias in meters on most likely failed satellite

8.  Standard deviation of bias estimate

9.  Checksum

**GPRMC**: (GP) Global Positioning System receiver. (RMC) Recommended
Minimum Navigation Information\
This is one of the sentences commonly emitted by GPS units.\
**Format**:
\$--RMC,hhmmss.ss,A,ddmm.mm,a,dddmm.mm,a,x.x,x.x,xxxx,x.x,a\*hh$<$CR$>$$<$LF$>$
Format Description:

1.  UTC of position fix, hh is hours, mm is minutes, ss.ss is seconds.

2.  Status, A = Valid, V = Warning

3.  Latitude, dd is degrees. mm.mm is minutes.

4.  N or S

5.  Longitude, ddd is degrees. mm.mm is minutes.

6.  E or W

7.  Speed over ground, knots

8.  Track made good, degrees true

9.  Date, ddmmyy

10. Magnetic Variation, degrees

11. E or W

12. FAA mode indicator (NMEA 2.3 and later)

13. Nav Status (NMEA 4.1 and later) A=autonomous, D=differential,
    E=Estimated, M=Manual input mode N=not valid, S=Simulator, V = Valid

14. Checksum

**IIMWV**: (II) Integrated Instrumentation. (MWV) Wind Speed and Angle\
**Format**: \$--MWV,x.x,a,x.x,a\*hh$<$CR$>$$<$LF$>$ Format Description:

1.  Wind Angle, 0 to 359 degrees

2.  Reference, R = Relative, T = True

3.  Wind Speed

4.  Wind Speed Units, K/M/

5.  Status, A = Data Valid, V = Invalid

6.  Checksum

**GPVTG**: (GP) Global Positioning System receiver. (VTG) Track Made
Good and Ground Speed\
This is one of the sentences commonly emitted by GPS units.\
**Format**: \$--VTG,x.x,T,x.x,M,x.x,N,x.x,K,m\*hh$<$CR$>$$<$LF$>$ Format
Description:

1.  Course over ground, degrees True

2.  T = True

3.  Course over ground, degrees Magnetic

4.  M = Magnetic

5.  Speed over ground, knots

6.  N = Knots

7.  Speed over ground, km/hr

8.  K = Kilometers Per Hour

9.  FAA mode indicator (NMEA 2.3 and later)

10. Checksum

**GPZDA**: (GP) Global Positioning System receiver. (ZDA) Time and Date\
This is one of the sentences commonly emitted by GPS units.\
**Format**: \$--ZDA,hhmmss.ss,xx,xx,xxxx,xx,xx\*hh$<$CR$>$$<$LF$>$
Format Description:

1.  UTC time (hours, minutes, seconds, may have fractional subseconds)

2.  Day, 01 to 31

3.  Month, 01 to 12

4.  Year (4 digits)

5.  Local zone description, 00 to +- 13 hours

6.  Local zone minutes description, 00 to 59, apply same sign as local
    hours

7.  Checksum

**PSIMSNS**: (SNS) sensor values\
compliant telegram designed by Kongsberg Maritime. It holds sensor
values from a acoustic positioning transceivers. This telegram is
typically generated by a HiPAP or HPR system.\
**Format**: \$PSIMSNS,hhmmss.ss,c--c,xx\_\_,xx\_\_,x.x,x.x,x.x,x.x, , ,
, , ,\*hh$<$CR$>$$<$LF$>$

Format description

1.  PSIMSNS = talker identifier and telegram identifier

2.  hhmmss.ss = coordinated universal time (UTC) of position. The
    decimal fraction is optional

3.  xx\_\_ = Transceiver number

4.  xx\_\_ = Transducer number

5.  x.x = The roll angle in degrees

6.  x.x = The pitch angle in degrees

7.  x.x= The heave in metres

8.  x.x= The heading in degrees. A value between 0 and 360

9.  = empty field. May be used in the future

10. = empty field. May be used in the future

11. = empty field. May be used in the future

12. = empty field. May be used in the future

13. \*= checksum delimiter

14. hh= checksum

**VDVBW**: (VD) Velocity Sensor, Doppler, other/general (VBW) Dual
Ground/Water Speed\
**Format**: \$--VBW,x.x,x.x,A,x.x,x.x,A,x.x,A,x.x,A\*hh$<$CR$>$$<$LF$>$
Format Description:

1.  Longitudinal water speed, \"-\" means astern, knots

2.  Transverse water speed, \"-\" means port, knots

3.  Status, A = Data Valid

4.  Longitudinal ground speed, \"-\" means astern, knots

5.  Transverse ground speed, \"-\" means port, knots

6.  Status, A = Data Valid

7.  Stern traverse water speed, knots \*NMEA 3 and above)

8.  Status, stern traverse water speed A = Valid (NMEA 3 and above)

9.  Stern traverse ground speed, knots \*NMEA 3 and above)

10. Status, stern ground speed A = Valid (NMEA 3 and above)

11. Checksum

**GPGGA**: (GP) Global Positioning System receiver. (GGA) Global
Positioning System Fix Data\
**Format**:
\$--GGA,hhmmss.ss,ddmm.mm,a,ddmm.mm,a,x,xx,x.x,x.x,M,x.x,M,x.x,xxxx\*hh$<$CR$>$$<$LF$>$
Format Description:

1.  UTC of this position report, hh is hours, mm is minutes, ss.ss is
    seconds.

2.  Latitude, dd is degrees, mm.mm is minutes

3.  N or S (North or South)

4.  Longitude, dd is degrees, mm.mm is minutes

5.  E or W (East or West)

6.  GPS Quality Indicator (non null)

7.  Number of satellites in use, 00 - 12

8.  Horizontal Dilution of precision (meters)

9.  Antenna Altitude above/below mean-sea-level (geoid) (in meters)

10. Units of antenna altitude, meters

11. Geoidal separation, the difference between the WGS-84 earth
    ellipsoid and mean-sea-level (geoid), \"-\" means mean-sea-level
    below ellipsoid

12. Units of geoidal separation, meters

13. Age of differential GPS data, time in seconds since last SC104 type
    1 or 9 update, null field when DGPS is not used

14. Differential reference station ID, 0000-1023

15. Checksum

**VDVLW** : (VD) Velocity Sensor, Doppler, other/general. (VLW) Distance
Traveled through Water\
**Format**: \$--VLW,x.x,N,x.x,N,x.x,N,x.x,N\*hh$<$CR$>$$<$LF$>$ Format
Description:

1.  Total cumulative water distance, nm

2.  N = Nautical Miles

3.  Water distance since Reset, nm

4.  N = Nautical Miles

5.  Total cumulative ground distance, nm (NMEA 3 and above)

6.  N = Nautical Miles (NMEA 3 and above)

7.  Ground distance since reset, nm (NMEA 3 and above)

8.  N = Nautical Miles (NMEA 3 and above)

9.  Checksum

**RAOSD**: (RA) RADAR and/or ARPA. (OSD) Own Ship Data\
**Format**:
\$--OSD,x.x,A,x.x,a,x.x,a,x.x,x.x,a\*hh\<CR\>\<LF\>\*hh$<$CR$>$$<$LF$>$
Format Description:

1.  Heading, degrees True

2.  Status, A = Data Valid, V = Invalid

3.  Vessel Course, degrees True

4.  Course Reference B/M/W/R/P

5.  Vessel Speed

6.  Speed Reference B/M/W/R/P

7.  Vessel Set, degrees True

8.  Vessel drift (speed)

9.  Speed Units K/N

10. Checksum

**RATTM**: (RA) RADAR and/or ARPA. (TTM) Tracked Target Message\
**Format**:
\$--TTM,xx,x.x,x.x,a,x.x,x.x,a,x.x,x.x,a,c--c,a,a,hhmmss.ss,a\*hh$<$CR$>$$<$LF$>$
Format Description:

1.  Target Number (0-99)

2.  Target Distance

3.  Bearing from own ship

4.  T = True, R = Relative

5.  Target Speed

6.  Target Course

7.  T = True, R = Relative

8.  Distance of closest-point-of-approach

9.  Time until closest-point-of-approach \"-\" means increasing

10. Speed/distance units, K/N

11. Target name

12. Target Status

13. Reference Target

14. UTC of data (NMEA 3 and above) hh is hours, mm is minutes, ss.ss is
    seconds.

15. Type, A = Auto, M = Manual, R = Reported (NMEA 3 and above)

16. Checksum
