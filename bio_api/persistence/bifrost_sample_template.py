bifrost_sample_template = {
    "name": "Sample ID here",
    "components": [
        {
            "name": "chewbbaca__v1.0.5__",
            "status": "Success"
        }
    ],
    "categories": {
        "contigs": {
            "summary": {
                "data": "/some/path"
            }
        },
        "species_detection": {
            "summary": {
                "detected_species": "Salmonella enterica"
            }
        },
        "sample_info": {
            "summary": {
                "institution": "SSI",
                "sample_name":"Sequence ID here"
            }
        },
        "cgmlst": {
            "name": "cgmlst",
            "component": {
                "name": "chewbbaca__v1.0.5__"
            },
            "summary": {
                "sequence_type": None,
                "call_percent": 43.66
            },
            "report": {
                "data":
                    {"alleles": {}}
            },
            "metadata": {
                "created_at": {
                    "$date": "2023-02-23T08:32:24Z"
                },
                "updated_at": {
                    "$date": "2023-02-23T08:32:24Z"
                }
            },
            "version": {
                "schema": [
                    "v2_1_0"
                ]
            }
        }
    },
    "metadata": {
        "created_at": {
            "$date": "2023-02-22T14:17:06Z"
        },
        "updated_at": {
            "$date": "2023-02-23T08:32:39Z"
        }
    },
    "version": {
        "schema": [
            "v2_1_0"
        ]
    }
}
