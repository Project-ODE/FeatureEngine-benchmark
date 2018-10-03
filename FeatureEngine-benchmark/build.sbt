/** Copyright (C) 2017-2018 Project-ODE
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

// Project Settings
name := "FeatureEngine-benchmark"
version := "0.1"

// Scala version to use
scalaVersion := "2.11.12"

// Configuration for tests to run with Spark
fork in Test := true
parallelExecution in Test := false
javaOptions ++= Seq(
  "-Xms512M",
  "-Xmx2048M",
  "-XX:MaxPermSize=2048M",
  "-XX:+CMSClassUnloadingEnabled"
)

// Bouldless and hadoop-io-extensions Repositories needed for FeatureEngine dependancy resolution
resolvers += "Ode hadoop-io-extensions Repository" at "https://github.com/Project-ODE/hadoop-io-extensions/raw/repository"
resolvers += "Boundless Repository" at "http://repo.boundlessgeo.com/main/"
resolvers += "Ode FeatureEngine Repository" at "https://github.com/Project-ODE/FeatureEngine/raw/repository"

// Explicitly get scala version and don't show warnings
// https://mvnrepository.com/artifact/org.scala-lang/scala-library
libraryDependencies += "org.scala-lang" % "scala-library" % "2.11.12"

// https://github.com/Project-ODE/FeatureEngine
libraryDependencies += "org.oceandataexplorer" % "FeatureEngine_2.11" % "0.1"
