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

import java.io.{File, FileOutputStream}

import org.oceandataexplorer.engine.workflows._

import java.net.URI

import org.joda.time.{DateTime, DateTimeZone}
import play.api.libs.json._


// scalastyle:off

case class SingleFileHandler (
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
) extends Runnable {
  /**
   * Worker class applying [[ScalaBenchmarkWorkflow]] to a wav file.
   */

  val recordSizeInFrame: Int = (soundSamplingRate * recordSizeInSec).toInt

  val scalaOnlyWorkflow = new ScalaBenchmarkWorkflow(
    recordSizeInSec,
    windowSize,
    windowOverlap,
    nfft,
    lowFreqTOL,
    highFreqTOL
  )

  override def run(): Unit = {
    val results = scalaOnlyWorkflow(
      soundUri,
      soundSamplingRate,
      soundChannels,
      soundSampleSizeInBits,
      soundStartDate
    )

    val resultFileName = s"${soundId}_${recordSizeInFrame}_${windowSize}_${windowOverlap}_$nfft.json"

    val resultFile = new File(
      new URI(resultsDestination + "/" + resultFileName)
    )

    val fos = new FileOutputStream(resultFile)

    results.foreach(
      record => {
        val jsonRecord = Json.obj(
          "timestamp" -> new DateTime(record._1, DateTimeZone.UTC).toString,
            "welch" -> record._2,
            "spl" -> record._3,
            "tol" -> record._4
          )

          fos.write((jsonRecord.toString + "\n").getBytes("UTF-8"))

      }
    )

    fos.close()
  }
}
