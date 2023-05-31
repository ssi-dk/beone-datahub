// This script can be executed from the command line ind the mongo container by typing:
// mongosh -f /scripts/find_sample_one.js

config.set('inspectDepth', Infinity);
db = connect( 'mongodb://localhost/bifrost_test' );
db.samples.updateMany(
    {'categories.sample_info.summary.institution': {$exists: false}},
    {$set: {'categories.sample_info.summary.institution': 'FVST'}}
);