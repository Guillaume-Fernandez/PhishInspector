from geoip import geolite2
match = geolite2.lookup('8.8.8.8')
return match.country, match.timezone, match.location[0], match.location[1]
