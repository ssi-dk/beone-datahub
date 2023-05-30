// This script can be executed from the command line ind the mongo container by typing:
// mongosh -f /scripts/find_sample_one.js

config.set('inspectDepth', Infinity);
db = connect( 'mongodb://localhost/bifrost_test' );
printjson(db.samples.find({},{
    'categories.sample_info.summary.sample_name': 1,
    'categories.species_detection.summary.detected_species': 1,
}));