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

import org.oceandataexplorer.engine.io.HadoopWavReader
import org.oceandataexplorer.engine.signalprocessing.SoundCalibration

import org.apache.spark.rdd.RDD
import org.apache.spark.sql.SparkSession

import org.apache.spark.sql._

import com.github.nscala_time.time.Imports._

import org.oceandataexplorer.engine.workflows._

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

    val resourcesDir = new File("../test/resources")
    val metadataFile = new File("../test/resources/metadata/Example_metadata.csv")


    // Signal processing parameters
    val soundSamplingRate = 1500.0f
    val recordSizeInSec = 1.0f
    val recordSizeInFrame = (soundSamplingRate * recordSizeInSec).toInt
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

    val runId = s"Example_${recordSizeInFrame}_${windowSize}_${windowOverlap}_${nfft}"

    val resultsDestination = resourcesDir.getCanonicalFile.toURI.toString +
      "/results/feature_engine_benchmark/" + runId

    val hadoopWavReader = new HadoopWavReader(
      spark,
      recordSizeInSec
    )

    val records = hadoopWavReader.readWavRecords(
      soundsPath,
      soundsNameAndStartDate,
      soundSamplingRate,
      soundChannels,
      soundSampleSizeInBits
    )

    val calibrationClass = SoundCalibration(0.0)

    val calibratedRecords: RDD[Record] = records.mapValues(chan => chan.map(calibrationClass.compute))


    val welchSplWorkflow = new WelchSplWorkflow(
      spark,
      recordSizeInSec,
      windowSize,
      windowOverlap,
      nfft
    )

    val welchsSpls = welchSplWorkflow(
      calibratedRecords,
      soundSamplingRate
    )

    val tolWorkflow = new TolWorkflow(
      spark,
      recordSizeInSec,
      lowFreq,
      highFreq
    )

    val tols = tolWorkflow(
      calibratedRecords,
      soundSamplingRate
    )


    import spark.implicits._

    welchsSpls
      .join(tols, tols("timestamp") === welchsSpls("timestamp"))
      .drop(tols("timestamp"))
      .repartition(1)
      .sort($"timestamp")
      .write
      .json(resultsDestination)

    spark.close()
  }
}
