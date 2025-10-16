import xml.etree.ElementTree as ET
import json

def parse_and_reduce_xml(xml_file, output_file="schema_reduced.json"):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    reduced_tables = []

    for item in root.findall(".//ItemTable"):
        table_name = item.findtext("TableName")
        description = item.findtext("TableComment")

        # Foreign keys (solo table, key, ref)
        foreign_keys = []
        for fk in item.findall(".//TableForeignkey"):
            foreign_keys.append({
                "table": fk.findtext("ForeignkeyTable"),
                "key": fk.findtext("ForeignkeyKey"),
                "ref": fk.findtext("ForeignkeyRef"),
            })

        # Fields (solo name, key, description)
        fields = []
        for field in item.findall(".//TableField"):
            fields.append({
                "name": field.findtext("FieldName"),
                "key": field.findtext("FieldKey") == "1",
                "description": field.findtext("FieldComment") or ""
            })

        reduced_tables.append({
            "table_name": table_name,
            "description": description or "",
            "foreign_keys": foreign_keys,
            "fields": fields
        })

    # Salva in JSON
    with open(output_file, "w") as f:
        json.dump(reduced_tables, f, indent=2, ensure_ascii=False)

    print(f"✅ Schema ridotto salvato in {output_file}")


if __name__ == "__main__":
    parse_and_reduce_xml("table_summary_ahbase.xml")
