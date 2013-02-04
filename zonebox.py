#!python

# Parse UW-III ZONE .BOX file. 
# davep 27-Jan-2013

import sys

class ParseException(Exception) : 
    pass

def tokenize( line ) : 
    # split a line into tokens
    return [ s.strip() for s in line.split() ]

def check_num_fields(num_have, num_required) : 
    if num_have != num_required : 
        errmsg = "found fields={0} but expected fields={1}".format( len(tokens), 3 )
        raise ParseException(errmsg)

def check_equal( tokens ) : 
    if tokens[1] != "=" : 
        errmsg = "didn't find \"=\" at expected position [1] in line"
        raise ParseException(errmsg)

class ZoneBox( object ) : 
    def __init__( self ) : 
        self.document_id = None
        self.zone_id = None
        self.corner_one = None
        self.corner_two = None

    def parse_document_id( self, s ) : 
        tokens = tokenize(s)
        check_num_fields(len(tokens),3)
        check_equal(tokens)

        self.document_id = tokens[2]

    def parse_zone_id( self, s ) : 
        tokens = tokenize(s)
        check_num_fields(len(tokens),3)
        check_equal(tokens)
        # zone ID is a string
        self.zone_id = tokens[2]

    def parse_corner( self, tokens ) :
        # the box file uses x,y order
        # we want explicitly row,col
        return { "row": int(tokens[3]),
                 "col": int(tokens[2])}
#        return { "row": int(tokens[2]),
#                 "col": int(tokens[3])}

    def parse_corner_one( self, s ) : 
        tokens = tokenize(s)
        check_num_fields(len(tokens),4)
        check_equal(tokens)
        self.corner_one = self.parse_corner(tokens)

    def parse_corner_two( self, s ) : 
        tokens = tokenize(s)
        check_num_fields(len(tokens),4)
        check_equal(tokens)
        self.corner_two = self.parse_corner(tokens)

    def sanity( self ) : 
        if self.document_id is None : 
            raise ParseException( "missing document_id" )
        if self.zone_id is None : 
            raise ParseException( "missing zone_id" )
        if self.corner_one is None : 
            raise ParseException( "missing corner_one" )
        if self.corner_two is None : 
            raise ParseException( "missing corner_two" )

    def __repr__( self ) : 
        return "doc={0} zone_id={1} corner_one={2} corner_two={3}".format(
                self.document_id, self.zone_id, self.corner_one,
                self.corner_two )

def parse_box_file( lines ) :
    # Parse box file into array of array of ZoneBox objects.
    #
    # box file seems to be : 
    #   { "DOCUMENT_ID" : string,
    #     "ZONE_ID" :  integer,
    #     "CORNER_ONE_RC" : integer,
    #     "CORNER_TWO_RC" : integer 
    #   }
    #
    #   Positions are upper-left and lower-right of a bounding box. Numbers are
    #   in X,Y order (as opposed to row,col order).
    #   

    box_list = []

    # simple recursive descent parser
    idx = 0
    l = lines[idx]
    idx += 1

    box = None

    while 1 : 
#        print idx, l

        if l=="BBBBB" : 
            if box is not None : 
                box_list.append(box)
                # detach the reference so the list owns it
                box = None
            box = ZoneBox()
        elif l.startswith("DOCUMENT_ID") : 
            box.parse_document_id( l ) 
        elif l.startswith("ZONE_ID") : 
            box.parse_zone_id( l ) 
        elif l.startswith("CORNER_ONE_RC") : 
            box.parse_corner_one( l ) 
        elif l.startswith("CORNER_TWO_RC") :
            box.parse_corner_two( l ) 

        else : 
            errmsg = "Invalid line of data at line {0}".format(idx)
            raise ParseException(errmsg)

        if idx >= len(lines) : 
            # save the curret box under parse
            if box is not None : 
                box_list.append(box)
                box = None

            break

        l = lines[idx]
        idx+=1

    return box_list

def load_boxes( boxfilename ) :
    infile = open(boxfilename,"r")

    lines = [ s.strip() for s in infile.readlines() ]
    infile.close()

    box_list = parse_box_file( lines ) 

    return box_list

def main() : 
    boxfilename = sys.argv[1]
    box_list = load_boxes( boxfilename ) 

    for box in box_list:
        print box
#    print box_list

if __name__=='__main__' :
    main()

