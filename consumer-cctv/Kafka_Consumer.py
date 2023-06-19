from PIL import Image
from io import BytesIO
from kafka import KafkaConsumer
import sqlite3
# kafka 다운 받아야 함 (with zookeeper)


conn = sqlite3.connect('/Users/seonminbaek/Desktop/cctv_test.db', isolation_level=None)

c = conn.cursor()

c.execute("CREATE TABLE IF NOT EXISTS cctv_test (id integer PRIMARY KEY, pic text, name text)")

consumer = KafkaConsumer('kafka-cctv',
                         bootstrap_servers = ['localhost:9092'],
                         auto_offset_reset='earliest',
                         enable_auto_commit=True,
                         consumer_timeout_ms=1000
                         )

i = 0

for message in consumer :
    stream = BytesIO(message.value)
    c.execute('INSERT INTO cctv_test (id, pic, name) VALUES (?,?,?)',(i+10,message.value,"공학관"))
    #image = Image.open(stream).convert("RGB")
    #image.save('{}.jpg'.format(i))
    i+=1
    stream.close()

conn.close()
