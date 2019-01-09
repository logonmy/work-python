from my_mongodb import MyMongo
import zlib
import bson
from cStringIO import StringIO
# f = open('../test1/tianyancha/detail.html')
# s = f.read()
# content = StringIO(f.read())

db = MyMongo().get_db()


# db['test'].save({'source': bson.binary.Binary(zlib.compress(s))})
# db['test'].save({'source': content.getvalue()})
print ''
print db['raw_result_gzcc'].find({'_id': {'$gt': bson.ObjectId('5bd90a48c02bfe18842558e9')}}).count()
