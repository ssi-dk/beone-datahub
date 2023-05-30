// This script can be executed from the command line ind the mongo container by typing:
// mongosh -f /scripts/find_sample_one.js

config.set('inspectDepth', Infinity);
db = connect( 'mongodb://localhost/bifrost_test' );
db.samples.updateOne(
    {_id: ObjectId("6380c4dd72ea90601dbf01cb")},
    {
        $set: {'org': 'FVST'}
    }
);