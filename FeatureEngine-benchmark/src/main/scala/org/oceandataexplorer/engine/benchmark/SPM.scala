/** Copyright (C) 2017-2018 Project-ODE
 *
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
import org.apache.spark.rdd.RDD

import com.github.nscala_time.time.Imports._

import org.oceandataexplorer.engine.workflows._
import org.oceandataexplorer.engine.io.HadoopWavReader
import org.oceandataexplorer.engine.signalprocessing.SoundCalibration

// scalastyle:off

/**
 * Benchmark workflow main object
 */
object SPM {
  /**
   * Function runnning benchmark workflow on SPM dataset
   * @param args The arguments for the run. Two arguments (Ints) are expected:
   * - nNodes: The number of datarmor nodes used in this run.
   * - nFiles: The number of SPM wav files to be processed in this run.
   */
  def main(args: Array[String]): Unit = {
    val spark = SparkSession.builder.getOrCreate()

    // number of datarmor nodes used in this run
    val nNodes = args(0).toInt
    // number of files to be processed in this run
    val nFiles = args(1).toInt

    val inputBaseDir = new File("/home/datawork-alloha-ode/Datasets/SPM")
    val wavDir = new File(inputBaseDir.getCanonicalFile + "/PAM/SPMAuralA2010")
    val metadataFile = new File(inputBaseDir.getCanonicalFile + "/PAM/Metadata_SPMAuralA2010.csv")
    val outputBaseDir = new File("/home/datawork-alloha-ode/benchmark")

    // Signal processing parameters
    val recordSizeInSec = 1.0f
    val soundSamplingRate = 32768.0f
    val recordSizeInFrame = (recordSizeInSec * soundSamplingRate).toInt
    val recordSize = (recordSizeInSec * soundSamplingRate).toInt
    val windowSize = 256
    val windowOverlap = 128
    val nfft = 256
    val lowFreq = Some(0.2 * soundSamplingRate)
    val highFreq = Some(0.4 * soundSamplingRate)

    // Sound parameters
    val soundPath = wavDir.getCanonicalFile.toURI.toString
    val soundChannels = 1
    val soundSampleSizeInBits = 16

    /** read metadata & drop header
     * We're using the following fields of the metadata file (semi-colon separated csv):
     *   - 0: the wav file name, eg "A32C0000.WAV"
     *   - 9: the date on which the recording begins, eg "2010-04-12"
     *   - 10: the time on which the recording begins, eg "12:41:23"
     * For more information on the metadata file content see p39 of (french):
     * http://www.multi-electronique.com/files/AURAL/user/AURAL-M2_MANUEL_D_UTILISATION.pdf
     */
    val metadata = Source.fromFile(metadataFile).mkString.split("\n").drop(1).toList

    val soundsNameAndStartDate = metadata
      .map(fileMetadata => {
        val metadataArray = fileMetadata.split(";")
        val date = metadataArray(9).replace("/", "-")
        val time = metadataArray(10)

        (metadataArray(0), new DateTime(date + "T" + time, DateTimeZone.UTC))
      })
      .take(nFiles)

    val soundNames = soundsNameAndStartDate.map(_._1).reduce((p,n) => p + "," + n)
    val soundsPath = soundPath + "/{" + soundNames + "}"

    val runId = s"Example_${recordSizeInFrame}_${windowSize}_${windowOverlap}_$nfft"

    val resultsDestination = resourcesDir.getCanonicalFile.toURI.toString +
      s"/results/$nNodes/feature_engine_benchmark/" + runId

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
      .sort($"timestamp")
      .write
      .json(resultsDestination)

    spark.close()
  }
}
