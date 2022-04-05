package conference.command

import org.apache.flink.api.common.eventtime.WatermarkStrategy
import org.apache.flink.api.scala.createTypeInformation
import org.apache.flink.connector.jdbc.{
  JdbcConnectionOptions,
  JdbcExecutionOptions,
  JdbcSink,
  JdbcStatementBuilder
}
import org.apache.flink.connector.kafka.source.KafkaSource
import org.apache.flink.connector.kafka.source.reader.deserializer.KafkaRecordDeserializationSchema
import org.apache.flink.streaming.api.functions.sink.SinkFunction
import org.apache.flink.streaming.api.scala.StreamExecutionEnvironment
import org.apache.kafka.clients.consumer.ConsumerConfig
import org.apache.kafka.common.serialization.Deserializer
import org.json4s._
import org.json4s.jackson.JsonMethods._

import java.sql.PreparedStatement
import java.util.Properties

object CommandHandler extends App {

  val statementBuilder: JdbcStatementBuilder[BookingEvent] =
    new JdbcStatementBuilder[BookingEvent] {
      override def accept(
          preparedStatement: PreparedStatement,
          bookingEvent: BookingEvent
      ): Unit = {
        preparedStatement.setString(1, bookingEvent.date)
        preparedStatement.setLong(2, bookingEvent.number_of_seats)
        preparedStatement.setLong(3, bookingEvent.number_of_seats)
      }
    }

  val jdbcSink: SinkFunction[BookingEvent] = JdbcSink.sink[BookingEvent](
    """
        |INSERT INTO conference_seats (date, booked_seats)
        |VALUES (?, ?)
        |ON CONFLICT (date) DO UPDATE SET booked_seats = ?
        |""".stripMargin,
    statementBuilder,
    JdbcExecutionOptions
      .builder()
      .withBatchSize(1000)
      .withBatchIntervalMs(200)
      .withMaxRetries(0)
      .build(),
    new JdbcConnectionOptions.JdbcConnectionOptionsBuilder()
      .withUrl("jdbc:postgresql://localhost:5432/postgres")
      .withDriverName("org.postgresql.Driver")
      .withUsername("postgres")
      .withPassword("admin123")
      .build()
  )

  val env = StreamExecutionEnvironment.getExecutionEnvironment

  val topics = List("bookings")
  val properties = new Properties()
  properties.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092")

  val bookingEventDeserializer = KafkaRecordDeserializationSchema.valueOnly(
    classOf[BookingEventDeserializer]
  )
  val source = KafkaSource
    .builder()
    .setProperties(properties)
    .setDeserializer(bookingEventDeserializer)
    .setTopics(topics: _*)
    .build()

  val bookingEventStream = env
    .fromSource(source, WatermarkStrategy.noWatermarks(), "Kafka Source")
    .keyBy(bookingEvent => bookingEvent.date)
    .reduce { (event1, event2) =>
      BookingEvent(
        event2.timestamp,
        event2.date,
        event1.number_of_seats + event2.number_of_seats
      )
    }

  bookingEventStream.addSink(jdbcSink).name("jdbc-sink")

  env.execute("Stock stream")
}

case class BookingEvent(timestamp: Long, date: String, number_of_seats: Int)

class BookingEventDeserializer extends Deserializer[BookingEvent] {

  override def deserialize(topic: String, data: Array[Byte]): BookingEvent = {
    implicit val formats: Formats = DefaultFormats
    val json = parse(new String(data))
    json.extract[BookingEvent]
  }
}
