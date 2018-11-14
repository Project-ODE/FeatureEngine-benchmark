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

package org.oceandataexplorer.engine.benchmark


import java.io.File
import scala.io.Source

import org.apache.spark.sql._

import com.github.nscala_time.time.Imports._

import org.oceandataexplorer.engine.benchmark.workflow.BenchmarkWorkflow

// scalastyle:off

/**
 * Benchmark workflow main object
 */
object Example {
  /**
   * Function runnning benchmark workflow on example files
   * @param args The arguments for the run
   */
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder.getOrCreate()

    import spark.implicits._

    val resourcesDir = new File("../test/resources")
    val metadataFile = new File("../test/resources/metadata/Example_metadata.csv")

    // Signal processing parameters
    val recordSizeInSec = 1.0f
    val soundSamplingRate = 1500.0f
    val windowSize = 256
    val windowOverlap = 128
    val nfft = 256
    val lowFreq = Some(0.2 * soundSamplingRate)
    val highFreq = Some(0.4 * soundSamplingRate)

    // Sound parameters
    val soundsPath = resourcesDir.getCanonicalFile.toURI.toString + "/sounds"
    // read metadata & drop header
    val metadata = Source.fromFile(metadataFile).mkString.split("\n").drop(1).toList
    val soundsNameAndStartDate = metadata.map(fileMetadata => {
      val metadataArray = fileMetadata.split(",")
      (metadataArray(0), new DateTime(metadataArray(1), DateTimeZone.UTC))
    })

    val soundChannels = 1
    val soundSampleSizeInBits = 16

    val resultsDestination = resourcesDir.getCanonicalFile.toURI.toString +
      "/results/feature_engine_benchmark"

    val benchWorkflow = new BenchmarkWorkflow(
      spark,
      recordSizeInSec,
      windowSize,
      windowOverlap,
      nfft,
      lowFreq,
      highFreq
    )

    val results = benchWorkflow(
      soundsPath,
      soundsNameAndStartDate,
      soundSamplingRate,
      soundChannels,
      soundSampleSizeInBits
    )

    results
      .repartition(1)
      .sort($"timestamp")
      .write
      .json(resultsDestination)

    spark.close()
  }
}
