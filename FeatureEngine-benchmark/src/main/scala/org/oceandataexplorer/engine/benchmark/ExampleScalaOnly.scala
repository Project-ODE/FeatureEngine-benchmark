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
import java.net.URI

import scala.collection.parallel._
import scala.concurrent.forkjoin.ForkJoinPool

// scalastyle:off

/**
 * Benchmark workflow main object
 */
object ExampleScalaOnly {
  /**
   * Function runnning benchmark workflow on example files
   * @param args The arguments for the run
   */
  def main(args: Array[String]): Unit = {
    val resourcesDir = new File("../test/resources")
    val wavFilesMetadataFile = new File("../test/resources/metadata/Example_metadata.csv")


    // Signal processing parameters
    val soundSamplingRate = 1500.0f
    val recordSizeInSec = 1.0f
    val windowSize = 256
    val windowOverlap = 128
    val nfft = 256
    val lowFreqTOL = Some(0.2 * soundSamplingRate)
    val highFreqTOL = Some(0.4 * soundSamplingRate)

    // Sound parameters
    val soundsPath = resourcesDir.getCanonicalFile.toURI.toString + "/sounds"
    // read wavFilesMetadata & drop header
    val wavFilesMetadata = Source.fromFile(wavFilesMetadataFile).mkString.split("\n").drop(1).toList
    val soundsNameAndStartDate = wavFilesMetadata.map(wavFileMetadata => {
      val metadataArray = wavFileMetadata.split(",")
      (metadataArray(0), metadataArray(1))
    })

    val soundChannels = 1
    val soundSampleSizeInBits = 16

    val runId = s"Example_${recordSizeInSec}_${windowSize}_${windowOverlap}_$nfft"

    val resultsDestination = resourcesDir.getCanonicalFile.toURI.toString +
      "results/scala_only/1/" + runId

    val resultDestinationFile = new File(new URI(resultsDestination))

    if (!resultDestinationFile.exists()) {
      resultDestinationFile.mkdirs()
    }

    val handlers = soundsNameAndStartDate.map{ case (soundName, soundStartDate) => {
        val soundUri = new URI(soundsPath + "/" + soundName)
        val soundId = soundName.split("_")(0)

        SingleFileHandler(
          recordSizeInSec: Float,
          windowSize: Int,
          windowOverlap: Int,
          nfft: Int,
          lowFreqTOL: Option[Double],
          highFreqTOL: Option[Double],
          soundUri: URI,
          soundId: String,
          soundSamplingRate: Float,
          soundChannels: Int,
          soundSampleSizeInBits: Int,
          soundStartDate: String,
          resultsDestination: String
        )
      }
    }
    .toVector
    .par

    val pool = new scala.concurrent.forkjoin.ForkJoinPool(2)
    handlers.tasksupport = new ForkJoinTaskSupport(pool)

    handlers.foreach(_.execute)

    pool.shutdown()
  }
}
