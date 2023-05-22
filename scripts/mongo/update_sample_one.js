// This script can be executed from the command line ind the mongo container by typing:
// mongosh -f /scripts/find_sample_one.js

config.set('inspectDepth', Infinity);
db = connect( 'mongodb://localhost/bifrost_test' );
db.samples.updateOne(
    {_id: ObjectId("000000000000000000000001")},
    {
        $set: {'categories.sample_info.summary.sample_name': '0000000001'}
    }
);