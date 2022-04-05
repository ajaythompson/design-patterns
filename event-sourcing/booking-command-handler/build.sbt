import Dependencies._

ThisBuild / scalaVersion := "2.12.15"
ThisBuild / version := "0.1.0-SNAPSHOT"
ThisBuild / organization := "com.example"
ThisBuild / organizationName := "example"

val flink_version = "1.14.4"

lazy val root = (project in file("."))
  .settings(
    name := "booking-command-handler",
    resolvers += "Confluent" at "https://packages.confluent.io/maven/",
    libraryDependencies += scalaTest % Test,
    libraryDependencies += "org.apache.flink" %% "flink-connector-kafka" % flink_version,
    libraryDependencies += "org.apache.flink" %% "flink-streaming-scala" % flink_version,
    libraryDependencies += "org.apache.flink" %% "flink-clients" % flink_version,
    libraryDependencies += "org.apache.flink" %% "flink-connector-jdbc" % flink_version,
    libraryDependencies += "org.json4s" %% "json4s-jackson" % "4.0.4",
    libraryDependencies += "org.postgresql" % "postgresql" % "42.3.3"
  )

// See https://www.scala-sbt.org/1.x/docs/Using-Sonatype.html for instructions on how to publish to Sonatype.
