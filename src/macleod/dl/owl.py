import functools
import itertools
import xml.etree.ElementTree as ET
import enum as Enum
import xml.dom.minidom
import logging

class Owl(object):
    """
    Class wrapper for an OWL/XML formatted file with convenience wrappers for
    adding owl specific data
    """

    tld = "http://macleod.org/"

    class Connectives(Enum.Enum):
        UNION = 0
        INTERSECTION = 1

    class Relations(Enum.Enum):
        NORMAL = 0
        INVERSE = 1
        OTHER = 2

    class Profile(Enum.Enum):
        OWL2_FULL = 0
        OWL2_DL = 1
        OWL2_RL = 2
        OWL2_QL = 3
        OWL2_EL = 4

    def get_profile_string(self):
        if self.profile == Owl.Profile.OWL2_DL:
            return "owl2-DL"
        if self.profile == Owl.Profile.OWL2_RL:
            return "owl2-RL"
        if self.profile == Owl.Profile.OWL2_QL:
            return "owl2-QL"
        if self.profile == Owl.Profile.OWL2_EL:
            return "owl2-EL"
        else:
            return "owl2"


    def __init__(self, filename, uri, profile):
        """
        Create a new Owl class

        :param str name, name used to internally reference the ontology
        """

        template = '''<?xml version="1.0"?>
        <Ontology xmlns="http://www.w3.org/2002/07/owl#"
            xml:base="{0}#"
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            xmlns:xml="http://www.w3.org/XML/1998/namespace"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
            xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
            ontologyIRI="{0}"
            versionIRI="{0}">
            <Prefix name="" IRI="{0}#"/>
            <Prefix name="owl" IRI="http://www.w3.org/2002/07/owl#"/>
            <Prefix name="rdf" IRI="http://www.w3.org/1999/02/22-rdf-syntax-ns#"/>
            <Prefix name="xml" IRI="http://www.w3.org/XML/1998/namespace"/>
            <Prefix name="xsd" IRI="http://www.w3.org/2001/XMLSchema#"/>
            <Prefix name="rdfs" IRI="http://www.w3.org/2000/01/rdf-schema#"/>
        </Ontology>
        '''

        #
        self.profile = profile

        self.name = filename
        self.base_uri = uri
        self.uri = ''
        self.properties = {}
        self.classes = {}
        self.individuals = {}
        start = template.format(self.base_uri)
        ET.register_namespace('', 'http://www.w3.org/2002/07/owl#')
        ET.register_namespace('rdf', 'http://www.w3.org/2000/01/rdf-schema#')
        ET.register_namespace('xml', 'http://www.w3.org/XML/1998/namespace')
        ET.register_namespace('xsd', "http://www.w3.org/2001/XMLSchema#")
        ET.register_namespace('rdfs', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        self.root = ET.fromstring(start)

        # TODO keeping track of more advanced constructs
        # want a set to not have to manually deal with duplicates
        self.disjointclasses = set()
        self.simple_subclasses = set()
        self.complex_subclasses = []

        self.disjoints_processed = False
        self.equivalents_processed = False

        # these are maintained for statistical purposes
        self.disjointclasses_backup = set()
        self.simple_subclasses_backup = set()
        self.complex_subclasses_backup = []
        self.equivalent_classes = 0
        self.disjoint_classes = 0
        self.subproperties = 0
        self.disjointproperties = 0
        self.domain_range_properties = 0
        self.properties_other = 0
        self.quantified_class_axioms = 0
        self.propositional_constructs = 0
        self.inverses = 0
        self.chains = 0

    def tostring(self, pretty_print=False):

        # make sure that the simple subclasses are added (if it hasn't been done yet) before producing XML
        self.add_simple_subclasses()
        xmlstring = ET.tostring(self.root, encoding="unicode", short_empty_elements=False)
        if not pretty_print:
            return xmlstring
        else:
            dom = xml.dom.minidom.parseString(xmlstring)
            return dom.toprettyxml()



    def declare_class(self, class_name):
        """
        Add a class to the OWL ontology

        :param str class_name
        :return Element class
        """

        if class_name not in self.classes:
            declaration = ET.SubElement(self.root, 'Declaration')
            owl_class = ET.SubElement(declaration, 'Class', attrib={'IRI': self.uri + class_name})
            self.classes[class_name] = owl_class
            return owl_class

    def declare_property(self, property_name):
        """
        Add a property to the OWL ontology

        :param str property_name
        :return Element property
        """

        if property_name not in self.properties:
            declaration = ET.SubElement(self.root, 'Declaration')
            owl_property = ET.SubElement(declaration, 'ObjectProperty', attrib={'IRI': self.uri + property_name})
            self.properties[property_name] = owl_property
            return owl_property

    def declare_individual(self, individual_name):
        """
        Add a class to the OWL ontology

        :param str class_name
        :return Element class
        """

        declaration = ET.SubElement(self.root, 'Declaration')
        owl_individual = ET.SubElement(declaration, 'NamedIndividual', attrib={'IRI': self.uri + individual_name})
        self.individuals[individual_name] = owl_individual
        return owl_individual

    def class_assertion(self, classname, individual):
        """
        Declare that an individual is of type classname
        """

        assertion = ET.SubElement(self.root, 'ClassAssertion')
        assertion.append(self.classes[classname])
        assertion.append(self.individuals[individual])

        return assertion

    def property_assertion(self, property_name, individuals):
        """
        Declare that an individual is of type classname
        """

        assertion = ET.SubElement(self.root, 'ObjectPropertyAssertion')
        assertion.append(self.properties[property_name])
        assertion.append(self.individuals[individuals[0]])
        assertion.append(self.individuals[individuals[1]])

        return assertion

    def negative_property_assertion(self, property_name, individuals):
        """
        Declare that an individual is of type classname
        """

        assertion = ET.SubElement(self.root, 'NegativeObjectPropertyAssertion')
        assertion.append(self.properties[property_name])
        assertion.append(self.individuals[individuals[0]])
        assertion.append(self.individuals[individuals[1]])

        return assertion



    def add_subclass(self, subclass, superclass):
        """
        Adds a subclass property to the OWL ontology. Assumes that both the subclass has already been added.

        :param list subclass, list of subclass names
        :param list superclass, list of superclass names
        """

        saved_subclass = None
        #print(repr(subclass) + " is a subclass of " + repr(superclass))

        if len(subclass) > 1:
            subclass_element = self._get_object_intersection(subclass)
        else:
            # single subclass
            subclass_element = self.classes[subclass[0]]

        if len(superclass) > 1:
            superclass_element = self._get_object_union(superclass)
            # TODO: really want to check whether this makes an EquivalentClass construct
            #print("Found Object Union in Superclass to " + repr(saved_subclass))
        else:
            superclass_element = self.classes[superclass[0]]
            #self.subclass_of_single_class.append((saved_subclass, superclass[0]))

        if len(subclass)== 1 and len(superclass)==1:
            self.simple_subclasses.add((subclass[0], superclass[0]))
        elif len(subclass)== 1 or len(superclass)==1:
            self.complex_subclasses.append((subclass, superclass))
        # do not keep track of n-to-m subclass relationships (intersection subclass of union)

        return None

    def add_subproperty(self, subproperty, superproperty):
        """
        Adds a subproperty property to the OWL ontology. Assumes that both subproperties have already been added.

        :param Tuple(str, Owl.Relations) subproperty
        :param Tuple(str, Owl.Relations) superproperty
        """
        sup_name, sup_state = superproperty
        if sup_state == Owl.Relations.INVERSE:
            if self.profile in [Owl.Profile.OWL2_EL]:
                return
            sup_element = self._get_object_inverse(sup_name)
        else:
            sup_element = self.properties[sup_name]

        # need to distinguish simple subproperties from subproperty chains
        if isinstance(subproperty, tuple):
            sub_name, sub_state = subproperty
            if sub_state == Owl.Relations.INVERSE:
                if self.profile in [Owl.Profile.OWL2_EL]:
                    return
                sub_element = self._get_object_inverse(sub_name)
            else:
                sub_element = self.properties[sub_name]
        else:
            if self.profile in [Owl.Profile.OWL2_EL, Owl.Profile.OWL2_QL]:
                return
            sub_element = self._get_property_chain(subproperty)

        subproperty_declaration = ET.Element('SubObjectPropertyOf')

        subproperty_declaration.append(sub_element)
        subproperty_declaration.append(sup_element)
        self.root.append(subproperty_declaration)

        self.subproperties += 1
        return subproperty_declaration

    def _get_object_union(self, union_classes):
        """
        Utility method which returns an ObjectUnionOf property for use in
        declarations.  Assumes that each class name provided has already been created. 

        :param lst(str) union, list of class names part of the union
        """

        union = ET.Element('ObjectUnionOf')
        for c in union_classes:
            if isinstance(c, tuple):
                # Sign information provided
                name, sign = c
                if sign == Owl.Relations.NORMAL:
                    #print(name, 'This one')
                    union.append(self.classes[name])
                elif sign == Owl.Relations.INVERSE:
                    union.append(self._get_object_complement(name))
                else:
                    #print(sign, name)
                    raise ValueError("HUH")
            else:
                union.append(self.classes[c])

        #print(union_classes, ET.tostring(union))

        self.propositional_constructs += 1
        return union

    def _get_object_intersection(self, intersection_classes):
        """
        Utility method which returns an ObjectIntersectionOf property for use in
        declarations.  Assumes that each class name provided has already been created.

        :param lst(str) intersection, list of class names part of the intersection
        """

        intersection = ET.Element('ObjectIntersectionOf')
        for c in intersection_classes:
            if isinstance(c, tuple):
                # Sign information provided
                name, sign = c
                if sign == Owl.Relations.NORMAL:
                    intersection.append(self.classes[name])
                elif sign == Owl.Relations.INVERSE:
                    intersection.append(self._get_object_complement(name))
            else:
                name = c
                intersection.append(self.classes[name])

        self.propositional_constructs += 1
        return intersection

    def _get_property_chain(self, properties):
        """
        Utility method which returns an ObjectUnionOf property for use in
        declarations.  Assumes that each class name provided has already been created.

        :param lst(str) union, list of class names part of the union
        """

        chain = ET.Element('ObjectPropertyChain')
        for p in properties:
            if isinstance(p, tuple):
                # Sign information provided
                name, sign = p
                if sign == Owl.Relations.NORMAL:
                    chain.append(self.properties[name])
                elif sign == Owl.Relations.INVERSE:
                    chain.append(self._get_object_inverse([name]))
            else:
                raise ValueError("HUH")

        self.chains += 1
        return chain

    def _get_object_inverse(self, inverted_property):
        """
        Utility method which returns an ObjectInverseOf property for use in
        declarations.  Assumes that the property name provided has already been created.

        :param lst(str) inverted_property, prperty to obtain the inverse of
        """

        inverse = ET.Element('ObjectInverseOf')
        inverse.append(self.properties[inverted_property])

        self.inverses += 1
        return inverse

    def _get_object_complement(self, inverted_class):
        """
        Utility method which returns an ObjectComplementOf class for use in
        declarations.  Assumes that the class name provided has already been created. 

        :param lst(str) inverted_class, class to obtain the inverse of
        """

        inverse = ET.Element('ObjectComplementOf')
        inverse.append(self.classes[inverted_class])

        self.propositional_constructs += 1
        return inverse

    def add_equivalent_classes(self, equivalent_classes):
        """
        Add an axiom declaring equivalence among a list of classes. If the list
        contains a tuple then proceed with the correct connective
        """

        equivalent = ET.Element('EquivalentClasses')
        for c in equivalent_classes:

            if isinstance(c, tuple):
                group = None
                if c[0] == Owl.Connectives.UNION:
                    group = self._get_object_union(c[1])
                elif c[0] == Owl.Connectives.INTERSECTION:
                    group = self._get_object_intersection(c[1])

                if group is not None:
                    equivalent.append(group)
                else:
                    print("Wat")
            else:
                equivalent.append(self.classes[c])
        self.root.append(equivalent)

        return equivalent

    def add_equivalent_properties(self, equivalent_properties):
        """
        Add an axiom declaring equivalence among a list of properties. If the list
        contains a tuple then proceed with the correct connective

        :param List(Tuple(str, int)), list of tuples for properties
        :return Et.Element, reference added declaration
        """

        equivalent = ET.Element('EquivalentObjectProperties')

        for pair in itertools.combinations(equivalent_properties, 2):
            print(pair)
            for prop, state in pair:
                if state == Owl.Relations.INVERSE:
                    prop = self._get_object_inverse(prop)
                equivalent.append(self.properties[prop])

        self.root.append(equivalent)

        return equivalent

    def add_disjoint_classes(self, disjoint_pair):
        """
        Add an axiom declaring that two classes are disjoint
        """

        new = True
        # keeping track of SETS of disjoint classes (multiple pairs)
        self.disjointclasses.add((disjoint_pair[0], disjoint_pair[1]))
        self.disjointclasses.add((disjoint_pair[1], disjoint_pair[0]))

        # for d in self.disjointclasses:
        #     if disjoint_pair[0] in d:
        #         if not (disjoint_pair[1] in d):
        #             d.append(disjoint_pair[1])
        #         new = False
        #         break
        #     elif disjoint_pair[1] in d:
        #         if not (disjoint_pair[0] in d):
        #             d.append(disjoint_pair[0])
        #         new = False
        #         break
        # if new:
        #     self.disjointclasses.append([disjoint_pair[0], disjoint_pair[1]])

        # do nothing immediately --> only processed at the very end
        # disjoint = ET.Element('DisjointClasses')
        # disjoint.append(self.classes[disjoint_pair[0]])
        # disjoint.append(self.classes[disjoint_pair[1]])
        # self.root.append(disjoint)

    def add_disjoint_properties(self, disjoint_pair):
        """
        Add an axiom declaring that two classes are disjoint
        """

        if self.profile in [Owl.Profile.OWL2_EL]:
            return

        disjoint = ET.Element('DisjointObjectProperties')
        property_one, property_two = disjoint_pair

        element_one = self._get_object_inverse(property_one[0]) if property_one[1] == Owl.Relations.INVERSE else self.properties[property_one[0]]
        element_two = self._get_object_inverse(property_two[0]) if property_two[1] == Owl.Relations.INVERSE else self.properties[property_two[0]]
        disjoint.append(element_one)
        disjoint.append(element_two)
        self.root.append(disjoint)

        self.disjointproperties += 1

    def declare_reflexive_property(self, reflexive_property):
        """
        Add a declaration that a property is reflexive
        """

        if self.profile in [Owl.Profile.OWL2_RL]:
            return

        reflexive = ET.Element('ReflexiveObjectProperty')
        reflexive.append(self.properties[reflexive_property])
        self.root.append(reflexive)

        self.properties_other += 1

    def declare_irreflexive_property(self, irreflexive_property):
        """
        Add a declaration that a property is reflexive
        """
        if self.profile in [Owl.Profile.OWL2_EL]:
            return

        irreflexive = ET.Element('IrreflexiveObjectProperty')
        irreflexive.append(self.properties[irreflexive_property])
        self.root.append(irreflexive)

        self.properties_other += 1

    def declare_symmetric_property(self, symmetric_property):
        """
        Add a declaration that a property is reflexive
        """
        if self.profile in [Owl.Profile.OWL2_EL]:
            return

        symmetric = ET.Element('SymmetricObjectProperty')
        symmetric.append(self.properties[symmetric_property])
        self.root.append(symmetric)

        self.properties_other += 1

    def declare_asymmetric_property(self, asymmetric_property):
        """
        Add a declaration that a property is reflexive
        """

        if self.profile in [Owl.Profile.OWL2_EL]:
            return

        asymmetric = ET.Element('AsymmetricObjectProperty')
        asymmetric.append(self.properties[asymmetric_property])
        self.root.append(asymmetric)

        self.properties_other += 1

    def declare_transitive_property(self, transitive_property):
        """
        Add a declaration that a property is reflexive
        """

        if self.profile in [Owl.Profile.OWL2_QL]:
            return

        transitive = ET.Element('TransitiveObjectProperty')
        transitive.append(self.properties[transitive_property])
        self.root.append(transitive)

        self.properties_other += 1

    def declare_functional_property(self, functional_property):
        """
        Add a declaration that a property is reflexive
        """

        if self.profile in [Owl.Profile.OWL2_EL, Owl.Profile.OWL2_QL]:
            return

        functional = ET.Element('FunctionalObjectProperty')
        functional.append(self.properties[functional_property])
        self.root.append(functional)

        self.properties_other += 1

    def declare_inverse_functional_property(self, functional_property):
        """
        Add a declaration that a property is reflexive
        """
        if self.profile in [Owl.Profile.OWL2_EL, Owl.Profile.OWL2_QL]:
            return

        functional = ET.Element('InverseFunctionalObjectProperty')
        functional.append(self.properties[functional_property])
        self.root.append(functional)

        self.properties_other += 1

    def declare_range_restriction(self, prop, restriction):
        """
        :param prop str, name of property being restricted
        :param list(tuple) restriction, list of tuples for classes
        """

        rr = ET.Element('ObjectPropertyRange')
        rr.append(self.properties[prop])

        if len(restriction) > 1:
            if self.profile in [Owl.Profile.OWL2_RL, Owl.Profile.OWL2_QL, Owl.Profile.OWL2_EL]:
                return
            restriction_element = self._get_object_union(restriction)
        else:
            name, state = restriction[0]

            if state == Owl.Relations.INVERSE:
                if self.profile in [Owl.Profile.OWL2_EL]:
                    return
                restriction_element = self._get_object_complement(name)
            else:
                restriction_element = self.classes[name]

        rr.append(restriction_element)

        self.root.append(rr)

        self.domain_range_properties += 1

    def declare_domain_restriction(self, prop, restriction):
        """
        Add a declaration that a property is range restricted
        """

        dr = ET.Element('ObjectPropertyDomain')
        dr.append(self.properties[prop])

        if len(restriction) > 1:
            if self.profile in [Owl.Profile.OWL2_RL, Owl.Profile.OWL2_QL, Owl.Profile.OWL2_EL]:
                return
            restriction_element = self._get_object_union(restriction)
        else:
            name, state = restriction[0]

            if state == Owl.Relations.INVERSE:
                if self.profile in [Owl.Profile.OWL2_EL]:
                    return
                restriction_element = self._get_object_complement(name)
            else:
                restriction_element = self.classes[name]

        dr.append(restriction_element)

        self.root.append(dr)

        self.domain_range_properties += 1

    def declare_all_values_from_subclass(self, relation, subclass, limit):
        """
        Add a subclass axiom where the superclass is a allValuesFrom class expression
        
        :param str relation, name of relation universal is over
        :param list(str) subclass, list of subclass names joined in union
        :param list(str) limit, list of limiting class names
        """

        if self.profile in [Owl.Profile.OWL2_EL, Owl.Profile.OWL2_QL]:
            return

        # TODO: For now just make the whole subclass here instead of naming the anonymous
        #       class that is defined by the allValuesFrom. The approach affects the profile
        #       that the produced ontology will fall into.
        subclass_element = ET.Element('SubClassOf')

        if len(subclass) == 1:
            if subclass[0][1] == Owl.Relations.NORMAL:
                subclass_element.append(self.classes[subclass[0][0]])
            else:
                if self.profile in [Owl.Profile.OWL2_RL, Owl.Profile.OWL2_QL]:
                    return
                subclass_element.append(self._get_object_complement(subclass[0][0]))
        else:
            subclass_element.append(self._get_object_intersection(subclass))

        all_values_from = ET.Element('ObjectAllValuesFrom')
        (property, inverted) = relation
        if inverted == Owl.Relations.INVERSE:
            # Disallowed in certain OWL2 Profiles
            if self.profile in [Owl.Profile.OWL2_RL, Owl.Profile.OWL2_QL, Owl.Profile.OWL2_EL]:
                return
            all_values_from.append(self._get_object_inverse(property))
        else:
            all_values_from.append(self.properties[property])

        # limit need to have at least one element
        if len(limit) == 1:
            if limit[0][1] == Owl.Relations.NORMAL:
                all_values_from.append(self.classes[limit[0][0]])
            else:
                all_values_from.append(self._get_object_complement(limit[0][0]))
        elif len(limit) > 1:
            all_values_from.append(self._get_object_union(limit))

        subclass_element.append(all_values_from)
        self.root.append(subclass_element)

        self.quantified_class_axioms += 1

    def declare_some_values_from_subclass(self, relation, subclass, limit):
        """
        Add a subclass axiom where the superclass is a allValuesFrom class expression
        """

        # TODO: For now just make the whole subclass here instead of naming the anonymous
        #       class that is defined by the allValuesFrom. The approach affects the profile
        #       that the produced ontology will fall into.
        subclass_element = ET.Element('SubClassOf')


        if len(subclass) > 1:
            subclass_element.append(self._get_object_intersection(subclass))
        else:
            subclass_element.append(self.classes[subclass[0]])

        some_values_from = ET.Element('ObjectSomeValuesFrom')
        some_values_from.append(self.properties[relation])

        if len(limit) > 1:
            some_values_from.append(self._get_object_union(limit))
        else:
            some_values_from.append(self.classes[limit[0]])

        subclass_element.append(some_values_from)
        self.root.append(subclass_element)

        self.quantified_class_axioms += 1

    def declare_universe(self, superclass):
        """
        Add a subclass axiom where the superclass is a allValuesFrom class expression
        """

        # TODO: For now just make the whole subclass here instead of naming the anonymous
        #       class that is defined by the allValuesFrom. The approach affects the profile
        #       that the produced ontology will fall into.
        subclass_element = ET.Element('SubClassOf')
        if len(superclass) > 1:
            superclass_element = self._get_object_union(superclass)
        else:
            superclass_element = self.classes[superclass[0]]

        owl_class = ET.Element('Class', attrib={'abbreviatedIRI':'owl:Thing'})
        subclass_element.append(owl_class)
        subclass_element.append(superclass_element)

        self.root.append(subclass_element)

    def infer_disjoint_classes(self):
        """
        Adds sets of pairwise disjoint classes to the XML output, deletes the temporary information
        :return:
        """

        if not self.disjoints_processed:

            self.disjointclasses_backup = self.disjointclasses.copy()

            #print(repr(self.disjointclasses))

            disjoints = list(self.disjointclasses)

            disjointsets = []

            while len(disjoints)>0:
                (c1, c2) = disjoints.pop()
                #print("Processing disjoint classes " + c1 + ", " + c2)
                #print ("Current disjoint set " + repr(disjointsets))
                # check if c1 is in any set in disjointsets
                sets = [c for c in disjointsets if c1 in c]
                #print (repr(sets))
                # now check whether c2 is also in the set in disjointsets
                if len(sets)==0:
                    disjointsets.append([c1, c2])
                else:
                    create_set = True
                    for aset in sets:
                        if c2 in aset:
                            # do nothing: c1 and c2 are already part of the same set
                            create_set = False
                            continue
                        elif len([c for c in aset if (c2,c) not in self.disjointclasses])==0:
                            # check whether c2 is disjoint with all other classes in set
                            #print("Appending " + c2 + " to set " + repr(set))
                            aset.append(c2)
                            create_set = False
                            break
                    if create_set:
                        #print("Creating new disjoint set")
                        disjointsets.append([c1,c2])

            #print("Resulting Lists of Disjoint Classes = " + str(len(disjointsets)))

            # convert disjointsets to a set of sets to eliminate duplicates
            disjointsets = [set(x) for x in disjointsets]
            dsets = []
            for d in disjointsets:
                if d not in dsets:
                    dsets.append(d)
            logging.getLogger(__name__).info("Reduced {0} pairs to {1} sets of disjoint classes".format(int(len(self.disjointclasses)/2),len(dsets)))
            #print("Pairs of Disjoint Classes = " + str(len(self.disjointclasses)/2))
            #print("Resulting Sets of Disjoint Classes = " + str(len(dsets)))

            for d in dsets:
                #print(repr(d))
                disjoint = ET.Element('DisjointClasses')
                for c in d:
                    disjoint.append(self.classes[c])
                self.root.append(disjoint)

                self.disjoint_classes += 1

            self.disjoints_processed = True

    def infer_equivalent_classes(self):
        """
        Inferring any equivalent class definitions from subclass definitions that use unions
        :return:
        """
        #print("Sets of Subclasses of Class Unions = " + str(len(self.subclass_of_class_union)))
        #print("Starting with " + str(len(self.simple_subclasses)) + " sets of Simple Subclasses")

        if not self.equivalents_processed:

            self.simple_subclasses_backup = self.simple_subclasses.copy()
            self.complex_subclasses_backup = self.complex_subclasses.copy()

            for (sub, super) in self.complex_subclasses:
                #print("Processing complex subclass relation: " + str(sub) + " subclass of " + str(super))
                equivalent = 0

                if len(super)> 1:
                    if self.profile in [Owl.Profile.OWL2_RL, Owl.Profile.OWL2_QL, Owl.Profile.OWL2_EL]:
                        # union of classes not allowed in equivalent class statements in some OWL2 Profiles
                        continue

                    equivalent = 0
                    for s in super:
                        # need to check that for every s a pair (c[0],s) exists in self.simple_subclasses
                        #print(len(self.simple_subclasses))
                        equivalent = len([(x, y) for (x, y) in self.simple_subclasses if x == s and y==sub[0]])>0
                        if equivalent==0:
                            break
                    # create equivalent class statement
                    if equivalent==0:
                        subclass_declaration = ET.Element("SubClassOf")
                        subclass_declaration.append(self.classes[sub[0]])
                        subclass_declaration.append(self._get_object_union(super))
                        self.root.append(subclass_declaration)
                    else:
                        logging.getLogger(__name__).info("Found equivalent classes: {0} and  {1} ".format(
                            sub[0], repr(super)))
                        equivalent_declaration = ET.Element("EquivalentClasses")
                        equivalent_declaration.append(self.classes[sub[0]])
                        equivalent_declaration.append(self._get_object_union(super))
                        self.root.append(equivalent_declaration)

                        self.equivalent_classes += 1

                        # check whether the union of classes on the super side are pairwise disjoint as well
                        filtered_classes = [c for c in self.disjointclasses if super[0] in c]
                        for s in super:
                            filtered_classes = [c for c in filtered_classes if s in c]
                        if len(filtered_classes)>0:
                            # classes are all disjoint
                            disjoint_declaration = ET.Element("DisjointUnion")
                            disjoint_declaration.append(self.classes[sub[0]])
                            for s in super:
                                disjoint_declaration.append(self.classes[s])
                            self.root.append(disjoint_declaration)

                elif len(sub)>1:
                    equivalent = 0
                    for s in sub:
                        # need to check that for every s a pair (s,super) exists in self.simple_subclasses
                        #print(len(self.simple_subclasses))
                        equivalent = len([(x, y) for (x, y) in self.simple_subclasses if x == super[0] and y==s])>0
                        if equivalent==0:
                            break
                    # create equivalent class statement
                    if equivalent==0:
                        subclass_declaration = ET.Element("SubClassOf")
                        subclass_declaration.append(self._get_object_intersection(sub))
                        subclass_declaration.append(self.classes[super[0]])
                        self.root.append(subclass_declaration)
                    else:
                        equivalent_declaration = ET.Element("EquivalentClasses")
                        equivalent_declaration.append(self._get_object_intersection(sub))
                        equivalent_declaration.append(self.classes[super[0]])
                        self.root.append(equivalent_declaration)

                        self.equivalent_classes += 1

            self.add_simple_subclasses()
            self.equivalents_processed = True

    def add_simple_subclasses(self):
        if self.equivalents_processed:
            return
        else:
            #print(str(len(self.simple_subclasses)) + " sets of Simple Subclasses to be Processed")
            #print(repr(self.simple_subclasses))

            while len(self.simple_subclasses)>0:
                (sub, super) = self.simple_subclasses.pop()
                #print("Checking whether " + super + " is a subclass of " + sub)
                #print ((super,sub) in self.simple_subclasses)
                if (super,sub) in self.simple_subclasses:
                    self.simple_subclasses.remove((super,sub))
                    logging.getLogger(__name__).info("Found equivalent classes: {0} and  {1} ".format(
                        sub, super))
                    # the inverse is a subclass as well, thus they are equivalent
                    subclass_declaration = ET.Element("EquivalentClasses")
                else:
                    subclass_declaration = ET.Element("SubClassOf")
                subclass_declaration.append(self.classes[sub])
                subclass_declaration.append(self.classes[super])
                self.root.append(subclass_declaration)
