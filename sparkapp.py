from __future__ import print_function
from pyspark import SparkConf, SparkContext
from pyspark.streaming import  StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from decimal import Decimal
from kafka import KafkaProducer
import json
import boto3

producer = KafkaProducer(bootstrap_servers='172.31.86.66:9092')

def handler(message, topic):
    records = message.collect()
    for record in records:
        producer.send(topic, json.dumps(record))
        producer.flush()

def main():

    sc = SparkContext(appName="SparkApp")
    ssc = StreamingContext(sc, 3)
    topic = 'iot-data-sensor'

    kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": '172.31.86.66:9092'})

    jsonRDD = kvs.map(lambda x: json.loads(x[1]))
    jsonRDD.pprint()
    jsonRDD.foreachRDD(lambda x: save2('alldata', x))

    #Rata-rata setiap 1 detik
    #temp = jsonRDD.map(lambda x: save('suhu', x['sensor'], x['waktu'], x['suhu']))
    avgsuhu = jsonRDD.map(lambda x: (x['waktu'], (x['suhu'], 1))) \
          .reduceByKey(lambda x,y: (x[0]+y[0], x[1]+y[1])) \
          .map(lambda x: (x[0], float(x[1][0])/x[1][1])).transform(lambda x: x.sortBy(lambda a: a[0]))
    avgsuhu.pprint()


    avgsuhu.foreachRDD(lambda x: handler(x, 'avgsuhu'))
    avgsuhu.foreachRDD(lambda x: save('suhu', x))

#Kelembapan
    #temp = jsonRDD.map(lambda x: save('kelembapan', x['sensor'], x['waktu'], x['kelembapan']))
    avgkelembapan = jsonRDD.map(lambda x: (x['waktu'], (x['kelembapan'], 1))) \
          .reduceByKey(lambda x,y: (x[0]+y[0], x[1]+y[1])) \
          .map(lambda x: (x[0], float(x[1][0])/x[1][1])).transform(lambda x: x.sortBy(lambda a: a[0]))
    avgkelembapan.pprint()

    avgkelembapan.foreachRDD(lambda x: handler(x, 'avgkelembapan'))
    avgkelembapan.foreachRDD(lambda x: save('kelembapan', x))

#pH
    #temp = jsonRDD.map(lambda x: save('vpH', x['sensor'], x['waktu'], x['pH']))
    avgph = jsonRDD.map(lambda x: (x['waktu'], (x['pH'], 1))) \
          .reduceByKey(lambda x,y: (x[0]+y[0], x[1]+y[1])) \
          .map(lambda x: (x[0], float(x[1][0])/x[1][1])).transform(lambda x: x.sortBy(lambda a: a[0]))
    avgph.pprint()

    avgph.foreachRDD(lambda x: handler(x, 'avgpH'))
    avgph.foreachRDD(lambda x: save('vpH', x))

    ssc.start()
    ssc.awaitTermination()

def save(table, message):
  dynamodb = boto3.resource('dynamodb')
  tabledb = dynamodb.Table(table)
  #tabledb.put_item(Item=nilai)
  records = message.collect()
  for record in records:
     temp = json.loads(json.dumps(record), parse_float=Decimal)
     tabledb.put_item(Item={'waktu':str(temp[0]),'nilai':temp[1]})


def save2(table, message):
  dynamodb = boto3.resource('dynamodb')
  tabledb = dynamodb.Table(table)
  #tabledb.put_item(Item=nilai)
  records = message.collect()
  for record in records:
     temp = json.loads(json.dumps(record))
     tabledb.put_item(Item={'id':temp['id'],'waktu':temp['waktu'],'sensor':temp['sensor'],'lat':temp['lat'],'lng':temp['lng'],'suhu':temp['suhu'], 'ph':temp['pH'],'kelembapan':temp['kelembapan']})

if __name__ == "__main__":
    main()

