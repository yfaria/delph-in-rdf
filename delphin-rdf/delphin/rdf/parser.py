from rdflib import Graph
from rdflib import Literal
from rdflib import RDF
from rdflib import RDFS
from rdflib import URIRef
from rdflib import Namespace

import delphin  
from delphin import mrs

# some usefull namespaces
MRS = Namespace("http://www.delph-in.net/schema/mrs#")
ERG = Namespace("http://www.delph-in.net/schema/erg#")

def __vars_to_rdf__(m, variables, graph, VARS):
    """
    Creates nodes of variables and nodes specifying their properties.

    m - a delphin mrs instance to be parsed into RDF format.
    
    vars - list of variables of the in 'm', maybe redundant.
    
    graph - and rdflib graph that is used to store the mrs as RDF
    representation.

    VARS - the URI namespace dedicated to variables.
    """
    for v in variables.items():
        graph.add((VARS[v[0]], RDF.type, ERG[delphin.variable.type(v[0])]))
        for props in v[1].items():
            graph.add((VARS[v[0]], ERG[props[0].lower()], Literal(props[1])))
            #maybe it won't be harmful to reassure that the property is defined in ERG, but it'll be like that for now.
            
def __rels_to_rdf__(m, rels, graph, mrsi, RELS, VARS):
    """
    Creates nodes and relations of EPs and its parts.

    m - a delphin mrs instance to be parsed into RDF format.
    
    rels - list of EPs in 'm', maybe redundant.
    
    graph - and rdflib graph that is used to store the mrs as RDF
    representation.

    mrsi - the URI dedicated to the a specific MRS, which is 'm'

    RELS - the URI namespace dedicated to EPs

    VARS - the URI namespace dedicated to variables.
    """
    for rel in range(len(rels)):
        mrs_rel = rels[rel]
        rdf_rel = RELS["EP{rel}".format(rel=rel)] #maybe label EPs in a different manner is better because they aren't ordered.
        pred_rel = RELS["EP{rel}#predicate".format(rel=rel)] #revise

        graph.add((mrsi, MRS.hasEP, rdf_rel))
        graph.add((rdf_rel, RDF.type, MRS.ElementaryPredication))
        
        graph.add((rdf_rel, MRS.label, VARS[mrs_rel.label]))
        # graph.add((rdf_rel, MRS.var, VARS[mrs_rel.iv])) #not needed because ARG0 is already being included at the end of function
        graph.add((rdf_rel, MRS.hasPredicate, pred_rel))
            
        splittedPredicate = delphin.predicate.split(delphin.predicate.normalize(mrs_rel.predicate))
        if (delphin.predicate.is_surface(mrs_rel.predicate)):
            graph.add((pred_rel, RDF.type, MRS.SurfacePredicate))
            graph.add((pred_rel, MRS.hasLemma, Literal(splittedPredicate[0])))
        elif (delphin.predicate.is_abstract(mrs_rel.predicate)):
            graph.add((pred_rel, RDF.type, MRS.AbstractPredicate))
            graph.add((pred_rel, MRS.name, Literal(splittedPredicate[0])))
        else: #not(delphin.predicate.is_valid(mrs_rel.predicate))
            print("{} is an invalid predicate.".format(mrs_rel.predicate)) #revise; maybe something stronger.
            graph.add((pred_rel, RDF.type, MRS.Predicate)) #revise
            #put lemma or name?
         
        if splittedPredicate[1] is not None:
            graph.add((pred_rel, MRS.hasPos, MRS[splittedPredicate[1]]))
            
        if splittedPredicate[2] is not None:
            graph.add((pred_rel, MRS.hasSense, Literal(splittedPredicate[2])))

        graph.add((rdf_rel, MRS.cto, Literal(mrs_rel.cto)))     # integer
        graph.add((rdf_rel, MRS.cfrom, Literal(mrs_rel.cfrom))) # integer

        # parse arguments
        
        for hole, arg in mrs_rel.args.items():
            #if hole == "ARG0": continue
            # arg_type = type(eval(arg.title()))

            # mrs variables as arguments
            if arg in m.variables:
                graph.add((rdf_rel, MRS[hole.lower()], VARS[arg]))
            # any other kind of arguments
            else:
                graph.add((rdf_rel, MRS[hole.lower()], Literal(arg)))
        

def __hcons_to_rdf__(m, hcons, graph, mrsi, HCONS, VARS):
    """
    Creates nodes and relations of handle constraints of a MRS.

    m - a delphin mrs instance to be parsed into RDF format.
    
    hcons - list of HCONSs in 'm', maybe redundant.
    
    graph - and rdflib graph that is used to store the mrs as RDF
    representation.

    mrsi - the URI dedicated to the a specific MRS, which is 'm'.

    HCONS - the URI namespace dedicated to HCONSs.

    VARS - the URI namespace dedicated to variables.
    """
    for hcon in range(len(hcons)):
        mrs_hcon = hcons[hcon]
        rdf_hcon = HCONS["hcon{hcon}".format(hcon=hcon)]
        
        # adds hcon to graph
        graph.add((mrsi, MRS.hasHcons, rdf_hcon))
        graph.add((rdf_hcon, RDF.type, MRS[mrs_hcon.relation]))
        graph.add((rdf_hcon, MRS.leftHcons, VARS[mrs_hcon.hi]))
        graph.add((rdf_hcon, MRS.rightHcons, VARS[mrs_hcon.lo]))

        # this relation must be defined in MRS
        graph.add((MRS[mrs_hcon.relation], RDF.type, RDFS.Class))
        graph.add((MRS[mrs_hcon.relation], RDFS.subClassOf, MRS.Hcons))
        
def __icons_to_rdf__(m, icons, graph, mrsi, ICONS, VARS):
    """
    Creates nodes and relations of individual constraints of a MRS.

    m - a delphin mrs instance to be parsed into RDF format.
    
    icons - list of ICONSs in 'm', maybe redundant.
    
    graph - and rdflib graph that is used to store the mrs as RDF
    representation.

    mrsi - the URI dedicated to the a specific MRS, which is 'm'.

    ICONS - the URI namespace dedicated to ICONSs.

    VARS - the URI namespace dedicated to variables.
    """    
    for icon in range(len(icons)):
        mrs_icon = icons[icon]
        rdf_icon = ICONS["icon{icon}".format(icon=icon)]
        
        # adds hcon to graph
        graph.add((mrsi, MRS.hasIcons, rdf_icon))
        graph.add((rdf_icon, RDF.type, MRS[mrs_icon.relation]))
        graph.add((rdf_icon, MRS.leftIcons, VARS[mrs_icon.left])) # should be revisited
        graph.add((rdf_icon, MRS.rightIcons, VARS[mrs_icon.right])) # should be revisited

        # this relation must be defined in MRS
        graph.add((MRS[mrs_icon.relation], RDF.type, RDFS.Class))
        graph.add((MRS[mrs_icon.relation], RDFS.subClassOf, MRS.Icons))
        

def mrs_to_rdf(m, prefix: str, identifier, iname="mrsi#mrs", graph=None, out=None, text=None, format="turtle"):
    """
    Parses a pydelphin mrs into RDF representation.

    m - a delphin mrs instance to be parsed into RDF format.
    
    prefix - the URI to be prefixed to the RDF formated mrs.
    
    identifier - an string or a list of strings identifying
    the mrs. It should be unique, possibly using a composite
    identifier, given in list.
    For instance one may use it as [textid, mrs-id] if the
    same text admits various mrs interpretations.

    iname - the mrs instance name (the mrs as RDF node name)
    to be used. As default, it is "mrsi#mrs".

    graph - and rdflib graph. If given, uses it to store the
    mrs as RDF representation.

    out - filename to serialize the output into.

    text - the text that is represented in mrs as RDF. 

    format - file format to serialize the output into.
    """
    
    # making sure of the well formedness of the MRS (remove ?)
    if not(delphin.mrs.is_well_formed(m)):
        print("MRS passed is not well formed")
        return graph
    
    # same graph for different mrs
    if not graph: graph = Graph()
    if type(identifier) == list:
        identifier = "/".join(identifier)
    
    namespace = prefix + "/" + identifier + "/"

    mrsi = URIRef(namespace + iname)
    graph.add((mrsi, RDF.type, MRS.MRS))

    VARS = Namespace(namespace + "variables#")
    RELS = Namespace(namespace + "rels#")
    HCONS = Namespace(namespace + "hcons#")
    ICONS = Namespace(namespace + "icons#")

    __vars_to_rdf__(m, m.variables, graph, VARS)
    #Adding top
    graph.add((mrsi, MRS['top'], VARS[m.top]))
    #Adding index
    graph.add((mrsi, MRS['index'], VARS[m.index]))
    
    __rels_to_rdf__(m, m.rels, graph, mrsi, RELS, VARS)
    __hcons_to_rdf__(m, m.hcons, graph, mrsi, HCONS, VARS)
    __icons_to_rdf__(m, m.icons, graph, mrsi, ICONS, VARS)

    # add text as one graph node if it's given
    if text: graph.add((mrsi, MRS.text, Literal(text)))
    # serializes graph if given an output file
    if out: graph.serialize(destination=out, format=format)

    return graph
