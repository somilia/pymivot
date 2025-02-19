"""
Set of 2 classes operating the join operations.
Retrieve ad format data that are joined with a particular primary row

Created on 22 Dec 2021

@author: laurentmichel
"""
from copy import deepcopy
from pymivot.validator.mivot_validator.instance_checking.xml_interpreter.exceptions import (
    MappingException,
)
from pymivot.validator.mivot_validator.instance_checking.xml_interpreter.table_iterator import (
    TableIterator,
)
from pymivot.validator.mivot_validator.instance_checking import logger
from pymivot.validator.mivot_validator.instance_checking.xml_interpreter.static_reference_resolver import (
    StaticReferenceResolver,
)


class Where:
    """
    Evaluator of foreign data against a primary key
    """

    def __init__(self, resource_seeker, foreignkey, primarykey, fk_is_constant=False):
        """
        :param foreignkey: identifier of the column used for the foreign key
        :param primarykey: identifier of the column used for the primary key
        """
        self.resource_seeker = resource_seeker
        self.foreignkey = foreignkey
        # Number of foreign table used as foreign key
        self.foreign_col = None
        self.primarykey = primarykey
        # Number of primary table used as primary key
        self.primary_col = None
        # flag telling thta the primary key must be evaluated against a constant value
        self.fk_is_constant = fk_is_constant

    def __repr__(self):
        return (
            f"(foreign: {self.primarykey}:{self.foreign_col}  "
            f"primary: {self.primarykey}:{self.primary_col})"
        )

    def set_primary_col(self, primary_table_ref):
        index_map = self.resource_seeker.get_id_index_mapping(primary_table_ref)
        self.primary_col = index_map[self.primarykey]

    def set_foreign_col(self, foreign_table_ref):
        if self.fk_is_constant is False:
            index_map = self.resource_seeker.get_id_index_mapping(foreign_table_ref)
            self.foreign_col = index_map[self.foreignkey]

    def match(self, primary_key_value, foreign_row):
        """
        Returns True if the value of the foreign key read out of the
        foreign row matches primary_key_value
        The comparisons are based on string representations of the evaluated values
        :param primary_key: value of the primary key
        :param foreign_row: Numpy data row of the joined table that must
               be checked against the primary key
        """
        if self.fk_is_constant is False:
            return str(foreign_row[self.foreign_col]) == str(primary_key_value)
        return str(self.foreignkey) == str(foreign_row[self.primary_col])


class JoinOperator:
    """
    classdocs
    """

    def __init__(self, model_view, table_ref, xml_join_block):
        """
        Constructor
        """
        self.resource_seeker = model_view.resource_seeker
        self.annotation_seeker = model_view.annotation_seeker
        self.table_ref = table_ref
        self.xml_join_block = xml_join_block
        self.target_id = None
        self.target_table_id = None
        self.wheres = []
        self.table_iterator = None
        self.last_joined_data = None

    def _set_filter(self):
        for ele in self.xml_join_block.xpath("//*[starts-with(name(), 'JOIN_')]"):
            self.target_id = ele.get("dmref")

        self.target_table_id = self.annotation_seeker.get_globals_collection(
            self.target_id
        )
        if self.target_table_id is not None:
            raise MappingException("Join with GLOBALS not implemented yet")

        for tableref in self.annotation_seeker.get_tablerefs():
            if (
                self.annotation_seeker.get_templates_instance_by_dmid(
                    tableref, self.target_id
                )
                is not None
            ):
                self.foreign_xml_instance = (
                    self.annotation_seeker.get_templates_instance_by_dmid(
                        tableref, self.target_id
                    )
                )
                self.target_table_id = tableref
                logger.debug(
                    "Found INSTANCE dmid=%s in table %s ",
                    self.target_id,
                    self.target_table_id,
                )
                break

        if self.target_table_id is None:
            raise MappingException(
                "Cannot find joined INSTANCE dmid={}".format(self.target_id)
            )

        for ele in self.xml_join_block.xpath("//WHERE"):
            if ele.get("foreignkey") is not None:
                where = Where(
                    self.resource_seeker, ele.get("foreignkey"), ele.get("primarykey")
                )
            else:
                where = Where(
                    self.resource_seeker,
                    ele.get("value"),
                    ele.get("primarykey"),
                    fk_is_constant=True,
                )

            where.set_primary_col(self.table_ref)
            where.set_foreign_col(self.target_table_id)
            self.wheres.append(where)

        self.table_iterator = TableIterator(
            self.target_table_id,
            self.resource_seeker.get_table((self.target_table_id)).to_table(),
        )

    def _set_foreign_instance(self):
        # TODO should be done once for ever
        index_map = self.resource_seeker.get_id_index_mapping(self.target_table_id)
        for ele in self.foreign_xml_instance.xpath("//ATTRIBUTE"):
            ref = ele.get("ref")
            if ref is not None:
                ele.attrib["index"] = str(index_map[ref])

    def get_matching_data(self, primary_row):
        retour = []
        self.table_iterator._rewind()
        while True:
            row = self.table_iterator._get_next_row()
            if row is None:
                break
            is_valid = True
            for where in self.wheres:
                # the primary col is in the GLOBALS: no row and the foreign_key is constant
                if primary_row is None:
                    where_match = where.match(None, row)
                else:
                    where_match = where.match(primary_row[where.primary_col], row)

                if where_match is False:
                    is_valid = False
                    break
            if is_valid is True:
                retour.append(row)
        self.last_joined_data = retour
        return retour

    def get_matching_model_view(self, resolve_ref=True):
        if self.last_joined_data is None:
            return None
        retour = []

        for joined_row in self.last_joined_data:
            templates_copy = deepcopy(self.foreign_xml_instance)
            for ele in templates_copy.xpath("//FOREIGN_KEY"):
                ref = ele.get("ref")
                if ref is not None:
                    # We add the PK value for the current row,
                    # so that the ref can be resolved as a static one
                    ele.attrib["value"] = str(joined_row[ref])
            if resolve_ref is True:
                StaticReferenceResolver.resolve(
                    self.annotation_seeker, self.table_ref, templates_copy
                )

            # resolve references in attributes
            for ele in templates_copy.xpath("//ATTRIBUTE"):
                ref = ele.get("ref")
                if ref is not None:
                    index = ele.attrib["index"]
                    ele.attrib["value"] = str(joined_row[int(index)])
            retour.append(templates_copy)
        return retour
