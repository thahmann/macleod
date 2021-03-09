import functools
import itertools
import xml.etree.ElementTree as ET
import enum as Enum
import xml.dom.minidom

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

    def __init__(self, filename, uri):
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
        self.disjointclasses = []
        self.subclass_of_class_union = []
        self.subclass_of_single_class = []

        self.disjoints_processed = False
        self.equivalents_processed = False

    def tostring(self, pretty_print=False):

        if not self.disjoints_processed:
            self.infer_disjoint_classes()
        if not self.equivalents_processed:
            self.infer_equivalent_classes()

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

        declaration = ET.SubElement(self.root, 'Declaration')
        owl_class = ET.SubElement(declaration, 'Class', attrib={'IRI': self.uri + class_name})
        self.classes[class_name] = owl_class
        return owl_class

    def declare_property(self, property_name):
        """
        Add a class to the OWL ontology

        :param str property_name
        :return Element property
        """

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

        if len(subclass) > 1:
            # TODO where does this come from? Is it an intersection or indeed a set of subclass relations
            subclass_element = self._get_object_intersection(subclass)
        else:
            # single subclass
            subclass_element = self.classes[subclass[0]]
            saved_subclass = subclass[0]

        if len(superclass) > 1:
            superclass_element = self._get_object_union(superclass)
            # TODO: really want to check whether this makes an EquivalentClass construct
            if saved_subclass is not None:
                #print("Found Object Union in Superclass to " + repr(saved_subclass))
                self.subclass_of_class_union.append((saved_subclass, superclass))
        else:
            superclass_element = self.classes[superclass[0]]
            if saved_subclass:
                self.subclass_of_single_class.append((saved_subclass, superclass[0]))

        subclass_declaration = ET.Element("SubClassOf")
        subclass_declaration.append(subclass_element)
        subclass_declaration.append(superclass_element)
        self.root.append(subclass_declaration)
        return subclass_declaration

    def add_subproperty(self, subproperty, superproperty):
        """
        Adds a subproperty property to the OWL ontology. Assumes that both the subproperty has already been added.

        :param Tuple(str, Owl.Relations) subproperty
        :param Tuple(str, Owl.Relations) superproperty
        """

        sub_name, sub_state = subproperty
        sup_name, sup_state = superproperty

        sub_element = self._get_object_inverse(sub_name) if sub_state == Owl.Relations.INVERSE else self.properties[sub_name]
        sup_element = self._get_object_inverse(sup_name) if sup_state == Owl.Relations.INVERSE else self.properties[sup_name]

        subproperty_declaration = ET.Element('SubObjectPropertyOf')

        subproperty_declaration.append(sub_element)
        subproperty_declaration.append(sup_element)
        self.root.append(subproperty_declaration)
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
                    print(name, 'This one')
                    union.append(self.classes[name])
                elif sign == Owl.Relations.INVERSE:
                    union.append(self._get_object_complement(name))
                else:
                    print(sign, name)
                    raise ValueError("HUH")
            else:
                union.append(self.classes[c])

        print(union_classes, ET.tostring(union))

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

        return intersection

    def _get_object_inverse(self, inverted_property):
        """
        Utility method which returns an ObjectInverseOf property for use in
        declarations.  Assumes that the class name provided has already been created. 

        :param lst(str) inverted_class, class to obtain the inverse of
        """

        inverse = ET.Element('ObjectInverseOf')
        inverse.append(self.properties[inverted_property])

        return inverse

    def _get_object_complement(self, inverted_class):
        """
        Utility method which returns an ObjectInverseOf property for use in
        declarations.  Assumes that the class name provided has already been created. 

        :param lst(str) inverted_class, class to obtain the inverse of
        """

        inverse = ET.Element('ObjectComplementOf')
        inverse.append(self.classes[inverted_class])

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
        Add an axiom declaring equivalence among a list of classes. If the list
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
        for d in self.disjointclasses:
            if disjoint_pair[0] in d:
                if not (disjoint_pair[1] in d):
                    d.append(disjoint_pair[1])
                new = False
                break
            elif disjoint_pair[1] in d:
                if not (disjoint_pair[0] in d):
                    d.append(disjoint_pair[0])
                new = False
                break
        if new:
            self.disjointclasses.append([disjoint_pair[0], disjoint_pair[1]])

        # do nothing immediately --> only processed at the very end
        # disjoint = ET.Element('DisjointClasses')
        # disjoint.append(self.classes[disjoint_pair[0]])
        # disjoint.append(self.classes[disjoint_pair[1]])
        # self.root.append(disjoint)

    def add_disjoint_properties(self, disjoint_pair):
        """
        Add an axiom declaring that two classes are disjoint
        """

        disjoint = ET.Element('DisjointObjectProperties')
        property_one, property_two = disjoint_pair

        element_one = self._get_object_inverse(property_one[0]) if property_one[1] == Owl.Relations.INVERSE else self.properties[property_one[0]]
        element_two = self._get_object_inverse(property_two[0]) if property_two[1] == Owl.Relations.INVERSE else self.properties[property_two[0]]
        disjoint.append(element_one)
        disjoint.append(element_two)
        self.root.append(disjoint)

    def declare_reflexive_property(self, reflexive_property):
        """
        Add a declaration that a property is reflexive
        """

        reflexive = ET.Element('ReflexiveObjectProperty')
        reflexive.append(self.properties[reflexive_property])
        self.root.append(reflexive)

    def declare_irreflexive_property(self, reflexive_property):
        """
        Add a declaration that a property is reflexive
        """

        reflexive = ET.Element('ReflexiveObjectProperty')
        reflexive.append(self.properties[reflexive_property])
        self.root.append(reflexive)

    def declare_symmetric_property(self, symmetric_property):
        """
        Add a declaration that a property is reflexive
        """

        symmetric = ET.Element('SymmetricObjectProperty')
        symmetric.append(self.properties[symmetric_property])
        self.root.append(symmetric)

    def declare_asymmetric_property(self, asymmetric_property):
        """
        Add a declaration that a property is reflexive
        """

        asymmetric = ET.Element('AsymmetricObjectProperty')
        asymmetric.append(self.properties[asymmetric_property])
        self.root.append(asymmetric)

    def declare_transitive_property(self, transitive_property):
        """
        Add a declaration that a property is reflexive
        """

        transitive = ET.Element('TransitiveObjectProperty')
        transitive.append(self.properties[transitive_property])
        self.root.append(transitive)

    def declare_functional_property(self, functional_property):
        """
        Add a declaration that a property is reflexive
        """

        functional = ET.Element('FunctionalObjectProperty')
        functional.append(self.properties[functional_property])
        self.root.append(functional)

    def declare_inverse_functional_property(self, functional_property):
        """
        Add a declaration that a property is reflexive
        """

        functional = ET.Element('InverseFunctionalObjectProperty')
        functional.append(self.properties[functional_property])
        self.root.append(functional)

    def declare_range_restriction(self, prop, restriction):
        """
        :param prop str, name of property being restricted
        :param list(tuple) restriction, list of tuples for classes
        """

        rr = ET.Element('ObjectPropertyRange')
        rr.append(self.properties[prop])

        if len(restriction) > 1:
            restriction_element = self._get_object_union(restriction)
        else:
            name, state = restriction[0]
            restriction_element = self.classes[name] if state != Owl.Relations.INVERSE else self._get_object_complement(name)

        rr.append(restriction_element)

        self.root.append(rr)

    def declare_domain_restriction(self, prop, restriction):
        """
        Add a declaration that a property is range restricted
        """

        dr = ET.Element('ObjectPropertyDomain')
        dr.append(self.properties[prop])

        if len(restriction) > 1:
            restriction_element = self._get_object_union(restriction)
        else:
            name, state = restriction[0]
            restriction_element = self.classes[name] if state != Owl.Relations.INVERSE else self._get_object_complement(name)

        dr.append(restriction_element)

        self.root.append(dr)

    def declare_all_values_from_subclass(self, relation, subclass, limit):
        """
        Add a subclass axiom where the superclass is a allValuesFrom class expression
        
        :param str relation, name of relation universal is over
        :param list(str) subclass, list of subclass names joined in union
        :param list(str) limit, list of limiting class names
        """

        # TODO: For now just make the whole subclass here instead of naming the anonymous
        #       class that is defined by the allValuesFrom. The approach affects the profile
        #       that the produced ontology will fall into.
        subclass_element = ET.Element('SubClassOf')

        if len(subclass) > 1:
            subclass_element.append(self._get_object_union(subclass))
        else:
            subclass_element.append(self.classes[subclass[0]])

        all_values_from = ET.Element('ObjectAllValuesFrom')
        all_values_from.append(self.properties[relation])

        if len(limit) > 1:
            all_values_from.append(self._get_object_union(limit))
        else:
            all_values_from.append(self.classes[limit[0]])

        subclass_element.append(all_values_from)
        self.root.append(subclass_element)

    def declare_some_values_from_subclass(self, relation, subclass, limit):
        """
        Add a subclass axiom where the superclass is a allValuesFrom class expression
        """

        # TODO: For now just make the whole subclass here instead of naming the anonymous
        #       class that is defined by the allValuesFrom. The approach affects the profile
        #       that the produced ontology will fall into.
        subclass_element = ET.Element('SubClassOf')


        if len(subclass) > 1:
            subclass_element.append(self._get_object_union(subclass))
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

        print("Sets of Disjoint Classes = " + str(len(self.disjointclasses)))

        for s in self.disjointclasses:
            disjoint = ET.Element('DisjointClasses')
            for c in s:
                disjoint.append(self.classes[c])
            self.root.append(disjoint)
        self.disjoints_processed = True

    def infer_equivalent_classes(self):
        """
        Inferring any equivalent class definitions from subclass definitions that use unions
        :return:
        """
        #print("Sets of Subclasses of Class Unions = " + str(len(self.subclass_of_class_union)))
        for (sub, super) in self.subclass_of_class_union:
            #print(sub + " subclass of " + str(super))
            equivalent = 0
            for s in super:
                # need to check that for every s a pair (c[0],s) exists in self.subclass_of_single_class
                #print(len(self.subclass_of_single_class))
                if len([(x, y) for (x, y) in self.subclass_of_single_class if x == s and y==sub])>0:
                    continue
                else:
                    break
            # create equivalent class statement
            equivalent_declaration = ET.Element("EquivalentClasses")
            equivalent_declaration.append(self.classes[sub])
            equivalent_declaration.append(self._get_object_union(super))
            self.root.append(equivalent_declaration)

            # check whether the union of classes on the super side are pairwise disjoint as well
            filtered_classes = [c for c in self.disjointclasses if super[0] in c]
            for s in super:
                filtered_classes = [c for c in filtered_classes if s in c]
            if len(filtered_classes)>0:
                # classes are all disjoint
                disjoint_declaration = ET.Element("DisjointUnion")
                disjoint_declaration.append(self.classes[sub])
                for s in super:
                    disjoint_declaration.append(self.classes[s])
                self.root.append(disjoint_declaration)

        self.equivalents_processed = True
