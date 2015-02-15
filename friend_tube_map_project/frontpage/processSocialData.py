import networkx as nx
import random
import os
from django.conf import settings
import community
from frontpage.models import UserSession

class ProcessSocial:

    def __init__(self, user):
        self.user = user


    def readFile(self, sessionID):
        self.file = os.path.join(settings.MEDIA_ROOT, settings.SOCIAL_FILE_SUFFIX,  '%s-graph.gml' % sessionID)
        f = open(self.file, 'r')
        #record the names in an array so we can preserve their unicode strings
        self.names = []
        i = 0
        for line in f:
            name = line.strip()
            if name.startswith('label '):
                name = name.replace('label "', '')
                name = name[0:(len(name)-1)]
                self.names.append(name)
                line = line.replace(name, str(i))
                i+=1

        f.close()

        self.readGraphs()


    def processFile(self, file):
        self.file = os.path.join(settings.MEDIA_ROOT, str(file))
        f = open(self.file, 'r')
        f_out = open(self.file+'~', 'wb')
        #record the names in an array so we can preserve their unicode strings
        self.names = []
        i = 0
        for line in f:
            name = line.strip()
            if name.startswith('label '):
                name = name.replace('label "', '')
                name = name[0:(len(name)-1)]
                self.names.append(name)
                line = line.replace(name, str(i))
                i+=1
            f_out.write(line)

        f.close()
        f_out.close()

        self.readGraphs()



    def readGraphs(self):
        self.user.setStatus('')
        self.G = nx.read_gml(self.file+'~')
        self.Tube_graph = nx.read_gml(os.path.join('media', 'tube-lines.gml'),relabel=True)
        self.NUM_STATIONS = len(self.Tube_graph.nodes())

        if len(self.G.nodes()) <= self.NUM_STATIONS / 2:
            self.user.setStatus('Not so popular are you, well we\'ll try and fill as much of the map as we can')
        elif len(self.G.nodes()) <= self.NUM_STATIONS:
            self.user.setStatus('Hmm, looks like there are more tube stations than you have friends, so there may be some original station names left over')
        elif len(self.G.nodes()) <= 3 * self.NUM_STATIONS / 2:
            self.user.setStatus('Look at the popular one over here, plenty of friends to choose from!')
        elif len(self.G.nodes()) >= 2 * self.NUM_STATIONS:
            self.user.setStatus('You must be a social butterfly with this many friends! Do you even know all of them?')


    def getRandomMapping(self, techniques=[]):
        self.user.setStatus('Time to do some fancy graph processing to fit your friends onto the tube network, just sit back and relax a moment')
        techniquesToUse = list(set(range(0, settings.NUMBER_OF_CLUSTERING_ALGORITHMS)) - set(techniques))
        if len(techniquesToUse) == 0:
            #if we've already used all clustering techniques, then just pick one at random
            clusterTechnique = random.randint(0, settings.NUMBER_OF_CLUSTERING_ALGORITHMS - 1)
        else:
            clusterTechnique = random.choice(techniquesToUse)
        if clusterTechnique == 0:
            return (self.getRandomNames(), 0)
        elif clusterTechnique == 1:
            return (self.getRandomWalkNames(), 1)
        elif clusterTechnique == 2:
            return (self.getClusteredNames(True), 2)
        else:
            return (self.getClusteredNames(False), 3)


    def getRandomNames(self):
        randomMap = random.sample(self.G.nodes(), min(len(self.G.nodes()), self.NUM_STATIONS))
        assignment = [None]* min(len(self.G.nodes()), self.NUM_STATIONS)

        assignment = dict()
        i = 0
        tubeStationSample = random.sample(self.Tube_graph.nodes(),min(len(self.G.nodes()), self.NUM_STATIONS) )
        for station in tubeStationSample:
            assignment[station] = (self.names[int(randomMap[i])])
            i+=1
        return assignment

    def getRandomWalkNames(self):
        friendCopy = self.G.to_undirected()
        tubeCopy = self.Tube_graph.to_undirected()
        assignment = dict()

        nextFriend = None
        nextStation = None

        for i in range(0, min(len(friendCopy.nodes()), self.NUM_STATIONS)):
            if nextFriend == None:
                startFriendNode = random.choice(friendCopy.nodes())
            else:
                startFriendNode = nextFriend
            if nextStation == None:
                startTubeNode = random.choice(tubeCopy.nodes())
            else:
                startTubeNode = nextStation

            assignment[startTubeNode] = self.names[startFriendNode]

            nextFriend = friendCopy.neighbors(startFriendNode)
            if len(nextFriend) == 0:
                nextFriend = None
            else:
                nextFriend = random.choice(nextFriend)

            nextStation = tubeCopy.neighbors(startTubeNode)
            if len(nextStation) == 0:
                nextStation = None
            else:
                nextStation = random.choice(nextStation)

            friendCopy.remove_node(startFriendNode)
            tubeCopy.remove_node(startTubeNode)
        return assignment


    def getClusteredNames(self, shuffle=False):

        tubePartition = {'Bond Street': 'Central', 'South Ruislip': 'Central', 'Leyton': 'Central', 'Kennington': 'Northern', 'Holland Park': 'Central', 'Lancaster Gate': 'Central', 'Highgate': 'Northern', 'West Finchley': 'Northern', 'Westbourne Park': 'Circle', 'Surrey Quays': 'Overground', 'Rayners Lane': 'Metropolitan', 'Mudchute': 'DLR', 'Woodside Park': 'Northern', 'Waterloo': 'Jubilee', 'Norwood Junction': 'Overground', 'Whitechapel': 'District', 'East Finchley': 'Northern', 'Moor Park': 'Metropolitan', 'Kensington (Olympia)': 'District', 'Poplar': 'DLR', 'Canons Park': 'Jubilee', 'Maida Vale': 'Bakerloo', 'Acton Town': 'Piccadilly', 'Sydenham': 'Overground', 'Leicester Square': 'Northern', 'Emirates Greenwich Peninsula': 'Emirates Air Line', 'Finchley Road': 'Jubilee', 'Harlesden': 'Bakerloo', 'Eastcote': 'Metropolitan', 'Baker Street': 'Circle', 'Clapham Common': 'Northern', 'Kilburn Park': 'Bakerloo', 'Harrow-on-the-Hill': 'Metropolitan', 'Hampstead Heath': 'Overground', 'Langdon Park': 'DLR', 'Park Royal': 'Piccadilly', 'Loughton': 'Central', 'Harringay Green Lanes': 'Overground', 'Upney': 'District', 'Bayswater': 'Circle', 'Kensal Rise': 'Overground', 'Chorleywood': 'Metropolitan', 'South Wimbledon': 'Northern', 'West Acton': 'Central', 'Dagenham East': 'District', 'Ruislip Gardens': 'Central', 'Kentish Town West': 'Overground', 'Kentish Town': 'Northern', 'Liverpool Street': 'Circle', 'Golders Green': 'Northern', 'Rickmansworth': 'Metropolitan', 'All Saints': 'DLR', 'Hainault': 'Central', 'Boston Manor': 'Piccadilly', 'Sudbury Town': 'Piccadilly', 'Greenwich': 'DLR', 'West Harrow': 'Metropolitan', 'Lewisham': 'DLR', 'Ruislip Manor': 'Metropolitan', 'Richmond': 'District', 'Bermondsey': 'Jubilee', 'New Cross': 'Overground', 'Hatch End': 'Overground', 'Tooting Broadway': 'Northern', 'Crouch Hill': 'Overground', 'Northwood': 'Metropolitan', 'East Ham': 'District', 'Theydon Bois': 'Central', 'Leytonstone High Road': 'Overground', 'Brent Cross': 'Northern', 'Tufnell Park': 'Northern', 'High Barnet': 'Northern', 'Latimer Road': 'Circle', 'Swiss Cottage': 'Jubilee', 'Barbican': 'Circle', 'Borough': 'Northern', 'Heron Quays': 'DLR', 'Clapham Junction': 'Overground', 'Pinner': 'Metropolitan', 'Canada Water': 'Jubilee', 'Euston Square': 'Circle', 'Camden Town': 'Northern', 'Hounslow West': 'Piccadilly', 'Great Portland Street': 'Circle', 'Preston Road': 'Metropolitan', 'Westferry': 'DLR', 'Aldgate East': 'District', 'Hornchurch': 'District', 'Hampstead': 'Northern', 'Roding Valley': 'Central', 'Ruislip': 'Metropolitan', 'Carpenders Park': 'Overground', 'Queens Road Peckham': 'Overground', 'King George V': 'DLR', 'Northwood Hills': 'Metropolitan', 'Watford Junction': 'Overground', 'Tooting Bec': 'Northern', 'Goldhawk Road': 'Circle', "St. Paul's": 'Central', 'Bow Road': 'District', 'Pontoon Dock': 'DLR', 'White City': 'Central', "Shepherd's Bush": 'Central', 'Blackhorse Road': 'Victoria', 'Upminster Bridge': 'District', "St. John's Wood": 'Jubilee', 'Southfields': 'District', 'Kilburn High Road': 'Overground', 'Highbury & Islington': 'Victoria', 'Moorgate': 'Circle', 'Croxley': 'Metropolitan', 'Elverson Road': 'DLR', 'South Kensington': 'Circle', 'Chancery Lane': 'Central', 'Warren Street': 'Northern', 'Stockwell': 'Victoria', 'South Ealing': 'Piccadilly', 'Forest Hill': 'Overground', 'North Acton': 'Central', 'West Ham': 'District', 'East India': 'DLR', 'Chalfont & Latimer': 'Metropolitan', 'Tower Gateway': 'DLR', 'Ravenscourt Park': 'District', 'Holloway Road': 'Piccadilly', 'Star Lane': 'DLR', 'Mill Hill East': 'Northern', 'West Hampstead': 'Jubilee', 'Charing Cross': 'Northern', 'Queensbury': 'Jubilee', 'Stratford High Street': 'DLR', 'Covent Garden': 'Piccadilly', 'Oxford Circus': 'Central', 'Northfields': 'Piccadilly', 'Parsons Green': 'District', 'Snaresbrook': 'Central', 'Colliers Wood': 'Northern', 'Notting Hill Gate': 'Central', 'Woolwich Arsenal': 'DLR', 'Archway': 'Northern', 'West Silvertown': 'DLR', 'Totteridge & Whetstone': 'Northern', 'Chigwell': 'Central', "Regent's Park": 'Bakerloo', 'Arsenal': 'Piccadilly', 'Perivale': 'Central', 'Euston': 'Northern', 'Elephant & Castle': 'Northern', 'Ealing Broadway': 'Central', 'Finsbury Park': 'Victoria', 'Manor House': 'Piccadilly', 'Crossharbour': 'DLR', 'Stanmore': 'Jubilee', 'High Street Kensington': 'Circle', 'Bounds Green': 'Piccadilly', 'Wembley Park': 'Metropolitan', 'Honor Oak Park': 'Overground', 'Seven Sisters': 'Victoria', 'Canning Town': 'DLR', 'Stratford International': 'DLR', 'South Quay': 'DLR', 'Gunnersbury': 'District', 'West Brompton': 'District', 'Dalston Junction': 'Overground', 'Canonbury': 'Overground', 'Chesham': 'Metropolitan', 'Penge West': 'Overground', 'Brixton': 'Victoria', 'Devons Road': 'DLR', 'Kilburn': 'Jubilee', 'Oval': 'Northern', 'Royal Victoria': 'DLR', 'Limehouse': 'DLR', 'New Cross Gate': 'Overground', 'Haggerston': 'Overground', 'Westminster': 'Circle', 'Marble Arch': 'Central', 'Newbury Park': 'Central', 'Osterley': 'Piccadilly', 'Prince Regent': 'DLR', "King's Cross St. Pancras": 'Victoria', 'Bank': 'Central', 'Chalk Farm': 'Northern', 'Cutty Sark for Maritime Greenwich': 'DLR', 'Shoreditch High Street': 'Overground', "St.James's Park": 'Circle', 'Amersham': 'Metropolitan', 'Leyton Midland Road': 'Overground', 'Tower Hill': 'Circle', 'Willesden Green': 'Jubilee', 'Gloucester Road': 'Piccadilly', 'Blackwall': 'DLR', 'Barking': 'District', 'Caledonian Road & Barnsbury': 'Overground', 'Upper Holloway': 'Overground', 'Watford High Street': 'Overground', 'Stepney Green': 'District', 'Wanstead Park': 'Overground', 'Heathrow Terminal 5': 'Piccadilly', 'Heathrow Terminal 4': 'Piccadilly', 'Finchley Road & Frognal': 'Overground', 'Hounslow East': 'Piccadilly', 'Wembley Central': 'Bakerloo', 'Hounslow Central': 'Piccadilly', 'Dalston Kingsland': 'Overground', 'Northolt': 'Central', 'Angel': 'Northern', 'Redbridge': 'Central', 'Crystal Palace': 'Overground', 'Abbey Road': 'DLR', 'Deptford Bridge': 'DLR', 'Hoxton': 'Overground', 'Clapham South': 'Northern', 'Brockley': 'Overground', 'Bromley-by-Bow': 'District', 'Fairlop': 'Central', 'Northwick Park': 'Metropolitan', 'Colindale': 'Northern', 'Walthamstow Central': 'Victoria', 'West Kensington': 'District', 'Island Gardens': 'DLR', 'Mornington Crescent': 'Northern', 'Mile End': 'Central', 'Beckton': 'DLR', 'Gospel Oak': 'Overground', 'Watford': 'Metropolitan', 'Hackney Central': 'Overground', 'Goodge Street': 'Northern', 'Hyde Park Corner': 'Piccadilly', 'Temple': 'Circle', 'Chiswick Park': 'District', 'Wandsworth Road': 'Overground', 'Arnos Grove': 'Piccadilly', 'Buckhurst Hill': 'Central', 'Old Street': 'Northern', 'South Woodford': 'Central', 'Piccadilly Circus': 'Piccadilly', 'Walthamstow Queens Road': 'Overground', 'Edgware': 'Northern', 'West India Quay': 'DLR', 'Ladbroke Grove': 'Circle', 'Wood Green': 'Piccadilly', 'Pudding Mill Lane': 'DLR', 'Brondesbury': 'Overground', 'Harrow & Wealdstone': 'Bakerloo', 'Dagenham Heathway': 'District', 'Canary Wharf': 'Jubilee', 'Cyprus': 'DLR', 'Southwark': 'Jubilee', 'Pimlico': 'Victoria', 'North Greenwich': 'Jubilee', 'Gants Hill': 'Central', 'Fulham Broadway': 'District', 'Stratford': 'Central', 'Neasden': 'Jubilee', 'London City Airport': 'DLR', 'Bethnal Green': 'Central', 'Turnpike Lane': 'Piccadilly', 'Vauxhall': 'Victoria', 'Clapham High Street': 'Overground', 'Uxbridge': 'Metropolitan', 'Kew Gardens': 'District', 'South Harrow': 'Piccadilly', 'West Ruislip': 'Central', 'Farringdon': 'Circle', 'Imperial Wharf': 'Overground', 'Ickenham': 'Metropolitan', 'Debden': 'Central', 'Tottenham Hale': 'Victoria', 'Gallions Reach': 'DLR', 'North Ealing': 'Piccadilly', 'Denmark Hill': 'Overground', 'Beckton Park': 'DLR', 'Putney Bridge': 'District', 'Royal Albert': 'DLR', 'Victoria': 'Victoria', 'Paddington': 'Bakerloo', 'Bow Church': 'District', 'Bushey': 'Overground', 'Cockfosters': 'Piccadilly', 'Upton Park': 'District', 'Barkingside': 'Central', 'Hackney Wick': 'Overground', 'Peckham Rye': 'Overground', 'Grange Hill': 'Central', 'South Hampstead': 'Overground', 'Stamford Brook': 'District', 'Elm Park': 'District', 'Kenton': 'Bakerloo', 'South Tottenham': 'Overground', 'East Putney': 'District', 'Balham': 'Northern', 'North Harrow': 'Metropolitan', 'Kensal Green': 'Bakerloo', "Shepherd's Bush Market": 'Circle', 'Blackfriars': 'Circle', 'Wapping': 'Overground', 'Warwick Avenue': 'Bakerloo', 'Edgware Road': 'Circle', 'London Bridge': 'Jubilee', 'Woodford': 'Central', 'Rotherhithe': 'Overground', 'South Acton': 'Overground', 'Hanger Lane': 'Central', 'Wimbledon Park': 'District', 'Becontree': 'District', 'Dollis Hill': 'Jubilee', 'Turnham Green': 'District', 'Epping': 'Central', 'Sudbury Hill': 'Piccadilly', 'Lambeth North': 'Bakerloo', 'Camden Road': 'Overground', 'Homerton': 'Overground', 'Marylebone': 'Bakerloo', 'Embankment': 'Circle', 'Wood Lane': 'Circle', 'Leytonstone': 'Central', 'Plaistow': 'District', 'Green Park': 'Piccadilly', 'Barons Court': 'Piccadilly', 'Acton Central': 'Overground', 'Aldgate': 'Circle', 'West Croydon': 'Overground', 'Morden': 'Northern', 'Queensway': 'Central', 'North Wembley': 'Bakerloo', 'East Acton': 'Central', "Earl's Court": 'Piccadilly', 'Anerley': 'Overground', 'Wanstead': 'Central', 'Hillingdon': 'Metropolitan', 'Southgate': 'Piccadilly', 'Heathrow Terminals 1, 2, 3': 'Piccadilly', 'South Kenton': 'Bakerloo', 'Kingsbury': 'Jubilee', 'Tottenham Court Road': 'Central', 'Hammersmith': 'Piccadilly', 'Finchley Central': 'Northern', 'Hendon Central': 'Northern', 'Oakwood': 'Piccadilly', 'Stonebridge Park': 'Bakerloo', 'Custom House for ExCel': 'DLR', "Queen's Park": 'Bakerloo', 'Holborn': 'Central', 'Knightsbridge': 'Piccadilly', 'Willesden Junction': 'Bakerloo', 'Wimbledon': 'District', 'Woodgrange Park': 'Overground', 'Burnt Oak': 'Northern', 'Mansion House': 'Circle', 'Hatton Cross': 'Piccadilly', 'Brondesbury Park': 'Overground', 'Clapham North': 'Northern', 'Alperton': 'Piccadilly', 'Cannon Street': 'Circle', 'Caledonian Road': 'Piccadilly', 'Headstone Lane': 'Overground', 'Upminster': 'District', 'Emirates Royal Docks': 'Emirates Air Line', 'Sloane Square': 'Circle', 'Monument': 'Circle', 'Ealing Common': 'Piccadilly', 'Greenford': 'Central', 'Belsize Park': 'Northern', 'Royal Oak': 'Circle', 'Russell Square': 'Piccadilly', 'Shadwell': 'DLR'}
        tubeLines = {'Jubilee': ['Stanmore', 'Canons Park', 'Queensbury', 'Kingsbury', 'Neasden', 'Dollis Hill', 'Willesden Green', 'Kilburn', 'West Hampstead', 'Finchley Road', 'Swiss Cottage', "St. John's Wood", 'Waterloo', 'Southwark', 'London Bridge', 'Bermondsey', 'Canada Water', 'Canary Wharf', 'North Greenwich'],
                    'Bakerloo': ['Harrow & Wealdstone', 'Kenton', 'South Kenton', 'North Wembley', 'Wembley Central', 'Stonebridge Park', 'Harlesden', 'Willesden Junction', 'Kensal Green', "Queen's Park", 'Kilburn Park', 'Maida Vale', 'Warwick Avenue', 'Paddington', 'Marylebone', "Regent's Park", 'Lambeth North'],
                    'Central': ['West Ruislip', 'Ruislip Gardens', 'South Ruislip', 'Northolt', 'Greenford', 'Perivale', 'Hanger Lane', 'Ealing Broadway', 'West Acton', 'North Acton', 'East Acton', 'White City', "Shepherd's Bush", 'Holland Park', 'Notting Hill Gate', 'Queensway', 'Lancaster Gate', 'Marble Arch', 'Bond Street', 'Oxford Circus', 'Tottenham Court Road', 'Holborn', 'Chancery Lane', "St. Paul's", 'Bank', 'Bethnal Green', 'Mile End', 'Stratford', 'Leyton', 'Leytonstone', 'Wanstead', 'Redbridge', 'Gants Hill', 'Newbury Park', 'Barkingside', 'Fairlop', 'Hainault', 'Grange Hill', 'Chigwell', 'Roding Valley', 'Snaresbrook', 'South Woodford', 'Woodford', 'Buckhurst Hill', 'Loughton', 'Debden', 'Theydon Bois', 'Epping'],
                    'Metropolitan': ['Amersham', 'Chesham', 'Chalfont & Latimer', 'Chorleywood', 'Rickmansworth', 'Watford', 'Croxley', 'Moor Park', 'Northwood', 'Northwood Hills', 'Pinner', 'North Harrow', 'Harrow-on-the-Hill', 'West Harrow', 'Rayners Lane', 'Eastcote', 'Ruislip Manor', 'Ruislip', 'Ickenham', 'Hillingdon', 'Uxbridge', 'Northwick Park', 'Preston Road', 'Wembley Park'],
                    'District': ['Richmond', 'Kew Gardens', 'Gunnersbury', 'Turnham Green', 'Chiswick Park', 'Stamford Brook', 'Ravenscourt Park', 'West Kensington', 'Kensington (Olympia)', 'West Brompton', 'Fulham Broadway', 'Parsons Green', 'Putney Bridge', 'East Putney', 'Southfields', 'Wimbledon Park', 'Wimbledon', 'Aldgate East', 'Whitechapel', 'Stepney Green', 'Bow Church', 'Bow Road', 'Bromley-by-Bow', 'West Ham', 'Plaistow', 'Upton Park', 'East Ham', 'Barking', 'Upney', 'Becontree', 'Dagenham Heathway', 'Dagenham East', 'Elm Park', 'Hornchurch', 'Upminster Bridge', 'Upminster'],
                    'Piccadilly': ['South Harrow', 'Sudbury Hill', 'Sudbury Town', 'Alperton', 'Park Royal', 'North Ealing', 'Ealing Common', 'Acton Town', 'South Ealing', 'Northfields', 'Boston Manor', 'Osterley', 'Hounslow East', 'Hounslow Central', 'Hounslow West', 'Hatton Cross', 'Heathrow Terminals 1, 2, 3', 'Heathrow Terminal 4', 'Heathrow Terminal 5', 'Hammersmith', 'Barons Court', "Earl's Court", 'Gloucester Road', 'Knightsbridge', 'Hyde Park Corner', 'Green Park', 'Piccadilly Circus', 'Covent Garden', 'Russell Square', 'Caledonian Road', 'Holloway Road', 'Arsenal', 'Manor House', 'Turnpike Lane', 'Wood Green', 'Bounds Green', 'Arnos Grove', 'Southgate', 'Oakwood', 'Cockfosters'],
                    'Overground': ['Watford Junction', 'Watford High Street', 'Bushey', 'Carpenders Park', 'Hatch End', 'Headstone Lane', 'South Acton', 'Acton Central', 'Imperial Wharf', 'Clapham Junction', 'Wandsworth Road', 'Clapham High Street', 'Denmark Hill', 'Peckham Rye', 'Queens Road Peckham', 'New Cross Gate', 'New Cross', 'Brockley', 'Honor Oak Park', 'Forest Hill', 'Sydenham', 'Penge West', 'Crystal Palace', 'Anerley', 'Norwood Junction', 'West Croydon', 'Surrey Quays', 'Rotherhithe', 'Wapping', 'Shoreditch High Street', 'Hoxton', 'Haggerston', 'Dalston Junction', 'Canonbury', 'Dalston Kingsland', 'Hackney Central', 'Homerton', 'Hackney Wick', 'Woodgrange Park', 'Wanstead Park', 'Leytonstone High Road', 'Leyton Midland Road', 'Walthamstow Queens Road', 'South Tottenham', 'Harringay Green Lanes', 'Crouch Hill', 'Upper Holloway', 'Gospel Oak', 'Caledonian Road & Barnsbury', 'Camden Road', 'Kentish Town West', 'Finchley Road & Frognal', 'Hampstead Heath', 'Brondesbury', 'Brondesbury Park', 'Kensal Rise', 'Kilburn High Road', 'South Hampstead'],
                    'Victoria': ['Walthamstow Central', 'Blackhorse Road', 'Tottenham Hale', 'Seven Sisters', 'Finsbury Park', 'Highbury & Islington', "King's Cross St. Pancras", 'Victoria', 'Pimlico', 'Vauxhall', 'Stockwell', 'Brixton'],
                    'DLR': ['Tower Gateway', 'Shadwell', 'Limehouse', 'Westferry', 'West India Quay', 'Heron Quays', 'South Quay', 'Crossharbour', 'Mudchute', 'Island Gardens', 'Cutty Sark for Maritime Greenwich', 'Greenwich', 'Deptford Bridge', 'Elverson Road', 'Lewisham', 'Woolwich Arsenal', 'King George V', 'London City Airport', 'Pontoon Dock', 'West Silvertown', 'Royal Victoria', 'Custom House for ExCel', 'Prince Regent', 'Royal Albert', 'Beckton Park', 'Cyprus', 'Gallions Reach', 'Beckton', 'Stratford International', 'Pudding Mill Lane', 'Devons Road', 'Langdon Park', 'All Saints', 'Poplar', 'Blackwall', 'East India', 'Canning Town', 'Star Lane', 'Abbey Road', 'Stratford High Street'],
                    'Circle': ['Edgware Road', 'Bayswater', 'High Street Kensington', 'South Kensington', 'Sloane Square', "St.James's Park", 'Westminster', 'Embankment', 'Temple', 'Blackfriars', 'Mansion House', 'Cannon Street', 'Monument', 'Tower Hill', 'Aldgate', 'Liverpool Street', 'Moorgate', 'Barbican', 'Farringdon', 'Euston Square', 'Great Portland Street', 'Baker Street', 'Royal Oak', 'Westbourne Park', 'Ladbroke Grove', 'Latimer Road', 'Wood Lane', "Shepherd's Bush Market", 'Goldhawk Road'],
                    'Northern': ['Edgware', 'Burnt Oak', 'Colindale', 'Hendon Central', 'Brent Cross', 'Golders Green', 'Hampstead', 'Belsize Park', 'Chalk Farm', 'Camden Town', 'Kentish Town', 'Tufnell Park', 'Archway', 'Highgate', 'East Finchley', 'Finchley Central', 'Mill Hill East', 'West Finchley', 'Woodside Park', 'Totteridge & Whetstone', 'High Barnet', 'Mornington Crescent', 'Euston', 'Warren Street', 'Goodge Street', 'Leicester Square', 'Charing Cross', 'Morden', 'South Wimbledon', 'Colliers Wood', 'Tooting Broadway', 'Tooting Bec', 'Balham', 'Clapham South', 'Clapham Common', 'Clapham North', 'Oval', 'Kennington', 'Elephant & Castle', 'Borough', 'Old Street', 'Angel'],
                    'Emirates Air Line': ['Emirates Greenwich Peninsula', 'Emirates Royal Docks']}


        friendPartition = community.best_partition(self.G)


        self.user.setStatus('...delays on the ' + random.choice(tubeLines.keys()) + ' Line...')

        friendClusters = cluster(friendPartition, self.G)

        tubeClusters = cluster(tubePartition, self.Tube_graph)

        friendBins = friendClusters.getBins()
        tubeBins = tubeClusters.getBins()

        clusterMap = friendClusters.findOptimalBinMapping(friendBins, tubeBins)

        emergencies = ['an emergency flood', 'a fist fight', 'an earthquake', 'case of Godzilla', 'defusing a bomb', 'driving the tube train']
        self.user.setStatus('Shouldn\'t be long now, just determining which of your friends would be ideal backup in ' + random.choice(emergencies))

        assignment = dict()

        for line in clusterMap:
            friends = []
            for i in range(0, len(clusterMap[line])):
                friends = friends + friendClusters.getRandomWalk(clusterMap[line][i][0], clusterMap[line][i][1], self.G)

            stations = tubeLines[line]
            if shuffle:
                random.shuffle(stations)

            for i in range(0, min(len(friends), len(stations))):
                assignment[stations[i]] = self.names[friends[i]]

        return assignment

class cluster:

    def __init__(self, part, G):
        self.clusters = dict()
        self.clusterNeighours = dict()
        for node in part:
            if part[node] not in self.clusters:
                self.clusters[part[node]] = []
            self.clusters[part[node]].append(node)

            neighbours = nx.all_neighbors(G, node)
            for neighbour in neighbours:
                if part[neighbour] != part[node]:
                    if (part[node], part[neighbour]) not in self.clusterNeighours:
                        self.clusterNeighours[(part[node], part[neighbour])] = []
                    self.clusterNeighours[(part[node], part[neighbour])].append((node, neighbour))

    def getBins(self):

        bins = []
        for partition in self.clusters:
            bins.append([partition, len(self.clusters[partition])])
        return bins

    def getRandomSample(self, clusterName, sampleSize):
        partition = self.clusters[clusterName]
        sample = []
        for i in range(0, min(sampleSize, len(partition))):
            random.shuffle(partition)
            sample.append(partition.pop())
        self.clusters[clusterName] = partition
        return sample

    def findOptimalBinMapping(self, tangible, fixed):
        t = sorted(tangible, key=lambda tup: tup[1])
        f = sorted(fixed, key=lambda tup: tup[1], reverse=True)

        mapping = dict()
        for i in range(0, len(f)):
            mapping[f[i][0]] = []
            for j in range(0, len(t)):
                if t[j][1] >= f[i][1]:
                    mapping[f[i][0]].append((t[j][0], f[i][1]))
                    t[j][1] -= f[i][1]
                    f[i][1] = 0
                    break
            if f[i][1] == 0:
                continue
            for j in xrange(len(t) - 1, -1, -1):
                if t[j][1] == 0:
                    continue
                tBefore = t[j][1]
                fBefore = f[i][1]
                f[i][1] = max(f[i][1] - t[j][1], 0)
                t[j][1] = max(t[j][1] - fBefore, 0)

                mapping[f[i][0]].append((t[j][0], tBefore - t[j][1]))
                if f[i][1] == 0:
                    break

        return mapping

    def getRandomWalk(self, clusterName, sampleSize, G):
        partition = self.clusters[clusterName]
        partitionGraph = G.subgraph(partition).to_undirected()

        sample = []


        nextFriend = None

        for i in range(0, sampleSize):
            if nextFriend == None:
                startFriendNode = random.choice(partitionGraph.nodes())
            else:
                startFriendNode = nextFriend

            sample.append(startFriendNode)

            nextFriend = partitionGraph.neighbors(startFriendNode)
            if len(nextFriend) == 0:
                nextFriend = None
            else:
                nextFriend = random.choice(nextFriend)

            partitionGraph.remove_node(startFriendNode)

        for friend in sample:
            self.clusters[clusterName].remove(friend)

        return sample